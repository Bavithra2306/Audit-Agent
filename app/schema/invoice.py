from datetime import date,datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

#FOR Extraction and create
class TaxExtract(BaseModel):
    tax_name: str
    tax_rate: Optional[Decimal] = None
    stated_tax_amount: Optional[Decimal] = None
    calculated_tax_amount: Optional[Decimal] = None  # always null from LLM


class ItemExtract(BaseModel):
    item_type: Optional[str] = None
    unit_type: Optional[str] = None
    description: str
    sac_code: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    taxable_amount: Optional[Decimal] = None
    stated_line_total: Optional[Decimal] = None
    calculated_line_total: Optional[Decimal] = None  # always null from LLM
    taxes: list[TaxExtract] = Field(default_factory=list)


class InvoiceCreate(BaseModel):
    company_name: Optional[str] = None   # nullable HERE — extraction can fail

    invoice_number: Optional[str] = None   # nullable HERE (extraction can fail);
                                             # made mandatory only at persistence, see note below
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    business_category: Optional[str] = None
    currency: Optional[str] = None

    subtotal: Optional[Decimal] = None
    total_discount: Optional[Decimal] = None
    additional_charges: Optional[Decimal] = None
    stated_tax_total: Optional[Decimal] = None
    stated_grand_total: Optional[Decimal] = None

    calculated_subtotal: Optional[Decimal] = None   # always null from LLM, discarded later
    calculated_tax_total: Optional[Decimal] = None
    calculated_grand_total: Optional[Decimal] = None

    description: Optional[str] = None   # extracted invoice-level text — dropped per Option A above

    items: list[ItemExtract] = Field(default_factory=list)
    
    
    
#FOR INVOICE RESPONSE:

class InvoiceTaxRead(BaseModel):
    id: int
    tax_name: str
    tax_rate: Optional[Decimal]
    stated_tax_amount: Optional[Decimal]
    calculated_tax_amount: Optional[Decimal]

    class Config:
        from_attributes = True


class InvoiceItemRead(BaseModel):
    id: int
    item_type: Optional[str]
    unit_type: Optional[str]
    description: str
    sac_code: Optional[str]
    quantity: Optional[Decimal]
    unit_price: Optional[Decimal]
    discount_percent: Optional[Decimal]
    discount_amount: Optional[Decimal]
    taxable_amount: Optional[Decimal]
    stated_line_total: Optional[Decimal]
    calculated_line_total: Optional[Decimal]
    taxes: list[InvoiceTaxRead] = []

    class Config:
        from_attributes = True


class InvoiceVersionRead(BaseModel):
    id: int
    version_number: int
    file_url: str            # plain field, filled manually below
    invoice_date: Optional[date]
    due_date: Optional[date]
    business_category: Optional[str]
    currency: Optional[str]
    subtotal: Optional[Decimal]
    total_discount: Optional[Decimal]
    additional_charges: Optional[Decimal]
    stated_tax_total: Optional[Decimal]
    stated_grand_total: Optional[Decimal]
    calculated_subtotal: Optional[Decimal]
    calculated_tax_total: Optional[Decimal]
    calculated_grand_total: Optional[Decimal]
    status: Optional[str]
    description: Optional[str]      # explanation text, Option A
    original_filename: Optional[str]
    created_at: datetime
    items: list[InvoiceItemRead] = []

    class Config:
        from_attributes = True


class InvoiceRead(BaseModel):
    id: int
    company_name: str
    invoice_number: str
    created_at: datetime
    updated_at: datetime
    versions: list[InvoiceVersionRead] = []

    class Config:
        from_attributes = True