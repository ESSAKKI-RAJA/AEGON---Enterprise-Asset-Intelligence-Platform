import uuid
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey, Date, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase
from app.models.enums import AssetStatus, LifecycleStage
from app.models.mixins import GeoLocationMixin

class AssetCategory(AuditableBase):
    """
    Broad categorization of assets (e.g. IT Equipment, Lab Equipment, Furniture).
    """
    __tablename__ = "asset_categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    subcategories: Mapped[List["AssetSubCategory"]] = relationship("AssetSubCategory", back_populates="category", cascade="all, delete-orphan")
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="category")

class AssetSubCategory(AuditableBase):
    """
    Refined categorization (e.g., Laptop, Desktop under IT Equipment).
    """
    __tablename__ = "asset_subcategories"

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_categories.id", ondelete="CASCADE"), nullable=False)

    category: Mapped["AssetCategory"] = relationship("AssetCategory", back_populates="subcategories")
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="subcategory")

class Manufacturer(AuditableBase):
    """
    Maker of the asset (e.g., Apple, Dell, Eppendorf).
    """
    __tablename__ = "manufacturers"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    support_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    support_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="manufacturer")

class Vendor(AuditableBase):
    """
    Merchant supplying the asset or services.
    """
    __tablename__ = "vendors"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="vendor")
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="vendor")
    quotations: Mapped[List["VendorQuotation"]] = relationship("VendorQuotation", back_populates="vendor")

class Supplier(AuditableBase):
    """
    Alternative supplier source if different from immediate Vendor.
    """
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class Asset(AuditableBase, GeoLocationMixin):
    """
    Core asset representing institutional properties.
    """
    __tablename__ = "assets"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    barcode: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    model_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[AssetStatus] = mapped_column(Enum(AssetStatus), default=AssetStatus.ACTIVE, nullable=False)
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    purchase_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    health_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    health_status: Mapped[str] = mapped_column(String(50), default="excellent", nullable=False)
    next_maintenance: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_maintenance: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    maintenance_cost_ytd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    utilization_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    warranty_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    subcategory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_subcategories.id", ondelete="RESTRICT"), nullable=False, index=True)
    manufacturer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("manufacturers.id", ondelete="SET NULL"), nullable=True, index=True)
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True, index=True)
    room_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True, index=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)

    category: Mapped["AssetCategory"] = relationship("AssetCategory", back_populates="assets")
    subcategory: Mapped["AssetSubCategory"] = relationship("AssetSubCategory", back_populates="assets")
    manufacturer: Mapped[Optional["Manufacturer"]] = relationship("Manufacturer", back_populates="assets")
    vendor: Mapped[Optional["Vendor"]] = relationship("Vendor", back_populates="assets")
    room: Mapped[Optional["Room"]] = relationship("Room", back_populates="assets")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="assets")

    assignments: Mapped[List["AssetAssignment"]] = relationship("AssetAssignment", back_populates="asset", cascade="all, delete-orphan")
    location_histories: Mapped[List["AssetLocationHistory"]] = relationship("AssetLocationHistory", back_populates="asset", cascade="all, delete-orphan")
    transfers: Mapped[List["AssetTransfer"]] = relationship("AssetTransfer", back_populates="asset", cascade="all, delete-orphan")
    disposals: Mapped[List["AssetDisposal"]] = relationship("AssetDisposal", back_populates="asset", cascade="all, delete-orphan")
    depreciations: Mapped[List["AssetDepreciation"]] = relationship("AssetDepreciation", back_populates="asset", cascade="all, delete-orphan")
    warranties: Mapped[List["AssetWarranty"]] = relationship("AssetWarranty", back_populates="asset", cascade="all, delete-orphan")
    lifecycles: Mapped[List["AssetLifecycle"]] = relationship("AssetLifecycle", back_populates="asset", cascade="all, delete-orphan")
    attachments: Mapped[List["AssetAttachment"]] = relationship("AssetAttachment", back_populates="asset", cascade="all, delete-orphan")
    documents: Mapped[List["AssetDocument"]] = relationship("AssetDocument", back_populates="asset", cascade="all, delete-orphan")
    images: Mapped[List["AssetImage"]] = relationship("AssetImage", back_populates="asset", cascade="all, delete-orphan")
    maintenance_records: Mapped[List["MaintenanceRecord"]] = relationship("MaintenanceRecord", back_populates="asset", cascade="all, delete-orphan")
    work_orders: Mapped[List["WorkOrder"]] = relationship("WorkOrder", back_populates="asset", cascade="all, delete-orphan")
    recommendations: Mapped[List["Recommendation"]] = relationship("Recommendation", back_populates="asset", cascade="all, delete-orphan")
    predictions: Mapped[List["Prediction"]] = relationship("Prediction", back_populates="asset", cascade="all, delete-orphan")

class AssetAssignment(AuditableBase):
    """
    Tracks allocation of assets to specific users or divisions.
    """
    __tablename__ = "asset_assignments"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_to_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    returned_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="assignments")

class AssetLocationHistory(AuditableBase, GeoLocationMixin):
    """
    Tracks coordinate and spatial audit trails for location updates.
    """
    __tablename__ = "asset_location_histories"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    moved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="location_histories")

class AssetTransfer(AuditableBase):
    """
    Formal custody transfer records between rooms or departments.
    """
    __tablename__ = "asset_transfers"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    from_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    to_department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    approved_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    transfer_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="transfers")

class AssetDisposal(AuditableBase):
    """
    Formal disposal logging (scrapping, donating, selling retired assets).
    """
    __tablename__ = "asset_disposals"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    disposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    proceeds: Mapped[Optional[float]] = mapped_column(Float, default=0.0)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="disposals")

class AssetDepreciation(AuditableBase):
    """
    Main depreciation calculations configurations per asset.
    """
    __tablename__ = "asset_depreciations"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(50), default="Straight Line", nullable=False) # Straight Line, Double Declining, etc.
    salvage_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    useful_life_years: Mapped[int] = mapped_column(nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="depreciations")
    records: Mapped[List["DepreciationRecord"]] = relationship("DepreciationRecord", back_populates="depreciation", cascade="all, delete-orphan")

class AssetWarranty(AuditableBase):
    """
    Warranty tracking information.
    """
    __tablename__ = "asset_warranties"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    policy_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="warranties")

class AssetLifecycle(AuditableBase):
    """
    Tracks state transitions of the asset state model.
    """
    __tablename__ = "asset_lifecycles"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    stage: Mapped[LifecycleStage] = mapped_column(Enum(LifecycleStage), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="lifecycles")

class AssetAttachment(AuditableBase):
    """
    Arbitrary file metadata attachment tracking.
    """
    __tablename__ = "asset_attachments"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="attachments")

class AssetDocument(AuditableBase):
    """
    Specific contracts, agreements, user guides, receipts.
    """
    __tablename__ = "asset_documents"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. Contract, Invoice
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="documents")

class AssetImage(AuditableBase):
    """
    Asset photographic records.
    """
    __tablename__ = "asset_images"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="images")
