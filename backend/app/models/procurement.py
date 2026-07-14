import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, Enum, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase
from app.models.enums import ApprovalStatus, PaymentStatus

class PurchaseRequest(AuditableBase):
    """
    Departmental request to purchase new assets or items.
    """
    __tablename__ = "purchase_requests"

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    justification: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)

    items: Mapped[List["PurchaseRequestItem"]] = relationship("PurchaseRequestItem", back_populates="purchase_request", cascade="all, delete-orphan")
    department: Mapped["Department"] = relationship("Department", foreign_keys=[department_id])

class PurchaseRequestItem(AuditableBase):
    """
    Lines details of a Purchase Request.
    """
    __tablename__ = "purchase_request_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("estimated_unit_cost >= 0", name="cost_non_negative"),
    )

    purchase_request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    item_description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_unit_cost: Mapped[float] = mapped_column(Float, nullable=False)

    purchase_request: Mapped["PurchaseRequest"] = relationship("PurchaseRequest", back_populates="items")

class PurchaseOrder(AuditableBase):
    """
    Formal procurement agreement with Vendor.
    """
    __tablename__ = "purchase_orders"

    po_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)

    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="purchase_orders")
    items: Mapped[List["PurchaseOrderItem"]] = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="purchase_order", cascade="all, delete-orphan")

class PurchaseOrderItem(AuditableBase):
    """
    Firmed PO lines.
    """
    __tablename__ = "purchase_order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price >= 0", name="price_non_negative"),
    )

    purchase_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    item_description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="items")

class Quotation(AuditableBase):
    """
    Tender/RFQ configuration details.
    """
    __tablename__ = "quotations"

    rfq_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    close_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    vendor_quotations: Mapped[List["VendorQuotation"]] = relationship("VendorQuotation", back_populates="quotation", cascade="all, delete-orphan")

class VendorQuotation(AuditableBase):
    """
    Vendor bids against an RFQ.
    """
    __tablename__ = "vendor_quotations"

    quotation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    submitted_cost: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)

    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="vendor_quotations")
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="quotations")

class Invoice(AuditableBase):
    """
    Invoices mapping to specific PO.
    """
    __tablename__ = "invoices"

    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchase_orders.id", ondelete="RESTRICT"), nullable=False)
    total_due: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.UNPAID, nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="invoices")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

class Payment(AuditableBase):
    """
    Completed transactions matching invoices.
    """
    __tablename__ = "payments"

    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_paid: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. ACH, Wire Transfer
    reference_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")

class ApprovalWorkflow(AuditableBase):
    """
    Stores sequential authorization levels configuration steps.
    """
    __tablename__ = "approval_workflows"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    threshold_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

class ApprovalHistory(AuditableBase):
    """
    Record of approvals (or rejections) executed.
    """
    __tablename__ = "approval_histories"

    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False) # e.g., PurchaseRequest.id or PurchaseOrder.id
    target_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. PURCHASE_REQUEST, PURCHASE_ORDER
    approver_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), nullable=False)
    comments: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

class BudgetAllocation(AuditableBase):
    """
    Budgets configurations used specifically for procurement.
    """
    __tablename__ = "budget_allocations"

    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    allocated_amount: Mapped[float] = mapped_column(Float, nullable=False)
    remaining_amount: Mapped[float] = mapped_column(Float, nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
