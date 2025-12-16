"""
Pydantic schemas for message generation API.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class BriefingData(BaseModel):
    """Campaign and organizational briefing information."""

    campaign_name: str = Field(
        ...,
        description="Name of the fundraising campaign",
        examples=["Annual Fund 2025"]
    )
    campaign_goal: Optional[float] = Field(
        None,
        description="Financial goal for the campaign",
        examples=[50000.00]
    )
    campaign_description: Optional[str] = Field(
        None,
        description="Detailed description of the campaign purpose",
        examples=["Support our scholarship program for underserved students"]
    )
    organization_mission: Optional[str] = Field(
        None,
        description="Organization's mission statement",
        examples=["Empowering youth through education and mentorship"]
    )
    key_talking_points: List[str] = Field(
        default_factory=list,
        description="Important points to include in the message",
        examples=[["Last year we served 500 students", "Every $100 provides books for one student"]]
    )
    deadline: Optional[str] = Field(
        None,
        description="Campaign deadline or important date",
        examples=["December 31, 2025"]
    )
    additional_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Any additional context for message generation"
    )


class SegmentContext(BaseModel):
    """Donor segment context information."""

    segment_name: str = Field(
        ...,
        description="Name of the donor segment",
        examples=["Major Donors", "Monthly Sustainers", "Lapsed Donors"]
    )
    segment_characteristics: Optional[str] = Field(
        None,
        description="Key characteristics of this segment",
        examples=["High-capacity donors who have given $10,000+ lifetime"]
    )
    giving_pattern: Optional[str] = Field(
        None,
        description="Typical giving patterns for this segment",
        examples=["Annual gifts of $1,000-5,000, typically in November/December"]
    )


class MessageGenerationRequest(BaseModel):
    """Request schema for generating a fundraising message."""

    briefing: BriefingData = Field(
        ...,
        description="Campaign and organizational briefing information"
    )
    segment_context: Optional[SegmentContext] = Field(
        None,
        description="Optional donor segment context"
    )
    tone: str = Field(
        default="warm, human, relationship-forward",
        description="Desired tone for the message",
        examples=["warm, human, relationship-forward", "formal and professional", "casual and friendly"]
    )
    target_length: int = Field(
        default=200,
        ge=150,
        le=500,
        description="Target length for the message in words"
    )
    generate_alternates: bool = Field(
        default=False,
        description="Whether to generate alternate message versions"
    )
    num_alternates: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of alternate versions to generate (if generate_alternates is True)"
    )

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        """Ensure tone is not empty."""
        if not v or not v.strip():
            raise ValueError("Tone cannot be empty")
        return v.strip()


class AlternateMessage(BaseModel):
    """An alternate version of the fundraising message."""

    subject_line: str = Field(
        ...,
        description="Email subject line for this alternate version"
    )
    message: str = Field(
        ...,
        description="Message body for this alternate version"
    )


class MessageMetadata(BaseModel):
    """Metadata about the message generation."""

    model: str = Field(
        ...,
        description="Claude model used for generation"
    )
    tone: str = Field(
        ...,
        description="Tone used for message generation"
    )
    target_length: int = Field(
        ...,
        description="Target word count for the message"
    )
    timestamp: str = Field(
        ...,
        description="ISO format timestamp of generation"
    )
    constituent_id: Optional[int] = Field(
        None,
        description="ID of the constituent this message is for"
    )
    constituent_name: Optional[str] = Field(
        None,
        description="Name of the constituent this message is for"
    )


class MessageGenerationResponse(BaseModel):
    """Response schema for generated fundraising message."""

    subject_line: str = Field(
        ...,
        description="Generated email subject line"
    )
    message: str = Field(
        ...,
        description="Generated fundraising message body (150-220 words)"
    )
    alternates: List[AlternateMessage] = Field(
        default_factory=list,
        description="Alternate message versions (if requested)"
    )
    metadata: MessageMetadata = Field(
        ...,
        description="Generation metadata"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "subject_line": "Your Impact: Transforming Lives Through Education",
                "message": "Dear Sarah, your generous support has been instrumental in our mission...",
                "alternates": [],
                "metadata": {
                    "model": "claude-sonnet-4-20250514",
                    "tone": "warm, human, relationship-forward",
                    "target_length": 200,
                    "timestamp": "2025-01-15T10:30:00",
                    "constituent_id": 123,
                    "constituent_name": "Sarah Johnson"
                }
            }
        }
    }
