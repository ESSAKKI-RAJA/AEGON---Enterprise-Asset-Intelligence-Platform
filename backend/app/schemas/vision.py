"""
AEGON Vision Intelligence — Pydantic Schemas
Enterprise-grade DTOs for the multi-angle asset inspection system.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class VisionViewType(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    FRONT = "front"
    REAR = "rear"
    LEFT = "left"
    RIGHT = "right"
    COMPOSITE_360 = "360"


class DefectSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class InspectionStatus(str, Enum):
    IDLE = "idle"
    UPLOADING = "uploading"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class MaintenancePriority(str, Enum):
    IMMEDIATE = "immediate"
    WITHIN_7_DAYS = "within_7_days"
    WITHIN_30_DAYS = "within_30_days"
    WITHIN_90_DAYS = "within_90_days"
    SCHEDULED = "scheduled"
    NONE_REQUIRED = "none_required"


# ---------------------------------------------------------------------------
# Core Finding DTO
# ---------------------------------------------------------------------------

class BoundingBoxMock(BaseModel):
    """Mock bounding box — ready for real YOLO/DETR integration."""
    x: float = Field(ge=0.0, le=1.0, description="Normalised x position (0-1)")
    y: float = Field(ge=0.0, le=1.0, description="Normalised y position (0-1)")
    width: float = Field(ge=0.0, le=1.0, description="Normalised width (0-1)")
    height: float = Field(ge=0.0, le=1.0, description="Normalised height (0-1)")
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class DefectFinding(BaseModel):
    """
    A single defect detected during vision inspection.
    Designed to be output-compatible with YOLOv11 / RT-DETR / SAM results.
    """
    finding_id: UUID = Field(default_factory=uuid4)
    defect_type: str
    severity: DefectSeverity
    confidence: float = Field(ge=0.0, le=1.0, description="AI confidence 0.0-1.0")
    description: str
    recommended_action: str
    bounding_box: Optional[BoundingBoxMock] = None
    area_affected_pct: float = Field(default=0.0, ge=0.0, le=100.0)


# ---------------------------------------------------------------------------
# Per-View Result
# ---------------------------------------------------------------------------

class ViewInspectionResult(BaseModel):
    """Result of a single-view AI inspection pass."""
    view_type: VisionViewType
    status: InspectionStatus
    image_filename: Optional[str] = None
    image_base64_preview: Optional[str] = None  # thumbnail only

    # AI output
    findings: list[DefectFinding] = Field(default_factory=list)
    view_health_score: float = Field(ge=0.0, le=100.0, default=100.0)
    defect_count: int = 0
    critical_count: int = 0
    processing_time_ms: float = 0.0
    inference_engine: str = "MockInferenceEngine"

    # Metadata
    inspected_at: Optional[datetime] = None
    operator: Optional[str] = None


# ---------------------------------------------------------------------------
# 360° Composite
# ---------------------------------------------------------------------------

class CompositeAnalysis(BaseModel):
    """Fused 360° analysis — synthesised from all view results."""
    overall_health_score: float = Field(ge=0.0, le=100.0)
    risk_score: float = Field(ge=0.0, le=100.0)
    quality_score: float = Field(ge=0.0, le=100.0)
    inspection_confidence: float = Field(ge=0.0, le=1.0)
    total_defects: int
    critical_defects: int
    views_inspected: int
    remaining_useful_life_years: float
    maintenance_priority: MaintenancePriority
    maintenance_cost_estimate_usd: float
    asset_readiness_pct: float
    deployment_status: str


# ---------------------------------------------------------------------------
# Executive Summary
# ---------------------------------------------------------------------------

class ExecutiveSummary(BaseModel):
    """AI-generated executive narrative."""
    summary_id: UUID = Field(default_factory=uuid4)
    narrative: str
    key_findings: list[str] = Field(default_factory=list)
    risk_matrix: dict[str, int] = Field(default_factory=dict)  # severity -> count
    recommendations: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Digital Twin State
# ---------------------------------------------------------------------------

class DigitalTwinState(BaseModel):
    """Real-time state of the asset Digital Twin, updated per inspection."""
    asset_name: str = "Asset Under Inspection"
    health_score: float = Field(ge=0.0, le=100.0, default=100.0)
    risk_score: float = Field(ge=0.0, le=100.0, default=0.0)
    temperature_celsius: float = 25.0
    maintenance_status: str = "Up to Date"
    inspection_progress_pct: float = Field(ge=0.0, le=100.0, default=0.0)
    views_completed: list[VisionViewType] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Inspection Session
# ---------------------------------------------------------------------------

class InspectionSession(BaseModel):
    """A complete inspection session encompassing all views."""
    session_id: UUID = Field(default_factory=uuid4)
    asset_id: Optional[str] = None
    asset_name: str = "Enterprise Asset"
    operator: str = "System"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: InspectionStatus = InspectionStatus.IDLE

    # Per-view results keyed by view type
    view_results: dict[str, ViewInspectionResult] = Field(default_factory=dict)

    # 360° analysis (populated after composite)
    composite: Optional[CompositeAnalysis] = None
    executive_summary: Optional[ExecutiveSummary] = None
    digital_twin: DigitalTwinState = Field(default_factory=DigitalTwinState)


# ---------------------------------------------------------------------------
# API Request / Response Schemas
# ---------------------------------------------------------------------------

class AnalyzeViewRequest(BaseModel):
    session_id: str
    view_type: VisionViewType
    asset_id: Optional[str] = None
    asset_name: Optional[str] = None
    operator: Optional[str] = "System"


class Generate360Request(BaseModel):
    session_id: str


class VisionStatistics(BaseModel):
    total_inspections: int
    avg_health_score: float
    avg_risk_score: float
    most_common_defect: str
    critical_defect_rate_pct: float
    avg_inspection_time_seconds: float
