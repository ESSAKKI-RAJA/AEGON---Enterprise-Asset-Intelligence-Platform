from __future__ import annotations
from .base import Base, AuditableBase
from .enums import (
    AssetStatus, MaintenanceStatus, WorkOrderStatus, ApprovalStatus,
    InventoryStatus, NotificationStatus, Priority, Severity, UserRole,
    PermissionType, BudgetStatus, VendorStatus, PaymentStatus,
    LifecycleStage, HealthStatus, FailureRisk
)
from .mixins import TimestampMixin, AuditMixin, SoftDeleteMixin, VersionMixin, OwnershipMixin, GeoLocationMixin
from .identity import Role, Permission, RolePermission, User, UserSession, PasswordResetToken, RefreshToken, AuditLog, LoginHistory, ActivityLog
from .organization import University, Campus, Faculty, Department, Building, Floor, Room
from .asset import (
    AssetCategory, AssetSubCategory, Manufacturer, Vendor, Supplier, Asset,
    AssetAssignment, AssetLocationHistory, AssetTransfer, AssetDisposal,
    AssetDepreciation, AssetWarranty, AssetLifecycle, AssetAttachment,
    AssetDocument, AssetImage
)
from .inventory import (
    Warehouse, InventoryItem, InventoryTransaction, InventoryAdjustment,
    InventoryConsumption, InventoryTransfer, InventoryReservation, StockAlert, StockAudit
)
from .procurement import (
    PurchaseRequest, PurchaseRequestItem, PurchaseOrder, PurchaseOrderItem,
    Quotation, VendorQuotation, Invoice, Payment, ApprovalWorkflow, ApprovalHistory, BudgetAllocation
)
from .maintenance import (
    MaintenancePlan, MaintenanceSchedule, MaintenanceRecord, MaintenanceTask,
    MaintenanceChecklist, WorkOrder, WorkOrderTask, MaintenanceCost,
    MaintenanceHistory, FailureEvent, Downtime, TechnicianAssignment
)
from .finance import (
    CostCenter, Budget, DepartmentBudget, Expense, DepreciationRecord,
    FinancialTransaction, AssetValuation, InsurancePolicy
)
from .analytics import (
    DashboardMetric, KPI, DepartmentKPI, FinancialKPI, MaintenanceKPI,
    InventoryKPI, ExecutiveSummary, Snapshot, HistoricalMetric, Trend
)
from .ai import (
    FeatureStore, Prediction, PredictionHistory, Recommendation,
    RecommendationHistory, ModelRegistry, ModelVersion, TrainingDataset,
    InferenceLog, RiskAssessment, HealthScore, FailurePrediction,
    BudgetForecast, VendorScore, AssetUtilization, RemainingUsefulLife
)
from .copilot import (
    Conversation, ConversationMessage, PromptTemplate, KnowledgeDocument,
    Embedding, VectorReference, RetrievedContext, Citation, LLMRequest,
    LLMResponse, ConversationMemory
)
from .reporting import (
    ReportTemplate, Report, ScheduledReport, ReportExecution, ExportHistory,
    PDFExport, ExcelExport, CSVExport
)
from .notifications import (
    NotificationTemplate, Notification, NotificationChannel, NotificationHistory,
    AlertRule, Alert, AlertHistory, Reminder
)
from .system import (
    SystemSetting, ApplicationConfig, FeatureFlag, APIKey, Webhook,
    WebhookLog, Integration, IntegrationLog
)

__all__ = [
    "Base", "AuditableBase",
    "AssetStatus", "MaintenanceStatus", "WorkOrderStatus", "ApprovalStatus",
    "InventoryStatus", "NotificationStatus", "Priority", "Severity", "UserRole",
    "PermissionType", "BudgetStatus", "VendorStatus", "PaymentStatus",
    "LifecycleStage", "HealthStatus", "FailureRisk",
    "TimestampMixin", "AuditMixin", "SoftDeleteMixin", "VersionMixin", "OwnershipMixin", "GeoLocationMixin",
    "Role", "Permission", "RolePermission", "User", "UserSession", "PasswordResetToken", "RefreshToken", "AuditLog", "LoginHistory", "ActivityLog",
    "University", "Campus", "Faculty", "Department", "Building", "Floor", "Room",
    "AssetCategory", "AssetSubCategory", "Manufacturer", "Vendor", "Supplier", "Asset",
    "AssetAssignment", "AssetLocationHistory", "AssetTransfer", "AssetDisposal",
    "AssetDepreciation", "AssetWarranty", "AssetLifecycle", "AssetAttachment",
    "AssetDocument", "AssetImage",
    "Warehouse", "InventoryItem", "InventoryTransaction", "InventoryAdjustment",
    "InventoryConsumption", "InventoryTransfer", "InventoryReservation", "StockAlert", "StockAudit",
    "PurchaseRequest", "PurchaseRequestItem", "PurchaseOrder", "PurchaseOrderItem",
    "Quotation", "VendorQuotation", "Invoice", "Payment", "ApprovalWorkflow", "ApprovalHistory", "BudgetAllocation",
    "MaintenancePlan", "MaintenanceSchedule", "MaintenanceRecord", "MaintenanceTask",
    "MaintenanceChecklist", "WorkOrder", "WorkOrderTask", "MaintenanceCost",
    "MaintenanceHistory", "FailureEvent", "Downtime", "TechnicianAssignment",
    "CostCenter", "Budget", "DepartmentBudget", "Expense", "DepreciationRecord",
    "FinancialTransaction", "AssetValuation", "InsurancePolicy",
    "DashboardMetric", "KPI", "DepartmentKPI", "FinancialKPI", "MaintenanceKPI",
    "InventoryKPI", "ExecutiveSummary", "Snapshot", "HistoricalMetric", "Trend",
    "FeatureStore", "Prediction", "PredictionHistory", "Recommendation",
    "RecommendationHistory", "ModelRegistry", "ModelVersion", "TrainingDataset",
    "InferenceLog", "RiskAssessment", "HealthScore", "FailurePrediction",
    "BudgetForecast", "VendorScore", "AssetUtilization", "RemainingUsefulLife",
    "Conversation", "ConversationMessage", "PromptTemplate", "KnowledgeDocument",
    "Embedding", "VectorReference", "RetrievedContext", "Citation", "LLMRequest",
    "LLMResponse", "ConversationMemory",
    "ReportTemplate", "Report", "ScheduledReport", "ReportExecution", "ExportHistory",
    "PDFExport", "ExcelExport", "CSVExport",
    "NotificationTemplate", "Notification", "NotificationChannel", "NotificationHistory",
    "AlertRule", "Alert", "AlertHistory", "Reminder",
    "SystemSetting", "ApplicationConfig", "FeatureFlag", "APIKey", "Webhook",
    "WebhookLog", "Integration", "IntegrationLog"
]
