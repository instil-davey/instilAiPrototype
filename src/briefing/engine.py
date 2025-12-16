"""
AI-Powered Constituent Briefing Engine

This module generates comprehensive, AI-powered briefings for nonprofit constituents
by analyzing their contributions, interactions, opportunities, and segment membership.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

# Import models from parent directory
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from models import Constituent, Contribution, Interaction, Opportunity


load_dotenv()


class BriefingEngine:
    """
    Core engine for generating AI-powered constituent briefings.

    Uses Claude AI to analyze constituent data and generate personalized insights
    including giving summaries, engagement patterns, and recommended actions.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the briefing engine with Anthropic API credentials.

        Args:
            api_key: Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.model = "claude-sonnet-4-5-20250929"  # Latest Claude model

    def generate_briefing(
        self,
        constituent_id: str,
        db_session: Session,
        segment_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive AI-powered briefing for a constituent.

        Args:
            constituent_id: Unique identifier for the constituent
            db_session: SQLAlchemy database session
            segment_names: Optional list of segment names the constituent belongs to

        Returns:
            Dictionary containing:
                - summary: Who they are (paragraph)
                - giving_summary: Overview of their giving history
                - engagement_pattern: Analysis of their interaction patterns
                - why_they_matter: Strategic importance to the organization
                - segment_reason: Why they're in their current segment(s)
                - suggested_action: Personalized next step recommendation
                - metadata: Additional context (generated_at, constituent_id, etc.)

        Raises:
            ValueError: If constituent not found
        """
        # Gather all constituent data
        data = self._gather_constituent_data(constituent_id, db_session, segment_names)

        if not data['constituent']:
            raise ValueError(f"Constituent with ID '{constituent_id}' not found")

        # Generate AI-powered insights
        briefing = self._generate_ai_briefing(data)

        # Add metadata
        briefing['metadata'] = {
            'constituent_id': constituent_id,
            'generated_at': datetime.utcnow().isoformat(),
            'data_points': {
                'contributions': len(data['contributions']),
                'interactions': len(data['interactions']),
                'opportunities': len(data['opportunities']),
                'transactions': len(data['transactions']),
                'segments': len(segment_names) if segment_names else 0
            }
        }

        return briefing

    def _gather_constituent_data(
        self,
        constituent_id: str,
        db_session: Session,
        segment_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Gather all relevant data for a constituent from the database.

        Args:
            constituent_id: Unique identifier for the constituent
            db_session: SQLAlchemy database session
            segment_names: Optional list of segment names

        Returns:
            Dictionary containing constituent and all related records
        """
        # Fetch constituent
        constituent = db_session.query(Constituent).filter(
            Constituent.constituent_id == constituent_id
        ).first()

        if not constituent:
            return {'constituent': None}

        # Fetch contributions (sorted by date, most recent first)
        contributions = db_session.query(Contribution).filter(
            Contribution.constituent_id == constituent_id
        ).order_by(desc(Contribution.contribution_date)).all()

        # Fetch interactions (sorted by date, most recent first)
        interactions = db_session.query(Interaction).filter(
            Interaction.constituent_id == constituent_id
        ).order_by(desc(Interaction.interaction_date)).all()

        # Fetch opportunities (sorted by expected close date)
        opportunities = db_session.query(Opportunity).filter(
            Opportunity.constituent_id == constituent_id
        ).order_by(desc(Opportunity.expected_close_date)).all()

        # Transactions not yet implemented
        transactions = []

        return {
            'constituent': constituent,
            'contributions': contributions,
            'interactions': interactions,
            'opportunities': opportunities,
            'transactions': transactions,
            'segments': segment_names or []
        }

    def _generate_ai_briefing(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Use Claude AI to generate intelligent briefing insights.

        Args:
            data: Dictionary containing constituent and related data

        Returns:
            Dictionary with AI-generated briefing fields
        """
        # Prepare structured data for AI analysis
        context = self._prepare_context_for_ai(data)

        # If AI client unavailable, immediately use fallback briefing
        if not self.client:
            return self._generate_fallback_briefing(data)

        # Create the prompt for Claude
        prompt = self._create_briefing_prompt(context)

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse the response
            ai_response = response.content[0].text
            briefing = self._parse_ai_response(ai_response)

            return briefing

        except Exception:
            # Fallback to basic briefing if AI fails
            return self._generate_fallback_briefing(data)

    def _prepare_context_for_ai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare constituent data in a structured format for AI analysis.

        Args:
            data: Raw data from database

        Returns:
            Structured context dictionary optimized for AI analysis
        """
        constituent = data['constituent']
        contributions = data['contributions']
        interactions = data['interactions']
        opportunities = data['opportunities']
        transactions = data['transactions']
        segments = data['segments']

        # Basic constituent info
        context = {
            'name': constituent.full_name,
            'type': constituent.constituent_type,
            'email': constituent.email,
            'phone': constituent.phone,
            'location': f"{constituent.city}, {constituent.state}" if constituent.city else None,
            'lifetime_giving': float(constituent.total_lifetime_giving) if constituent.total_lifetime_giving else 0,
            'member_since': constituent.created_date.isoformat() if constituent.created_date else None,
        }

        # Giving history
        if contributions:
            total_contributions = sum(float(c.amount) for c in contributions)
            context['giving_history'] = {
                'total_gifts': len(contributions),
                'total_amount': total_contributions,
                'average_gift': total_contributions / len(contributions),
                'largest_gift': float(max(c.amount for c in contributions)),
                'most_recent_gift': {
                    'date': contributions[0].contribution_date.isoformat(),
                    'amount': float(contributions[0].amount),
                    'type': contributions[0].contribution_type
                },
                'first_gift': {
                    'date': contributions[-1].contribution_date.isoformat(),
                    'amount': float(contributions[-1].amount)
                },
                'gifts_by_type': self._count_by_field(contributions, 'contribution_type'),
                'campaigns': self._count_by_field(contributions, 'campaign'),
                'recent_gifts': [
                    {
                        'date': c.contribution_date.isoformat(),
                        'amount': float(c.amount),
                        'type': c.contribution_type,
                        'campaign': c.campaign
                    }
                    for c in contributions[:5]  # Last 5 gifts
                ]
            }
        else:
            context['giving_history'] = None

        # Interaction history
        if interactions:
            context['interaction_history'] = {
                'total_interactions': len(interactions),
                'types': self._count_by_field(interactions, 'interaction_type'),
                'most_recent': {
                    'date': interactions[0].interaction_date.isoformat(),
                    'type': interactions[0].interaction_type,
                    'subject': interactions[0].subject,
                    'notes': interactions[0].notes
                },
                'follow_ups_needed': sum(
                    1 for i in interactions if getattr(i, 'follow_up_required', '') == 'Yes'
                ),
                'recent_interactions': [
                    {
                        'date': i.interaction_date.isoformat(),
                        'type': i.interaction_type,
                        'subject': i.subject,
                        'staff': getattr(i, 'staff_member', None)
                    }
                    for i in interactions[:5]  # Last 5 interactions
                ]
            }
        else:
            context['interaction_history'] = None

        # Opportunities
        if opportunities:
            context['opportunities'] = {
                'total_opportunities': len(opportunities),
                'stages': self._count_by_field(opportunities, 'stage'),
                'total_expected_amount': sum(float(o.amount) for o in opportunities if o.amount),
                'total_weighted_amount': sum(float(o.weighted_amount) for o in opportunities if o.weighted_amount),
                'active_opportunities': [
                    {
                        'name': o.opportunity_name,
                        'stage': o.stage,
                        'amount': float(o.amount) if o.amount else 0,
                        'probability': o.probability,
                        'close_date': o.expected_close_date.isoformat() if o.expected_close_date else None
                    }
                    for o in opportunities
                ]
            }
        else:
            context['opportunities'] = None

        # Transaction history
        if transactions:
            context['transaction_history'] = {
                'total_transactions': len(transactions),
                'types': self._count_by_field(transactions, 'transaction_type'),
                'statuses': self._count_by_field(transactions, 'status'),
                'payment_methods': self._count_by_field(transactions, 'payment_processor')
            }
        else:
            context['transaction_history'] = None

        # Segments
        context['segments'] = segments

        return context

    def _count_by_field(self, records: List[Any], field_name: str) -> Dict[str, int]:
        """
        Count occurrences of values in a field across a list of records.

        Args:
            records: List of ORM objects
            field_name: Name of the field to count

        Returns:
            Dictionary with value: count pairs
        """
        counts = {}
        for record in records:
            value = getattr(record, field_name, None)
            if value:
                counts[value] = counts.get(value, 0) + 1
        return counts

    def _create_briefing_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for Claude to generate the briefing.

        Args:
            context: Structured constituent data

        Returns:
            Formatted prompt string
        """
        import json

        prompt = f"""You are a nonprofit development officer's AI assistant. Generate a comprehensive constituent briefing based on the following data.

CONSTITUENT DATA:
{json.dumps(context, indent=2, default=str)}

Generate a briefing with the following sections. Return your response in this EXACT format, with each section clearly labeled:

[SUMMARY]
(Write a 2-3 sentence paragraph describing who this constituent is, their relationship with the organization, and their overall profile. Be personable and insightful.)

[GIVING_SUMMARY]
(Provide a clear summary of their giving history, including total amounts, frequency, preferences, and trends. Mention specific numbers and patterns.)

[ENGAGEMENT_PATTERN]
(Analyze their interaction patterns, communication preferences, and level of engagement. Identify trends in how they engage with the organization.)

[WHY_THEY_MATTER]
(Explain the strategic importance of this constituent to the organization. Consider their giving capacity, influence, engagement level, and potential.)

[SEGMENT_REASON]
(Explain why this constituent is categorized in their segment(s): {', '.join(context['segments']) if context['segments'] else 'No segments assigned'}. If no segments, suggest appropriate segments based on their profile.)

[SUGGESTED_ACTION]
(Provide ONE specific, actionable next step that a development officer should take with this constituent. Be concrete and time-specific.)

IMPORTANT:
- Be concise but insightful
- Use specific data points from the constituent's record
- Write in a professional but warm tone
- Focus on actionable insights
- Each section should be 2-4 sentences maximum (except summary which can be 2-3 sentences)
"""

        return prompt

    def _parse_ai_response(self, ai_response: str) -> Dict[str, str]:
        """
        Parse Claude's response into structured briefing fields.

        Args:
            ai_response: Raw text response from Claude

        Returns:
            Dictionary with parsed briefing sections
        """
        sections = {
            'summary': '',
            'giving_summary': '',
            'engagement_pattern': '',
            'why_they_matter': '',
            'segment_reason': '',
            'suggested_action': ''
        }

        # Parse sections using markers
        markers = {
            '[SUMMARY]': 'summary',
            '[GIVING_SUMMARY]': 'giving_summary',
            '[ENGAGEMENT_PATTERN]': 'engagement_pattern',
            '[WHY_THEY_MATTER]': 'why_they_matter',
            '[SEGMENT_REASON]': 'segment_reason',
            '[SUGGESTED_ACTION]': 'suggested_action'
        }

        current_section = None
        lines = []

        for line in ai_response.split('\n'):
            line = line.strip()

            # Check if this line is a section marker
            if line in markers:
                # Save previous section
                if current_section and lines:
                    sections[current_section] = '\n'.join(lines).strip()
                    lines = []

                # Start new section
                current_section = markers[line]
            elif current_section and line:
                lines.append(line)

        # Save last section
        if current_section and lines:
            sections[current_section] = '\n'.join(lines).strip()

        return sections

    def _generate_fallback_briefing(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a basic briefing without AI when API call fails.

        Args:
            data: Raw constituent data

        Returns:
            Dictionary with basic briefing sections
        """
        constituent = data['constituent']
        contributions = data['contributions']
        interactions = data['interactions']
        opportunities = data['opportunities']
        segments = data['segments']

        # Basic summary
        summary = f"{constituent.full_name} is a {constituent.constituent_type.lower()} "
        if constituent.total_lifetime_giving and constituent.total_lifetime_giving > 0:
            summary += f"who has contributed ${float(constituent.total_lifetime_giving):,.2f} to the organization."
        else:
            summary += "with engagement history in the organization."

        # Giving summary
        if contributions:
            total = sum(float(c.amount) for c in contributions)
            avg = total / len(contributions)
            giving_summary = f"Total giving: ${total:,.2f} across {len(contributions)} gift(s). Average gift size: ${avg:,.2f}."
        else:
            giving_summary = "No contribution history on record."

        # Engagement pattern
        if interactions:
            types = self._count_by_field(interactions, 'interaction_type')
            most_common = max(types.items(), key=lambda x: x[1])[0] if types else "Unknown"
            engagement_pattern = f"Has {len(interactions)} recorded interaction(s), primarily through {most_common}."
        else:
            engagement_pattern = "Limited interaction history on record."

        # Why they matter
        if constituent.total_lifetime_giving and float(constituent.total_lifetime_giving) >= 10000:
            why_they_matter = "Major donor with significant giving capacity and demonstrated commitment."
        elif opportunities:
            why_they_matter = f"Active prospect with {len(opportunities)} open opportunity(ies)."
        elif interactions and len(interactions) > 5:
            why_they_matter = "Highly engaged constituent with strong connection to the organization."
        else:
            why_they_matter = "Valued member of the organization's community."

        # Segment reason
        if segments:
            segment_reason = f"Classified in segment(s): {', '.join(segments)} based on giving history and engagement patterns."
        else:
            segment_reason = "Not currently assigned to any segments. Consider segmentation based on engagement level."

        # Suggested action
        if interactions and getattr(interactions[0], 'follow_up_required', '') == 'Yes':
            suggested_action = "Complete pending follow-up from most recent interaction."
        elif opportunities and any(o.stage in ['Cultivation', 'Proposal'] for o in opportunities):
            suggested_action = "Advance active opportunity through the pipeline."
        elif contributions and (datetime.now().date() - contributions[0].contribution_date).days > 365:
            suggested_action = "Re-engage donor with personalized outreach; last gift was over one year ago."
        else:
            suggested_action = "Schedule a thank you call or meeting to strengthen the relationship."

        return {
            'summary': summary,
            'giving_summary': giving_summary,
            'engagement_pattern': engagement_pattern,
            'why_they_matter': why_they_matter,
            'segment_reason': segment_reason,
            'suggested_action': suggested_action
        }
