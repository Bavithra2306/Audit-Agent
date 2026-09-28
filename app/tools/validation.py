from decimal import Decimal

from app.schema.invoice import InvoiceCreate


TOLERANCE = Decimal("0.01")


def validate_value(
    field: str,
    stated: Decimal | None,
    calculated: Decimal,
) -> dict | None:

    # The invoice did not provide this value
    if stated is None:
        return {
            "field": field,
            "issue": "Stated value is missing",
            "stated": None,
            "calculated": calculated,
            "difference": None,
        }

    # Compare invoice value with our calculated value
    difference = stated - calculated

    # Allow small differences caused by rounding
    if abs(difference) > TOLERANCE:
        return {
            "field": field,
            "issue": "Value mismatch",
            "stated": stated,
            "calculated": calculated,
            "difference": difference,
        }

    # Values match within tolerance
    return None


def validate_invoice(
    invoice: InvoiceCreate,
    calculated: dict,
    extraction_issues: list | None = None,
) -> dict:

    discrepancies = []

    # ---------------------------------------------------------
    # 1. EXTRACTION ISSUES
    # ---------------------------------------------------------

    if extraction_issues:
        discrepancies.extend(extraction_issues)

    # ---------------------------------------------------------
    # 2. CALCULATION ISSUES
    # ---------------------------------------------------------

    calculation_issues = calculated.get(
        "calculation_issues",
        [],
    )

    discrepancies.extend(calculation_issues)

    # ---------------------------------------------------------
    # 3. INVOICE-LEVEL TOTAL VALIDATION
    # ---------------------------------------------------------

    checks = [
        (
            "subtotal",
            invoice.subtotal,
            calculated["calculated_subtotal"],
        ),
        (
            "tax_total",
            invoice.stated_tax_total,
            calculated["calculated_tax_total"],
        ),
        (
            "grand_total",
            invoice.stated_grand_total,
            calculated["calculated_grand_total"],
        ),
    ]

    for field, stated, calculated_value in checks:

        discrepancy = validate_value(
            field,
            stated,
            calculated_value,
        )

        if discrepancy is not None:
            discrepancies.append(discrepancy)

    # ---------------------------------------------------------
    # 4. LINE-LEVEL VALIDATION
    # ---------------------------------------------------------

    # The calculation tool only returns successfully
    # calculated items.
    #
    # Therefore, we must NOT use:
    #
    # zip(invoice.items, calculated["items"])
    #
    # because a skipped invoice line would shift the positions.

    calculated_items = calculated.get(
        "items",
        [],
    )

    # Group calculated items by description.
    # This allows us to match them with the original
    # invoice items without depending on list position.

    calculated_by_description = {}

    for calculated_item in calculated_items:

        description = calculated_item["description"]

        calculated_by_description.setdefault(
            description,
            [],
        ).append(calculated_item)

    for invoice_item in invoice.items:

        description = invoice_item.description

        matching_items = calculated_by_description.get(
            description,
            [],
        )

        # This line was probably skipped by the calculation tool because required data was missing.
        # The calculation issue has already been added above,
        # so there is nothing else to validate for this line.

        if not matching_items:
            continue

        calculated_item = matching_items.pop(0)

        # -----------------------------------------------------
        # 4A. TAXABLE AMOUNT
        # -----------------------------------------------------

        discrepancy = validate_value(
            f"{description}.taxable_amount",
            invoice_item.taxable_amount,
            calculated_item["calculated_taxable_amount"],
        )

        if discrepancy is not None:
            discrepancies.append(discrepancy)

        # -----------------------------------------------------
        # 4B. LINE TOTAL
        # -----------------------------------------------------

        discrepancy = validate_value(
            f"{description}.line_total",
            invoice_item.stated_line_total,
            calculated_item["calculated_line_total"],
        )

        if discrepancy is not None:
            discrepancies.append(discrepancy)

        # -----------------------------------------------------
        # 4C. TAX VALIDATION
        # -----------------------------------------------------

        calculated_taxes = calculated_item.get(
            "calculated_taxes",
            [],
        )

        for stated_tax in invoice_item.taxes:

            matching_tax = next(
                (
                    tax
                    for tax in calculated_taxes
                    if tax["tax_name"] == stated_tax.tax_name
                ),
                None,
            )

            # Tax could not be calculated.
            #
            # Usually this happens when the tax rate
            # was missing.

            if matching_tax is None:

                discrepancies.append(
                    {
                        "field": (
                            f"{description}."
                            f"{stated_tax.tax_name}.tax_amount"
                        ),
                        "issue": "Tax could not be calculated",
                        "stated": stated_tax.stated_tax_amount,
                        "calculated": None,
                        "difference": None,
                    }
                )

                continue

            # Compare stated tax amount with calculated
            # tax amount.

            discrepancy = validate_value(
                (
                    f"{description}."
                    f"{stated_tax.tax_name}.tax_amount"
                ),
                stated_tax.stated_tax_amount,
                matching_tax["calculated_tax_amount"],
            )

            if discrepancy is not None:
                discrepancies.append(discrepancy)

    # ---------------------------------------------------------
    # 5. FINAL STATUS
    # ---------------------------------------------------------

    if discrepancies:
        status = "DISCREPANCY_FOUND"
    else:
        status = "PASSED"

    return {
        "status": status,
        "discrepancies": discrepancies,
    }

