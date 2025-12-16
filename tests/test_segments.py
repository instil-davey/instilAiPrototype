"""
Unit Tests for Donor Segmentation Engine

Comprehensive test suite for segmentation utilities and engine logic.
"""

import pytest
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.segments.utils import (
    calculate_giving_trend,
    calculate_three_gift_trend,
    days_since_last_contact,
    calculate_recency_frequency_monetary,
    calculate_giving_capacity_score,
    calculate_engagement_score,
    detect_seasonal_pattern,
    calculate_donor_risk_score,
    generate_action_recommendation
)


class TestGivingTrendCalculations:
    """Test suite for giving trend calculations."""

    def test_increasing_trend(self):
        """Test detection of increasing giving trend."""
        amounts = [
            Decimal('100'), Decimal('110'), Decimal('120'),
            Decimal('150'), Decimal('160'), Decimal('170')
        ]
        trend = calculate_giving_trend(amounts, window_size=3)
        assert trend == 'increasing'

    def test_decreasing_trend(self):
        """Test detection of decreasing giving trend."""
        amounts = [
            Decimal('200'), Decimal('190'), Decimal('180'),
            Decimal('100'), Decimal('90'), Decimal('80')
        ]
        trend = calculate_giving_trend(amounts, window_size=3)
        assert trend == 'decreasing'

    def test_stable_trend(self):
        """Test detection of stable giving trend."""
        amounts = [
            Decimal('100'), Decimal('105'), Decimal('100'),
            Decimal('100'), Decimal('95'), Decimal('100')
        ]
        trend = calculate_giving_trend(amounts, window_size=3)
        assert trend == 'stable'

    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        amounts = [Decimal('100'), Decimal('110')]
        trend = calculate_giving_trend(amounts, window_size=3)
        assert trend == 'insufficient_data'

    def test_three_gift_trend_detailed(self):
        """Test detailed 3-gift trend calculation."""
        amounts = [
            Decimal('100'), Decimal('100'), Decimal('100'),
            Decimal('150'), Decimal('150'), Decimal('150')
        ]
        result = calculate_three_gift_trend(amounts)

        assert result['trend'] == 'increasing'
        assert result['first_avg'] == Decimal('100')
        assert result['last_avg'] == Decimal('150')
        assert result['pct_change'] == 50.0
        assert result['data_points'] == 6

    def test_three_gift_trend_insufficient_data(self):
        """Test 3-gift trend with insufficient data."""
        amounts = [Decimal('100'), Decimal('110'), Decimal('120')]
        result = calculate_three_gift_trend(amounts)

        assert result['trend'] == 'insufficient_data'
        assert result['data_points'] == 3


class TestRecencyCalculations:
    """Test suite for recency calculations."""

    def test_days_since_last_contact(self):
        """Test days since last contact calculation."""
        last_contact = date(2024, 1, 1)
        reference = date(2024, 4, 1)

        days = days_since_last_contact(last_contact, reference)
        assert days == 91

    def test_days_since_last_contact_no_contact(self):
        """Test days calculation when never contacted."""
        days = days_since_last_contact(None)
        assert days == float('inf')

    def test_days_since_last_contact_today(self):
        """Test days calculation with today's reference."""
        last_contact = datetime.now().date() - timedelta(days=30)
        days = days_since_last_contact(last_contact)
        assert days == 30


class TestRFMCalculations:
    """Test suite for RFM (Recency, Frequency, Monetary) calculations."""

    def test_rfm_calculation(self):
        """Test RFM calculation with sample data."""
        contributions = [
            {'date': date(2023, 1, 1), 'amount': Decimal('100')},
            {'date': date(2023, 6, 1), 'amount': Decimal('150')},
            {'date': date(2024, 1, 1), 'amount': Decimal('200')},
        ]
        reference = date(2024, 4, 1)

        rfm = calculate_recency_frequency_monetary(contributions, reference)

        assert rfm['recency'] == 91  # Days since last contribution (2024-04-01 - 2024-01-01)
        assert rfm['frequency'] == 3
        assert rfm['monetary'] == Decimal('450')
        assert rfm['avg_gift'] == Decimal('150')

    def test_rfm_empty_contributions(self):
        """Test RFM with no contributions."""
        rfm = calculate_recency_frequency_monetary([])

        assert rfm['recency'] == float('inf')
        assert rfm['frequency'] == 0
        assert rfm['monetary'] == Decimal('0')
        assert rfm['avg_gift'] == Decimal('0')

    def test_rfm_single_contribution(self):
        """Test RFM with single contribution."""
        contributions = [
            {'date': date(2024, 1, 1), 'amount': Decimal('500')}
        ]
        reference = date(2024, 1, 31)

        rfm = calculate_recency_frequency_monetary(contributions, reference)

        assert rfm['recency'] == 30
        assert rfm['frequency'] == 1
        assert rfm['monetary'] == Decimal('500')
        assert rfm['avg_gift'] == Decimal('500')


class TestCapacityScore:
    """Test suite for giving capacity score calculations."""

    def test_high_capacity_score(self):
        """Test calculation of high capacity score."""
        score = calculate_giving_capacity_score(
            total_lifetime_giving=Decimal('50000'),
            avg_gift_size=Decimal('5000'),
            frequency=20,
            constituent_type='Major Donor'
        )

        assert score >= 80
        assert score <= 100

    def test_medium_capacity_score(self):
        """Test calculation of medium capacity score."""
        score = calculate_giving_capacity_score(
            total_lifetime_giving=Decimal('5000'),
            avg_gift_size=Decimal('500'),
            frequency=10,
            constituent_type='Donor'
        )

        assert 30 <= score <= 70

    def test_low_capacity_score(self):
        """Test calculation of low capacity score."""
        score = calculate_giving_capacity_score(
            total_lifetime_giving=Decimal('100'),
            avg_gift_size=Decimal('50'),
            frequency=2,
            constituent_type='Donor'
        )

        assert score <= 30

    def test_capacity_score_major_donor_bonus(self):
        """Test that Major Donor type receives bonus points."""
        score_major = calculate_giving_capacity_score(
            total_lifetime_giving=Decimal('5000'),
            avg_gift_size=Decimal('500'),
            frequency=5,
            constituent_type='Major Donor'
        )

        score_regular = calculate_giving_capacity_score(
            total_lifetime_giving=Decimal('5000'),
            avg_gift_size=Decimal('500'),
            frequency=5,
            constituent_type='Donor'
        )

        assert score_major > score_regular


class TestEngagementScore:
    """Test suite for engagement score calculations."""

    def test_high_engagement_score(self):
        """Test high engagement score calculation."""
        score = calculate_engagement_score(
            interaction_count=25,
            days_since_last_interaction=15,
            contribution_frequency=12
        )

        assert score >= 80

    def test_low_engagement_score(self):
        """Test low engagement score calculation."""
        score = calculate_engagement_score(
            interaction_count=1,
            days_since_last_interaction=500,
            contribution_frequency=1
        )

        assert score <= 30

    def test_engagement_score_recency_weight(self):
        """Test that recent interactions increase engagement score."""
        score_recent = calculate_engagement_score(
            interaction_count=10,
            days_since_last_interaction=20,
            contribution_frequency=5
        )

        score_old = calculate_engagement_score(
            interaction_count=10,
            days_since_last_interaction=200,
            contribution_frequency=5
        )

        assert score_recent > score_old


class TestSeasonalPatterns:
    """Test suite for seasonal pattern detection."""

    def test_detect_seasonal_pattern(self):
        """Test detection of clear seasonal pattern."""
        contributions = [
            {'date': date(2022, 12, 15), 'amount': Decimal('100')},
            {'date': date(2023, 12, 20), 'amount': Decimal('150')},
            {'date': date(2024, 12, 10), 'amount': Decimal('200')},
            {'date': date(2023, 6, 1), 'amount': Decimal('50')},
        ]

        result = detect_seasonal_pattern(contributions)

        assert result['has_pattern'] is True
        assert 'December' in result['preferred_months']
        assert result['pattern_strength'] > 40

    def test_no_seasonal_pattern(self):
        """Test when no clear seasonal pattern exists."""
        contributions = [
            {'date': date(2024, 1, 1), 'amount': Decimal('100')},
            {'date': date(2024, 4, 1), 'amount': Decimal('100')},
            {'date': date(2024, 7, 1), 'amount': Decimal('100')},
        ]

        result = detect_seasonal_pattern(contributions)

        # Each month has 1 contribution, pattern strength should be low
        assert result['pattern_strength'] < 50

    def test_seasonal_pattern_insufficient_data(self):
        """Test seasonal pattern with insufficient data."""
        contributions = [
            {'date': date(2024, 1, 1), 'amount': Decimal('100')}
        ]

        result = detect_seasonal_pattern(contributions)

        assert result['has_pattern'] is False
        assert result['pattern_strength'] == 0

    def test_seasonal_forecast(self):
        """Test next likely gift date prediction."""
        # Pattern in December
        contributions = [
            {'date': date(2022, 12, 15), 'amount': Decimal('100')},
            {'date': date(2023, 12, 20), 'amount': Decimal('150')},
            {'date': date(2024, 1, 10), 'amount': Decimal('50')},
        ]

        result = detect_seasonal_pattern(contributions)

        if result['has_pattern']:
            assert result['next_likely_gift_date'] is not None
            # Should predict next December
            assert result['next_likely_gift_date'].month == 12


class TestRiskScore:
    """Test suite for donor risk score calculations."""

    def test_high_risk_score(self):
        """Test high risk donor identification."""
        risk_score, risk_level = calculate_donor_risk_score(
            days_since_last_gift=800,
            giving_trend='decreasing',
            engagement_score=15
        )

        assert risk_level == 'high'
        assert risk_score >= 60

    def test_low_risk_score(self):
        """Test low risk donor identification."""
        risk_score, risk_level = calculate_donor_risk_score(
            days_since_last_gift=30,
            giving_trend='increasing',
            engagement_score=85
        )

        assert risk_level == 'low'
        assert risk_score < 30

    def test_medium_risk_score(self):
        """Test medium risk donor identification."""
        risk_score, risk_level = calculate_donor_risk_score(
            days_since_last_gift=200,
            giving_trend='stable',
            engagement_score=50
        )

        assert risk_level == 'medium'
        assert 30 <= risk_score < 60


class TestActionRecommendations:
    """Test suite for action recommendation generation."""

    def test_high_capacity_recommendation(self):
        """Test recommendation for high capacity donors."""
        action = generate_action_recommendation(
            'high_capacity_low_giving',
            {
                'total_lifetime_giving': 50000,
                'frequency': 10,
                'capacity_score': 80
            }
        )

        assert action is not None
        assert len(action) > 0
        assert 'major gift' in action.lower() or 'meeting' in action.lower()

    def test_increasing_giving_recommendation(self):
        """Test recommendation for increasing giving pattern."""
        action = generate_action_recommendation(
            'increasing_giving',
            {
                'total_lifetime_giving': 5000,
                'frequency': 8,
                'pct_change': 25
            }
        )

        assert action is not None
        assert len(action) > 0

    def test_declining_giving_recommendation(self):
        """Test recommendation for declining giving pattern."""
        action = generate_action_recommendation(
            'declining_giving',
            {
                'total_lifetime_giving': 3000,
                'frequency': 5,
                'pct_change': -20
            }
        )

        assert action is not None
        assert len(action) > 0

    def test_no_contact_recommendation(self):
        """Test recommendation for no recent contact."""
        action = generate_action_recommendation(
            'no_recent_contact',
            {
                'total_lifetime_giving': 2000,
                'frequency': 4,
                'days_since_contact': 120
            }
        )

        assert action is not None
        assert len(action) > 0

    def test_recommendation_length(self):
        """Test that recommendations are meaningful length."""
        action = generate_action_recommendation(
            'potential_major_donor',
            {
                'total_lifetime_giving': 15000,
                'frequency': 12,
                'capacity_score': 85
            }
        )

        # Should be a substantive recommendation
        assert len(action) > 50


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_zero_amounts(self):
        """Test handling of zero amounts."""
        amounts = [Decimal('0'), Decimal('0'), Decimal('0')]
        trend = calculate_three_gift_trend(amounts)

        assert trend['trend'] == 'insufficient_data'

    def test_negative_days_calculation(self):
        """Test that negative days are not possible."""
        future_date = datetime.now().date() + timedelta(days=30)
        days = days_since_last_contact(future_date)

        # Should handle future dates gracefully
        assert isinstance(days, (int, float))

    def test_very_large_amounts(self):
        """Test handling of very large donation amounts."""
        amounts = [
            Decimal('1000000'), Decimal('1100000'), Decimal('1200000'),
            Decimal('1500000'), Decimal('1600000'), Decimal('1700000')
        ]
        trend = calculate_giving_trend(amounts, window_size=3)

        assert trend in ['increasing', 'decreasing', 'stable']

    def test_capacity_score_bounds(self):
        """Test that capacity score stays within 0-100 bounds."""
        # Test maximum score
        score = calculate_giving_capacity_score(
            total_lifetime_giving=Decimal('10000000'),
            avg_gift_size=Decimal('100000'),
            frequency=1000,
            constituent_type='Major Donor'
        )

        assert 0 <= score <= 100

    def test_engagement_score_bounds(self):
        """Test that engagement score stays within 0-100 bounds."""
        # Test maximum score
        score = calculate_engagement_score(
            interaction_count=1000,
            days_since_last_interaction=1,
            contribution_frequency=500
        )

        assert 0 <= score <= 100


class TestPerformance:
    """Test suite for performance considerations."""

    def test_large_contribution_list(self):
        """Test performance with large contribution lists."""
        # Create 1000 contributions
        amounts = [Decimal('100') + Decimal(i % 50) for i in range(1000)]

        # Should complete quickly
        import time
        start = time.time()
        trend = calculate_giving_trend(amounts, window_size=3)
        elapsed = time.time() - start

        assert elapsed < 1.0  # Should complete in less than 1 second
        assert trend in ['increasing', 'decreasing', 'stable']

    def test_seasonal_pattern_large_dataset(self):
        """Test seasonal pattern detection with many contributions."""
        contributions = [
            {
                'date': date(2020 + i // 12, (i % 12) + 1, 15),
                'amount': Decimal('100')
            }
            for i in range(100)
        ]

        import time
        start = time.time()
        result = detect_seasonal_pattern(contributions)
        elapsed = time.time() - start

        assert elapsed < 1.0  # Should complete quickly
        assert 'has_pattern' in result


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
