"""
Nonprofit Donor Segmentation Module

This module provides donor segmentation capabilities for nonprofit fundraising.
"""

from .engine import SegmentationEngine, Segment
from .utils import (
    calculate_giving_trend,
    calculate_three_gift_trend,
    calculate_recency_frequency_monetary,
    calculate_giving_capacity_score,
    calculate_engagement_score,
    detect_seasonal_pattern,
    calculate_donor_risk_score,
    generate_action_recommendation
)

__version__ = '1.0.0'

__all__ = [
    'SegmentationEngine',
    'Segment',
    'calculate_giving_trend',
    'calculate_three_gift_trend',
    'calculate_recency_frequency_monetary',
    'calculate_giving_capacity_score',
    'calculate_engagement_score',
    'detect_seasonal_pattern',
    'calculate_donor_risk_score',
    'generate_action_recommendation',
]
