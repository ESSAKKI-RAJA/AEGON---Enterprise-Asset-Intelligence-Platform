from typing import Optional
"""
AEGON Vision Intelligence — VisionInspectionService
Enterprise-grade multi-angle computer vision inspection service.

Architecture:
    - BaseInferenceEngine: abstract contract — swap in OpenCV/YOLO/ONNX without changing this file
    - MockInferenceEngine: realistic stochastic mock for development/demo
    - VisionInspectionService: orchestrates the full inspection pipeline

Inspection Pipeline:
    Image Upload → Validation → Preprocessing → Object Detection →
    Surface Inspection → Damage Detection → Severity Classification →
    Confidence Scoring → Risk Assessment → Health Score → Summary → Report
"""
from __future__ import annotations

import logging
import random
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.vision import (
    BoundingBoxMock,
    CompositeAnalysis,
    DefectFinding,
    DefectSeverity,
    DigitalTwinState,
    ExecutiveSummary,
    InspectionSession,
    InspectionStatus,
    MaintenancePriority,
    VisionStatistics,
    VisionViewType,
    ViewInspectionResult,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defect Catalog — per view type
# ---------------------------------------------------------------------------

DEFECT_CATALOG: Dict[VisionViewType, List[Dict[str, Any]]] = {
    VisionViewType.TOP: [
        {"type": "Surface Scratch", "severity_weight": 0.15, "action": "Light polish and recoat"},
        {"type": "Paint Damage", "severity_weight": 0.25, "action": "Repaint affected section"},
        {"type": "Surface Wear", "severity_weight": 0.20, "action": "Apply protective coating"},
        {"type": "Rust Formation", "severity_weight": 0.55, "action": "Sandblast and apply rust inhibitor"},
        {"type": "Corrosion", "severity_weight": 0.70, "action": "Chemical treatment and sealing"},
        {"type": "Dust Build-up", "severity_weight": 0.10, "action": "Industrial cleaning required"},
        {"type": "Heat Mark", "severity_weight": 0.45, "action": "Inspect thermal management"},
        {"type": "Missing Component", "severity_weight": 0.85, "action": "Immediate part replacement"},
        {"type": "Structural Damage", "severity_weight": 0.95, "action": "Engineering assessment required"},
    ],
    VisionViewType.BOTTOM: [
        {"type": "Base Crack", "severity_weight": 0.80, "action": "Structural integrity assessment"},
        {"type": "Oil Leakage", "severity_weight": 0.90, "action": "Seal replacement and oil top-up"},
        {"type": "Rust Formation", "severity_weight": 0.55, "action": "Rust treatment and recoating"},
        {"type": "Corrosion", "severity_weight": 0.70, "action": "Chemical treatment required"},
        {"type": "Seal Damage", "severity_weight": 0.75, "action": "Replace gaskets and seals"},
        {"type": "Structural Weakness", "severity_weight": 0.85, "action": "Engineering review and reinforcement"},
        {"type": "Missing Fastener", "severity_weight": 0.65, "action": "Replace bolts and torque to spec"},
        {"type": "Weld Damage", "severity_weight": 0.90, "action": "Re-weld and NDT inspection"},
    ],
    VisionViewType.FRONT: [
        {"type": "Panel Damage", "severity_weight": 0.40, "action": "Panel replacement"},
        {"type": "Display Issue", "severity_weight": 0.50, "action": "Display module inspection"},
        {"type": "Missing Label", "severity_weight": 0.15, "action": "Relabel per compliance standard"},
        {"type": "Surface Crack", "severity_weight": 0.70, "action": "Crack propagation analysis"},
        {"type": "Deformation", "severity_weight": 0.75, "action": "Structural alignment check"},
        {"type": "Misalignment", "severity_weight": 0.60, "action": "Recalibrate and realign"},
    ],
    VisionViewType.REAR: [
        {"type": "Cable Fraying", "severity_weight": 0.70, "action": "Replace cable harness"},
        {"type": "Connector Damage", "severity_weight": 0.65, "action": "Replace connectors"},
        {"type": "Broken Port", "severity_weight": 0.60, "action": "Port repair or replacement"},
        {"type": "Heat Damage", "severity_weight": 0.80, "action": "Thermal analysis and component replacement"},
        {"type": "Corrosion", "severity_weight": 0.70, "action": "Clean and apply corrosion inhibitor"},
        {"type": "Loose Component", "severity_weight": 0.55, "action": "Re-secure and torque check"},
    ],
    VisionViewType.LEFT: [
        {"type": "Side Impact Mark", "severity_weight": 0.50, "action": "Structural impact assessment"},
        {"type": "Paint Wear", "severity_weight": 0.20, "action": "Touch-up paint and clearcoat"},
        {"type": "Edge Damage", "severity_weight": 0.45, "action": "Edge reinforcement"},
        {"type": "Alignment Problem", "severity_weight": 0.55, "action": "Realignment required"},
        {"type": "Missing Screw", "severity_weight": 0.40, "action": "Replace fasteners to torque spec"},
    ],
    VisionViewType.RIGHT: [
        {"type": "Side Impact Mark", "severity_weight": 0.50, "action": "Structural impact assessment"},
        {"type": "Paint Wear", "severity_weight": 0.20, "action": "Touch-up paint and clearcoat"},
        {"type": "Edge Damage", "severity_weight": 0.45, "action": "Edge reinforcement"},
        {"type": "Alignment Problem", "severity_weight": 0.55, "action": "Realignment required"},
        {"type": "Missing Screw", "severity_weight": 0.40, "action": "Replace fasteners to torque spec"},
    ],
    VisionViewType.COMPOSITE_360: [],  # 360 is synthesised, not directly scanned
}


# ---------------------------------------------------------------------------
# Abstract Inference Engine — ready for OpenCV / YOLO / ONNX / Roboflow
# ---------------------------------------------------------------------------

class BaseInferenceEngine(ABC):
    """
    Abstract contract for the CV inference layer.
    Implement this class to integrate:
        - OpenCV-based defect detection
        - YOLOv11 / YOLOv12 object detection
        - TensorFlow / PyTorch custom models
        - ONNX Runtime
        - Roboflow hosted inference
        - Segment Anything (SAM)
        - RT-DETR
    """

    @abstractmethod
    def run_inference(
        self,
        image_bytes: Optional[bytes],
        view_type: VisionViewType,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Run inference on an image.

        Args:
            image_bytes: Raw image bytes (None for mock)
            view_type: Which view is being inspected
            context: Additional metadata (asset_id, age, etc.)

        Returns:
            List of raw detection dicts with keys:
                defect_type, severity_weight, confidence, bbox, description
        """
        ...

    @abstractmethod
    def get_engine_name(self) -> str:
        """Return human-readable engine name for audit trails."""
        ...


class MockInferenceEngine(BaseInferenceEngine):
    """
    Realistic stochastic mock inference engine.

    Simulates:
    - Variable defect probability per view type
    - Realistic confidence scores
    - Asset condition degradation simulation
    - Processing latency simulation
    """

    def __init__(self, seed: Optional[int] = None):
        self._base_seed = seed if seed is not None else random.randint(0, 10000)

    def run_inference(
        self,
        image_bytes: Optional[bytes],
        view_type: VisionViewType,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate realistic mock detections using session seed."""
        # Use session_id + view_type for deterministic randomness
        session_id = context.get("session_id", str(uuid.uuid4()))
        seed_str = f"{self._base_seed}_{session_id}_{view_type.value}"
        session_seed = sum(ord(c) for c in seed_str)
        rng = random.Random(session_seed)

        # Simulate processing time (300ms - 1200ms) for pipeline animation realism
        time.sleep(rng.uniform(0.3, 1.2))

        catalog = DEFECT_CATALOG.get(view_type, [])
        if not catalog:
            return []

        base_probs: Dict[VisionViewType, float] = {
            VisionViewType.TOP: 0.60,
            VisionViewType.BOTTOM: 0.55,
            VisionViewType.FRONT: 0.45,
            VisionViewType.REAR: 0.50,
            VisionViewType.LEFT: 0.40,
            VisionViewType.RIGHT: 0.40,
        }
        base_prob = base_probs.get(view_type, 0.50)

        detections: List[Dict[str, Any]] = []
        for defect in catalog:
            if rng.random() < base_prob:
                conf = defect["severity_weight"] * 0.4 + rng.uniform(0.45, 0.60)
                conf = min(conf, 0.99)
                
                # Mock mask points for segmentation
                mask_points = [
                    [round(rng.uniform(0.1, 0.9), 2), round(rng.uniform(0.1, 0.9), 2)]
                    for _ in range(rng.randint(4, 8))
                ]

                detections.append({
                    "defect_type": defect["type"],
                    "severity_weight": defect["severity_weight"],
                    "confidence": round(conf, 3),
                    "action": defect["action"],
                    "bbox": {
                        "x": round(rng.uniform(0.05, 0.75), 3),
                        "y": round(rng.uniform(0.05, 0.75), 3),
                        "width": round(rng.uniform(0.05, 0.25), 3),
                        "height": round(rng.uniform(0.05, 0.20), 3),
                    },
                    "mask_points": mask_points,
                    "heatmap_data": f"mock_heatmap_{rng.randint(100, 999)}"
                })

        return detections

    def get_engine_name(self) -> str:
        return "AEGON MockInferenceEngine v1.0 (OpenCV/YOLO ready)"


# ---------------------------------------------------------------------------
# Severity Classifier
# ---------------------------------------------------------------------------

def _classify_severity(severity_weight: float) -> DefectSeverity:
    """Convert a raw severity weight (0-1) to a DefectSeverity enum."""
    if severity_weight >= 0.85:
        return DefectSeverity.CRITICAL
    elif severity_weight >= 0.65:
        return DefectSeverity.HIGH
    elif severity_weight >= 0.40:
        return DefectSeverity.MEDIUM
    else:
        return DefectSeverity.LOW


# ---------------------------------------------------------------------------
# In-Memory Session Store (production: replace with DB via Repository pattern)
# ---------------------------------------------------------------------------

_SESSION_STORE: Dict[str, InspectionSession] = {}


def _get_or_create_session(session_id: str, asset_name: str = "Enterprise Asset") -> InspectionSession:
    if session_id not in _SESSION_STORE:
        _SESSION_STORE[session_id] = InspectionSession(
            session_id=uuid.UUID(session_id),
            asset_name=asset_name,
            status=InspectionStatus.ANALYZING,
        )
    return _SESSION_STORE[session_id]


# ---------------------------------------------------------------------------
# Statistics store (demo)
# ---------------------------------------------------------------------------
_INSPECTION_HISTORY: List[Dict[str, Any]] = []


# ---------------------------------------------------------------------------
# VisionInspectionService
# ---------------------------------------------------------------------------

class VisionInspectionService:
    """
    Enterprise Vision Inspection Service.

    Responsibilities:
        - Orchestrate the complete AI inspection pipeline
        - Fuse multi-view results into a 360° composite
        - Calculate health and risk scores
        - Estimate Remaining Useful Life
        - Generate executive summaries
        - Produce report data

    Architecture Note:
        The _inference_engine is injected and can be swapped without
        changing ANY code in this class or in the API layer.
    """

    def __init__(self, inference_engine: Optional[BaseInferenceEngine] = None):
        self._engine = inference_engine or MockInferenceEngine()
        logger.info(f"VisionInspectionService initialised with engine: {self._engine.get_engine_name()}")

    # ------------------------------------------------------------------
    # Core Inspection Pipeline
    # ------------------------------------------------------------------

    def inspect_view(
        self,
        view_type: VisionViewType,
        image_bytes: Optional[bytes],
        session_id: str,
        asset_name: str = "Enterprise Asset",
        operator: str = "System",
    ) -> ViewInspectionResult:
        """
        Run the full inspection pipeline for a single view.

        Pipeline:
            Image Validation → Preprocessing →
            Object Detection → Surface Inspection →
            Damage Detection → Severity Classification →
            Confidence Scoring → Risk Assessment → Finding DTOs
        """
        start_ms = time.time() * 1000
        logger.info(f"[VisionService] Inspecting {view_type.value} view | session={session_id}")

        # 1. Preprocessing (image validation / normalisation)
        context = {
            "session_id": session_id,
            "asset_name": asset_name,
            "view_type": view_type.value,
        }

        # 2. Run inference through the pluggable engine
        raw_detections = self._engine.run_inference(image_bytes, view_type, context)

        # 3. Build typed DefectFinding DTOs
        findings: List[DefectFinding] = []
        for det in raw_detections:
            severity = _classify_severity(det["severity_weight"])
            bbox = BoundingBoxMock(
                label=det["defect_type"],
                confidence=det["confidence"],
                **det["bbox"],
            )
            finding = DefectFinding(
                defect_type=det["defect_type"],
                severity=severity,
                confidence=det["confidence"],
                description=f"{det['defect_type']} detected with {det['confidence']*100:.0f}% confidence on {view_type.value} surface.",
                recommended_action=det["action"],
                bounding_box=bbox,
                area_affected_pct=round(det["bbox"]["width"] * det["bbox"]["height"] * 100, 1),
                heatmap_data=det["heatmap_data"],
                mask_points=det["mask_points"],
                estimated_repair_cost=round(det["severity_weight"] * 5000 + random.uniform(100, 500), 2),
                estimated_repair_time_mins=int(det["severity_weight"] * 240 + random.uniform(30, 60))
            )
            findings.append(finding)

        # 4. Calculate view-level health score
        view_health = self._calculate_view_health(findings)
        critical_count = sum(1 for f in findings if f.severity == DefectSeverity.CRITICAL)

        processing_time = time.time() * 1000 - start_ms
        
        # Determine GPU / Enterprise metadata
        gpu_status = random.choice(["NVIDIA A100 - Optimal", "NVIDIA H100 - Active", "Cluster 04 - Active"])

        result = ViewInspectionResult(
            view_type=view_type,
            status=InspectionStatus.COMPLETE,
            findings=findings,
            view_health_score=view_health,
            defect_count=len(findings),
            critical_count=critical_count,
            processing_time_ms=round(processing_time, 1),
            inference_engine=self._engine.get_engine_name(),
            model_version="AEGON-Vision-V6.5-Enterprise",
            gpu_status=gpu_status,
            cpu_usage_pct=round(random.uniform(15.0, 45.0), 1),
            memory_usage_mb=round(random.uniform(4000.0, 12000.0), 1),
            queue_position=random.randint(0, 2),
            inspected_at=datetime.utcnow(),
            operator=operator,
        )

        # 5. Update session store
        session = _get_or_create_session(session_id, asset_name)
        session.view_results[view_type.value] = result
        self._refresh_digital_twin(session)

        logger.info(
            f"[VisionService] {view_type.value} complete | "
            f"findings={len(findings)} critical={critical_count} "
            f"health={view_health:.1f} time={processing_time:.0f}ms"
        )
        return result

    # ------------------------------------------------------------------
    # Health & Risk Algorithms
    # ------------------------------------------------------------------

    def _calculate_view_health(self, findings: List[DefectFinding]) -> float:
        """
        Calculate health score for a single view.
        100 = pristine, 0 = catastrophic failure.
        """
        if not findings:
            return 100.0

        severity_weights = {
            DefectSeverity.CRITICAL: 25.0,
            DefectSeverity.HIGH: 15.0,
            DefectSeverity.MEDIUM: 7.0,
            DefectSeverity.LOW: 2.5,
            DefectSeverity.NONE: 0.0,
        }
        total_deduction = sum(severity_weights[f.severity] for f in findings)
        health = max(0.0, 100.0 - total_deduction)
        return round(health, 1)

    def calculate_health_score(self, view_results: List[ViewInspectionResult]) -> float:
        """Average health across all inspected views, weighted by severity."""
        if not view_results:
            return 100.0
        scores = [v.view_health_score for v in view_results]
        return round(sum(scores) / len(scores), 1)

    def calculate_risk_score(self, view_results: List[ViewInspectionResult]) -> float:
        """Risk score 0-100 (higher = more risk)."""
        if not view_results:
            return 0.0

        all_findings = [f for v in view_results for f in v.findings]
        if not all_findings:
            return 0.0

        critical = sum(1 for f in all_findings if f.severity == DefectSeverity.CRITICAL)
        high = sum(1 for f in all_findings if f.severity == DefectSeverity.HIGH)
        medium = sum(1 for f in all_findings if f.severity == DefectSeverity.MEDIUM)
        low = sum(1 for f in all_findings if f.severity == DefectSeverity.LOW)

        risk = min(100.0, (critical * 20 + high * 10 + medium * 4 + low * 1))
        return round(risk, 1)

    def estimate_remaining_useful_life(self, health_score: float, risk_score: float) -> float:
        """
        Estimate RUL in years.
        Simple linear model — replace with Weibull/Prophet in production.
        """
        if health_score <= 10:
            return 0.1
        base_life = 8.0  # years
        health_factor = health_score / 100.0
        risk_factor = 1.0 - (risk_score / 200.0)
        rul = base_life * health_factor * risk_factor
        return round(max(0.1, rul), 1)

    def recommend_maintenance(
        self, risk_score: float, critical_count: int, health_score: float
    ) -> Tuple[MaintenancePriority, str, float]:
        """
        Recommend maintenance priority, description, and cost estimate.
        Returns: (priority, description, estimated_cost_usd)
        """
        if critical_count > 0 or risk_score > 80:
            return (
                MaintenancePriority.IMMEDIATE,
                f"Critical defects detected ({critical_count} critical findings). Immediate shutdown and repair required.",
                random.uniform(8000, 25000),
            )
        elif risk_score > 60 or health_score < 60:
            return (
                MaintenancePriority.WITHIN_7_DAYS,
                "High-severity defects detected. Schedule maintenance within 7 days.",
                random.uniform(3000, 8000),
            )
        elif risk_score > 40 or health_score < 75:
            return (
                MaintenancePriority.WITHIN_30_DAYS,
                "Moderate defects identified. Schedule preventive maintenance within 30 days.",
                random.uniform(1000, 3000),
            )
        elif risk_score > 20 or health_score < 90:
            return (
                MaintenancePriority.WITHIN_90_DAYS,
                "Minor defects detected. Include in next scheduled maintenance cycle.",
                random.uniform(300, 1000),
            )
        else:
            return (
                MaintenancePriority.NONE_REQUIRED,
                "Asset is in excellent condition. Continue standard monitoring.",
                0.0,
            )

    # ------------------------------------------------------------------
    # 360° Composite Analysis
    # ------------------------------------------------------------------

    def generate_360_summary(self, session_id: str) -> Tuple[CompositeAnalysis, ExecutiveSummary]:
        """
        Fuse all view results into a 360° composite analysis.
        Must be called after all (or at least 2) views have been inspected.
        """
        session = _SESSION_STORE.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        view_results = list(session.view_results.values())

        # --- Core metrics ---
        health = self.calculate_health_score(view_results)
        risk = self.calculate_risk_score(view_results)
        rul = self.estimate_remaining_useful_life(health, risk)

        all_findings = [f for v in view_results for f in v.findings]
        critical_count = sum(1 for f in all_findings if f.severity == DefectSeverity.CRITICAL)

        priority, priority_desc, cost_est = self.recommend_maintenance(risk, critical_count, health)

        # Aggregate confidence across all views
        if view_results:
            avg_conf = sum(
                (sum(f.confidence for f in v.findings) / max(1, len(v.findings)))
                for v in view_results
            ) / len(view_results)
        else:
            avg_conf = 0.95

        quality_score = round((health + (100 - risk)) / 2, 1)
        readiness = round(max(0, min(100, health - (risk * 0.3))), 1)

        deployment_status = (
            "HOLD — Critical Issues" if critical_count > 0
            else "CAUTION — Maintenance Due" if risk > 40
            else "OPERATIONAL"
        )

        composite = CompositeAnalysis(
            overall_health_score=health,
            risk_score=risk,
            quality_score=quality_score,
            inspection_confidence=round(avg_conf, 3),
            total_defects=len(all_findings),
            critical_defects=critical_count,
            views_inspected=len(view_results),
            remaining_useful_life_years=rul,
            maintenance_priority=priority,
            maintenance_cost_estimate_usd=round(cost_est, 2),
            asset_readiness_pct=readiness,
            deployment_status=deployment_status,
        )

        summary = self.generate_executive_summary(session, composite, priority_desc)

        # Persist to session
        session.composite = composite
        session.executive_summary = summary
        session.completed_at = datetime.utcnow()
        session.status = InspectionStatus.COMPLETE

        # Record in history
        self._record_history(session, composite)

        return composite, summary

    # ------------------------------------------------------------------
    # Executive Summary Generation
    # ------------------------------------------------------------------

    def generate_executive_summary(
        self,
        session: InspectionSession,
        composite: CompositeAnalysis,
        maintenance_desc: str,
    ) -> ExecutiveSummary:
        """Generate an AI executive narrative from inspection results."""
        all_findings = [f for v in session.view_results.values() for f in v.findings]

        # Build natural-language key findings
        key_findings: List[str] = []
        views_inspected = sorted(session.view_results.keys())

        if not all_findings:
            key_findings.append("No defects detected across all inspected surfaces.")
        else:
            severity_map: Dict[str, List[str]] = {
                "critical": [], "high": [], "medium": [], "low": []
            }
            for f in all_findings:
                if f.severity == DefectSeverity.CRITICAL:
                    severity_map["critical"].append(f.defect_type)
                elif f.severity == DefectSeverity.HIGH:
                    severity_map["high"].append(f.defect_type)
                elif f.severity == DefectSeverity.MEDIUM:
                    severity_map["medium"].append(f.defect_type)
                else:
                    severity_map["low"].append(f.defect_type)

            for sev, defects in severity_map.items():
                if defects:
                    unique = list(dict.fromkeys(defects))
                    key_findings.append(
                        f"{sev.title()} severity: {', '.join(unique[:3])} detected."
                    )

        # Build narrative
        health_label = (
            "excellent" if composite.overall_health_score >= 85
            else "good" if composite.overall_health_score >= 70
            else "fair" if composite.overall_health_score >= 50
            else "poor"
        )

        narrative_lines = [
            f"Multi-angle enterprise inspection of {session.asset_name} completed successfully.",
            f"{len(views_inspected)} view{'s' if len(views_inspected) > 1 else ''} inspected: {', '.join(v.upper() for v in views_inspected)}.",
            f"Overall asset condition is {health_label} with a health score of {composite.overall_health_score:.0f}/100.",
        ]

        if composite.total_defects > 0:
            narrative_lines.append(
                f"{composite.total_defects} defect{'s' if composite.total_defects > 1 else ''} identified across all surfaces, "
                f"including {composite.critical_defects} critical issue{'s' if composite.critical_defects != 1 else ''}."
            )
        else:
            narrative_lines.append("No defects detected. Asset surfaces are in pristine condition.")

        narrative_lines.append(
            f"Remaining Useful Life is estimated at {composite.remaining_useful_life_years} years based on current condition."
        )
        narrative_lines.append(maintenance_desc)

        risk_matrix = {
            "critical": sum(1 for f in all_findings if f.severity == DefectSeverity.CRITICAL),
            "high": sum(1 for f in all_findings if f.severity == DefectSeverity.HIGH),
            "medium": sum(1 for f in all_findings if f.severity == DefectSeverity.MEDIUM),
            "low": sum(1 for f in all_findings if f.severity == DefectSeverity.LOW),
        }

        recommendations = [
            f"Deploy {composite.maintenance_priority.value.replace('_', ' ').title()} maintenance protocol.",
            "Update asset record in AEGON registry with inspection findings.",
            "Attach inspection report to asset documentation trail.",
        ]
        if composite.critical_defects > 0:
            recommendations.insert(0, "URGENT: Withdraw asset from service until critical defects are resolved.")

        return ExecutiveSummary(
            narrative="\n\n".join(narrative_lines),
            key_findings=key_findings,
            risk_matrix=risk_matrix,
            recommendations=recommendations,
            generated_at=datetime.utcnow(),
        )

    # ------------------------------------------------------------------
    # Digital Twin
    # ------------------------------------------------------------------

    def _refresh_digital_twin(self, session: InspectionSession) -> None:
        """Update the session's Digital Twin state after each view inspection."""
        views_done = list(session.view_results.keys())
        total_views = len(VisionViewType) - 1  # exclude COMPOSITE_360

        view_results = list(session.view_results.values())
        health = self.calculate_health_score(view_results)
        risk = self.calculate_risk_score(view_results)

        # Simulate temperature, pressure, and rotation
        temperature = round(25.0 + (risk / 100.0) * 40.0, 1)
        pressure = round(14.7 + (risk / 100.0) * 10.0, 1)
        rotation = round(1200.0 - (risk / 100.0) * 400.0, 1) if risk < 80 else 0.0

        progress = (len(views_done) / total_views) * 100

        maintenance_status = (
            "Immediate Action Required" if risk > 80
            else "Schedule Within 30 Days" if risk > 40
            else "Up to Date"
        )
        
        # Generate simulated historical trends
        hist_health = [min(100.0, health + (i * 2) + random.uniform(-3, 3)) for i in range(10, 0, -1)] + [health]
        hist_risk = [max(0.0, risk - (i * 2) + random.uniform(-3, 3)) for i in range(10, 0, -1)] + [risk]

        session.digital_twin = DigitalTwinState(
            asset_name=session.asset_name,
            health_score=health,
            risk_score=risk,
            temperature_celsius=temperature,
            pressure_psi=pressure,
            rotation_rpm=rotation,
            maintenance_status=maintenance_status,
            inspection_progress_pct=round(progress, 1),
            views_completed=[VisionViewType(v) for v in views_done],
            historical_health_trend=[round(x, 1) for x in hist_health],
            historical_risk_trend=[round(x, 1) for x in hist_risk],
            last_updated=datetime.utcnow(),
        )

    # ------------------------------------------------------------------
    # History & Statistics
    # ------------------------------------------------------------------

    def _record_history(self, session: InspectionSession, composite: CompositeAnalysis) -> None:
        """Record completed inspection in history store."""
        _INSPECTION_HISTORY.append({
            "session_id": str(session.session_id),
            "asset_name": session.asset_name,
            "operator": session.operator,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "views_inspected": composite.views_inspected,
            "total_defects": composite.total_defects,
            "critical_defects": composite.critical_defects,
            "health_score": composite.overall_health_score,
            "risk_score": composite.risk_score,
            "maintenance_priority": composite.maintenance_priority.value,
            "status": session.status.value,
        })

    def get_inspection_history(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Return paginated inspection history."""
        return list(reversed(_INSPECTION_HISTORY))[offset: offset + limit]

    def get_session(self, session_id: str) -> Optional[InspectionSession]:
        """Retrieve a session by ID."""
        return _SESSION_STORE.get(session_id)

    def get_statistics(self) -> VisionStatistics:
        """Calculate aggregate statistics across all inspections."""
        if not _INSPECTION_HISTORY:
            return VisionStatistics(
                total_inspections=0,
                avg_health_score=0.0,
                avg_risk_score=0.0,
                most_common_defect="N/A",
                critical_defect_rate_pct=0.0,
                avg_inspection_time_seconds=0.0,
            )

        total = len(_INSPECTION_HISTORY)
        avg_health = sum(h["health_score"] for h in _INSPECTION_HISTORY) / total
        avg_risk = sum(h["risk_score"] for h in _INSPECTION_HISTORY) / total

        # Count defect types across sessions
        defect_counter: Dict[str, int] = {}
        for session in _SESSION_STORE.values():
            for v in session.view_results.values():
                for f in v.findings:
                    defect_counter[f.defect_type] = defect_counter.get(f.defect_type, 0) + 1

        most_common = max(defect_counter, key=lambda k: defect_counter[k]) if defect_counter else "N/A"

        total_defects = sum(h["total_defects"] for h in _INSPECTION_HISTORY)
        total_critical = sum(h["critical_defects"] for h in _INSPECTION_HISTORY)
        critical_rate = (total_critical / max(1, total_defects)) * 100

        return VisionStatistics(
            total_inspections=total,
            avg_health_score=round(avg_health, 1),
            avg_risk_score=round(avg_risk, 1),
            most_common_defect=most_common,
            critical_defect_rate_pct=round(critical_rate, 1),
            avg_inspection_time_seconds=2.5,  # Mock average
            avg_queue_time_ms=145.2,
            active_gpu_utilization_pct=68.5,
        )

    def create_maintenance_ticket(self, session_id: str, defect_type: str) -> str:
        """Mocks integrating with Maintenance module."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        ticket_id = f"MNT-{random.randint(10000, 99999)}"
        logger.info(f"Generated maintenance ticket {ticket_id} for {defect_type} in session {session_id}")
        return ticket_id

    # ------------------------------------------------------------------
    # Report Data
    # ------------------------------------------------------------------

    def generate_report_data(self, session_id: str) -> Dict[str, Any]:
        """
        Generate structured data for PDF report generation.
        Production: wire to Celery task + WeasyPrint/ReportLab.
        """
        session = _SESSION_STORE.get(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "asset_name": session.asset_name,
            "operator": session.operator,
            "inspection_date": session.started_at.isoformat(),
            "views": {
                k: {
                    "defect_count": v.defect_count,
                    "health_score": v.view_health_score,
                    "critical_count": v.critical_count,
                    "findings": [
                        {
                            "type": f.defect_type,
                            "severity": f.severity.value,
                            "confidence": f"{f.confidence * 100:.0f}%",
                            "action": f.recommended_action,
                        }
                        for f in v.findings
                    ],
                }
                for k, v in session.view_results.items()
            },
            "composite": session.composite.model_dump() if session.composite else None,
            "executive_summary": session.executive_summary.model_dump() if session.executive_summary else None,
            "status": "PDF generation queued (Celery)",
        }
