"""
Segmentation Utility Functions

This module provides utility functions for donor segmentation analysis,
including trend calculations, statistical analysis, and predictive metrics.
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from statistics import mean, stdev
import math


def calculate_giving_trend(amounts: List[Decimal], window_size: int = 3) -> str:
    """
    Calculate giving trend based on rolling window comparison.

    Uses a 3-gift (or custom window) rolling average to determine if giving
    is increasing, decreasing, or stable.

    Args:
        amounts: List of contribution amounts in chronological order
        window_size: Number of gifts to include in rolling average (default: 3)

    Returns:
        'increasing', 'decreasing', 'stable', or 'insufficient_data'

    Example:
        >>> calculate_giving_trend([100, 150, 200, 250, 300], window_size=3)
        'increasing'
    """
    if len(amounts) < window_size * 2:
        return 'insufficient_data'

    # Calculate first window average (older gifts)
    first_window = amounts[:window_size]
    first_avg = sum(first_window) / window_size

    # Calculate last window average (recent gifts)
    last_window = amounts[-window_size:]
    last_avg = sum(last_window) / window_size

    # Calculate percentage change
    if first_avg == 0:
        return 'increasing' if last_avg > 0 else 'stable'

    pct_change = ((last_avg - first_avg) / first_avg) * 100

    # Threshold for considering a trend significant (10%)
    if pct_change > 10:
        return 'increasing'
    elif pct_change < -10:
        return 'decreasing'
    else:
        return 'stable'


def calculate_three_gift_trend(amounts: List[Decimal]) -> Dict[str, any]:
    """
    Calculate 3-gift rolling trend with detailed statistics.

    Args:
        amounts: List of contribution amounts in chronological order

    Returns:
        Dictionary containing trend direction, percentages, and averages
    """
    if len(amounts) < 6:
        return {
            'trend': 'insufficient_data',
            'first_avg': Decimal('0'),
            'last_avg': Decimal('0'),
            'pct_change': 0,
            'data_points': len(amounts)
        }

    first_three = amounts[:3]
    last_three = amounts[-3:]

    first_avg = sum(first_three) / 3
    last_avg = sum(last_three) / 3

    pct_change = 0
    if first_avg > 0:
        pct_change = float(((last_avg - first_avg) / first_avg) * 100)

    trend = calculate_giving_trend(amounts, window_size=3)

    return {
        'trend': trend,
        'first_avg': first_avg,
        'last_avg': last_avg,
        'pct_change': pct_change,
        'data_points': len(amounts)
    }


def days_since_last_contact(last_contact_date: Optional[date],
                            reference_date: Optional[date] = None) -> int:
    """
    Calculate days since last contact.

    Args:
        last_contact_date: Date of last interaction
        reference_date: Reference date (defaults to today)

    Returns:
        Number of days since last contact
    """
    if last_contact_date is None:
        return float('inf')  # Never contacted

    if reference_date is None:
        reference_date = datetime.now().date()

    delta = reference_date - last_contact_date
    return delta.days


def calculate_recency_frequency_monetary(
    contributions: List[Dict],
    reference_date: Optional[date] = None
) -> Dict[str, any]:
    """
    Calculate RFM (Recency, Frequency, Monetary) metrics for a donor.

    Args:
        contributions: List of contribution dictionaries with 'date' and 'amount'
        reference_date: Reference date (defaults to today)

    Returns:
        Dictionary with recency (days), frequency (count), and monetary (total)
    """
    if reference_date is None:
        reference_date = datetime.now().date()

    if not contributions:
        return {
            'recency': float('inf'),
            'frequency': 0,
            'monetary': Decimal('0'),
            'avg_gift': Decimal('0')
        }

    # Recency: days since last contribution
    last_contribution_date = max(c['date'] for c in contributions)
    recency = (reference_date - last_contribution_date).days

    # Frequency: number of contributions
    frequency = len(contributions)

    # Monetary: total amount given
    monetary = sum(c['amount'] for c in contributions if c['amount'])

    # Average gift
    avg_gift = monetary / frequency if frequency > 0 else Decimal('0')

    return {
        'recency': recency,
        'frequency': frequency,
        'monetary': monetary,
        'avg_gift': avg_gift
    }


def calculate_giving_capacity_score(
    total_lifetime_giving: Decimal,
    avg_gift_size: Decimal,
    frequency: int,
    constituent_type: str
) -> float:
    """
    Calculate a giving capacity score (0-100) based on multiple factors.

    Args:
        total_lifetime_giving: Total amount donated
        avg_gift_size: Average gift amount
        frequency: Number of donations
        constituent_type: Type of constituent (e.g., 'Major Donor', 'Donor')

    Returns:
        Capacity score from 0-100
    """
    score = 0.0

    # Lifetime giving component (0-40 points)
    if total_lifetime_giving >= 100000:
        score += 40
    elif total_lifetime_giving >= 50000:
        score += 30
    elif total_lifetime_giving >= 10000:
        score += 20
    elif total_lifetime_giving >= 5000:
        score += 10
    elif total_lifetime_giving > 0:
        score += 5

    # Average gift size component (0-30 points)
    if avg_gift_size >= 5000:
        score += 30
    elif avg_gift_size >= 1000:
        score += 20
    elif avg_gift_size >= 500:
        score += 10
    elif avg_gift_size > 0:
        score += 5

    # Frequency component (0-20 points)
    if frequency >= 20:
        score += 20
    elif frequency >= 10:
        score += 15
    elif frequency >= 5:
        score += 10
    elif frequency > 0:
        score += 5

    # Constituent type bonus (0-10 points)
    if constituent_type == 'Major Donor':
        score += 10
    elif constituent_type == 'Board Member':
        score += 8
    elif constituent_type == 'Donor':
        score += 5

    return min(score, 100.0)


def calculate_engagement_score(
    interaction_count: int,
    days_since_last_interaction: int,
    contribution_frequency: int
) -> float:
    """
    Calculate engagement score (0-100) based on interaction patterns.

    Args:
        interaction_count: Total number of interactions
        days_since_last_interaction: Days since last contact
        contribution_frequency: Number of contributions

    Returns:
        Engagement score from 0-100
    """
    score = 0.0

    # Interaction count component (0-40 points)
    if interaction_count >= 20:
        score += 40
    elif interaction_count >= 10:
        score += 30
    elif interaction_count >= 5:
        score += 20
    elif interaction_count > 0:
        score += 10

    # Recency component (0-30 points)
    if days_since_last_interaction <= 30:
        score += 30
    elif days_since_last_interaction <= 90:
        score += 20
    elif days_since_last_interaction <= 180:
        score += 10
    elif days_since_last_interaction <= 365:
        score += 5

    # Contribution frequency component (0-30 points)
    if contribution_frequency >= 12:
        score += 30
    elif contribution_frequency >= 6:
        score += 20
    elif contribution_frequency >= 3:
        score += 10
    elif contribution_frequency > 0:
        score += 5

    return min(score, 100.0)


def detect_seasonal_pattern(contributions: List[Dict]) -> Dict[str, any]:
    """
    Detect seasonal giving patterns by analyzing contribution dates.

    Args:
        contributions: List of contribution dictionaries with 'date' and 'amount'

    Returns:
        Dictionary with seasonal analysis including preferred months and patterns
    """
    if len(contributions) < 3:
        return {
            'has_pattern': False,
            'preferred_months': [],
            'pattern_strength': 0,
            'next_likely_gift_date': None
        }

    # Count contributions by month
    month_counts = {}
    month_amounts = {}

    for contrib in contributions:
        month = contrib['date'].month
        month_counts[month] = month_counts.get(month, 0) + 1
        month_amounts[month] = month_amounts.get(month, Decimal('0')) + contrib['amount']

    # Find months with highest activity
    sorted_months = sorted(month_counts.items(), key=lambda x: x[1], reverse=True)
    top_months = [month for month, count in sorted_months[:3] if count >= 2]

    # Calculate pattern strength (0-100)
    total_contributions = len(contributions)
    top_month_contributions = sum(month_counts.get(m, 0) for m in top_months)
    pattern_strength = (top_month_contributions / total_contributions * 100) if total_contributions > 0 else 0

    has_pattern = pattern_strength >= 40 and len(top_months) > 0

    # Predict next likely gift date
    next_likely_date = None
    if has_pattern and top_months:
        today = datetime.now().date()
        current_month = today.month

        # Find next occurrence of top month
        for month in sorted(top_months):
            if month > current_month:
                next_likely_date = date(today.year, month, 15)
                break

        if next_likely_date is None and top_months:
            # Next occurrence is next year
            next_likely_date = date(today.year + 1, top_months[0], 15)

    month_names = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    return {
        'has_pattern': has_pattern,
        'preferred_months': [month_names[m] for m in top_months],
        'pattern_strength': round(pattern_strength, 1),
        'next_likely_gift_date': next_likely_date,
        'month_breakdown': {
            month_names[m]: {
                'count': month_counts.get(m, 0),
                'total': float(month_amounts.get(m, Decimal('0')))
            }
            for m in range(1, 13)
        }
    }


def calculate_donor_risk_score(
    days_since_last_gift: int,
    giving_trend: str,
    engagement_score: float
) -> Tuple[float, str]:
    """
    Calculate donor retention risk score.

    Args:
        days_since_last_gift: Days since last contribution
        giving_trend: Trend direction ('increasing', 'decreasing', 'stable')
        engagement_score: Engagement score (0-100)

    Returns:
        Tuple of (risk_score, risk_level) where risk_score is 0-100
        and risk_level is 'low', 'medium', or 'high'
    """
    risk_score = 0.0

    # Recency risk (0-40 points)
    if days_since_last_gift > 730:  # 2+ years
        risk_score += 40
    elif days_since_last_gift > 365:  # 1-2 years
        risk_score += 30
    elif days_since_last_gift > 180:  # 6-12 months
        risk_score += 20
    elif days_since_last_gift > 90:  # 3-6 months
        risk_score += 10

    # Trend risk (0-30 points)
    if giving_trend == 'decreasing':
        risk_score += 30
    elif giving_trend == 'stable':
        risk_score += 10

    # Engagement risk (0-30 points)
    if engagement_score < 20:
        risk_score += 30
    elif engagement_score < 40:
        risk_score += 20
    elif engagement_score < 60:
        risk_score += 10

    # Determine risk level
    if risk_score >= 60:
        risk_level = 'high'
    elif risk_score >= 30:
        risk_level = 'medium'
    else:
        risk_level = 'low'

    return risk_score, risk_level


def generate_action_recommendation(
    segment_type: str,
    donor_data: Dict[str, any]
) -> str:
    """
    Generate AI-style action recommendations based on segment and donor data.

    Args:
        segment_type: Type of segment the donor belongs to
        donor_data: Dictionary containing donor metrics and characteristics

    Returns:
        Suggested next action string
    """
    recommendations = {
        'high_capacity_low_giving': [
            "Schedule a personal meeting to understand their philanthropic goals and present a major gift opportunity.",
            "Send a personalized impact report highlighting how their gifts have made a difference and invite them to a special donor event.",
            "Arrange a site visit to show the direct impact of donations and discuss opportunities for increased involvement.",
        ],
        'increasing_giving': [
            "Acknowledge the positive trend with a personalized thank you call and explore opportunities for sustainer giving.",
            "Present an opportunity to join a leadership giving circle or recurring donation program.",
            "Share impact stories that align with their interests and invite them to participate in upcoming events.",
        ],
        'declining_giving': [
            "Schedule a check-in call to understand any concerns and reaffirm the value of their support.",
            "Send a personal note from leadership thanking them for past support and inquiring about their current interests.",
            "Offer a portfolio of giving options at various levels to re-engage them based on current capacity.",
        ],
        'no_recent_contact': [
            "Reach out with a warm, no-ask touchpoint such as a personalized update on programs they've supported.",
            "Send an invitation to an exclusive donor appreciation event to re-establish connection.",
            "Share a compelling story or impact report and request a brief call to catch up.",
        ],
        'potential_major_donor': [
            "Initiate major donor cultivation with a face-to-face meeting to discuss their philanthropic vision.",
            "Present a customized proposal for a named gift opportunity or multi-year commitment.",
            "Invite them to join an advisory board or leadership committee to deepen engagement.",
        ],
        'major_donor_neglected': [
            "Immediately schedule a personal visit or call from executive leadership to express gratitude and strengthen the relationship.",
            "Arrange a VIP experience such as a behind-the-scenes tour or meeting with beneficiaries.",
            "Develop a stewardship plan with quarterly touchpoints including impact reports and exclusive updates.",
        ],
        'seasonal_giver': [
            "Time outreach to align with their historical giving pattern and reference past support during that season.",
            "Send a pre-season reminder highlighting urgent needs and matching gift opportunities.",
            "Create a multi-year sustainer opportunity that spreads their seasonal gift throughout the year.",
        ]
    }

    # Get recommendations for this segment type
    segment_recs = recommendations.get(segment_type, [
        "Review donor profile and develop a personalized engagement strategy based on their giving history and interests."
    ])

    # Select recommendation based on donor characteristics
    if donor_data.get('total_lifetime_giving', 0) > 10000:
        return segment_recs[0]
    elif donor_data.get('frequency', 0) > 5:
        return segment_recs[min(1, len(segment_recs) - 1)]
    else:
        return segment_recs[-1]
