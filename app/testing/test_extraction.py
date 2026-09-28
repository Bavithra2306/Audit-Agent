import json

from app.parsers.document_parser import parse_document
from app.tools.extraction import extract_invoice


FILE_PATH = "uploads/invoices/INV-STV-2026-0634.jpeg"


parsed_text = parse_document(FILE_PATH)

print("\n========== DOCLING OUTPUT ==========\n")
print(parsed_text)

invoice = extract_invoice(parsed_text)

print("\n========== LLM EXTRACTION ==========\n")
print(
    json.dumps(
        invoice.model_dump(mode="json"),
        indent=2
    )
)