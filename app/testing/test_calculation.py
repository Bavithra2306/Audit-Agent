
from decimal import Decimal

from app.schemas.invoice import InvoiceCreate
from app.tools.calculation import calculate_invoice


invoice_data = {
    "invoice_number": "INV-STV-2026-0634",
    "invoice_date": "2026-09-07",
    "due_date": "2026-10-07",
    "business_category": "IT & Technology",
    "currency": "INR",
    "subtotal": "1043340.0",
    "total_discount": "77660.0",
    "additional_charges": None,
    "stated_tax_total": "183301.2",
    "stated_grand_total": "1201641.2",
    "calculated_subtotal": None,
    "calculated_tax_total": None,
    "calculated_grand_total": None,
    "description": None,
    "items": [
        {
            "item_type": "SERVICE",
            "unit_type": "SERVICE",
            "description": "Inbound Voice Agent - 4 Languages",
            "sac_code": "998313",
            "quantity": "1",
            "unit_price": "396000.0",
            "discount_percent": "10",
            "discount_amount": "39600.0",
            "taxable_amount": "356400.0",
            "stated_line_total": "420552.0",
            "calculated_line_total": None,
            "taxes": [
                {
                    "tax_name": "IGST",
                    "tax_rate": "18",
                    "stated_tax_amount": "64152.0",
                    "calculated_tax_amount": None,
                }
            ],
        },
        {
            "item_type": "SERVICE",
            "unit_type": "SERVICE",
            "description": "Speech Analytics & QA Scoring Engine",
            "sac_code": None,
            "quantity": "1",
            "unit_price": "158000.0",
            "discount_percent": "5",
            "discount_amount": "7900.0",
            "taxable_amount": "150100.0",
            "stated_line_total": "177118.0",
            "calculated_line_total": None,
            "taxes": [
                {
                    "tax_name": "IGST",
                    "tax_rate": "18",
                    "stated_tax_amount": "27018.0",
                    "calculated_tax_amount": None,
                }
            ],
        },
        {
            "item_type": "SERVICE",
            "unit_type": "SERVICE",
            "description": "Agent Handoff & CRM Screen-pop Integration",
            "sac_code": "998319",
            "quantity": "1",
            "unit_price": "124000.0",
            "discount_percent": "8",
            "discount_amount": "9920.0",
            "taxable_amount": "114080.0",
            "stated_line_total": "134614.4",
            "calculated_line_total": None,
            "taxes": [
                {
                    "tax_name": "IGST",
                    "tax_rate": "18",
                    "stated_tax_amount": "20534.4",
                    "calculated_tax_amount": None,
                }
            ],
        },
        {
            "item_type": "SERVICE",
            "unit_type": "SERVICE",
            "description": "Prompt Guardrails & Jailbreak Testing",
            "sac_code": "998311",
            "quantity": "2",
            "unit_price": "68000.0",
            "discount_percent": "0",
            "discount_amount": "0.0",
            "taxable_amount": "136000.0",
            "stated_line_total": "160480.0",
            "calculated_line_total": None,
            "taxes": [
                {
                    "tax_name": "IGST",
                    "tax_rate": "18",
                    "stated_tax_amount": "24480.0",
                    "calculated_tax_amount": None,
                }
            ],
        },
        {
            "item_type": "SERVICE",
            "unit_type": "SERVICE",
            "description": "Realtime Barge-in Latency Tuning",
            "sac_code": "998311",
            "quantity": "1",
            "unit_price": "82000.0",
            "discount_percent": "12",
            "discount_amount": "9840.0",
            "taxable_amount": "72160.0",
            "stated_line_total": "85148.8",
            "calculated_line_total": None,
            "taxes": [
                {
                    "tax_name": "IGST",
                    "tax_rate": "18",
                    "stated_tax_amount": "12988.8",
                    "calculated_tax_amount": None,
                }
            ],
        },
        {
            "item_type": "SERVICE",
            "unit_type": "SERVICE",
            "description": "Knowledge Base Sync & Retrieval Tuning",
            "sac_code": "998319",
            "quantity": "1",
            "unit_price": "96000.0",
            "discount_percent": "15",
            "discount_amount": "0.0",
            "taxable_amount": "96000.0",
            "stated_line_total": "113280.0",
            "calculated_line_total": None,
            "taxes": [
                {
                    "tax_name": "IGST",
                    "tax_rate": "18",
                    "stated_tax_amount": "17280.0",
                    "calculated_tax_amount": None,
                }
            ],
        },
        {
            "item_type": "SERVICE",
            "unit_type": "SERVICE",
            "description": "Managed Operations - 2 Months",
            "sac_code": "998311",
            "quantity": "2",
            "unit_price": "52000.0",
            "discount_percent": "10",
            "discount_amount": "10400.0",
            "taxable_amount": "93600.0",
            "stated_line_total": "110448.0",
            "calculated_line_total": None,
            "taxes": [
                {
                    "tax_name": "IGST",
                    "tax_rate": "18",
                    "stated_tax_amount": "16848.0",
                    "calculated_tax_amount": None,
                }
            ],
        },
    ],
}


invoice = InvoiceCreate.model_validate(invoice_data)

result = calculate_invoice(invoice)

print("\n========== CALCULATION RESULT ==========\n")

print("Calculated Subtotal:")
print(result["calculated_subtotal"])

print("\nCalculated Tax Total:")
print(result["calculated_tax_total"])

print("\nCalculated Grand Total:")
print(result["calculated_grand_total"])

print("\nCalculation Issues:")
for issue in result["calculation_issues"]:
    print(issue)

print("\nCalculated Items:")
for item in result["items"]:
    print("\n", item)

