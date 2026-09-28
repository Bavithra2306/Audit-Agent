from uuid import uuid4

import magic
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.graph.workflow import build_workflow
from app.models.invoice import Invoice
from app.repositories.invoice_repository import (
    find_invoice_by_identity,
    get_or_create_invoice,
    get_invoice_by_id,
    get_next_version_number,
    create_invoice_version,
    set_current_version,
    get_all_invoices_repository,
)
from app.services.file_service import (
    MAX_FILE_SIZE,
    ALLOWED_MIME_TYPES,
    is_valid_docx,
    compute_file_hash,
    find_duplicate_version,
    save_to_staging,
    promote_to_permanent,
    discard_staged_file,
)


# ---------------------------------------------------------------
# Shared: validate + hash + stage. Used by BOTH initial + re-audit.
# ---------------------------------------------------------------

async def _validate_and_stage(file: UploadFile) -> dict:

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5 MB")

    mime_type = magic.from_buffer(content, mime=True)

    if mime_type in ALLOWED_MIME_TYPES:
        extension = ALLOWED_MIME_TYPES[mime_type]

    elif mime_type == "application/octet-stream" and is_valid_docx(content):
        extension = ".docx"

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {mime_type}",
        )

    file_hash = compute_file_hash(content)
    staging_path = save_to_staging(content, extension)

    return {
        "staging_path": staging_path,
        "extension": extension,
        "file_hash": file_hash,
        "original_filename": file.filename,
        "stored_filename": staging_path.name,
    }


# ---------------------------------------------------------------
# Invoice number typed in by the user (file had none)
# ---------------------------------------------------------------

def _clean_invoice_number(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    if len(value) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invoice number must be 100 characters or fewer",
        )

    return value


# ---------------------------------------------------------------
# Shared: run graph, then branch on outcome (persist vs discard)
# ---------------------------------------------------------------

def _run_and_finalize(
    db: Session,
    *,
    invoice_id: int | None,
    is_reaudit: bool,
    existing_invoice_number: str | None,
    existing_company_name: str | None,
    provided_invoice_number: str | None,
    staged: dict,
) -> dict:

    workflow = build_workflow()

    result = workflow.invoke(
        {
            "invoice_id": invoice_id,
            "is_reaudit": is_reaudit,
            "existing_invoice_number": existing_invoice_number,
            "existing_company_name": existing_company_name,
            "provided_invoice_number": provided_invoice_number,
            "staging_path": str(staged["staging_path"]),
            "original_filename": staged["original_filename"],
            "stored_filename": staged["stored_filename"],
            "file_hash": staged["file_hash"],
        }
    )

    status = result["status"]

    # -----------------------------------------------------------
    # File has no invoice number — nothing saved, ask the user
    # -----------------------------------------------------------
    if status == "NEEDS_INVOICE_NUMBER":
        discard_staged_file(staged["staging_path"])
        return {
            "invoice_id": invoice_id,
            "status": status,
            "explanation": (
                "The uploaded file has no invoice number. "
                "Please enter the invoice number."
            ),
        }

    # -----------------------------------------------------------
    # REJECTED, or FAILED on a brand-new upload (no company name =
    # no identity, so there is no invoice to attach a version to)
    # -----------------------------------------------------------
    if status == "REJECTED" or (status == "FAILED" and invoice_id is None):
        discard_staged_file(staged["staging_path"])
        return {
            "invoice_id": invoice_id,
            "status": status,
            "explanation": result["explanation"],
        }

    # -----------------------------------------------------------
    # PASSED / DISCREPANCY_FOUND / FAILED (re-audit) — all get an
    # InvoiceVersion row + a promoted file, so failures are inspectable.
    # -----------------------------------------------------------

    if invoice_id is None:
        existing = find_invoice_by_identity(
            db,
            result["invoice"].company_name,
            result["invoice"].invoice_number,
        )

        if existing is not None:
            discard_staged_file(staged["staging_path"])
            raise HTTPException(
                status_code=409,
                detail=(
                    f"An invoice from '{existing.company_name}' with number "
                    f"'{existing.invoice_number}' already exists "
                    f"(Invoice ID {existing.id}). "
                    f"Use the re-audit endpoint for that invoice instead."
                ),
            )

        invoice = get_or_create_invoice(
            db,
            result["invoice"].company_name,
            result["invoice"].invoice_number,
        )
    else:
        invoice = get_invoice_by_id(db, invoice_id)

    version_number = get_next_version_number(db, invoice.id)

    file_meta = {
        "original_filename": staged["original_filename"],
        "stored_filename": staged["stored_filename"],
        "file_hash": staged["file_hash"],
        # file_path filled in AFTER promotion, below
    }

    # FAILED never reached calculate/validate, so these are absent —
    # create_invoice_version tolerates missing calculated/validation.
    calculated = result.get("calculated", {})

    version = create_invoice_version(
        db,
        invoice.id,
        version_number,
        result["invoice"],
        calculated,
        status,
        result["explanation"],
        file_meta,
    )

    set_current_version(db, invoice, version)

    final_path = promote_to_permanent(
        staged["staging_path"],
        invoice.id,
        version_number,
        status,
        staged["extension"],
    )

    version.file_path = str(final_path)
    db.add(version)
    db.commit()
    db.refresh(invoice)

    return {
        "invoice_id": invoice.id,
        "version_number": version_number,
        "status": status,
        "explanation": result["explanation"],
        "discrepancies": result.get("validation", {}).get("discrepancies", []),
    }


# ---------------------------------------------------------------
# INITIAL upload
# ---------------------------------------------------------------

async def upload_invoice_service(
    db: Session,
    file: UploadFile,
    invoice_number: str | None = None,
) -> dict:

    # Clean first, so a bad value fails before anything is staged
    provided_invoice_number = _clean_invoice_number(invoice_number)

    staged = await _validate_and_stage(file)

    return _run_and_finalize(
        db,
        invoice_id=None,
        is_reaudit=False,
        existing_invoice_number=None,
        existing_company_name=None,
        provided_invoice_number=provided_invoice_number,
        staged=staged,
    )


# ---------------------------------------------------------------
# RE-AUDIT
# ---------------------------------------------------------------

async def re_audit_invoice_service(
    db: Session,
    invoice_id: int,
    file: UploadFile,
    invoice_number: str | None = None,
) -> dict:

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    provided_invoice_number = _clean_invoice_number(invoice_number)

    staged = await _validate_and_stage(file)

    # ------------------------------------------------------------
    # Duplicate check — BEFORE the graph runs, per your instruction
    # that dedup rejection must not go inside the workflow.
    # ------------------------------------------------------------
    duplicate = find_duplicate_version(db, invoice_id, staged["file_hash"])

    if duplicate is not None:
        discard_staged_file(staged["staging_path"])
        raise HTTPException(
            status_code=409,
            detail=(
                f"This exact file was already audited as version "
                f"{duplicate.version_number} (status: {duplicate.status}). "
                f"No changes detected."
            ),
        )

    return _run_and_finalize(
        db,
        invoice_id=invoice_id,
        is_reaudit=True,
        existing_invoice_number=invoice.invoice_number,
        existing_company_name=invoice.company_name,
        provided_invoice_number=provided_invoice_number,
        staged=staged,
    )


# ---------------------------------------------------------------
# GET endpoints
# ---------------------------------------------------------------

def _attach_file_urls(invoice: Invoice) -> Invoice:
    for version in invoice.versions:
        version.file_url = f"/invoices/version/{version.id}/file"
    return invoice


def get_all_invoices_service(db: Session):
    invoices = get_all_invoices_repository(db)
    return [_attach_file_urls(inv) for inv in invoices]


def get_invoice_by_id_service(db: Session, invoice_id: int):
    invoice = get_invoice_by_id(db, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _attach_file_urls(invoice)