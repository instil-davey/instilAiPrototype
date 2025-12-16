"""
Opportunities router for managing fundraising pipeline and opportunities.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db
from api.auth import get_current_active_user, User
from api.schemas import OpportunityCreate, OpportunityUpdate, OpportunityResponse
from models import Opportunity, Constituent


router = APIRouter()


@router.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    constituent_id: Optional[int] = None,
    stage: Optional[str] = None,
    campaign: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all opportunities with optional filtering and pagination.

    - **constituent_id**: Filter by specific constituent
    - **stage**: Filter by opportunity stage
    - **campaign**: Filter by campaign name
    """
    query = db.query(Opportunity)

    # Apply filters
    if constituent_id:
        query = query.filter(Opportunity.constituent_id == constituent_id)

    if stage:
        query = query.filter(Opportunity.stage == stage)

    if campaign:
        query = query.filter(Opportunity.campaign.ilike(f"%{campaign}%"))

    # Order by expected close date
    query = query.order_by(Opportunity.expected_close_date.asc())

    # Apply pagination
    opportunities = query.offset(skip).limit(limit).all()

    return opportunities


@router.post("/opportunities", response_model=OpportunityResponse, status_code=201)
async def create_opportunity(
    opportunity: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new opportunity record.

    Validates that the constituent exists before creating the opportunity.
    """
    # Verify constituent exists
    constituent = db.query(Constituent).filter(
        Constituent.constituent_id == opportunity.constituent_id
    ).first()
    if not constituent:
        raise HTTPException(status_code=404, detail="Constituent not found")

    db_opportunity = Opportunity(**opportunity.model_dump())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific opportunity by ID.
    """
    opportunity = db.query(Opportunity).filter(
        Opportunity.opportunity_id == opportunity_id
    ).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.put("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    opportunity_update: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an opportunity record.

    Only provided fields will be updated.
    """
    db_opportunity = db.query(Opportunity).filter(
        Opportunity.opportunity_id == opportunity_id
    ).first()
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    update_data = opportunity_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_opportunity, field, value)

    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity


@router.delete("/opportunities/{opportunity_id}", status_code=204)
async def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete an opportunity record.
    """
    db_opportunity = db.query(Opportunity).filter(
        Opportunity.opportunity_id == opportunity_id
    ).first()
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    db.delete(db_opportunity)
    db.commit()
    return None


@router.get("/opportunities/stats/pipeline")
async def get_pipeline_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get pipeline statistics grouped by stage.
    """
    stats = db.query(
        Opportunity.stage,
        func.count(Opportunity.opportunity_id).label("count"),
        func.sum(Opportunity.amount).label("total_value"),
        func.sum(Opportunity.amount * Opportunity.probability / 100).label("weighted_value"),
    ).filter(
        ~Opportunity.stage.in_(["closed_won", "closed_lost"])
    ).group_by(
        Opportunity.stage
    ).all()

    return [
        {
            "stage": stat.stage,
            "count": stat.count,
            "total_value": float(stat.total_value),
            "weighted_value": float(stat.weighted_value),
        }
        for stat in stats
    ]
