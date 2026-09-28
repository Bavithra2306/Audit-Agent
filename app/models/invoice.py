from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)

    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    # NOTE: unique=True REMOVED from here — no longer unique alone

    __table_args__ = (
        UniqueConstraint("company_name", "invoice_number", name="uq_company_invoice_number"),
    )
    # Points to the latest/current version of this invoice
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoice_versions.id"),
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

    # All versions of this invoice
    versions = relationship(
        "InvoiceVersion",
        foreign_keys="InvoiceVersion.invoice_id",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    # The latest/current version
    current_version = relationship(
        "InvoiceVersion",
        foreign_keys=[current_version_id],
        post_update=True,
    )