"""
FastAPI endpoint for suggested action generation
POST /api/suggested-action
"""

import sys
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import create_database_engine, get_session
from segments import SegmentType
from src.actions.generator import generate_suggested_action

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Nonprofit Fundraiser Action Generator API",
    description="Generate AI-powered, personalized action recommendations for nonprofit fundraisers",
    version="1.0.0"
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nonprofit_crm.db")
engine = create_database_engine(DATABASE_URL)


# Dependency to get database session
def get_db():
    """Dependency to provide database session."""
    session = get_session(engine)
    try:
        yield session
    finally:
        session.close()


# Request/Response models
class SuggestedActionRequest(BaseModel):
    """Request model for suggested action generation."""
    constituent_id: int = Field(..., description="ID of the constituent", example=1)
    segment_id: Optional[str] = Field(None, description="Optional segment to focus on", example="major_donor")

    class Config:
        json_schema_extra = {
            "example": {
                "constituent_id": 1,
                "segment_id": "major_donor"
            }
        }


class SuggestedActionResponse(BaseModel):
    """Response model for suggested action."""
    success: bool
    constituent_id: Optional[int] = None
    constituent_name: Optional[str] = None
    segments: Optional[list[str]] = None
    target_segment: Optional[str] = None
    suggested_action: Optional[str] = None
    generated_at: Optional[str] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "constituent_id": 1,
                "constituent_name": "John Smith",
                "segments": ["major_donor", "recurring_donor"],
                "target_segment": "major_donor",
                "suggested_action": "Action: Schedule a 45-minute video call with John...",
                "generated_at": "2025-01-15T10:30:00"
            }
        }


# Endpoints
@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Nonprofit Fundraiser Action Generator API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/suggested-action": "Generate a suggested action for a constituent",
            "GET /api/segments": "List all available segments",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "suggested-action-api"}


@app.get("/api/segments")
def list_segments():
    """List all available segment types."""
    from segments import SEGMENT_DEFINITIONS

    segments = []
    for segment_type, info in SEGMENT_DEFINITIONS.items():
        segments.append({
            "id": segment_type.value,
            "name": info["name"],
            "description": info["description"],
            "priority": info["priority"]
        })

    return {
        "segments": segments,
        "total": len(segments)
    }


@app.post("/api/suggested-action", response_model=SuggestedActionResponse)
def create_suggested_action(
    request: SuggestedActionRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a personalized action recommendation for a constituent.

    This endpoint uses AI to analyze constituent data including:
    - Giving history and patterns
    - Engagement and interaction history
    - Current opportunities in the pipeline
    - Constituent segments and characteristics

    Returns a specific, time-bound, stewardship-oriented action recommendation.

    Args:
        request: SuggestedActionRequest with constituent_id and optional segment_id
        db: Database session (injected)

    Returns:
        SuggestedActionResponse with the generated action and metadata

    Raises:
        HTTPException: If constituent not found or other errors occur
    """
    try:
        # Validate segment_id if provided
        if request.segment_id:
            try:
                SegmentType(request.segment_id)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid segment_id: {request.segment_id}. Use GET /api/segments to see available segments."
                )

        # Generate suggested action
        result = generate_suggested_action(
            session=db,
            constituent_id=request.constituent_id,
            segment_id=request.segment_id
        )

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            if "not found" in error_msg:
                raise HTTPException(status_code=404, detail=error_msg)
            else:
                raise HTTPException(status_code=500, detail=error_msg)

        return SuggestedActionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "suggested_action:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
