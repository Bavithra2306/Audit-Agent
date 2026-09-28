from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.invoice_version import InvoiceVersion
from app.models.invoice_item import InvoiceItem
from app.models.invoice_tax import InvoiceTax
from app.schema.invoice import InvoiceCreate


# =================================================================
# INVOICE-level operations
# =================================================================

def get_or_create_invoice(db: Session, company_name: str, invoice_number: str) -> Invoice:
    invoice = Invoice(company_name=company_name, invoice_number=invoice_number)
    db.add(invoice)
    db.flush()
    return invoice

def get_or_create_invoice(db: Session, company_name: str, invoice_number: str) -> Invoice:
    invoice = Invoice(company_name=company_name, invoice_number=invoice_number)
    db.add(invoice)
    db.flush()
    return invoice


def find_invoice_by_identity(db: Session, company_name: str, invoice_number: str) -> Invoice | None:
    """
    Used on INITIAL upload only — checks whether this exact
    (company_name, invoice_number) pair already exists as a
    different Invoice record, before creating a new one.
    """
    return (
        db.query(Invoice)
        .filter(
            Invoice.company_name == company_name,
            Invoice.invoice_number == invoice_number,
        )
        .first()
    )


def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice | None:
    return (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )


def get_all_invoices_repository(db: Session):
    """
    View all invoices uploaded and checked by the user.
    Returns Invoice rows; each one's `.versions` relationship
    gives access to its full audit history when needed.
    """
    return (
        db.query(Invoice)
        .order_by(Invoice.created_at.desc())
        .all()
    )


def set_current_version(
    db: Session,
    invoice: Invoice,
    version: "InvoiceVersion",
) -> None:
    invoice.current_version_id = version.id
    db.add(invoice)


# =================================================================
# INVOICE VERSION operations
# =================================================================

def get_next_version_number(db: Session, invoice_id: int) -> int:
    last = (
        db.query(InvoiceVersion)
        .filter(InvoiceVersion.invoice_id == invoice_id)
        .order_by(InvoiceVersion.version_number.desc())
        .first()
    )
    return (last.version_number + 1) if last else 1



def create_invoice_version(
    db: Session,
    invoice_id: int,
    version_number: int,
    invoice_data: InvoiceCreate,
    calculated: dict,
    status: str,
    explanation: str,
    file_meta: dict,
) -> InvoiceVersion:
    """
    Creates ONE InvoiceVersion row + its InvoiceItem/InvoiceTax
    children. Used for BOTH initial audits and re-audits — a
    re-audit simply calls this again with the same invoice_id
    and the next version_number; nothing is ever updated in place.

    `calculated` may be {} (when status == FAILED, since the graph
    never reached the calculate node) — every read uses .get() so
    this never raises a KeyError.
    """

    version = InvoiceVersion(
        invoice_id=invoice_id,
        version_number=version_number,

        invoice_date=invoice_data.invoice_date,
        due_date=invoice_data.due_date,
        business_category=invoice_data.business_category,
        currency=invoice_data.currency,

        subtotal=invoice_data.subtotal,
        total_discount=invoice_data.total_discount,
        additional_charges=calculated.get("additional_charges"),
        stated_tax_total=invoice_data.stated_tax_total,
        stated_grand_total=invoice_data.stated_grand_total,

        calculated_subtotal=calculated.get("calculated_subtotal"),
        calculated_tax_total=calculated.get("calculated_tax_total"),
        calculated_grand_total=calculated.get("calculated_grand_total"),

        status=status,
        description=explanation,

        original_filename=file_meta["original_filename"],
        stored_filename=file_meta["stored_filename"],
        file_path=file_meta.get("file_path"),  # filled in after promotion
        file_hash=file_meta["file_hash"],
    )

    db.add(version)
    db.flush()  # assigns version.id for items below

    # -----------------------------------------
    # Match calculated items by description
    # -----------------------------------------

    calculated_by_description = {}

    for calculated_item in calculated.get("items", []):
        description = calculated_item["description"]
        calculated_by_description.setdefault(description, []).append(calculated_item)

    # -----------------------------------------
    # Save invoice items + taxes
    # -----------------------------------------

    for item_data in invoice_data.items:

        matching_items = calculated_by_description.get(item_data.description, [])
        calculated_item = matching_items.pop(0) if matching_items else None

        item = InvoiceItem(
            invoice_version_id=version.id,

            item_type=item_data.item_type,
            unit_type=item_data.unit_type,

            description=item_data.description,
            sac_code=item_data.sac_code,

            quantity=item_data.quantity,
            unit_price=item_data.unit_price,

            discount_percent=item_data.discount_percent,
            discount_amount=(
                calculated_item.get("calculated_discount_amount")
                if calculated_item
                else item_data.discount_amount
            ),

            taxable_amount=item_data.taxable_amount,
            stated_line_total=item_data.stated_line_total,

            calculated_line_total=(
                calculated_item.get("calculated_line_total")
                if calculated_item
                else None
            ),
        )

        db.add(item)
        db.flush()  # assigns item.id for taxes below

        calculated_taxes = (
            calculated_item.get("calculated_taxes", [])
            if calculated_item
            else []
        )

        calculated_tax_by_name = {}

        for calculated_tax in calculated_taxes:
            tax_name = calculated_tax["tax_name"]
            calculated_tax_by_name.setdefault(tax_name, []).append(calculated_tax)

        for tax_data in item_data.taxes:

            matching_taxes = calculated_tax_by_name.get(tax_data.tax_name, [])
            calculated_tax = matching_taxes.pop(0) if matching_taxes else None

            tax = InvoiceTax(
                invoice_item_id=item.id,

                tax_name=tax_data.tax_name,
                tax_rate=tax_data.tax_rate,

                stated_tax_amount=tax_data.stated_tax_amount,

                calculated_tax_amount=(
                    calculated_tax.get("calculated_tax_amount")
                    if calculated_tax
                    else None
                ),
            )

            db.add(tax)

    return version