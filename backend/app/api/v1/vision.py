"""
AEGON Vision Intelligence — FastAPI Router
Enterprise multi-angle asset inspection API endpoints.

Endpoints:
    POST /upload/{view_type}      — Upload and analyse a single view
    POST /360                     — Generate 360° composite analysis
    POST /report                  — Generate enterprise report data
    GET  /history                 — Inspection history (paginated)
    GET  /inspection/{session_id} — Full session detail
    GET  /statistics              — Aggregate statistics
    GET  /digital-twin/{id}       — Live digital twin state
"""
from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from app.schemas.vision import (
    AnalyzeViewRequest,
    CompositeAnalysis,
    DigitalTwinState,
    ExecutiveSummary,
    Generate360Request,
    InspectionSession,
    VisionStatistics,
    VisionViewType,
    ViewInspectionResult,
)
from app.services.vision_service import VisionInspectionService

router = APIRouter()

# ---------------------------------------------------------------------------
# Singleton service instance (stateless — production: inject via DI Container)
# ---------------------------------------------------------------------------
_vision_service = VisionInspectionService()


def _standard_response(data: Any, message: str = "Success") -> dict:
    """Consistent AEGON StandardResponse wrapper."""
    return {"success": True, "message": message, "data": data}


# ---------------------------------------------------------------------------
# Upload + Analyse a single view
# ---------------------------------------------------------------------------

@router.post(
    "/upload/{view_type}",
    response_model=dict,
    summary="Upload and analyse a single view",
    description=(
        "Upload an image for a specific view angle and immediately run AI analysis. "
        "Creates or updates the inspection session identified by session_id."
    ),
)
async def upload_and_analyze_view(
    view_type: VisionViewType,
    session_id: str = Form(default_factory=lambda: str(uuid.uuid4())),
    asset_name: str = Form(default="Enterprise Asset"),
    operator: str = Form(default="System"),
    file: Optional[UploadFile] = File(default=None),
) -> dict:
    """
    Upload an image for the specified view and run AI inspection.
    If no file is uploaded, mock inference runs on simulated data.
    """
    image_bytes: Optional[bytes] = None
    image_filename: Optional[str] = None

    if file:
        # Validate content type
        allowed_types = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported image type: {file.content_type}. Accepted: {', '.join(allowed_types)}",
            )
        image_bytes = await file.read()
        image_filename = file.filename

    try:
        result: ViewInspectionResult = _vision_service.inspect_view(
            view_type=view_type,
            image_bytes=image_bytes,
            session_id=session_id,
            asset_name=asset_name,
            operator=operator,
        )
        if image_filename:
            result.image_filename = image_filename

        # Retrieve updated digital twin state
        session = _vision_service.get_session(session_id)
        twin = session.digital_twin if session else None

        return _standard_response(
            data={
                "session_id": session_id,
                "view_result": result.model_dump(),
                "digital_twin": twin.model_dump() if twin else None,
            },
            message=f"View '{view_type.value}' analysis complete.",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vision analysis failed: {str(exc)}",
        ) from exc


# ---------------------------------------------------------------------------
# Analyse without file upload (trigger re-analysis / programmatic)
# ---------------------------------------------------------------------------

@router.post("/analyze", response_model=dict, summary="Analyse a view (programmatic)")
async def analyze_view(body: AnalyzeViewRequest) -> dict:
    """Programmatically trigger analysis for a view (no file upload)."""
    try:
        result = _vision_service.inspect_view(
            view_type=body.view_type,
            image_bytes=None,
            session_id=body.session_id,
            asset_name=body.asset_name or "Enterprise Asset",
            operator=body.operator or "System",
        )
        session = _vision_service.get_session(body.session_id)
        twin = session.digital_twin if session else None

        return _standard_response(
            data={
                "session_id": body.session_id,
                "view_result": result.model_dump(),
                "digital_twin": twin.model_dump() if twin else None,
            },
            message=f"View '{body.view_type.value}' analysis complete.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# 360° Composite Analysis
# ---------------------------------------------------------------------------

@router.post("/360", response_model=dict, summary="Generate 360° composite analysis")
async def generate_360_analysis(body: Generate360Request) -> dict:
    """
    Fuse all available view results into a 360° composite analysis.
    Calculates overall health, risk, RUL, and generates executive summary.
    """
    try:
        composite, summary = _vision_service.generate_360_summary(body.session_id)
        session = _vision_service.get_session(body.session_id)
        twin = session.digital_twin if session else None

        return _standard_response(
            data={
                "session_id": body.session_id,
                "composite": composite.model_dump(),
                "executive_summary": summary.model_dump(),
                "digital_twin": twin.model_dump() if twin else None,
            },
            message="360° composite analysis generated successfully.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

@router.post("/report", response_model=dict, summary="Generate enterprise inspection report")
async def generate_report(body: Generate360Request) -> dict:
    """
    Generate structured report data for a completed inspection session.
    Production: triggers Celery background task for PDF generation.
    """
    try:
        report_data = _vision_service.generate_report_data(body.session_id)
        return _standard_response(data=report_data, message="Report data generated.")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# Inspection History
# ---------------------------------------------------------------------------

@router.get("/history", response_model=dict, summary="Get inspection history")
async def get_inspection_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    """Return paginated inspection history records."""
    history = _vision_service.get_inspection_history(limit=limit, offset=offset)
    return _standard_response(
        data={"items": history, "total": len(history), "limit": limit, "offset": offset},
        message="Inspection history retrieved.",
    )


# ---------------------------------------------------------------------------
# Session Detail
# ---------------------------------------------------------------------------

@router.get("/inspection/{session_id}", response_model=dict, summary="Get inspection session detail")
async def get_inspection_detail(session_id: str) -> dict:
    """Retrieve the full detail of an inspection session by ID."""
    session = _vision_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection session '{session_id}' not found.",
        )
    return _standard_response(
        data=session.model_dump(),
        message="Session retrieved.",
    )


# ---------------------------------------------------------------------------
# Digital Twin State
# ---------------------------------------------------------------------------

@router.get("/digital-twin/{session_id}", response_model=dict, summary="Get live Digital Twin state")
async def get_digital_twin(session_id: str) -> dict:
    """Return the live Digital Twin state for an inspection session."""
    session = _vision_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    return _standard_response(
        data=session.digital_twin.model_dump(),
        message="Digital Twin state retrieved.",
    )


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

@router.get("/statistics", response_model=dict, summary="Aggregate vision intelligence statistics")
async def get_statistics() -> dict:
    """Return aggregate statistics across all inspection sessions."""
    stats = _vision_service.get_statistics()
    return _standard_response(data=stats.model_dump(), message="Statistics computed.")
