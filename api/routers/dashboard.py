"""
Dashboard router for overview statistics and metrics.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from decimal import Decimal

from api.deps import get_db
from api.auth import get_current_active_user, User
from api.schemas import DashboardStats
from models import Constituent, Contribution, Interaction, Opportunity


router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get comprehensive dashboard statistics including:
    - Constituent counts
    - Contribution totals and averages
    - Opportunity pipeline metrics
    - Recent interaction counts
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    thirty_days_ago = datetime.now() - timedelta(days=30)

    # Constituent stats
    total_constituents = db.query(func.count(Constituent.constituent_id)).scalar() or 0
    active_constituents = db.query(func.count(Constituent.constituent_id)).filter(
        Constituent.status == "active"
    ).scalar() or 0

    # Contribution stats
    total_contributions = db.query(func.sum(Contribution.amount)).scalar() or Decimal(0)

    contributions_this_year = db.query(func.sum(Contribution.amount)).filter(
        extract('year', Contribution.contribution_date) == current_year
    ).scalar() or Decimal(0)

    contributions_this_month = db.query(func.sum(Contribution.amount)).filter(
        extract('year', Contribution.contribution_date) == current_year,
        extract('month', Contribution.contribution_date) == current_month
    ).scalar() or Decimal(0)

    contribution_count = db.query(func.count(Contribution.contribution_id)).scalar() or 0
    average_contribution = (
        total_contributions / contribution_count if contribution_count > 0 else Decimal(0)
    )

    # Opportunity stats
    total_opportunities = db.query(func.count(Opportunity.opportunity_id)).scalar() or 0
    open_opportunities = db.query(func.count(Opportunity.opportunity_id)).filter(
        ~Opportunity.stage.in_(["closed_won", "closed_lost"])
    ).scalar() or 0

    pipeline_value = db.query(func.sum(Opportunity.amount)).filter(
        ~Opportunity.stage.in_(["closed_won", "closed_lost"])
    ).scalar() or Decimal(0)

    # Weighted pipeline (amount * probability)
    opportunities = db.query(Opportunity).filter(
        ~Opportunity.stage.in_(["closed_won", "closed_lost"])
    ).all()
    weighted_pipeline = sum(
        float(opp.amount) * (opp.probability / 100) for opp in opportunities
    ) if opportunities else Decimal(0)

    # Recent interactions
    recent_interactions = db.query(func.count(Interaction.interaction_id)).filter(
        Interaction.interaction_date >= thirty_days_ago
    ).scalar() or 0

    return DashboardStats(
        total_constituents=total_constituents,
        active_constituents=active_constituents,
        total_contributions=total_contributions,
        contributions_this_year=contributions_this_year,
        contributions_this_month=contributions_this_month,
        average_contribution=average_contribution,
        total_opportunities=total_opportunities,
        open_opportunities=open_opportunities,
        pipeline_value=pipeline_value,
        weighted_pipeline=weighted_pipeline,
        recent_interactions=recent_interactions,
    )


@router.get("/dashboard/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get recent activity across all entities (contributions, interactions, opportunities).
    """
    from models import Contribution, Interaction, Opportunity, Constituent

    # Recent contributions
    recent_contributions = db.query(
        Contribution.contribution_id.label("id"),
        Contribution.contribution_date.label("date"),
        Contribution.amount,
        Constituent.first_name,
        Constituent.last_name,
    ).join(
        Constituent, Contribution.constituent_id == Constituent.constituent_id
    ).order_by(
        Contribution.contribution_date.desc()
    ).limit(limit).all()

    # Recent interactions
    recent_interactions = db.query(
        Interaction.interaction_id.label("id"),
        Interaction.interaction_date.label("date"),
        Interaction.interaction_type,
        Interaction.subject,
        Constituent.first_name,
        Constituent.last_name,
    ).join(
        Constituent, Interaction.constituent_id == Constituent.constituent_id
    ).order_by(
        Interaction.interaction_date.desc()
    ).limit(limit).all()

    return {
        "recent_contributions": [
            {
                "id": c.id,
                "date": c.date,
                "amount": float(c.amount),
                "constituent_name": f"{c.first_name} {c.last_name}",
            }
            for c in recent_contributions
        ],
        "recent_interactions": [
            {
                "id": i.id,
                "date": i.date,
                "type": i.interaction_type,
                "subject": i.subject,
                "constituent_name": f"{i.first_name} {i.last_name}",
            }
            for i in recent_interactions
        ],
    }
