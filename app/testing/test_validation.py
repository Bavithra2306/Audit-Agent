from decimal import Decimal

from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceItemBase,
    InvoiceTaxBase,
)

from app.tools.calculation import calculate_invoice
from app.tools.validation import validate_invoice


# ---------------------------------------------------------
# TEST INVOICE
# ---------------------------------------------------------

invoice = InvoiceCreate(
    invoice_number="INV-STV-2026-0634",
    invoice_date="2026-09-07",
    due_date="2026-10-07",
    business_category="IT & Technology",
    currency="INR",

    subtotal=Decimal("1043340.00"),
    total_discount=Decimal("77660.00"),
    additional_charges=None,
    stated_tax_total=Decimal("183301.20"),
    stated_grand_total=Decimal("1201641.20"),

    items=[
        InvoiceItemBase(
            item_type="SERVICE",
            unit_type="SERVICE",
            description="Inbound Voice Agent",
            quantity=Decimal("1"),
            unit_price=Decimal("396000"),
            discount_percent=Decimal("10"),
            discount_amount=Decimal("39600"),
            taxable_amount=Decimal("356400"),
            stated_line_total=Decimal("420552"),
            taxes=[
                InvoiceTaxBase(
                    tax_name="IGST",
                    tax_rate=Decimal("18"),
                    stated_tax_amount=Decimal("64152"),
                )
            ],
        ),

        InvoiceItemBase(
            item_type="SERVICE",
            unit_type="SERVICE",
            description="Speech Analytics",
            quantity=Decimal("1"),
            unit_price=Decimal("158000"),
            discount_percent=Decimal("5"),
            discount_amount=Decimal("7900"),
            taxable_amount=Decimal("150100"),
            stated_line_total=Decimal("177118"),
            taxes=[
                InvoiceTaxBase(
                    tax_name="IGST",
                    tax_rate=Decimal("18"),
                    stated_tax_amount=Decimal("27018"),
                )
            ],
        ),

        InvoiceItemBase(
            item_type="SERVICE",
            unit_type="SERVICE",
            description="Agent Handoff",
            quantity=Decimal("1"),
            unit_price=Decimal("124000"),
            discount_percent=Decimal("8"),
            discount_amount=Decimal("9920"),
            taxable_amount=Decimal("114080"),
            stated_line_total=Decimal("134614.40"),
            taxes=[
                InvoiceTaxBase(
                    tax_name="IGST",
                    tax_rate=Decimal("18"),
                    stated_tax_amount=Decimal("20534.40"),
                )
            ],
        ),

        InvoiceItemBase(
            item_type="SERVICE",
            unit_type="SERVICE",
            description="Prompt Guardrails",
            quantity=Decimal("2"),
            unit_price=Decimal("68000"),
            discount_percent=Decimal("0"),
            discount_amount=Decimal("0"),
            taxable_amount=Decimal("136000"),
            stated_line_total=Decimal("160480"),
            taxes=[
                InvoiceTaxBase(
                    tax_name="IGST",
                    tax_rate=Decimal("18"),
                    stated_tax_amount=Decimal("24480"),
                )
            ],
        ),

        InvoiceItemBase(
            item_type="SERVICE",
            unit_type="SERVICE",
            description="Realtime Barge-in",
            quantity=Decimal("1"),
            unit_price=Decimal("82000"),
            discount_percent=Decimal("12"),
            discount_amount=Decimal("9840"),
            taxable_amount=Decimal("72160"),
            stated_line_total=Decimal("85148.80"),
            taxes=[
                InvoiceTaxBase(
                    tax_name="IGST",
                    tax_rate=Decimal("18"),
                    stated_tax_amount=Decimal("12988.80"),
                )
            ],
        ),

        InvoiceItemBase(
            item_type="SERVICE",
            unit_type="SERVICE",
            description="Knowledge Base Sync",
            quantity=Decimal("1"),
            unit_price=Decimal("96000"),
            discount_percent=Decimal("15"),
            discount_amount=Decimal("0"),
            taxable_amount=Decimal("96000"),
            stated_line_total=Decimal("113280"),
            taxes=[
                InvoiceTaxBase(
                    tax_name="IGST",
                    tax_rate=Decimal("18"),
                    stated_tax_amount=Decimal("17280"),
                )
            ],
        ),

        InvoiceItemBase(
            item_type="SERVICE",
            unit_type="SERVICE",
            description="Managed Operations",
            quantity=Decimal("2"),
            unit_price=Decimal("52000"),
            discount_percent=Decimal("10"),
            discount_amount=Decimal("10400"),
            taxable_amount=Decimal("93600"),
            stated_line_total=Decimal("110448"),
            taxes=[
                InvoiceTaxBase(
                    tax_name="IGST",
                    tax_rate=Decimal("18"),
                    stated_tax_amount=Decimal("16848"),
                )
            ],
        ),
    ],
)


# ---------------------------------------------------------
# 1. CALCULATE
# ---------------------------------------------------------

calculated = calculate_invoice(invoice)


# ---------------------------------------------------------
# 2. VALIDATE
# ---------------------------------------------------------

validation = validate_invoice(
    invoice=invoice,
    calculated=calculated,
    extraction_issues=[],
)


# ---------------------------------------------------------
# 3. PRINT RESULT
# ---------------------------------------------------------

print("\n========== CALCULATION ==========\n")

print(
    "Calculated Subtotal:",
    calculated["calculated_subtotal"],
)

print(
    "Calculated Tax Total:",
    calculated["calculated_tax_total"],
)

print(
    "Calculated Grand Total:",
    calculated["calculated_grand_total"],
)


print("\n========== VALIDATION ==========\n")

print(
    "Status:",
    validation["status"],
)


print("\nDiscrepancies:\n")

if not validation["discrepancies"]:

    print("No discrepancies found.")

else:

    for discrepancy in validation["discrepancies"]:

        print("Field:")
        print(discrepancy["field"])

        print("Issue:")
        print(discrepancy["issue"])

        print("Stated:")
        print(discrepancy["stated"])

        print("Calculated:")
        print(discrepancy["calculated"])

        print("Difference:")
        print(discrepancy["difference"])

        print("-" * 50)