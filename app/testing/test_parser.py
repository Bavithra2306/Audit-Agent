from pathlib import Path

from app.parsers.document_parser import parse_document


files = list(Path("uploads/invoices").iterdir())

if not files:
    raise RuntimeError("No invoice file found")

invoice_path = files[0]

print(f"Parsing: {invoice_path}")

content = parse_document(str(invoice_path))

print("\n========== PARSED INVOICE ==========\n")
print(content)