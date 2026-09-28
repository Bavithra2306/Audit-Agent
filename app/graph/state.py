from typing import TypedDict

from app.schema.invoice import InvoiceCreate


class InvoiceState(TypedDict, total=False):

    # ------------------------------------------------------------
    # Request context (set by the service layer before graph.invoke)
    # ------------------------------------------------------------
    invoice_id: int | None   # None on INITIAL upload, set on RE-AUDIT
    
    provided_invoice_number: str | None   # typed by the user when the file has none
    
    is_reaudit: bool
    existing_invoice_number: str | None   # only set on RE-AUDIT, for identity_guard_node
    existing_company_name: str | None

    # ------------------------------------------------------------
    # Uploaded file information
    # ------------------------------------------------------------
    staging_path: str
    original_filename: str
    stored_filename: str
    file_hash: str

    # ------------------------------------------------------------
    # Document processing
    # ------------------------------------------------------------
    parsed_text: str

    # ------------------------------------------------------------
    # Extracted invoice
    # ------------------------------------------------------------
    invoice: InvoiceCreate
    extraction_issues: list

    # ------------------------------------------------------------
    # Identity guard (re-audit only)
    # ------------------------------------------------------------
    identity_mismatch: bool
    identity_mismatch_reason: str | None

    # ------------------------------------------------------------
    # Mathematical calculation
    # ------------------------------------------------------------
    calculated: dict

    # ------------------------------------------------------------
    # Validation result
    # ------------------------------------------------------------
    validation: dict

    # ------------------------------------------------------------
    # LLM explanation
    # ------------------------------------------------------------
    explanation: str

    # ------------------------------------------------------------
    # Final outcome
    #
    # PASSED / DISCREPANCY_FOUND / FAILED → persisted, file promoted
    # REJECTED → in-memory only, staged file deleted, nothing persisted
    # ------------------------------------------------------------
    status: str