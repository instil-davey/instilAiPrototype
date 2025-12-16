"""
Interactions router for managing constituent interactions and communications.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from api.auth import get_current_active_user, User
from api.schemas import InteractionCreate, InteractionUpdate, InteractionResponse
from models import Interaction, Constituent


router = APIRouter()


@router.get("/interactions", response_model=List[InteractionResponse])
async def list_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    constituent_id: Optional[int] = None,
    interaction_type: Optional[str] = None,
    days: Optional[int] = Query(None, description="Filter interactions from last N days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all interactions with optional filtering and pagination.

    - **constituent_id**: Filter by specific constituent
    - **interaction_type**: Filter by interaction type (email, phone, meeting, etc.)
    - **days**: Show only interactions from the last N days
    """
    query = db.query(Interaction)

    # Apply filters
    if constituent_id:
        query = query.filter(Interaction.constituent_id == constituent_id)

    if interaction_type:
        query = query.filter(Interaction.interaction_type == interaction_type)

    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(Interaction.interaction_date >= cutoff_date)

    # Order by most recent
    query = query.order_by(Interaction.interaction_date.desc())

    # Apply pagination
    interactions = query.offset(skip).limit(limit).all()

    return interactions


@router.post("/interactions", response_model=InteractionResponse, status_code=201)
async def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new interaction record.

    Validates that the constituent exists before creating the interaction.
    """
    # Verify constituent exists
    constituent = db.query(Constituent).filter(
        Constituent.constituent_id == interaction.constituent_id
    ).first()
    if not constituent:
        raise HTTPException(status_code=404, detail="Constituent not found")

    db_interaction = Interaction(**interaction.model_dump())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific interaction by ID.
    """
    interaction = db.query(Interaction).filter(
        Interaction.interaction_id == interaction_id
    ).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.put("/interactions/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: int,
    interaction_update: InteractionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an interaction record.

    Only provided fields will be updated.
    """
    db_interaction = db.query(Interaction).filter(
        Interaction.interaction_id == interaction_id
    ).first()
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = interaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_interaction, field, value)

    db.commit()
    db.refresh(db_interaction)
    return db_interaction


@router.delete("/interactions/{interaction_id}", status_code=204)
async def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete an interaction record.
    """
    db_interaction = db.query(Interaction).filter(
        Interaction.interaction_id == interaction_id
    ).first()
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    db.delete(db_interaction)
    db.commit()
    return None
