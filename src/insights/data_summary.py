"""
Data Summary Functions

Aggregates database statistics for AI insight generation.
"""

from typing import Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import Constituent, Contribution, Interaction, Opportunity


def get_database_summary(db_session: Session) -> Dict[str, Any]:
    """
    Generate comprehensive database summary statistics.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary containing summary statistics across all tables
    """
    summary = {}

    # Constituent statistics
    constituent_stats = db_session.query(
        func.count(Constituent.constituent_id).label('total'),
        func.count(func.distinct(Constituent.constituent_type)).label('types')
    ).first()

    summary['total_constituents'] = constituent_stats.total or 0
    summary['constituent_types'] = constituent_stats.types or 0

    # Contribution statistics
    contribution_stats = db_session.query(
        func.count(Contribution.contribution_id).label('total'),
        func.sum(Contribution.amount).label('total_amount'),
        func.avg(Contribution.amount).label('average_amount'),
        func.min(Contribution.amount).label('min_amount'),
        func.max(Contribution.amount).label('max_amount'),
        func.count(func.distinct(Contribution.constituent_id)).label('unique_donors')
    ).first()

    summary['total_contributions'] = contribution_stats.total or 0
    summary['total_contribution_amount'] = float(contribution_stats.total_amount or 0)
    summary['average_gift'] = float(contribution_stats.average_amount or 0)
    summary['min_gift'] = float(contribution_stats.min_amount or 0)
    summary['max_gift'] = float(contribution_stats.max_amount or 0)
    summary['unique_donors'] = contribution_stats.unique_donors or 0

    # Interaction statistics
    interaction_stats = db_session.query(
        func.count(Interaction.interaction_id).label('total'),
        func.count(func.distinct(Interaction.constituent_id)).label('unique_constituents'),
        func.count(func.distinct(Interaction.interaction_type)).label('interaction_types')
    ).first()

    summary['total_interactions'] = interaction_stats.total or 0
    summary['constituents_with_interactions'] = interaction_stats.unique_constituents or 0
    summary['interaction_types_count'] = interaction_stats.interaction_types or 0

    # Opportunity statistics
    opportunity_stats = db_session.query(
        func.count(Opportunity.opportunity_id).label('total'),
        func.sum(Opportunity.expected_amount).label('total_value'),
        func.avg(Opportunity.probability).label('avg_probability'),
        func.count(func.distinct(Opportunity.stage)).label('stages')
    ).first()

    summary['total_opportunities'] = opportunity_stats.total or 0
    summary['total_opportunity_value'] = float(opportunity_stats.total_value or 0)
    summary['average_opportunity_probability'] = float(opportunity_stats.avg_probability or 0)
    summary['opportunity_stages'] = opportunity_stats.stages or 0

    # Transaction statistics (not yet implemented)
    summary['total_transactions'] = 0
    summary['total_transaction_amount'] = 0.0
    summary['total_processor_fees'] = 0.0

    # Calculate derived metrics
    if summary['unique_donors'] > 0:
        summary['average_gifts_per_donor'] = round(
            summary['total_contributions'] / summary['unique_donors'], 2
        )
        summary['average_lifetime_value'] = round(
            summary['total_contribution_amount'] / summary['unique_donors'], 2
        )
    else:
        summary['average_gifts_per_donor'] = 0
        summary['average_lifetime_value'] = 0

    if summary['total_contributions'] > 0:
        summary['interaction_to_contribution_ratio'] = round(
            summary['total_interactions'] / summary['total_contributions'], 2
        )
    else:
        summary['interaction_to_contribution_ratio'] = 0

    return summary


def get_giving_trends(db_session: Session) -> Dict[str, Any]:
    """
    Analyze giving trends over time.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary containing trend analysis
    """
    # Get contributions by month
    # Note: Using SQLite-compatible date functions
    monthly_giving = db_session.query(
        func.strftime('%Y-%m', Contribution.contribution_date).label('month'),
        func.count(Contribution.contribution_id).label('count'),
        func.sum(Contribution.amount).label('total'),
        func.avg(Contribution.amount).label('average')
    ).group_by(
        func.strftime('%Y-%m', Contribution.contribution_date)
    ).order_by(
        func.strftime('%Y-%m', Contribution.contribution_date)
    ).all()

    trends = {
        'monthly_data': [
            {
                'month': row.month,
                'count': row.count,
                'total': float(row.total),
                'average': float(row.average)
            }
            for row in monthly_giving
        ]
    }

    # Calculate growth if we have data
    if len(trends['monthly_data']) >= 2:
        first_month = trends['monthly_data'][0]
        last_month = trends['monthly_data'][-1]

        if first_month['total'] > 0:
            growth_rate = (
                (last_month['total'] - first_month['total']) / first_month['total'] * 100
            )
            trends['growth_rate_percent'] = round(growth_rate, 2)
        else:
            trends['growth_rate_percent'] = 0

    # Get giving by contribution type
    by_type = db_session.query(
        Contribution.contribution_type,
        func.count(Contribution.contribution_id).label('count'),
        func.sum(Contribution.amount).label('total')
    ).group_by(
        Contribution.contribution_type
    ).all()

    trends['by_type'] = [
        {
            'type': row.contribution_type,
            'count': row.count,
            'total': float(row.total)
        }
        for row in by_type
    ]

    # Get giving by payment method
    by_payment = db_session.query(
        Contribution.payment_method,
        func.count(Contribution.contribution_id).label('count'),
        func.sum(Contribution.amount).label('total')
    ).group_by(
        Contribution.payment_method
    ).all()

    trends['by_payment_method'] = [
        {
            'method': row.payment_method,
            'count': row.count,
            'total': float(row.total)
        }
        for row in by_payment
    ]

    return trends


def get_engagement_analysis(db_session: Session) -> Dict[str, Any]:
    """
    Analyze constituent engagement patterns.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary containing engagement analysis
    """
    # Engagement by interaction type
    by_type = db_session.query(
        Interaction.interaction_type,
        func.count(Interaction.interaction_id).label('count'),
        func.count(func.distinct(Interaction.constituent_id)).label('unique_constituents')
    ).group_by(
        Interaction.interaction_type
    ).all()

    engagement = {
        'by_interaction_type': [
            {
                'type': row.interaction_type,
                'count': row.count,
                'unique_constituents': row.unique_constituents
            }
            for row in by_type
        ]
    }

    # Follow-up required analysis
    followup_stats = db_session.query(
        func.sum(func.cast(Interaction.follow_up_required, int)).label('requires_followup'),
        func.count(Interaction.interaction_id).label('total')
    ).first()

    if followup_stats.total and followup_stats.total > 0:
        engagement['followup_required_count'] = followup_stats.requires_followup or 0
        engagement['followup_required_percent'] = round(
            (followup_stats.requires_followup or 0) / followup_stats.total * 100, 2
        )
    else:
        engagement['followup_required_count'] = 0
        engagement['followup_required_percent'] = 0

    # Staff member engagement distribution
    by_staff = db_session.query(
        Interaction.staff_member,
        func.count(Interaction.interaction_id).label('count')
    ).group_by(
        Interaction.staff_member
    ).all()

    engagement['by_staff_member'] = [
        {
            'staff_member': row.staff_member,
            'interaction_count': row.count
        }
        for row in by_staff
    ]

    return engagement


def get_opportunity_analysis(db_session: Session) -> Dict[str, Any]:
    """
    Analyze opportunity pipeline.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary containing opportunity analysis
    """
    # Opportunities by stage
    by_stage = db_session.query(
        Opportunity.stage,
        func.count(Opportunity.opportunity_id).label('count'),
        func.sum(Opportunity.expected_amount).label('total_value'),
        func.avg(Opportunity.probability).label('avg_probability')
    ).group_by(
        Opportunity.stage
    ).all()

    analysis = {
        'by_stage': [
            {
                'stage': row.stage,
                'count': row.count,
                'total_value': float(row.total_value),
                'average_probability': round(row.avg_probability, 2),
                'weighted_value': float(row.total_value * row.avg_probability / 100)
            }
            for row in by_stage
        ]
    }

    # Opportunities by assigned staff
    by_staff = db_session.query(
        Opportunity.assigned_to,
        func.count(Opportunity.opportunity_id).label('count'),
        func.sum(Opportunity.expected_amount).label('total_value')
    ).group_by(
        Opportunity.assigned_to
    ).all()

    analysis['by_assigned_staff'] = [
        {
            'staff_member': row.assigned_to,
            'opportunity_count': row.count,
            'total_value': float(row.total_value)
        }
        for row in by_staff
    ]

    return analysis


def generate_complete_summary(db_session: Session) -> Dict[str, Any]:
    """
    Generate a complete summary combining all analysis functions.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary containing complete database analysis
    """
    return {
        'database_summary': get_database_summary(db_session),
        'giving_trends': get_giving_trends(db_session),
        'engagement_analysis': get_engagement_analysis(db_session),
        'opportunity_analysis': get_opportunity_analysis(db_session)
    }
