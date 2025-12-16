"""
AI Prompt Templates for Donor Insights Generation

These prompts guide Claude 3.5 Sonnet to generate actionable insights
from donor segmentation and database analysis.
"""

from typing import Dict, Any


SYSTEM_PROMPT = """You are an expert nonprofit fundraising strategist and data analyst specializing in donor relationship management. Your role is to analyze donor data and generate actionable, strategic insights that help nonprofit organizations optimize their fundraising efforts.

When analyzing data, focus on:
1. Identifying trends and patterns in giving behavior
2. Spotting risks to donor retention and engagement
3. Finding opportunities for donor upgrades and major gifts
4. Providing specific, actionable recommendations
5. Quantifying impact wherever possible

Your insights should be:
- Strategic: Tied to fundraising goals and donor lifetime value
- Actionable: Include specific next steps
- Data-driven: Based on the provided metrics and segments
- Practical: Implementable by a small to mid-sized nonprofit team
- Impact-focused: Clearly state expected outcomes"""


def generate_insights_prompt(
    segment_data: Dict[str, Any],
    database_summary: Dict[str, Any]
) -> str:
    """
    Generate the main prompt for Claude to analyze donor data and create insights.

    Args:
        segment_data: Output from DonorSegmentationEngine.generate_complete_segments()
        database_summary: Summary statistics from the database

    Returns:
        Formatted prompt string
    """
    segments = segment_data.get('segments', [])
    segment_summary = segment_data.get('segment_summary', {})
    total_constituents = segment_data.get('total_constituents', 0)

    # Calculate key metrics
    total_giving = sum(s['monetary'] for s in segments)
    total_pipeline = sum(s['pipeline_value'] for s in segments)
    avg_engagement = sum(s['engagement_score'] for s in segments) / len(segments) if segments else 0

    # Count constituents by segment
    segment_counts = {}
    for s in segments:
        seg_name = s['segment']
        segment_counts[seg_name] = segment_counts.get(seg_name, 0) + 1

    # Identify top donors
    top_donors = sorted(segments, key=lambda x: x['monetary'], reverse=True)[:5]

    # Identify at-risk donors
    at_risk_segments = ['At Risk', 'Need Attention', 'Lost', 'Hibernating']
    at_risk_donors = [s for s in segments if s['segment'] in at_risk_segments]

    # Format the prompt
    prompt = f"""Please analyze the following nonprofit donor database and generate 4-6 strategic insights for the development team.

## DATABASE OVERVIEW

**Total Constituents:** {total_constituents}
**Total Lifetime Giving:** ${total_giving:,.2f}
**Total Opportunity Pipeline:** ${total_pipeline:,.2f}
**Average Engagement Score:** {avg_engagement:.1f}/100

**Contributions Summary:**
- Total Contributions: {database_summary.get('total_contributions', 0)}
- Total Amount: ${database_summary.get('total_contribution_amount', 0):,.2f}
- Average Gift: ${database_summary.get('average_gift', 0):,.2f}

**Interaction Summary:**
- Total Interactions: {database_summary.get('total_interactions', 0)}
- Unique Constituents Contacted: {database_summary.get('constituents_with_interactions', 0)}

**Opportunity Summary:**
- Active Opportunities: {database_summary.get('total_opportunities', 0)}
- Total Expected Value: ${database_summary.get('total_opportunity_value', 0):,.2f}

## DONOR SEGMENTATION (RFM Analysis)

**Segment Distribution:**
{_format_segment_distribution(segment_counts, total_constituents)}

**Segment Details:**
{_format_segment_summary(segment_summary)}

**Top 5 Donors by Lifetime Giving:**
{_format_top_donors(top_donors)}

**At-Risk Analysis:**
- Total At-Risk/Lost Donors: {len(at_risk_donors)} ({len(at_risk_donors)/total_constituents*100:.1f}%)
- Combined Lifetime Value: ${sum(d['monetary'] for d in at_risk_donors):,.2f}

## YOUR TASK

Generate exactly 4-6 strategic insights covering these areas:

1. **Giving Trends**: Patterns in contribution behavior, seasonality, gift sizes
2. **Engagement Risks**: Constituents at risk of lapsing, declining engagement
3. **Upgrade Opportunities**: Donors with potential for increased giving
4. **Portfolio Suggestions**: Strategic recommendations for portfolio management

For each insight, provide:
- **title**: A clear, compelling headline (max 10 words)
- **description**: 2-3 sentences explaining the insight and supporting data
- **impact**: Quantified potential impact (e.g., "Could retain $X in giving" or "Potential to grow portfolio by X%")
- **recommended_action**: 1-2 specific, actionable next steps

Return your response as a valid JSON array of insight objects. Use this exact format:

```json
[
  {{
    "title": "Your compelling insight title here",
    "description": "Your detailed description with supporting data and context. Include specific numbers and percentages from the data provided.",
    "impact": "Clear statement of potential financial or strategic impact with quantification",
    "recommended_action": "Specific next steps the development team should take"
  }}
]
```

Focus on insights that are:
- Actionable and specific to this donor file
- Supported by the data provided
- Valuable for a development team making strategic decisions
- Prioritized by potential impact on fundraising goals"""

    return prompt


def _format_segment_distribution(segment_counts: Dict[str, int], total: int) -> str:
    """Format segment distribution for prompt."""
    lines = []
    for segment, count in sorted(segment_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        lines.append(f"  - {segment}: {count} ({pct:.1f}%)")
    return "\n".join(lines)


def _format_segment_summary(summary: Dict[str, Any]) -> str:
    """Format detailed segment summary for prompt."""
    lines = []
    for segment, metrics in sorted(summary.items(), key=lambda x: x[1]['count'], reverse=True):
        lines.append(f"\n**{segment}:**")
        lines.append(f"  - Count: {metrics['count']}")
        lines.append(f"  - Total Giving: ${metrics['total_monetary']:,.2f}")
        lines.append(f"  - Average Gift: ${metrics['avg_monetary']:,.2f}")
        lines.append(f"  - Average Engagement: {metrics['avg_engagement']}/100")
        lines.append(f"  - Average Frequency: {metrics['avg_frequency']} gifts")
        if metrics['total_pipeline'] > 0:
            lines.append(f"  - Pipeline Value: ${metrics['total_pipeline']:,.2f}")
    return "\n".join(lines)


def _format_top_donors(donors: list) -> str:
    """Format top donors list for prompt."""
    lines = []
    for i, donor in enumerate(donors, 1):
        lines.append(
            f"  {i}. {donor['first_name']} {donor['last_name']}: "
            f"${donor['monetary']:,.2f} ({donor['frequency']} gifts, "
            f"{donor['segment']} segment, "
            f"engagement: {donor['engagement_score']}/100)"
        )
    return "\n".join(lines)


VALIDATION_PROMPT = """Review the following insights and ensure they meet quality standards:

1. Each insight must have all four required fields: title, description, impact, recommended_action
2. Titles should be clear and compelling (max 10 words)
3. Descriptions should include specific data points and context
4. Impact should be quantified when possible
5. Recommended actions should be specific and actionable

If any insight doesn't meet these standards, improve it. Return the validated insights in the same JSON format."""


def generate_followup_prompt(insights: list, focus_area: str) -> str:
    """
    Generate a follow-up prompt to expand on a specific insight.

    Args:
        insights: Previously generated insights
        focus_area: Specific area to expand on (e.g., "engagement risks", "upgrade opportunities")

    Returns:
        Formatted follow-up prompt
    """
    return f"""Based on the insights already generated:

{insights}

Please provide additional analysis and recommendations specifically focused on: {focus_area}

Include:
1. Deeper analysis of the underlying data patterns
2. Specific donor examples or scenarios
3. Step-by-step implementation guidance
4. Expected timeline and resources needed
5. Key metrics to track success

Provide your response in a structured format with clear sections."""
