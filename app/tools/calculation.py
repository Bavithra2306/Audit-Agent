from decimal import Decimal, ROUND_HALF_UP

from app.schema.invoice import InvoiceCreate


TWO_PLACES = Decimal("0.01")


def money(value: Decimal | None) -> Decimal:
    if value is None:
        return Decimal("0.00")

    return value.quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def calculate_invoice(invoice: InvoiceCreate) -> dict:

    calculated_items = []
    calculation_issues = []

    calculated_subtotal = Decimal("0.00")
    calculated_tax_total = Decimal("0.00")

    for item in invoice.items:

        # --------------------------------
        # 1. Check required calculation data
        # --------------------------------

        if item.quantity is None:
            calculation_issues.append({
                "field": f"{item.description}.quantity",
                "issue": "Quantity is missing. This line could not be calculated.",
            })
            continue

        if item.unit_price is None:
            calculation_issues.append({
                "field": f"{item.description}.unit_price",
                "issue": "Unit price is missing. This line could not be calculated.",
            })
            continue

        # --------------------------------
        # 2. Gross amount
        # --------------------------------

        gross_amount = (
            item.quantity * item.unit_price
        )

        # --------------------------------
        # 3. Calculate discount
        # --------------------------------

        if item.discount_amount is not None:

            discount_amount = item.discount_amount

        elif item.discount_percent is not None:

            discount_amount = (
                gross_amount
                * item.discount_percent
                / Decimal("100")
            )

        else:

            # No discount is completely valid
            discount_amount = Decimal("0")

        discount_amount = money(discount_amount)

        # --------------------------------
        # 4. Taxable amount
        # --------------------------------

        taxable_amount = money(
            gross_amount - discount_amount
        )

        # --------------------------------
        # 5. Calculate taxes
        # --------------------------------

        line_tax_total = Decimal("0.00")

        calculated_taxes = []

        for tax in item.taxes:

            # Tax rate missing → skip only this tax
            if tax.tax_rate is None:

                calculation_issues.append({
                    "field": (
                        f"{item.description}."
                        f"{tax.tax_name}.tax_rate"
                    ),
                    "issue": (
                        "Tax rate is missing. "
                        "This tax could not be calculated."
                    ),
                })

                continue

            tax_amount = (
                taxable_amount
                * tax.tax_rate
                / Decimal("100")
            )

            tax_amount = money(tax_amount)

            line_tax_total += tax_amount

            calculated_taxes.append({
                "tax_name": tax.tax_name,
                "tax_rate": tax.tax_rate,
                "calculated_tax_amount": tax_amount,
            })

        line_tax_total = money(line_tax_total)

        # --------------------------------
        # 6. Line total
        # --------------------------------

        line_total = money(
            taxable_amount
            + line_tax_total
        )

        # --------------------------------
        # 7. Add to invoice totals
        # --------------------------------

        calculated_subtotal += taxable_amount
        calculated_tax_total += line_tax_total

        # --------------------------------
        # 8. Store calculated item
        # --------------------------------

        calculated_items.append({
            "description": item.description,
            "calculated_gross_amount": money(gross_amount),
            "calculated_discount_amount": discount_amount,
            "calculated_taxable_amount": taxable_amount,
            "calculated_tax_total": line_tax_total,
            "calculated_line_total": line_total,
            "calculated_taxes": calculated_taxes,
        })

    # --------------------------------
    # 9. Invoice-level totals
    # 

    calculated_subtotal = money(
        calculated_subtotal
    )

    calculated_tax_total = money(
        calculated_tax_total
    )

    # --------------------------------
    # 10. Additional charges
    # --------------------------------

    additional_charges = (
        invoice.additional_charges
        if invoice.additional_charges is not None
        else Decimal("0")
    )

    additional_charges = money(
        additional_charges
    )

    # --------------------------------
    # 11. Grand total
    # --------------------------------

    calculated_grand_total = money(
        calculated_subtotal
        + calculated_tax_total
        + additional_charges
    )

    # --------------------------------
    # 12. Return result
    # --------------------------------

    return {
        "calculated_subtotal": calculated_subtotal,
        "calculated_tax_total": calculated_tax_total,
        "calculated_grand_total": calculated_grand_total,
        "additional_charges": additional_charges,
        "items": calculated_items,
        "calculation_issues": calculation_issues,
    }