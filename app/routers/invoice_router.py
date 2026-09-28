from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.invoice_version import InvoiceVersion
from app.schema.invoice import InvoiceRead
from app.services.invoice_service import (
    upload_invoice_service,
    get_all_invoices_service,
    get_invoice_by_id_service,
    re_audit_invoice_service,
)

InvoiceRouter = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


# ---------------------------------------------------------------
# Outcomes where nothing was saved (no version_number in the result):
# NEEDS_INVOICE_NUMBER, REJECTED, FAILED on a brand-new upload
# ---------------------------------------------------------------

NOT_SAVED_MESSAGES = {
    "NEEDS_INVOICE_NUMBER": "Invoice number required",
    "REJECTED": "Invoice rejected",
    "FAILED": "Audit could not be completed",
}


def _not_saved_response(result: dict) -> dict:
    return {
        "message": NOT_SAVED_MESSAGES.get(result["status"], "Not saved"),
        "invoice_id": result["invoice_id"],
        "status": result["status"],
        "explanation": result["explanation"],
    }


# ---------------------------------------------------------------
# INITIAL upload
# ---------------------------------------------------------------

@InvoiceRouter.post("/upload")
async def upload_invoice_endpoint(
    file: UploadFile = File(...),
    invoice_number: str | None = Form(None),
    db: Session = Depends(get_db),
):
    result = await upload_invoice_service(db, file, invoice_number)

    if "version_number" not in result:
        return _not_saved_response(result)

    return {
        "message": "Invoice audited successfully",
        "invoice_id": result["invoice_id"],
        "version_number": result["version_number"],
        "status": result["status"],
        "explanation": result["explanation"],
        "discrepancies": result["discrepancies"],
    }


# ---------------------------------------------------------------
# GET all invoices
# ---------------------------------------------------------------

@InvoiceRouter.get("/all", response_model=list[InvoiceRead])
def get_all_invoices(db: Session = Depends(get_db)):
    return get_all_invoices_service(db)


# ---------------------------------------------------------------
# GET one invoice (full version history — every version + file_url)
# ---------------------------------------------------------------

@InvoiceRouter.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice_by_id(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    return get_invoice_by_id_service(db, invoice_id)


# ---------------------------------------------------------------
# GET a SPECIFIC version's file (view inline) — this is what
# each version's `file_url` in the UI points to.
# ---------------------------------------------------------------

@InvoiceRouter.get("/version/{version_id}/file")
def get_invoice_version_file(
    version_id: int,
    db: Session = Depends(get_db),
):
    version = (
        db.query(InvoiceVersion)
        .filter(InvoiceVersion.id == version_id)
        .first()
    )

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if not version.file_path:
        raise HTTPException(status_code=404, detail="No file available for this version")

    file_path = Path(version.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist on disk")

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        media_type = "application/pdf"
    elif extension in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"
    elif extension == ".docx":
        media_type = (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        content_disposition_type="inline",
    )


# ---------------------------------------------------------------
# RE-AUDIT
# ---------------------------------------------------------------

@InvoiceRouter.post("/{invoice_id}/re-audit")
async def re_audit_invoice_endpoint(
    invoice_id: int,
    file: UploadFile = File(...),
    invoice_number: str | None = Form(None),
    db: Session = Depends(get_db),
):
    result = await re_audit_invoice_service(
        db=db,
        invoice_id=invoice_id,
        file=file,
        invoice_number=invoice_number,
    )

    if "version_number" not in result:
        return _not_saved_response(result)

    return {
        "message": "Invoice re-audited successfully",
        "invoice_id": result["invoice_id"],
        "version_number": result["version_number"],
        "status": result["status"],
        "explanation": result["explanation"],
        "discrepancies": result["discrepancies"],
    }