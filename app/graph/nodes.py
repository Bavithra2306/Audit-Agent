from app.graph.state import InvoiceState

from app.parsers.document_parser import parse_document

from app.tools.extraction import extract_invoice
from app.tools.calculation import calculate_invoice
from app.tools.validation import validate_invoice
from app.tools.explanation import explain_validation_tool


def parse_node(state: InvoiceState) -> dict:

    parsed_text = parse_document(
        state["staging_path"]
    )

    return {
        "parsed_text": parsed_text
    }


def extraction_node(state: InvoiceState) -> dict:

    result = extract_invoice(
        state["parsed_text"]
    )

    invoice = result["invoice"]
    extraction_issues = result["extraction_issues"]

     # User typed the number in → it wins over whatever was extracted
    provided = (state.get("provided_invoice_number") or "").strip()
    if provided:
        invoice.invoice_number = provided

    # Company name is still required
    if not invoice.company_name:
        return {"invoice": invoice, "extraction_issues": extraction_issues, "status": "FAILED"}

    # No invoice number → stop and ask the user
    if not invoice.invoice_number:
        return {"invoice": invoice, "extraction_issues": extraction_issues, "status": "NEEDS_INVOICE_NUMBER"}

    return {"invoice": invoice, "extraction_issues": extraction_issues}


def identity_guard_node(state: InvoiceState) -> dict:
    existing_number = state.get("existing_invoice_number")
    existing_company = state.get("existing_company_name")

    new_number = state["invoice"].invoice_number
    new_company = state["invoice"].company_name

    def normalize(value: str) -> str:
        return value.strip().lower()

    number_matches = normalize(existing_number) == normalize(new_number)
    company_matches = normalize(existing_company) == normalize(new_company)

    if not (number_matches and company_matches):
        return {
            "status": "REJECTED",
            "identity_mismatch": True,
            "identity_mismatch_reason": (
                f"Uploaded file is '{new_company} / {new_number}', "
                f"but this invoice record is '{existing_company} / {existing_number}'."
            ),
        }

    return {"identity_mismatch": False}


def calculation_node(state: InvoiceState) -> dict:

    calculated = calculate_invoice(
        state["invoice"]
    )

    return {
        "calculated": calculated
    }


def validation_node(state: InvoiceState) -> dict:

    validation = validate_invoice(
        invoice=state["invoice"],
        calculated=state["calculated"],
        extraction_issues=state.get(
            "extraction_issues",
            [],
        ),
    )

    return {
        "validation": validation,
        "status": validation["status"],   # PASSED | DISCREPANCY_FOUND
    }


def explanation_node(state: InvoiceState) -> dict:

    status = state["status"]

    # ---------------------------------------------------------
    # Build the payload the LLM explains, based on WHICH path
    # got us here — normal validation vs. a hard-stop.
    # ---------------------------------------------------------

    if status == "FAILED":
        payload = {
            "status": "FAILED",
            "reason": "The issuing company's name could not be extracted from the document.",
            "extraction_issues": state.get("extraction_issues", []),
        }

    elif status == "REJECTED":
        payload = {
            "status": "REJECTED",
            "reason": state.get("identity_mismatch_reason"),
        }

    else:
        # PASSED or DISCREPANCY_FOUND — normal validation result
        payload = state["validation"]

    explanation = explain_validation_tool(payload)



    return {
        "explanation": explanation,
    }