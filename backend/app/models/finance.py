import uuid
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Float, Integer, ForeignKey, Date, DateTime, Enum, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditableBase
from app.models.enums import BudgetStatus

class CostCenter(AuditableBase):
    """
    Standard general ledger accounting cost segment.
    """
    __tablename__ = "cost_centers"

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    budgets: Mapped[List["Budget"]] = relationship("Budget", back_populates="cost_center", cascade="all, delete-orphan")
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="cost_center", cascade="all, delete-orphan")

class Budget(AuditableBase):
    """
    Top-level financial budget allocations configuration.
    """
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="amount_non_negative"),
    )

    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[BudgetStatus] = mapped_column(Enum(BudgetStatus), default=BudgetStatus.ACTIVE, nullable=False)
    cost_center_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cost_centers.id", ondelete="CASCADE"), nullable=False)

    cost_center: Mapped["CostCenter"] = relationship("CostCenter", back_populates="budgets")
    department_budgets: Mapped[List["DepartmentBudget"]] = relationship("DepartmentBudget", back_populates="budget", cascade="all, delete-orphan")

class DepartmentBudget(AuditableBase):
    """
    Allocations down to the department level.
    """
    __tablename__ = "department_budgets"

    budget_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    allocated_amount: Mapped[float] = mapped_column(Float, nullable=False)
    spent_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    budget: Mapped["Budget"] = relationship("Budget", back_populates="department_budgets")
    department: Mapped["Department"] = relationship("Department", foreign_keys=[department_id])

class Expense(AuditableBase):
    """
    Individual payments or operational costs incurred.
    """
    __tablename__ = "expenses"

    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    cost_center_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cost_centers.id", ondelete="RESTRICT"), nullable=False)

    cost_center: Mapped["CostCenter"] = relationship("CostCenter", back_populates="expenses")

class DepreciationRecord(AuditableBase):
    """
    Individual depreciation adjustments calculations log.
    """
    __tablename__ = "depreciation_records"

    depreciation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_depreciations.id", ondelete="CASCADE"), nullable=False)
    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    depreciation_amount: Mapped[float] = mapped_column(Float, nullable=False)
    book_value: Mapped[float] = mapped_column(Float, nullable=False)

    depreciation: Mapped["AssetDepreciation"] = relationship("AssetDepreciation", back_populates="records")

class FinancialTransaction(AuditableBase):
    """
    Audit log of financial movements.
    """
    __tablename__ = "financial_transactions"

    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. DEBIT, CREDIT
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class AssetValuation(AuditableBase):
    """
    Valuation assessments logs for high value assets.
    """
    __tablename__ = "asset_valuations"

    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    valuation_amount: Mapped[float] = mapped_column(Float, nullable=False)
    valuation_date: Mapped[date] = mapped_column(Date, nullable=False)
    assessor: Mapped[str] = mapped_column(String(100), nullable=False)

class InsurancePolicy(AuditableBase):
    """
    Assets general insurance cover configuration.
    """
    __tablename__ = "insurance_policies"

    policy_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(150), nullable=False)
    coverage_limit: Mapped[float] = mapped_column(Float, nullable=False)
    annual_premium: Mapped[float] = mapped_column(Float, nullable=False)
    expiration_date: Mapped[date] = mapped_column(Date, nullable=False)
