"""
Constituents router for managing constituent data.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from api.deps import get_db
from api.auth import get_current_active_user, User
from api.schemas import ConstituentCreate, ConstituentUpdate, ConstituentResponse
from models import Constituent
from src.segments.engine import SegmentationEngine


router = APIRouter()


@router.get("/constituents", response_model=List[ConstituentResponse])
async def list_constituents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    constituent_type: Optional[str] = None,
    status: Optional[str] = None,
    segment_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all constituents with optional filtering and pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search term for name or email
    - **constituent_type**: Filter by constituent type
    - **status**: Filter by status (active/inactive/deceased)
    """
    query = db.query(Constituent)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Constituent.first_name.ilike(search_term),
                Constituent.last_name.ilike(search_term),
                Constituent.email.ilike(search_term),
            )
        )

    if constituent_type:
        query = query.filter(Constituent.constituent_type == constituent_type)

    if status:
        query = query.filter(Constituent.status == status)

    if segment_id:
        engine = SegmentationEngine(db)
        segments = engine.generate_all_segments()
        segment = next((s for s in segments if s.segment_id == segment_id), None)
        if segment:
            if segment.constituent_ids:
                query = query.filter(Constituent.constituent_id.in_(segment.constituent_ids))
            else:
                return []
        else:
            return []

    # Order by most recently updated
    query = query.order_by(Constituent.updated_at.desc())

    # Apply pagination
    constituents = query.offset(skip).limit(limit).all()

    return constituents


@router.post("/constituents", response_model=ConstituentResponse, status_code=201)
async def create_constituent(
    constituent: ConstituentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new constituent.

    Requires all mandatory fields per the ConstituentCreate schema.
    """
    db_constituent = Constituent(**constituent.model_dump())
    db.add(db_constituent)
    db.commit()
    db.refresh(db_constituent)
    return db_constituent


@router.get("/constituents/{constituent_id}", response_model=ConstituentResponse)
async def get_constituent(
    constituent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific constituent by ID.

    Returns detailed information about a single constituent.
    """
    constituent = db.query(Constituent).filter(Constituent.constituent_id == constituent_id).first()
    if not constituent:
        raise HTTPException(status_code=404, detail="Constituent not found")
    return constituent


@router.put("/constituents/{constituent_id}", response_model=ConstituentResponse)
async def update_constituent(
    constituent_id: int,
    constituent_update: ConstituentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a constituent's information.

    Only provided fields will be updated. All fields are optional.
    """
    db_constituent = db.query(Constituent).filter(Constituent.constituent_id == constituent_id).first()
    if not db_constituent:
        raise HTTPException(status_code=404, detail="Constituent not found")

    # Update only provided fields
    update_data = constituent_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_constituent, field, value)

    db.commit()
    db.refresh(db_constituent)
    return db_constituent


@router.delete("/constituents/{constituent_id}", status_code=204)
async def delete_constituent(
    constituent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a constituent.

    **Warning:** This will also delete all related contributions, interactions, and opportunities.
    """
    db_constituent = db.query(Constituent).filter(Constituent.constituent_id == constituent_id).first()
    if not db_constituent:
        raise HTTPException(status_code=404, detail="Constituent not found")

    db.delete(db_constituent)
    db.commit()
    return None


@router.get("/constituents/{constituent_id}/summary")
async def get_constituent_summary(
    constituent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a comprehensive summary of a constituent including:
    - Total contributions
    - Recent interactions
    - Active opportunities
    """
    from models import get_constituent_summary

    summary = get_constituent_summary(db, constituent_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Constituent not found")

    return summary
