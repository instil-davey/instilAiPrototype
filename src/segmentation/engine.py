"""
Donor Segmentation Engine

Performs RFM (Recency, Frequency, Monetary) analysis on donor data
to create actionable segments for fundraising strategy.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from sqlalchemy import func, case, and_, or_
from sqlalchemy.orm import Session
from models import Constituent, Contribution, Interaction, Opportunity


class DonorSegmentationEngine:
    """
    Segments donors using RFM analysis and engagement metrics.

    Segments:
    - Champions: High RFM scores, most engaged
    - Loyal: Regular givers with consistent engagement
    - Potential Loyalists: Recent donors with growth potential
    - At Risk: Previously engaged, declining activity
    - Lost: No recent engagement
    - Major Gift Prospects: High capacity, upgrade opportunities
    """

    def __init__(self, db_session: Session):
        self.session = db_session
        self.reference_date = datetime.now()

    def calculate_rfm_scores(self) -> List[Dict[str, Any]]:
        """
        Calculate RFM (Recency, Frequency, Monetary) scores for all donors.

        Returns:
            List of dicts with constituent_id, recency_days, frequency, monetary,
            recency_score, frequency_score, monetary_score, rfm_segment
        """
        # Get contribution data with RFM metrics
        rfm_data = self.session.query(
            Constituent.constituent_id,
            Constituent.first_name,
            Constituent.last_name,
            Constituent.email,
            Constituent.constituent_type,
            Constituent.total_lifetime_giving,
            func.max(Contribution.contribution_date).label('last_contribution_date'),
            func.count(Contribution.contribution_id).label('contribution_count'),
            func.sum(Contribution.amount).label('total_given'),
            func.avg(Contribution.amount).label('average_gift')
        ).outerjoin(
            Contribution, Constituent.constituent_id == Contribution.constituent_id
        ).group_by(
            Constituent.constituent_id
        ).all()

        results = []

        for row in rfm_data:
            # Calculate recency (days since last contribution)
            if row.last_contribution_date:
                recency_days = (self.reference_date.date() - row.last_contribution_date).days
            else:
                recency_days = 9999  # Never contributed

            frequency = row.contribution_count or 0
            monetary = float(row.total_given or 0)
            average_gift = float(row.average_gift or 0)

            # Score recency (1-5, 5 is best - most recent)
            if recency_days <= 90:
                recency_score = 5
            elif recency_days <= 180:
                recency_score = 4
            elif recency_days <= 365:
                recency_score = 3
            elif recency_days <= 730:
                recency_score = 2
            else:
                recency_score = 1

            # Score frequency (1-5, 5 is best - most frequent)
            if frequency >= 10:
                frequency_score = 5
            elif frequency >= 5:
                frequency_score = 4
            elif frequency >= 3:
                frequency_score = 3
            elif frequency >= 2:
                frequency_score = 2
            elif frequency >= 1:
                frequency_score = 1
            else:
                frequency_score = 0

            # Score monetary (1-5, 5 is best - highest value)
            if monetary >= 10000:
                monetary_score = 5
            elif monetary >= 5000:
                monetary_score = 4
            elif monetary >= 1000:
                monetary_score = 3
            elif monetary >= 500:
                monetary_score = 2
            elif monetary > 0:
                monetary_score = 1
            else:
                monetary_score = 0

            # Determine segment
            rfm_segment = self._determine_segment(
                recency_score, frequency_score, monetary_score
            )

            results.append({
                'constituent_id': row.constituent_id,
                'first_name': row.first_name,
                'last_name': row.last_name,
                'email': row.email,
                'constituent_type': row.constituent_type,
                'recency_days': recency_days,
                'frequency': frequency,
                'monetary': monetary,
                'average_gift': average_gift,
                'recency_score': recency_score,
                'frequency_score': frequency_score,
                'monetary_score': monetary_score,
                'rfm_score': f"{recency_score}{frequency_score}{monetary_score}",
                'segment': rfm_segment
            })

        return results

    def _determine_segment(self, r: int, f: int, m: int) -> str:
        """Determine donor segment based on RFM scores."""
        # Champions: High across the board
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"

        # Loyal: Regular givers, even if not highest monetary
        if r >= 3 and f >= 4:
            return "Loyal"

        # Potential Loyalists: Recent donors with potential
        if r >= 4 and f >= 2 and f <= 3:
            return "Potential Loyalists"

        # Major Gift Prospects: High monetary, room for engagement
        if m >= 4 and (r >= 3 or f >= 2):
            return "Major Gift Prospects"

        # At Risk: Previously engaged but declining
        if r <= 2 and f >= 3:
            return "At Risk"

        # Need Attention: Low recency, some history
        if r <= 2 and f >= 2 and m >= 2:
            return "Need Attention"

        # Lost: No recent engagement
        if r == 1:
            return "Lost"

        # New/Promising: Recent but limited history
        if r >= 4 and f <= 2 and m <= 2:
            return "New/Promising"

        # Hibernating: Long time since engagement
        if r <= 2 and f <= 2:
            return "Hibernating"

        # Default
        return "Casual"

    def get_engagement_metrics(self) -> List[Dict[str, Any]]:
        """
        Calculate engagement metrics for all constituents.

        Returns:
            List of dicts with constituent_id, interaction_count,
            last_interaction_date, engagement_score
        """
        engagement_data = self.session.query(
            Constituent.constituent_id,
            func.count(Interaction.interaction_id).label('interaction_count'),
            func.max(Interaction.interaction_date).label('last_interaction_date'),
            func.sum(
                case(
                    (Interaction.interaction_type == 'Phone Call', 2),
                    (Interaction.interaction_type == 'In-Person Meeting', 3),
                    (Interaction.interaction_type == 'Email', 1),
                    else_=1
                )
            ).label('weighted_interactions')
        ).outerjoin(
            Interaction, Constituent.constituent_id == Interaction.constituent_id
        ).group_by(
            Constituent.constituent_id
        ).all()

        results = []

        for row in engagement_data:
            interaction_count = row.interaction_count or 0
            weighted = row.weighted_interactions or 0

            # Calculate days since last interaction
            if row.last_interaction_date:
                days_since = (self.reference_date.date() - row.last_interaction_date).days
            else:
                days_since = 9999

            # Calculate engagement score (0-100)
            # Based on: interaction count, recency, and weighted interactions
            recency_factor = max(0, 100 - (days_since / 3.65))  # Decay over ~1 year
            frequency_factor = min(100, interaction_count * 10)
            weighted_factor = min(100, weighted * 5)

            engagement_score = int(
                (recency_factor * 0.4) +
                (frequency_factor * 0.3) +
                (weighted_factor * 0.3)
            )

            results.append({
                'constituent_id': row.constituent_id,
                'interaction_count': interaction_count,
                'last_interaction_date': row.last_interaction_date,
                'days_since_interaction': days_since,
                'engagement_score': engagement_score,
                'engagement_level': self._categorize_engagement(engagement_score)
            })

        return results

    def _categorize_engagement(self, score: int) -> str:
        """Categorize engagement level based on score."""
        if score >= 80:
            return "Highly Engaged"
        elif score >= 60:
            return "Engaged"
        elif score >= 40:
            return "Moderately Engaged"
        elif score >= 20:
            return "Low Engagement"
        else:
            return "Disengaged"

    def get_opportunity_pipeline(self) -> List[Dict[str, Any]]:
        """
        Get opportunity pipeline analysis.

        Returns:
            List of dicts with constituent_id, opportunity_count,
            total_pipeline_value, probability_weighted_value
        """
        pipeline_data = self.session.query(
            Constituent.constituent_id,
            func.count(Opportunity.opportunity_id).label('opportunity_count'),
            func.sum(Opportunity.expected_amount).label('total_pipeline_value'),
            func.sum(
                Opportunity.expected_amount * Opportunity.probability / 100
            ).label('probability_weighted_value'),
            func.max(Opportunity.probability).label('max_probability')
        ).outerjoin(
            Opportunity, Constituent.constituent_id == Opportunity.constituent_id
        ).group_by(
            Constituent.constituent_id
        ).all()

        results = []

        for row in pipeline_data:
            results.append({
                'constituent_id': row.constituent_id,
                'opportunity_count': row.opportunity_count or 0,
                'total_pipeline_value': float(row.total_pipeline_value or 0),
                'probability_weighted_value': float(row.probability_weighted_value or 0),
                'max_probability': row.max_probability or 0
            })

        return results

    def generate_complete_segments(self) -> Dict[str, Any]:
        """
        Generate complete segmentation analysis combining RFM,
        engagement, and opportunity data.

        Returns:
            Dict with:
            - segments: List of all constituents with complete segmentation data
            - segment_summary: Count and metrics by segment
            - insights: Key findings from segmentation
        """
        # Get all three analyses
        rfm_data = self.calculate_rfm_scores()
        engagement_data = self.get_engagement_metrics()
        pipeline_data = self.get_opportunity_pipeline()

        # Create lookup dictionaries
        engagement_lookup = {e['constituent_id']: e for e in engagement_data}
        pipeline_lookup = {p['constituent_id']: p for p in pipeline_data}

        # Merge data
        segments = []
        for rfm in rfm_data:
            constituent_id = rfm['constituent_id']
            engagement = engagement_lookup.get(constituent_id, {})
            pipeline = pipeline_lookup.get(constituent_id, {})

            merged = {
                **rfm,
                'engagement_score': engagement.get('engagement_score', 0),
                'engagement_level': engagement.get('engagement_level', 'Disengaged'),
                'interaction_count': engagement.get('interaction_count', 0),
                'opportunity_count': pipeline.get('opportunity_count', 0),
                'pipeline_value': pipeline.get('total_pipeline_value', 0),
                'weighted_pipeline_value': pipeline.get('probability_weighted_value', 0)
            }

            segments.append(merged)

        # Generate segment summary
        segment_summary = self._summarize_segments(segments)

        # Generate insights
        insights = self._generate_segment_insights(segments, segment_summary)

        return {
            'segments': segments,
            'segment_summary': segment_summary,
            'insights': insights,
            'total_constituents': len(segments),
            'analysis_date': self.reference_date.isoformat()
        }

    def _summarize_segments(self, segments: List[Dict]) -> Dict[str, Any]:
        """Create summary statistics by segment."""
        summary = {}

        for segment in segments:
            seg_name = segment['segment']

            if seg_name not in summary:
                summary[seg_name] = {
                    'count': 0,
                    'total_monetary': 0,
                    'total_pipeline': 0,
                    'avg_engagement': 0,
                    'avg_frequency': 0
                }

            summary[seg_name]['count'] += 1
            summary[seg_name]['total_monetary'] += segment['monetary']
            summary[seg_name]['total_pipeline'] += segment['pipeline_value']
            summary[seg_name]['avg_engagement'] += segment['engagement_score']
            summary[seg_name]['avg_frequency'] += segment['frequency']

        # Calculate averages
        for seg_name in summary:
            count = summary[seg_name]['count']
            summary[seg_name]['avg_engagement'] = round(
                summary[seg_name]['avg_engagement'] / count, 1
            )
            summary[seg_name]['avg_frequency'] = round(
                summary[seg_name]['avg_frequency'] / count, 1
            )
            summary[seg_name]['avg_monetary'] = round(
                summary[seg_name]['total_monetary'] / count, 2
            )

        return summary

    def _generate_segment_insights(
        self,
        segments: List[Dict],
        summary: Dict[str, Any]
    ) -> List[str]:
        """Generate key insights from segmentation data."""
        insights = []

        # Identify largest segments
        sorted_segments = sorted(
            summary.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        if sorted_segments:
            largest = sorted_segments[0]
            insights.append(
                f"Largest segment is '{largest[0]}' with {largest[1]['count']} constituents"
            )

        # Identify at-risk donors
        at_risk_count = sum(
            1 for s in segments
            if s['segment'] in ['At Risk', 'Need Attention', 'Lost']
        )
        if at_risk_count > 0:
            pct = round(at_risk_count / len(segments) * 100, 1)
            insights.append(
                f"{at_risk_count} constituents ({pct}%) are at risk or lost"
            )

        # Identify high-value opportunities
        champions_count = sum(1 for s in segments if s['segment'] == 'Champions')
        if champions_count > 0:
            insights.append(
                f"{champions_count} Champions represent your most valuable donors"
            )

        # Pipeline opportunities
        total_pipeline = sum(s['pipeline_value'] for s in segments)
        if total_pipeline > 0:
            insights.append(
                f"Total opportunity pipeline: ${total_pipeline:,.2f}"
            )

        return insights


def create_segmentation_engine(db_session: Session) -> DonorSegmentationEngine:
    """Factory function to create a segmentation engine instance."""
    return DonorSegmentationEngine(db_session)
