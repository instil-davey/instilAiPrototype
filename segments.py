"""
Donor Segmentation Definitions for Nonprofit CRM
Defines constituent segments for targeted fundraising actions
"""

from enum import Enum
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from models import Constituent, Contribution, Interaction
from decimal import Decimal


class SegmentType(str, Enum):
    """Standard nonprofit donor segments"""
    MAJOR_DONOR = "major_donor"
    LAPSED_DONOR = "lapsed_donor"
    FIRST_TIME_DONOR = "first_time_donor"
    RECURRING_DONOR = "recurring_donor"
    HIGH_ENGAGEMENT = "high_engagement"
    LOW_ENGAGEMENT = "low_engagement"
    PLANNED_GIVING_PROSPECT = "planned_giving_prospect"
    BOARD_MEMBER = "board_member"
    VOLUNTEER = "volunteer"
    EVENT_ATTENDEE = "event_attendee"


SEGMENT_DEFINITIONS = {
    SegmentType.MAJOR_DONOR: {
        "name": "Major Donor",
        "description": "Constituents who have given $5,000+ in lifetime contributions",
        "priority": "high",
        "criteria": {
            "min_lifetime_giving": 5000.00
        }
    },
    SegmentType.LAPSED_DONOR: {
        "name": "Lapsed Donor",
        "description": "Previous donors who haven't given in 18+ months",
        "priority": "medium",
        "criteria": {
            "months_since_last_gift": 18,
            "min_past_contributions": 1
        }
    },
    SegmentType.FIRST_TIME_DONOR: {
        "name": "First-Time Donor",
        "description": "Donors who made their first gift in the last 90 days",
        "priority": "high",
        "criteria": {
            "days_since_first_gift": 90,
            "total_contributions": 1
        }
    },
    SegmentType.RECURRING_DONOR: {
        "name": "Recurring Donor",
        "description": "Donors who have given 3+ times in the last 12 months",
        "priority": "high",
        "criteria": {
            "contributions_in_months": 12,
            "min_contribution_count": 3
        }
    },
    SegmentType.HIGH_ENGAGEMENT: {
        "name": "High Engagement",
        "description": "Constituents with 5+ interactions in the last 6 months",
        "priority": "medium",
        "criteria": {
            "interactions_in_months": 6,
            "min_interaction_count": 5
        }
    },
    SegmentType.LOW_ENGAGEMENT: {
        "name": "Low Engagement",
        "description": "Donors with no interactions in 12+ months but have given",
        "priority": "medium",
        "criteria": {
            "months_since_last_interaction": 12,
            "min_past_contributions": 1
        }
    },
    SegmentType.PLANNED_GIVING_PROSPECT: {
        "name": "Planned Giving Prospect",
        "description": "Donors 60+ years old with $10,000+ lifetime giving",
        "priority": "high",
        "criteria": {
            "min_age": 60,
            "min_lifetime_giving": 10000.00
        }
    },
    SegmentType.BOARD_MEMBER: {
        "name": "Board Member",
        "description": "Current board members requiring stewardship",
        "priority": "high",
        "criteria": {
            "constituent_type": "Board Member"
        }
    },
    SegmentType.VOLUNTEER: {
        "name": "Volunteer",
        "description": "Active volunteers who could become donors",
        "priority": "medium",
        "criteria": {
            "constituent_type": "Volunteer"
        }
    },
    SegmentType.EVENT_ATTENDEE: {
        "name": "Event Attendee",
        "description": "Recent event attendees (last 3 months)",
        "priority": "medium",
        "criteria": {
            "event_in_months": 3
        }
    }
}


def get_constituent_segment(session: Session, constituent_id: int) -> List[SegmentType]:
    """
    Determine which segments a constituent belongs to based on their data.

    Args:
        session: Database session
        constituent_id: ID of the constituent to segment

    Returns:
        List of SegmentType enum values the constituent belongs to
    """
    constituent = session.query(Constituent).filter_by(
        constituent_id=constituent_id
    ).first()

    if not constituent:
        return []

    segments = []

    # Get contribution data
    total_contributions = session.query(func.count(Contribution.contribution_id)).filter(
        Contribution.constituent_id == constituent_id
    ).scalar() or 0

    latest_contribution = session.query(Contribution).filter(
        Contribution.constituent_id == constituent_id
    ).order_by(Contribution.contribution_date.desc()).first()

    earliest_contribution = session.query(Contribution).filter(
        Contribution.constituent_id == constituent_id
    ).order_by(Contribution.contribution_date.asc()).first()

    # Get interaction data
    total_interactions = session.query(func.count(Interaction.interaction_id)).filter(
        Interaction.constituent_id == constituent_id
    ).scalar() or 0

    latest_interaction = session.query(Interaction).filter(
        Interaction.constituent_id == constituent_id
    ).order_by(Interaction.interaction_date.desc()).first()

    # Get event interactions
    event_interactions = session.query(func.count(Interaction.interaction_id)).filter(
        and_(
            Interaction.constituent_id == constituent_id,
            Interaction.interaction_type == 'Event',
            Interaction.interaction_date >= datetime.now().date() - timedelta(days=90)
        )
    ).scalar() or 0

    # Recent contributions (last 12 months)
    recent_contributions = session.query(func.count(Contribution.contribution_id)).filter(
        and_(
            Contribution.constituent_id == constituent_id,
            Contribution.contribution_date >= datetime.now().date() - timedelta(days=365)
        )
    ).scalar() or 0

    # Recent interactions (last 6 months)
    recent_interactions = session.query(func.count(Interaction.interaction_id)).filter(
        and_(
            Interaction.constituent_id == constituent_id,
            Interaction.interaction_date >= datetime.now().date() - timedelta(days=180)
        )
    ).scalar() or 0

    # Check Major Donor
    if constituent.total_lifetime_giving and constituent.total_lifetime_giving >= 5000:
        segments.append(SegmentType.MAJOR_DONOR)

    # Check Planned Giving Prospect
    if constituent.total_lifetime_giving and constituent.total_lifetime_giving >= 10000:
        segments.append(SegmentType.PLANNED_GIVING_PROSPECT)

    # Check First-Time Donor
    if (total_contributions == 1 and earliest_contribution and
        earliest_contribution.contribution_date >= datetime.now().date() - timedelta(days=90)):
        segments.append(SegmentType.FIRST_TIME_DONOR)

    # Check Recurring Donor
    if recent_contributions >= 3:
        segments.append(SegmentType.RECURRING_DONOR)

    # Check Lapsed Donor
    if (total_contributions > 0 and latest_contribution and
        latest_contribution.contribution_date < datetime.now().date() - timedelta(days=540)):
        segments.append(SegmentType.LAPSED_DONOR)

    # Check High Engagement
    if recent_interactions >= 5:
        segments.append(SegmentType.HIGH_ENGAGEMENT)

    # Check Low Engagement
    if (total_contributions > 0 and latest_interaction and
        latest_interaction.interaction_date < datetime.now().date() - timedelta(days=365)):
        segments.append(SegmentType.LOW_ENGAGEMENT)

    # Check Board Member
    if constituent.constituent_type == "Board Member":
        segments.append(SegmentType.BOARD_MEMBER)

    # Check Volunteer
    if constituent.constituent_type == "Volunteer":
        segments.append(SegmentType.VOLUNTEER)

    # Check Event Attendee
    if event_interactions > 0:
        segments.append(SegmentType.EVENT_ATTENDEE)

    return segments


def get_segment_info(segment_type: SegmentType) -> Dict:
    """
    Get information about a specific segment.

    Args:
        segment_type: The segment type to get info for

    Returns:
        Dictionary with segment details
    """
    return SEGMENT_DEFINITIONS.get(segment_type, {})
