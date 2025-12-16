"""
Segments router providing AI-style segmentation insights.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import get_db
from src.segments.engine import SegmentationEngine


class ConstituentSegmentInsight(BaseModel):
    """Insight for an individual constituent inside a segment."""
    constituent_id: int
    name: str
    email: Optional[str] = None
    segment_reason: str = Field(..., description="Why this constituent belongs to the segment")
    suggested_action: Optional[str] = Field(None, description="Recommended next step")
    metrics: Dict[str, Any]


class SegmentSuggestion(BaseModel):
    """Segment suggestion payload for senior fundraising leaders."""
    segment_id: str
    name: str
    description: str
    why_segment: str
    metrics: Dict[str, Any]
    constituents: List[ConstituentSegmentInsight]


class ConstituentSegmentSuggestion(BaseModel):
    """Single constituent view of their recommended segment."""
    segment_id: str
    segment_name: str
    description: str
    segment_reason: str
    constituent_reason: str
    suggested_action: Optional[str] = None
    metrics: Dict[str, Any]


router = APIRouter(prefix="/segments", tags=["Segments"])


def _build_constituent_payload(
    engine: SegmentationEngine,
    segment,
    constituent_id: int
) -> Optional[ConstituentSegmentInsight]:
    """Build detailed payload for a constituent in a segment."""
    data = engine.get_constituent_data(constituent_id)
    if not data:
        return None
    rfm = data['rfm']
    serialized_rfm = {
        "recency": rfm['recency'],
        "frequency": rfm['frequency'],
        "monetary": float(rfm['monetary']),
        "avg_gift": float(rfm['avg_gift']),
    }

    return ConstituentSegmentInsight(
        constituent_id=constituent_id,
        name=data['constituent'].full_name,
        email=data['constituent'].email,
        segment_reason=segment.constituent_reasons.get(
            constituent_id,
            segment.description
        ),
        suggested_action=segment.suggested_actions.get(constituent_id),
        metrics={
            "lifetime_giving": data['total_lifetime_giving'],
            "rfm": serialized_rfm,
            "engagement_score": data['engagement_score'],
            "capacity_score": data['capacity_score'],
            "days_since_last_interaction": data['days_since_last_interaction'],
        },
    )


@router.get("/suggestions", response_model=List[SegmentSuggestion])
def get_segment_suggestions(
    limit: int = Query(5, ge=1, le=10),
    per_segment: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """
    Return AI-style segment recommendations with reasoning and sample constituents.
    """
    engine = SegmentationEngine(db)
    segments = engine.generate_all_segments()

    segments.sort(key=lambda seg: len(seg.constituent_ids), reverse=True)
    response: List[SegmentSuggestion] = []

    for segment in segments[:limit]:
        constituent_payloads: List[ConstituentSegmentInsight] = []
        for cid in segment.constituent_ids[:per_segment]:
            payload = _build_constituent_payload(engine, segment, cid)
            if payload:
                constituent_payloads.append(payload)

        response.append(
            SegmentSuggestion(
                segment_id=segment.segment_id,
                name=segment.name,
                description=segment.description,
                why_segment=(
                    f"{segment.reasoning_formula}. "
                    f"{len(segment.constituent_ids)} constituents currently qualify."
                ),
                metrics=segment.segment_metrics,
                constituents=constituent_payloads,
            )
        )

    return response


@router.get(
    "/constituents/{constituent_id}/suggestion",
    response_model=ConstituentSegmentSuggestion,
)
def get_constituent_segment_suggestion(
    constituent_id: int,
    db: Session = Depends(get_db),
):
    """
    Return the best-fit segment recommendation for a specific constituent.
    """
    engine = SegmentationEngine(db)
    segments = engine.generate_all_segments()
    for segment in segments:
        if constituent_id in segment.constituent_ids:
            const_payload = _build_constituent_payload(engine, segment, constituent_id)
            if not const_payload:
                break
            return ConstituentSegmentSuggestion(
                segment_id=segment.segment_id,
                segment_name=segment.name,
                description=segment.description,
                segment_reason=segment.reasoning_formula,
                constituent_reason=const_payload.segment_reason,
                suggested_action=const_payload.suggested_action,
                metrics=const_payload.metrics,
            )

    data = engine.get_constituent_data(constituent_id)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Constituent {constituent_id} not found for segmentation",
        )

    fallback_reason = (
        "No strong segment signal detected yet. "
        "Monitor engagement and giving trends to determine the best outreach lane."
    )

    serialized_rfm = {
        "recency": data['rfm']['recency'],
        "frequency": data['rfm']['frequency'],
        "monetary": float(data['rfm']['monetary']),
        "avg_gift": float(data['rfm']['avg_gift']),
    }

    return ConstituentSegmentSuggestion(
        segment_id="no_segment_signal",
        segment_name="Needs Monitoring",
        description="Constituent does not currently meet thresholds for any flagship segment.",
        segment_reason="All segment formulas evaluated but no trigger conditions were satisfied.",
        constituent_reason=fallback_reason,
        suggested_action="Review their recent interactions manually and determine next best touchpoint.",
        metrics={
            "lifetime_giving": data['total_lifetime_giving'],
            "rfm": serialized_rfm,
            "engagement_score": data['engagement_score'],
            "capacity_score": data['capacity_score'],
            "days_since_last_interaction": data['days_since_last_interaction'],
        },
    )


class SegmentDefinition(BaseModel):
    segment_id: str
    name: str
    description: str
    constituent_count: int


@router.get("/definitions", response_model=List[SegmentDefinition])
def list_segment_definitions(db: Session = Depends(get_db)):
    """Return all available segment definitions with counts."""
    engine = SegmentationEngine(db)
    segments = engine.generate_all_segments()
    return [
        SegmentDefinition(
            segment_id=segment.segment_id,
            name=segment.name,
            description=segment.description,
            constituent_count=len(segment.constituent_ids),
        )
        for segment in segments
    ]
