"""
Nonprofit Donor Segmentation Engine

This module provides the core segmentation logic for analyzing donor behavior
and generating actionable segments for fundraising teams.
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

# Import models
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models import Constituent, Contribution, Interaction, Opportunity

# Import utility functions
from .utils import (
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


@dataclass
class Segment:
    """
    Data class representing a donor segment.
    """
    segment_id: str
    name: str
    description: str
    reasoning_formula: str
    constituent_ids: List[int]
    suggested_actions: Dict[int, str]
    segment_metrics: Dict[str, Any]
    constituent_reasons: Dict[int, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert segment to dictionary format."""
        return asdict(self)


class SegmentationEngine:
    """
    Main segmentation engine for nonprofit donor analysis.
    """

    def __init__(self, session: Session, reference_date: Optional[date] = None):
        """
        Initialize the segmentation engine.

        Args:
            session: SQLAlchemy database session
            reference_date: Reference date for calculations (defaults to today)
        """
        self.session = session
        self.reference_date = reference_date or datetime.now().date()
        self._constituent_cache = {}

    @staticmethod
    def _format_days(value: float) -> str:
        """Convert day counts to readable text."""
        if value == float('inf'):
            return "no recorded contact"
        return f"{int(value)} days"

    def get_constituent_data(self, constituent_id: int) -> Dict[str, Any]:
        """
        Get comprehensive data for a constituent with caching.

        Args:
            constituent_id: ID of the constituent

        Returns:
            Dictionary with constituent data and metrics
        """
        if constituent_id in self._constituent_cache:
            return self._constituent_cache[constituent_id]

        constituent = self.session.query(Constituent).filter_by(
            constituent_id=constituent_id
        ).first()

        if not constituent:
            return None

        # Get contributions
        contributions = self.session.query(Contribution).filter(
            Contribution.constituent_id == constituent_id,
            Contribution.amount.isnot(None)
        ).order_by(Contribution.contribution_date).all()

        # Get interactions
        interactions = self.session.query(Interaction).filter(
            Interaction.constituent_id == constituent_id
        ).order_by(Interaction.interaction_date).all()

        # Get opportunities
        opportunities = self.session.query(Opportunity).filter(
            Opportunity.constituent_id == constituent_id
        ).all()

        # Process contributions
        contrib_data = [
            {'date': c.contribution_date, 'amount': c.amount}
            for c in contributions
            if c.amount
        ]

        amounts = [c.amount for c in contributions if c.amount]

        # Calculate RFM metrics
        rfm = calculate_recency_frequency_monetary(contrib_data, self.reference_date)

        # Calculate giving trend
        trend_analysis = calculate_three_gift_trend(amounts) if amounts else None

        # Get last interaction date
        if interactions:
            last_record = max([i.interaction_date for i in interactions])
            last_interaction_date = (
                last_record.date() if hasattr(last_record, 'date') else last_record
            )
        else:
            last_interaction_date = None

        days_since_interaction = days_since_last_contact(
            last_interaction_date, self.reference_date
        )

        # Calculate engagement score
        engagement = calculate_engagement_score(
            len(interactions),
            days_since_interaction if days_since_interaction != float('inf') else 999,
            rfm['frequency']
        )

        # Calculate capacity score
        capacity = calculate_giving_capacity_score(
            constituent.total_lifetime_giving or Decimal('0'),
            rfm['avg_gift'],
            rfm['frequency'],
            constituent.constituent_type
        )

        # Detect seasonal patterns
        seasonal = detect_seasonal_pattern(contrib_data) if contrib_data else None

        # Calculate risk score
        risk_score, risk_level = calculate_donor_risk_score(
            rfm['recency'],
            trend_analysis['trend'] if trend_analysis else 'insufficient_data',
            engagement
        )

        data = {
            'constituent_id': constituent_id,
            'constituent': constituent,
            'contributions': contributions,
            'interactions': interactions,
            'opportunities': opportunities,
            'rfm': rfm,
            'trend_analysis': trend_analysis,
            'engagement_score': engagement,
            'capacity_score': capacity,
            'seasonal_analysis': seasonal,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'days_since_last_gift': rfm['recency'],
            'days_since_last_interaction': days_since_interaction,
            'total_lifetime_giving': float(constituent.total_lifetime_giving or 0),
            'contribution_count': len(contributions),
            'interaction_count': len(interactions)
        }

        self._constituent_cache[constituent_id] = data
        return data

    def segment_high_capacity_low_giving(self) -> Segment:
        """
        Segment: High Capacity, Low Recent Giving

        Identifies donors with high giving capacity (based on wealth indicators,
        constituent type, and past giving) but low recent giving amounts.

        Formula: capacity_score >= 60 AND (recent_avg < 50% of capacity OR recency > 180 days)
        """
        matching_constituents = []
        actions = {}
        reasons = {}

        # Query all constituents with some giving history
        constituents = self.session.query(Constituent).filter(
            Constituent.total_lifetime_giving > 0
        ).all()

        for constituent in constituents:
            data = self.get_constituent_data(constituent.constituent_id)
            if not data:
                continue

            capacity = data['capacity_score']
            rfm = data['rfm']
            avg_gift = float(rfm['avg_gift'])

            # High capacity but low recent giving or lapsed
            if capacity >= 60 and (rfm['recency'] > 180 or avg_gift < capacity * 0.5):
                matching_constituents.append(constituent.constituent_id)
                actions[constituent.constituent_id] = generate_action_recommendation(
                    'high_capacity_low_giving',
                    {
                        'total_lifetime_giving': data['total_lifetime_giving'],
                        'frequency': rfm['frequency'],
                        'capacity_score': capacity
                    }
                )
                reasons[constituent.constituent_id] = (
                    f"Capacity score {capacity:.0f} with lifetime giving ${data['total_lifetime_giving']:,.0f}, "
                    f"but average gift ${avg_gift:,.0f} and last gift {self._format_days(rfm['recency'])}."
                )

        return Segment(
            segment_id='high_capacity_low_giving',
            name='High Capacity, Low Recent Giving',
            description='Donors with high giving capacity but low recent contributions or lapsed giving',
            reasoning_formula='capacity_score >= 60 AND (recency > 180 days OR avg_gift < 50% capacity)',
            constituent_ids=matching_constituents,
            suggested_actions=actions,
            segment_metrics={
                'count': len(matching_constituents),
                'avg_capacity_score': sum(
                    self.get_constituent_data(cid)['capacity_score']
                    for cid in matching_constituents
                ) / len(matching_constituents) if matching_constituents else 0
            },
            constituent_reasons=reasons
        )

    def segment_increasing_giving(self) -> Segment:
        """
        Segment: Increasing Giving Patterns

        Identifies donors whose giving has been trending upward over time.

        Formula: 3-gift rolling trend shows > 10% increase
        """
        matching_constituents = []
        actions = {}
        reasons = {}

        # Query constituents with at least 6 contributions
        constituents = self.session.query(
            Constituent.constituent_id
        ).join(Contribution).group_by(
            Constituent.constituent_id
        ).having(
            func.count(Contribution.contribution_id) >= 6
        ).all()

        for (constituent_id,) in constituents:
            data = self.get_constituent_data(constituent_id)
            if not data:
                continue
            trend = data.get('trend_analysis')

            if trend and trend['trend'] == 'increasing':
                matching_constituents.append(constituent_id)
                actions[constituent_id] = generate_action_recommendation(
                    'increasing_giving',
                    {
                        'total_lifetime_giving': data['total_lifetime_giving'],
                        'frequency': data['rfm']['frequency'],
                        'pct_change': trend['pct_change']
                    }
                )
                reasons[constituent_id] = (
                    f"Last three gifts average ${float(trend['last_avg']):,.0f}, up "
                    f"{trend['pct_change']:.1f}% over the prior window."
                )

        return Segment(
            segment_id='increasing_giving',
            name='Increasing Giving Patterns',
            description='Donors showing upward giving trends over their last 6+ contributions',
            reasoning_formula='3-gift rolling average shows > 10% increase',
            constituent_ids=matching_constituents,
            suggested_actions=actions,
            segment_metrics={
                'count': len(matching_constituents),
                'avg_increase': sum(
                    self.get_constituent_data(cid)['trend_analysis']['pct_change']
                    for cid in matching_constituents
                ) / len(matching_constituents) if matching_constituents else 0
            },
            constituent_reasons=reasons
        )

    def segment_declining_giving(self) -> Segment:
        """
        Segment: Declining Giving Patterns

        Identifies donors whose giving has been trending downward.

        Formula: 3-gift rolling trend shows > 10% decrease
        """
        matching_constituents = []
        actions = {}
        reasons = {}

        # Query constituents with at least 6 contributions
        constituents = self.session.query(
            Constituent.constituent_id
        ).join(Contribution).group_by(
            Constituent.constituent_id
        ).having(
            func.count(Contribution.contribution_id) >= 6
        ).all()

        for (constituent_id,) in constituents:
            data = self.get_constituent_data(constituent_id)
            if not data:
                continue
            trend = data.get('trend_analysis')

            if trend and trend['trend'] == 'decreasing':
                matching_constituents.append(constituent_id)
                actions[constituent_id] = generate_action_recommendation(
                    'declining_giving',
                    {
                        'total_lifetime_giving': data['total_lifetime_giving'],
                        'frequency': data['rfm']['frequency'],
                        'pct_change': trend['pct_change']
                    }
                )
                reasons[constituent_id] = (
                    f"Rolling average fell {abs(trend['pct_change']):.1f}% "
                    f"(from ${float(trend['first_avg']):,.0f} to ${float(trend['last_avg']):,.0f})."
                )

        return Segment(
            segment_id='declining_giving',
            name='Declining Giving Patterns',
            description='Donors showing downward giving trends over their last 6+ contributions',
            reasoning_formula='3-gift rolling average shows > 10% decrease',
            constituent_ids=matching_constituents,
            suggested_actions=actions,
            segment_metrics={
                'count': len(matching_constituents),
                'avg_decline': sum(
                    self.get_constituent_data(cid)['trend_analysis']['pct_change']
                    for cid in matching_constituents
                ) / len(matching_constituents) if matching_constituents else 0
            },
            constituent_reasons=reasons
        )

    def segment_no_recent_contact(self, days_threshold: int = 90) -> Segment:
        """
        Segment: No Contact in X Days

        Identifies donors who haven't been contacted in X days.

        Formula: days_since_last_interaction > days_threshold
        """
        matching_constituents = []
        actions = {}
        reasons = {}

        # Get all constituents with contribution history
        constituents = self.session.query(Constituent).filter(
            Constituent.total_lifetime_giving > 0
        ).all()

        for constituent in constituents:
            data = self.get_constituent_data(constituent.constituent_id)
            if not data:
                continue
            days_since = data['days_since_last_interaction']

            if days_since == float('inf') or days_since > days_threshold:
                matching_constituents.append(constituent.constituent_id)
                actions[constituent.constituent_id] = generate_action_recommendation(
                    'no_recent_contact',
                    {
                        'total_lifetime_giving': data['total_lifetime_giving'],
                        'frequency': data['rfm']['frequency'],
                        'days_since_contact': days_since
                    }
                )
                reasons[constituent.constituent_id] = (
                    f"No interaction recorded for {self._format_days(days_since)} "
                    f"despite ${data['total_lifetime_giving']:,.0f} lifetime giving."
                )

        return Segment(
            segment_id=f'no_contact_{days_threshold}_days',
            name=f'No Contact in {days_threshold} Days',
            description=f'Donors who have not been contacted in the last {days_threshold} days',
            reasoning_formula=f'days_since_last_interaction > {days_threshold}',
            constituent_ids=matching_constituents,
            suggested_actions=actions,
            segment_metrics={
                'count': len(matching_constituents),
                'threshold_days': days_threshold,
                'avg_days_since_contact': sum(
                    d if (d := self.get_constituent_data(cid)['days_since_last_interaction']) != float('inf') else 999
                    for cid in matching_constituents
                ) / len(matching_constituents) if matching_constituents else 0
            },
            constituent_reasons=reasons
        )

    def segment_potential_major_donors(self) -> Segment:
        """
        Segment: Potential Major Donors

        Identifies donors with high potential for major gifts based on
        wealth indicators, engagement, and giving trends.

        Formula: capacity_score >= 70 AND engagement_score >= 50 AND
                 (giving_trend = 'increasing' OR total_giving >= $10,000)
        """
        matching_constituents = []
        actions = {}
        reasons = {}

        # Query all constituents
        constituents = self.session.query(Constituent).all()

        for constituent in constituents:
            data = self.get_constituent_data(constituent.constituent_id)
            if not data:
                continue

            capacity = data['capacity_score']
            engagement = data['engagement_score']
            total_giving = data['total_lifetime_giving']
            trend_data = data.get('trend_analysis') or {}
            trend = trend_data.get('trend', 'insufficient_data')

            # High capacity + high engagement + positive indicators
            if (capacity >= 70 and engagement >= 50 and
                (trend == 'increasing' or total_giving >= 10000)):
                matching_constituents.append(constituent.constituent_id)
                actions[constituent.constituent_id] = generate_action_recommendation(
                    'potential_major_donor',
                    {
                        'total_lifetime_giving': total_giving,
                        'frequency': data['rfm']['frequency'],
                        'capacity_score': capacity,
                        'engagement_score': engagement
                    }
                )
                reasons[constituent.constituent_id] = (
                    f"Capacity score {capacity:.0f}, engagement {engagement:.0f}, "
                    f"lifetime giving ${total_giving:,.0f} with trend {trend}."
                )

        return Segment(
            segment_id='potential_major_donors',
            name='Potential Major Donors',
            description='Donors with high capacity, strong engagement, and positive giving trends',
            reasoning_formula='capacity_score >= 70 AND engagement_score >= 50 AND (trend = increasing OR total >= $10K)',
            constituent_ids=matching_constituents,
            suggested_actions=actions,
            segment_metrics={
                'count': len(matching_constituents),
                'avg_capacity': sum(
                    self.get_constituent_data(cid)['capacity_score']
                    for cid in matching_constituents
                ) / len(matching_constituents) if matching_constituents else 0,
                'avg_engagement': sum(
                    self.get_constituent_data(cid)['engagement_score']
                    for cid in matching_constituents
                ) / len(matching_constituents) if matching_constituents else 0,
                'total_potential': sum(
                    self.get_constituent_data(cid)['total_lifetime_giving']
                    for cid in matching_constituents
                )
            },
            constituent_reasons=reasons
        )

    def segment_major_donors_neglected(self) -> Segment:
        """
        Segment: Major Donors Taken For Granted

        Identifies major donors (high lifetime giving or constituent_type = 'Major Donor')
        who haven't been contacted recently.

        Formula: (total_lifetime_giving >= $5,000 OR type = 'Major Donor') AND
                 days_since_last_interaction > 60
        """
        matching_constituents = []
        actions = {}
        reasons = {}

        # Query major donors or high lifetime giving
        constituents = self.session.query(Constituent).filter(
            or_(
                Constituent.total_lifetime_giving >= 5000,
                Constituent.constituent_type == 'Major Donor'
            )
        ).all()

        for constituent in constituents:
            data = self.get_constituent_data(constituent.constituent_id)
            if not data:
                continue
            days_since = data['days_since_last_interaction']

            if days_since == float('inf') or days_since > 60:
                matching_constituents.append(constituent.constituent_id)
                actions[constituent.constituent_id] = generate_action_recommendation(
                    'major_donor_neglected',
                    {
                        'total_lifetime_giving': data['total_lifetime_giving'],
                        'frequency': data['rfm']['frequency'],
                        'days_since_contact': days_since
                    }
                )
                reasons[constituent.constituent_id] = (
                    f"Major supporter (${data['total_lifetime_giving']:,.0f}) with "
                    f"{self._format_days(days_since)} since last interaction."
                )

        return Segment(
            segment_id='major_donors_neglected',
            name='Major Donors Taken For Granted',
            description='Major donors or high lifetime givers who haven\'t been contacted in 60+ days',
            reasoning_formula='(total_lifetime_giving >= $5,000 OR type = Major Donor) AND days_since_interaction > 60',
            constituent_ids=matching_constituents,
            suggested_actions=actions,
            segment_metrics={
                'count': len(matching_constituents),
                'total_lifetime_value': sum(
                    self.get_constituent_data(cid)['total_lifetime_giving']
                    for cid in matching_constituents
                ),
                'avg_days_neglected': sum(
                    d if (d := self.get_constituent_data(cid)['days_since_last_interaction']) != float('inf') else 999
                    for cid in matching_constituents
                ) / len(matching_constituents) if matching_constituents else 0
            },
            constituent_reasons=reasons
        )

    def segment_seasonal_givers(self) -> Segment:
        """
        Segment: Seasonal Givers (with forecast)

        Identifies donors with clear seasonal giving patterns and predicts
        next likely gift dates.

        Formula: seasonal_pattern_strength >= 40% AND preferred_months identified
        """
        matching_constituents = []
        actions = {}
        reasons = {}

        # Query constituents with at least 3 contributions
        constituents = self.session.query(
            Constituent.constituent_id
        ).join(Contribution).group_by(
            Constituent.constituent_id
        ).having(
            func.count(Contribution.contribution_id) >= 3
        ).all()

        for (constituent_id,) in constituents:
            data = self.get_constituent_data(constituent_id)
            if not data:
                continue
            seasonal = data.get('seasonal_analysis')

            if seasonal and seasonal['has_pattern']:
                matching_constituents.append(constituent_id)

                # Customize action with seasonal info
                next_date = seasonal.get('next_likely_gift_date')
                preferred = ', '.join(seasonal['preferred_months'][:2])
                next_date_str = (
                    seasonal.get('next_likely_gift_date').isoformat()
                    if seasonal.get('next_likely_gift_date') else 'during their peak months'
                )

                custom_action = (
                    f"Time outreach to align with their historical giving pattern "
                    f"in {preferred}. "
                    f"{generate_action_recommendation('seasonal_giver', {'total_lifetime_giving': data['total_lifetime_giving'], 'frequency': data['rfm']['frequency']})}"
                )

                actions[constituent_id] = custom_action
                reasons[constituent_id] = (
                    f"Gives predictably around {preferred}; next likely gift {next_date_str}."
                )

        return Segment(
            segment_id='seasonal_givers',
            name='Seasonal Givers with Forecast',
            description='Donors with identifiable seasonal giving patterns and predicted next gift dates',
            reasoning_formula='seasonal_pattern_strength >= 40% AND preferred_months count >= 1',
            constituent_ids=matching_constituents,
            suggested_actions=actions,
            segment_metrics={
                'count': len(matching_constituents),
                'avg_pattern_strength': sum(
                    self.get_constituent_data(cid)['seasonal_analysis']['pattern_strength']
                    for cid in matching_constituents
                ) / len(matching_constituents) if matching_constituents else 0
            },
            constituent_reasons=reasons
        )

    def generate_all_segments(self) -> List[Segment]:
        """
        Generate all donor segments.

        Returns:
            List of all segment objects
        """
        print("🔍 Generating donor segments...")

        segments = [
            self.segment_high_capacity_low_giving(),
            self.segment_increasing_giving(),
            self.segment_declining_giving(),
            self.segment_no_recent_contact(days_threshold=90),
            self.segment_potential_major_donors(),
            self.segment_major_donors_neglected(),
            self.segment_seasonal_givers(),
        ]

        print(f"✓ Generated {len(segments)} segments")
        return segments

    def get_segment_summary(self, segments: List[Segment]) -> Dict[str, Any]:
        """
        Generate summary statistics for all segments.

        Args:
            segments: List of segment objects

        Returns:
            Dictionary with summary statistics
        """
        total_unique_constituents = len(set(
            cid for seg in segments for cid in seg.constituent_ids
        ))

        return {
            'total_segments': len(segments),
            'total_unique_constituents': total_unique_constituents,
            'segment_breakdown': [
                {
                    'segment_id': seg.segment_id,
                    'name': seg.name,
                    'count': len(seg.constituent_ids),
                    'percentage': (len(seg.constituent_ids) / total_unique_constituents * 100)
                    if total_unique_constituents > 0 else 0
                }
                for seg in segments
            ],
            'generated_at': datetime.now().isoformat()
        }
