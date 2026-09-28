import hashlib
import shutil
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from sqlalchemy.orm import Session

from app.models.invoice_version import InvoiceVersion


MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

# ---------------------------------------------------------------
# Storage layout — staging is transient, invoices/ is permanent
# ---------------------------------------------------------------

STAGING_DIR = Path("uploads/staging")
INVOICES_DIR = Path("uploads/invoices")

STAGING_DIR.mkdir(parents=True, exist_ok=True)
INVOICES_DIR.mkdir(parents=True, exist_ok=True)

DOCX_REQUIRED_FILES = {
    "[Content_Types].xml",
    "_rels/.rels",
    "word/document.xml",
}


# This will check the what type of DOCX file
def is_valid_docx(content: bytes) -> bool:
    try:
        with ZipFile(BytesIO(content), "r") as zip_file:

            # 1. Check ZIP integrity
            if zip_file.testzip() is not None:
                return False

            names = set(zip_file.namelist())

            # 2. Check required DOCX files
            if not DOCX_REQUIRED_FILES.issubset(names):
                return False

            # 3. Check that the main document actually exists
            document_info = zip_file.getinfo("word/document.xml")

            if document_info.file_size == 0:
                return False

            # 4. Check DOCX content types file is readable
            content_types = zip_file.read("[Content_Types].xml")

            if not content_types:
                return False

            return True

    except (BadZipFile, KeyError, OSError):
        return False


# =================================================================
# NEW: File hashing
# =================================================================

def compute_file_hash(content: bytes) -> str:
    """SHA-256 hash of the raw file bytes — used for dedup checks."""
    return hashlib.sha256(content).hexdigest()


# =================================================================
# NEW: Duplicate detection (runs BEFORE the graph — pure DB lookup)
# =================================================================

def find_duplicate_version(
    db: Session,
    invoice_id: int,
    file_hash: str,
) -> InvoiceVersion | None:
    """
    Checks if this exact file (by hash) has already been audited
    for this invoice — regardless of whether that prior attempt
    was PASSED or DISCREPANCY_FOUND (per your earlier decision:
    a passed invoice can still be re-audited with a genuinely new file).

    Returns the matching InvoiceVersion if found, else None.
    """
    return (
        db.query(InvoiceVersion)
        .filter(
            InvoiceVersion.invoice_id == invoice_id,
            InvoiceVersion.file_hash == file_hash,
        )
        .first()
    )


# =================================================================
# NEW: Staging lifecycle
# =================================================================

def save_to_staging(content: bytes, extension: str) -> Path:
    """
    Writes the uploaded file to uploads/staging/ under a temporary
    name. This is the ONLY place a file lives while the graph runs.
    """
    import uuid

    temp_name = f"{uuid.uuid4().hex}{extension}"
    staging_path = STAGING_DIR / temp_name

    with open(staging_path, "wb") as f:
        f.write(content)

    return staging_path


def promote_to_permanent(
    staging_path: Path,
    invoice_id: int,
    version_number: int,
    status: str,
    extension: str,
) -> Path:
    """
    Called ONLY after the graph reaches END with a persistable
    status (PASSED / DISCREPANCY_FOUND / FAILED). Moves the file
    out of staging into its permanent, version-tagged location.

    uploads/invoices/{invoice_id}/v{version_number}_{status}_invoice{ext}
    """
    invoice_folder = INVOICES_DIR / str(invoice_id)
    invoice_folder.mkdir(parents=True, exist_ok=True)

    final_name = f"v{version_number}_{status.lower()}_invoice{extension}"
    final_path = invoice_folder / final_name

    shutil.move(str(staging_path), str(final_path))

    return final_path


def discard_staged_file(staging_path: Path) -> None:
    """
    Called when the graph ends in REJECTED (identity mismatch) —
    the file does not belong to this invoice, so it is deleted
    outright. Nothing is kept, nothing is logged to a table.
    """
    if staging_path.exists():
        staging_path.unlink()