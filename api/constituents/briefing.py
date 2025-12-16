"""
Constituent Briefing API Endpoint

Provides REST API access to AI-powered constituent briefings.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import os

from api.deps import get_db
from src.briefing.engine import BriefingEngine
from src.segments.engine import SegmentationEngine


# Pydantic models for API request/response
class BriefingMetadata(BaseModel):
    """Metadata about the briefing generation."""
    constituent_id: str = Field(..., description="Unique identifier for the constituent")
    generated_at: str = Field(..., description="ISO 8601 timestamp when briefing was generated")
    data_points: dict = Field(..., description="Count of data points analyzed")


class ConstituentBriefing(BaseModel):
    """Complete constituent briefing response."""
    summary: str = Field(..., description="2-3 sentence overview of who the constituent is")
    giving_summary: str = Field(..., description="Analysis of giving history and patterns")
    engagement_pattern: str = Field(..., description="Analysis of interaction and engagement patterns")
    why_they_matter: str = Field(..., description="Strategic importance to the organization")
    segment_reason: str = Field(..., description="Explanation of segment membership")
    suggested_action: str = Field(..., description="Personalized recommended next step")
    metadata: BriefingMetadata = Field(..., description="Metadata about the briefing")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "Michael Brown is a Board Member and major donor who has demonstrated exceptional commitment with $50,000 in lifetime giving. He has been engaged with the organization since 2018 and maintains active involvement through both governance and philanthropy.",
                "giving_summary": "Total giving of $50,000 across 1 major gift to the Capital Campaign (CAMP003). This single transformational gift represents the largest contribution in the current campaign and demonstrates significant investment in the organization's future.",
                "engagement_pattern": "Highly engaged through board governance with 2 recorded interactions including strategic planning meetings. Most recent engagement was a board meeting in December 2023, indicating active leadership participation.",
                "why_they_matter": "As a Board Member with major donor capacity, Michael provides both strategic leadership and significant financial resources. His $50,000 gift represents transformational support and his governance role amplifies his influence and commitment.",
                "segment_reason": "Classified as Major Donor and Board Member based on $50,000+ giving level and governance role. This dual classification reflects both financial capacity and organizational leadership.",
                "suggested_action": "Schedule a one-on-one meeting within the next 30 days to discuss campaign progress, thank him for his leadership gift, and explore opportunities for additional board engagement or potential second gift.",
                "metadata": {
                    "constituent_id": "CONST003",
                    "generated_at": "2025-01-20T10:30:00.000Z",
                    "data_points": {
                        "contributions": 1,
                        "interactions": 2,
                        "opportunities": 0,
                        "transactions": 1,
                        "segments": 2
                    }
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


# Create router
router = APIRouter(
    prefix="/constituents",
    tags=["constituents", "briefings"]
)


# Dependency to get briefing engine
def get_briefing_engine() -> BriefingEngine:
    """Get briefing engine instance with API key from environment."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    return BriefingEngine(api_key=api_key)


@router.get(
    "/{constituent_id}/briefing",
    response_model=ConstituentBriefing,
    responses={
        200: {
            "description": "Successful briefing generation",
            "model": ConstituentBriefing
        },
        404: {
            "description": "Constituent not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Server error (API key not configured, AI service error, etc.)",
            "model": ErrorResponse
        }
    },
    summary="Generate AI-powered constituent briefing",
    description="""
    Generate a comprehensive AI-powered briefing for a specific constituent.

    This endpoint analyzes all available data for a constituent including:
    - Contribution history
    - Interaction records
    - Open opportunities
    - Transaction details
    - Segment membership

    The AI generates personalized insights including:
    - Who they are (summary paragraph)
    - Giving summary and patterns
    - Engagement pattern analysis
    - Why they matter to the organization
    - Why they're in their segment(s)
    - Personalized suggested next action

    **Authentication:** Not currently implemented (add auth as needed)

    **Rate Limiting:** Consider implementing rate limits for production use
    """
)
async def get_constituent_briefing(
    constituent_id: str,
    segments: Optional[str] = Query(
        None,
        description="Comma-separated list of segment names the constituent belongs to (e.g., 'Major Donors,Board Members')"
    ),
    db: Session = Depends(get_db),
    engine: BriefingEngine = Depends(get_briefing_engine)
) -> ConstituentBriefing:
    """
    Generate an AI-powered briefing for a constituent.

    Args:
        constituent_id: Unique identifier for the constituent (e.g., 'CONST001')
        segments: Optional comma-separated segment names
        db: Database session (injected)
        engine: Briefing engine instance (injected)

    Returns:
        ConstituentBriefing with AI-generated insights

    Raises:
        HTTPException: 404 if constituent not found, 500 for server errors
    """
    try:
        segment_list = []
        numeric_id = None
        try:
            numeric_id = int(constituent_id)
        except ValueError:
            numeric_id = None

        if segments:
            segment_list = [s.strip() for s in segments.split(',') if s.strip()]
        else:
            seg_engine = SegmentationEngine(db)
            generated_segments = seg_engine.generate_all_segments()
            segment_list = [
                seg.name
                for seg in generated_segments
                if numeric_id is not None and numeric_id in seg.constituent_ids
            ]

        # Generate briefing
        briefing_data = engine.generate_briefing(
            constituent_id=constituent_id,
            db_session=db,
            segment_names=segment_list
        )

        return ConstituentBriefing(**briefing_data)

    except ValueError as e:
        # Constituent not found
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Constituent not found",
                "detail": str(e)
            }
        )

    except Exception as e:
        # Other errors (AI service, database, etc.)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate briefing",
                "detail": str(e)
            }
        )


# Optional: Batch briefing endpoint for multiple constituents
@router.post(
    "/briefings/batch",
    response_model=List[ConstituentBriefing],
    responses={
        200: {
            "description": "Successful batch briefing generation",
        },
        400: {
            "description": "Invalid request (too many IDs, etc.)",
            "model": ErrorResponse
        },
        500: {
            "description": "Server error",
            "model": ErrorResponse
        }
    },
    summary="Generate briefings for multiple constituents",
    description="""
    Generate AI-powered briefings for multiple constituents in a single request.

    **Limits:** Maximum 10 constituents per batch to prevent timeout and excessive API usage.

    **Note:** This endpoint processes constituents sequentially. Consider implementing
    background jobs for larger batches in production.
    """
)
async def get_batch_briefings(
    constituent_ids: List[str],
    db: Session = Depends(get_db),
    engine: BriefingEngine = Depends(get_briefing_engine)
) -> List[ConstituentBriefing]:
    """
    Generate briefings for multiple constituents.

    Args:
        constituent_ids: List of constituent IDs (max 10)
        db: Database session (injected)
        engine: Briefing engine instance (injected)

    Returns:
        List of ConstituentBriefing objects

    Raises:
        HTTPException: 400 if too many IDs, 500 for server errors
    """
    # Validate batch size
    if len(constituent_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Too many constituent IDs",
                "detail": "Maximum 10 constituents per batch request"
            }
        )

    briefings = []
    errors = []

    for constituent_id in constituent_ids:
        try:
            briefing_data = engine.generate_briefing(
                constituent_id=constituent_id,
                db_session=db,
                segment_names=None  # Could be extended to support segments per constituent
            )
            briefings.append(ConstituentBriefing(**briefing_data))

        except ValueError:
            # Constituent not found - skip but record error
            errors.append({
                "constituent_id": constituent_id,
                "error": "Not found"
            })

        except Exception as e:
            # Other errors - skip but record
            errors.append({
                "constituent_id": constituent_id,
                "error": str(e)
            })

    # If no successful briefings, return error
    if not briefings:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No briefings generated",
                "detail": errors
            }
        )

    # Return successful briefings (could include errors in response metadata if needed)
    return briefings
