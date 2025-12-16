"""
API routes for fundraising message generation.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload

from api.schemas import (
    MessageGenerationRequest,
    MessageGenerationResponse,
    MessageMetadata
)
from src.messages.generator import MessageGenerator
from models import Constituent, Contribution, Interaction, Opportunity, get_db
from config import settings


router = APIRouter(prefix="/constituents", tags=["messages"])


def get_message_generator() -> MessageGenerator:
    """Dependency to get message generator instance."""
    return MessageGenerator()


def prepare_constituent_data(constituent: Constituent) -> Dict[str, Any]:
    """
    Prepare constituent data for message generation.

    Args:
        constituent: Constituent SQLAlchemy model instance

    Returns:
        Dictionary with constituent data formatted for message generation
    """
    # Prepare basic constituent info
    constituent_data = {
        "constituent_id": constituent.constituent_id,
        "full_name": constituent.full_name,
        "email": constituent.email,
        "constituent_type": constituent.constituent_type,
        "total_lifetime_giving": float(constituent.total_lifetime_giving or 0)
    }

    # Add contribution history
    contributions = []
    for contrib in constituent.contributions:
        contributions.append({
            "contribution_id": contrib.contribution_id,
            "contribution_date": contrib.contribution_date.isoformat() if contrib.contribution_date else None,
            "amount": float(contrib.amount or 0),
            "contribution_type": contrib.contribution_type,
            "campaign_id": contrib.campaign_id,
            "payment_method": contrib.payment_method
        })

    # Sort by date (most recent first)
    contributions.sort(key=lambda x: x["contribution_date"] or "", reverse=True)
    constituent_data["contributions"] = contributions

    # Add interaction history
    interactions = []
    for interaction in constituent.interactions:
        interactions.append({
            "interaction_id": interaction.interaction_id,
            "interaction_date": interaction.interaction_date.isoformat() if interaction.interaction_date else None,
            "interaction_type": interaction.interaction_type,
            "subject": interaction.subject,
            "notes": interaction.notes,
            "staff_member": interaction.staff_member
        })

    # Sort by date (most recent first)
    interactions.sort(key=lambda x: x["interaction_date"] or "", reverse=True)
    constituent_data["interactions"] = interactions

    # Add opportunity data
    opportunities = []
    for opp in constituent.opportunities:
        opportunities.append({
            "opportunity_id": opp.opportunity_id,
            "opportunity_name": opp.opportunity_name,
            "stage": opp.stage,
            "expected_amount": float(opp.expected_amount or 0),
            "probability": opp.probability,
            "expected_close_date": opp.expected_close_date.isoformat() if opp.expected_close_date else None
        })

    constituent_data["opportunities"] = opportunities

    return constituent_data


@router.post(
    "/{constituent_id}/message",
    response_model=MessageGenerationResponse,
    summary="Generate Fundraising Message",
    description="""
    Generate a personalized fundraising message for a specific constituent.

    This endpoint creates tailored outreach messages using Claude AI, taking into account:
    - The constituent's giving history and relationship with the organization
    - Campaign context and organizational messaging
    - Donor segment characteristics
    - Desired tone and message length

    The generated message includes a compelling subject line and a 150-220 word
    personalized message body optimized for fundraising effectiveness.
    """
)
async def generate_constituent_message(
    constituent_id: int,
    request: MessageGenerationRequest,
    db: Session = Depends(get_db),
    generator: MessageGenerator = Depends(get_message_generator)
) -> MessageGenerationResponse:
    """
    Generate a personalized fundraising message for a constituent.

    Args:
        constituent_id: ID of the constituent to generate message for
        request: Message generation request with briefing and parameters
        db: Database session
        generator: Message generator instance

    Returns:
        Generated message with subject line, body, and optional alternates

    Raises:
        HTTPException: If constituent not found or generation fails
    """
    # Fetch constituent with all relationships
    constituent = db.query(Constituent).options(
        joinedload(Constituent.contributions),
        joinedload(Constituent.interactions),
        joinedload(Constituent.opportunities)
    ).filter(
        Constituent.constituent_id == constituent_id
    ).first()

    if not constituent:
        raise HTTPException(
            status_code=404,
            detail=f"Constituent with ID {constituent_id} not found"
        )

    # Prepare constituent data for message generation
    constituent_data = prepare_constituent_data(constituent)

    # Prepare briefing data
    briefing_data = request.briefing.model_dump()

    # Prepare segment context (if provided)
    segment_context = None
    if request.segment_context:
        segment_context = request.segment_context.model_dump()

    try:
        # Generate the message
        result = generator.generate(
            constituent=constituent_data,
            briefing=briefing_data,
            segment_context=segment_context,
            tone=request.tone,
            target_length=request.target_length,
            generate_alternates=request.generate_alternates,
            num_alternates=request.num_alternates
        )

        # Convert to response model
        return MessageGenerationResponse(
            subject_line=result["subject_line"],
            message=result["message"],
            alternates=result.get("alternates", []),
            metadata=MessageMetadata(**result["metadata"])
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating message: {str(e)}"
        )


@router.get(
    "/{constituent_id}",
    summary="Get Constituent Details",
    description="Retrieve detailed information about a constituent including their giving history and interactions."
)
async def get_constituent(
    constituent_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get constituent details including relationships.

    Args:
        constituent_id: ID of the constituent
        db: Database session

    Returns:
        Constituent data with contributions, interactions, and opportunities

    Raises:
        HTTPException: If constituent not found
    """
    constituent = db.query(Constituent).options(
        joinedload(Constituent.contributions),
        joinedload(Constituent.interactions),
        joinedload(Constituent.opportunities)
    ).filter(
        Constituent.constituent_id == constituent_id
    ).first()

    if not constituent:
        raise HTTPException(
            status_code=404,
            detail=f"Constituent with ID {constituent_id} not found"
        )

    return prepare_constituent_data(constituent)
