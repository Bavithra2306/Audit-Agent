from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class InvoiceItem(Base):
    __tablename__ = "invoice_items"


    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    invoice_version_id: Mapped[int] = mapped_column(
        ForeignKey("invoice_versions.id"),
        nullable=False,
    )

    # PRODUCT or SERVICE
    item_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # UNIT, HOUR, DAY, SERVICE, VIDEO, METER, KG, etc.
    unit_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sac_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )

    unit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    discount_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    discount_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    taxable_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    stated_line_total: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    calculated_line_total: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    invoice_version = relationship(
        "InvoiceVersion",
        back_populates="items",
    )

    taxes = relationship(
        "InvoiceTax",
        back_populates="invoice_item",
        cascade="all, delete-orphan",
    )