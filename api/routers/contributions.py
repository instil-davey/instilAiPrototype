"""
Contributions router for managing donation and contribution data.
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from api.deps import get_db
from api.auth import get_current_active_user, User
from api.schemas import ContributionCreate, ContributionUpdate, ContributionResponse
from models import Contribution, Constituent


router = APIRouter()


@router.get("/contributions", response_model=List[ContributionResponse])
async def list_contributions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    constituent_id: Optional[int] = None,
    campaign: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all contributions with optional filtering and pagination.

    - **constituent_id**: Filter by specific constituent
    - **campaign**: Filter by campaign name
    - **start_date**: Filter contributions from this date onwards
    - **end_date**: Filter contributions up to this date
    """
    query = db.query(Contribution)

    # Apply filters
    if constituent_id:
        query = query.filter(Contribution.constituent_id == constituent_id)

    if campaign:
        query = query.filter(Contribution.campaign.ilike(f"%{campaign}%"))

    if start_date:
        query = query.filter(Contribution.contribution_date >= start_date)

    if end_date:
        query = query.filter(Contribution.contribution_date <= end_date)

    # Order by most recent
    query = query.order_by(Contribution.contribution_date.desc())

    # Apply pagination
    contributions = query.offset(skip).limit(limit).all()

    return contributions


@router.post("/contributions", response_model=ContributionResponse, status_code=201)
async def create_contribution(
    contribution: ContributionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new contribution record.

    Validates that the constituent exists before creating the contribution.
    """
    # Verify constituent exists
    constituent = db.query(Constituent).filter(
        Constituent.constituent_id == contribution.constituent_id
    ).first()
    if not constituent:
        raise HTTPException(status_code=404, detail="Constituent not found")

    db_contribution = Contribution(**contribution.model_dump())
    db.add(db_contribution)
    db.commit()
    db.refresh(db_contribution)
    return db_contribution


@router.get("/contributions/{contribution_id}", response_model=ContributionResponse)
async def get_contribution(
    contribution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific contribution by ID.
    """
    contribution = db.query(Contribution).filter(
        Contribution.contribution_id == contribution_id
    ).first()
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    return contribution


@router.put("/contributions/{contribution_id}", response_model=ContributionResponse)
async def update_contribution(
    contribution_id: int,
    contribution_update: ContributionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a contribution record.

    Only provided fields will be updated.
    """
    db_contribution = db.query(Contribution).filter(
        Contribution.contribution_id == contribution_id
    ).first()
    if not db_contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    update_data = contribution_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contribution, field, value)

    db.commit()
    db.refresh(db_contribution)
    return db_contribution


@router.delete("/contributions/{contribution_id}", status_code=204)
async def delete_contribution(
    contribution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a contribution record.
    """
    db_contribution = db.query(Contribution).filter(
        Contribution.contribution_id == contribution_id
    ).first()
    if not db_contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    db.delete(db_contribution)
    db.commit()
    return None


@router.get("/contributions/stats/by-campaign")
async def get_contributions_by_campaign(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get contribution statistics grouped by campaign.
    """
    stats = db.query(
        Contribution.campaign,
        func.count(Contribution.contribution_id).label("count"),
        func.sum(Contribution.amount).label("total"),
        func.avg(Contribution.amount).label("average"),
    ).filter(
        Contribution.campaign.isnot(None)
    ).group_by(
        Contribution.campaign
    ).all()

    return [
        {
            "campaign": stat.campaign,
            "count": stat.count,
            "total": float(stat.total),
            "average": float(stat.average),
        }
        for stat in stats
    ]
