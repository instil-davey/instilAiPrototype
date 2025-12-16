"""
Suggested Action Generator for Nonprofit Fundraisers
Generates AI-powered, personalized action recommendations for constituent engagement
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import anthropic
from sqlalchemy.orm import Session
from models import Constituent, Contribution, Interaction, Opportunity
from segments import SegmentType, get_constituent_segment, get_segment_info


class SuggestedActionGenerator:
    """
    Generates personalized fundraising action recommendations using Claude AI.

    Recommendations are:
    - Specific: Clear, actionable steps
    - Time-bound: Include specific timeframes
    - Stewardship-oriented: Focus on relationship building
    - Donor-centric: Prioritize donor experience over transactions
    - Non-generic: Tailored to individual constituent context
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the generator with Claude AI client.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def generate_suggested_action(
        self,
        session: Session,
        constituent_id: int,
        segment_id: Optional[str] = None
    ) -> Dict:
        """
        Generate a personalized action recommendation for a constituent.

        Args:
            session: Database session
            constituent_id: ID of the constituent
            segment_id: Optional specific segment to focus on

        Returns:
            Dictionary with suggested action and metadata
        """
        # Get constituent data
        constituent = session.query(Constituent).filter_by(
            constituent_id=constituent_id
        ).first()

        if not constituent:
            return {
                "success": False,
                "error": f"Constituent {constituent_id} not found"
            }

        # Get constituent segments
        segments = get_constituent_segment(session, constituent_id)

        # If specific segment provided, use it; otherwise use primary segment
        target_segment = None
        if segment_id:
            try:
                target_segment = SegmentType(segment_id)
                if target_segment not in segments:
                    # Still allow it but note in response
                    pass
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid segment_id: {segment_id}"
                }
        else:
            # Use highest priority segment
            target_segment = segments[0] if segments else None

        # Gather constituent history
        giving_history = self._get_giving_history(session, constituent_id)
        engagement_history = self._get_engagement_history(session, constituent_id)
        opportunity_data = self._get_opportunity_data(session, constituent_id)

        # Build context for AI
        context = self._build_context(
            constituent=constituent,
            segments=segments,
            target_segment=target_segment,
            giving_history=giving_history,
            engagement_history=engagement_history,
            opportunity_data=opportunity_data
        )

        # Generate action using Claude
        suggested_action = self._generate_action_with_ai(context, target_segment)

        return {
            "success": True,
            "constituent_id": constituent_id,
            "constituent_name": constituent.full_name,
            "segments": [s.value for s in segments],
            "target_segment": target_segment.value if target_segment else None,
            "suggested_action": suggested_action,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _get_giving_history(self, session: Session, constituent_id: int) -> Dict:
        """Get giving history summary for the constituent."""
        contributions = session.query(Contribution).filter(
            Contribution.constituent_id == constituent_id
        ).order_by(Contribution.contribution_date.desc()).limit(10).all()

        total_contributions = session.query(Contribution).filter(
            Contribution.constituent_id == constituent_id
        ).count()

        # Calculate recency, frequency, monetary
        latest_gift = contributions[0] if contributions else None
        days_since_last_gift = None
        if latest_gift:
            days_since_last_gift = (datetime.now().date() - latest_gift.contribution_date).days

        # Recent giving (last 12 months)
        recent_date = datetime.now().date() - timedelta(days=365)
        recent_contributions = session.query(Contribution).filter(
            Contribution.constituent_id == constituent_id,
            Contribution.contribution_date >= recent_date
        ).all()

        recent_total = sum((c.amount or Decimal('0')) for c in recent_contributions)
        recent_count = len(recent_contributions)

        # Average gift
        all_amounts = [c.amount for c in contributions if c.amount]
        avg_gift = sum(all_amounts) / len(all_amounts) if all_amounts else Decimal('0')

        return {
            "total_contributions": total_contributions,
            "days_since_last_gift": days_since_last_gift,
            "recent_count_12mo": recent_count,
            "recent_total_12mo": float(recent_total),
            "average_gift": float(avg_gift),
            "latest_gift_date": latest_gift.contribution_date.isoformat() if latest_gift else None,
            "latest_gift_amount": float(latest_gift.amount) if latest_gift and latest_gift.amount else None,
            "campaign_history": list(set([c.campaign_id for c in contributions if c.campaign_id]))
        }

    def _get_engagement_history(self, session: Session, constituent_id: int) -> Dict:
        """Get engagement/interaction history for the constituent."""
        interactions = session.query(Interaction).filter(
            Interaction.constituent_id == constituent_id
        ).order_by(Interaction.interaction_date.desc()).limit(10).all()

        total_interactions = session.query(Interaction).filter(
            Interaction.constituent_id == constituent_id
        ).count()

        # Recent interactions (last 6 months)
        recent_date = datetime.now().date() - timedelta(days=180)
        recent_interactions = session.query(Interaction).filter(
            Interaction.constituent_id == constituent_id,
            Interaction.interaction_date >= recent_date
        ).all()

        # Days since last interaction
        latest_interaction = interactions[0] if interactions else None
        days_since_last_interaction = None
        if latest_interaction:
            days_since_last_interaction = (datetime.now().date() - latest_interaction.interaction_date).days

        # Interaction types
        interaction_types = {}
        for interaction in recent_interactions:
            interaction_types[interaction.interaction_type] = interaction_types.get(interaction.interaction_type, 0) + 1

        return {
            "total_interactions": total_interactions,
            "recent_count_6mo": len(recent_interactions),
            "days_since_last_interaction": days_since_last_interaction,
            "latest_interaction_type": latest_interaction.interaction_type if latest_interaction else None,
            "latest_interaction_date": latest_interaction.interaction_date.isoformat() if latest_interaction else None,
            "interaction_types": interaction_types,
            "follow_up_required": any(i.follow_up_required == 'Yes' for i in interactions)
        }

    def _get_opportunity_data(self, session: Session, constituent_id: int) -> Dict:
        """Get fundraising opportunity data for the constituent."""
        opportunities = session.query(Opportunity).filter(
            Opportunity.constituent_id == constituent_id
        ).all()

        active_opportunities = [o for o in opportunities if o.stage not in ['Closed Won', 'Closed Lost']]

        total_pipeline = sum((o.expected_amount or Decimal('0')) for o in active_opportunities)

        return {
            "total_opportunities": len(opportunities),
            "active_opportunities": len(active_opportunities),
            "total_pipeline_value": float(total_pipeline),
            "opportunity_stages": [o.stage for o in active_opportunities]
        }

    def _build_context(
        self,
        constituent: Constituent,
        segments: List[SegmentType],
        target_segment: Optional[SegmentType],
        giving_history: Dict,
        engagement_history: Dict,
        opportunity_data: Dict
    ) -> str:
        """Build context string for AI prompt."""
        segment_names = [get_segment_info(s)["name"] for s in segments]
        target_segment_info = get_segment_info(target_segment) if target_segment else None

        context = f"""CONSTITUENT PROFILE:
Name: {constituent.full_name}
Type: {constituent.constituent_type}
Lifetime Giving: ${constituent.total_lifetime_giving or 0:,.2f}
Location: {constituent.city}, {constituent.state}

SEGMENTS:
Primary Segments: {', '.join(segment_names) if segment_names else 'None'}
Target Segment: {target_segment_info['name'] if target_segment_info else 'General'}
Segment Description: {target_segment_info['description'] if target_segment_info else 'N/A'}

GIVING HISTORY:
- Total Contributions: {giving_history['total_contributions']}
- Days Since Last Gift: {giving_history['days_since_last_gift'] or 'Never'}
- Recent Contributions (12mo): {giving_history['recent_count_12mo']} gifts totaling ${giving_history['recent_total_12mo']:,.2f}
- Average Gift: ${giving_history['average_gift']:,.2f}
- Latest Gift: ${giving_history['latest_gift_amount'] or 0} on {giving_history['latest_gift_date'] or 'N/A'}
- Campaign History: {', '.join(giving_history['campaign_history']) if giving_history['campaign_history'] else 'None'}

ENGAGEMENT HISTORY:
- Total Interactions: {engagement_history['total_interactions']}
- Recent Interactions (6mo): {engagement_history['recent_count_6mo']}
- Days Since Last Interaction: {engagement_history['days_since_last_interaction'] or 'Never'}
- Latest Interaction: {engagement_history['latest_interaction_type']} on {engagement_history['latest_interaction_date'] or 'N/A'}
- Interaction Types: {engagement_history['interaction_types']}
- Follow-up Required: {engagement_history['follow_up_required']}

PIPELINE:
- Active Opportunities: {opportunity_data['active_opportunities']}
- Total Pipeline Value: ${opportunity_data['total_pipeline_value']:,.2f}
- Opportunity Stages: {', '.join(opportunity_data['opportunity_stages']) if opportunity_data['opportunity_stages'] else 'None'}
"""
        return context

    def _generate_action_with_ai(self, context: str, segment: Optional[SegmentType]) -> str:
        """Generate action recommendation using Claude AI."""

        prompt = f"""You are an expert nonprofit fundraiser and donor relationship manager. Based on the constituent data below, generate ONE specific, actionable recommendation for a fundraiser to take.

{context}

REQUIREMENTS for the suggested action:
1. SPECIFIC: Include exact steps, not vague suggestions
2. TIME-BOUND: Specify when this should be done (e.g., "within 2 weeks", "by next Friday")
3. STEWARDSHIP-ORIENTED: Focus on building relationships, not just asking for money
4. DONOR-CENTRIC: Prioritize what benefits/interests the donor
5. AVOID GENERIC PHRASES: No "reach out", "touch base", "circle back", etc.

AVOID:
- Generic suggestions like "send a thank you note"
- Transactional asks without relationship context
- Vague timelines like "soon" or "follow up"
- One-size-fits-all recommendations

STRUCTURE your response as:
Action: [One clear sentence with specific action]
Timing: [Specific timeframe]
Why: [Brief rationale based on donor data]
Key Points: [2-3 bullet points with talking points or specifics]

Generate the suggested action now:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text.strip()

        except Exception as e:
            return f"Error generating action: {str(e)}"


def generate_suggested_action(
    session: Session,
    constituent_id: int,
    segment_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict:
    """
    Convenience function to generate a suggested action.

    Args:
        session: Database session
        constituent_id: ID of the constituent
        segment_id: Optional specific segment to focus on
        api_key: Optional Anthropic API key

    Returns:
        Dictionary with suggested action and metadata
    """
    generator = SuggestedActionGenerator(api_key=api_key)
    return generator.generate_suggested_action(session, constituent_id, segment_id)
