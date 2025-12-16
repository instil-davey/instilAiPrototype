"""
Fundraising message generator using Claude AI.

This module provides functionality to generate personalized fundraising messages
tailored to individual donors based on their giving history, interactions, and
organizational context.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import anthropic
from anthropic import Anthropic

from config import settings


class MessageGenerator:
    """
    Generates personalized fundraising messages using Claude AI.

    This class interfaces with the Anthropic Claude API to create tailored
    outreach messages for nonprofit fundraising campaigns.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the message generator.

        Args:
            api_key: Anthropic API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.client = Anthropic(api_key=self.api_key)
        self.model = settings.anthropic_model

    def generate(
        self,
        constituent: Dict[str, Any],
        briefing: Dict[str, Any],
        segment_context: Optional[Dict[str, Any]] = None,
        tone: str = "warm, human, relationship-forward",
        target_length: int = 200,
        generate_alternates: bool = False,
        num_alternates: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a personalized fundraising message for a constituent.

        Args:
            constituent: Dictionary containing constituent data including:
                - full_name: Donor's full name
                - email: Email address
                - constituent_type: Type of constituent
                - total_lifetime_giving: Total amount donated
                - contributions: List of contribution records
                - interactions: List of interaction records
                - opportunities: List of opportunity records
            briefing: Dictionary containing campaign/organizational context:
                - campaign_name: Name of the fundraising campaign
                - campaign_goal: Financial goal
                - campaign_description: Campaign details
                - organization_mission: Mission statement
                - key_talking_points: List of important points to include
                - deadline: Campaign deadline (if applicable)
            segment_context: Optional dictionary with donor segment information:
                - segment_name: Name of the donor segment
                - segment_characteristics: Key characteristics
                - giving_pattern: Typical giving patterns
            tone: Desired tone for the message (default: warm, human, relationship-forward)
            target_length: Target length for the message in words (default: 200)
            generate_alternates: Whether to generate alternate versions (default: False)
            num_alternates: Number of alternate versions to generate (default: 3)

        Returns:
            Dictionary containing:
                - subject_line: Email subject line
                - message: Main fundraising message body
                - alternates: List of alternate message versions (if requested)
                - metadata: Generation metadata (tokens used, model, timestamp)
        """
        # Build the prompt for Claude
        prompt = self._build_prompt(
            constituent=constituent,
            briefing=briefing,
            segment_context=segment_context,
            tone=tone,
            target_length=target_length
        )

        # Generate the primary message
        primary_response = self._call_claude(prompt)

        # Parse the response
        result = self._parse_response(primary_response)

        # Generate alternate versions if requested
        alternates = []
        if generate_alternates:
            for i in range(num_alternates):
                alternate_prompt = self._build_alternate_prompt(
                    original_prompt=prompt,
                    previous_version=result["message"],
                    version_number=i + 1
                )
                alternate_response = self._call_claude(alternate_prompt)
                alternate = self._parse_response(alternate_response)
                alternates.append({
                    "subject_line": alternate["subject_line"],
                    "message": alternate["message"]
                })

        result["alternates"] = alternates
        result["metadata"] = {
            "model": self.model,
            "tone": tone,
            "target_length": target_length,
            "timestamp": datetime.utcnow().isoformat(),
            "constituent_id": constituent.get("constituent_id"),
            "constituent_name": constituent.get("full_name")
        }

        return result

    def _build_prompt(
        self,
        constituent: Dict[str, Any],
        briefing: Dict[str, Any],
        segment_context: Optional[Dict[str, Any]],
        tone: str,
        target_length: int
    ) -> str:
        """Build the prompt for Claude to generate the fundraising message."""

        # Extract constituent information
        name = constituent.get("full_name", "Friend")
        constituent_type = constituent.get("constituent_type", "Supporter")
        lifetime_giving = constituent.get("total_lifetime_giving", 0)

        # Build giving history summary
        contributions = constituent.get("contributions", [])
        total_contributions = len(contributions)
        recent_contribution = None
        if contributions:
            # Assume contributions are sorted by date (most recent first)
            recent_contribution = contributions[0]

        # Build interaction history summary
        interactions = constituent.get("interactions", [])
        total_interactions = len(interactions)
        recent_interaction = None
        if interactions:
            recent_interaction = interactions[0]

        # Extract briefing information
        campaign_name = briefing.get("campaign_name", "our campaign")
        campaign_goal = briefing.get("campaign_goal", "")
        campaign_description = briefing.get("campaign_description", "")
        organization_mission = briefing.get("organization_mission", "")
        key_points = briefing.get("key_talking_points", [])
        deadline = briefing.get("deadline", "")

        # Build segment context
        segment_info = ""
        if segment_context:
            segment_name = segment_context.get("segment_name", "")
            segment_characteristics = segment_context.get("segment_characteristics", "")
            giving_pattern = segment_context.get("giving_pattern", "")
            segment_info = f"""
Donor Segment: {segment_name}
Segment Characteristics: {segment_characteristics}
Typical Giving Pattern: {giving_pattern}
"""

        # Construct the prompt
        prompt = f"""You are a skilled nonprofit development officer writing a personalized fundraising message.

TONE: {tone}

TARGET LENGTH: {target_length} words (between 150-220 words is ideal)

CONSTITUENT INFORMATION:
- Name: {name}
- Type: {constituent_type}
- Lifetime Giving: ${lifetime_giving:,.2f}
- Total Contributions: {total_contributions}
- Total Interactions: {total_interactions}
"""

        if recent_contribution:
            contribution_date = recent_contribution.get("contribution_date", "recently")
            contribution_amount = recent_contribution.get("amount", 0)
            prompt += f"- Most Recent Gift: ${contribution_amount:,.2f} on {contribution_date}\n"

        if recent_interaction:
            interaction_date = recent_interaction.get("interaction_date", "recently")
            interaction_type = recent_interaction.get("interaction_type", "contact")
            interaction_subject = recent_interaction.get("subject", "")
            prompt += f"- Most Recent Interaction: {interaction_type} on {interaction_date}"
            if interaction_subject:
                prompt += f" regarding {interaction_subject}"
            prompt += "\n"

        if segment_info:
            prompt += f"\n{segment_info}"

        prompt += f"""
CAMPAIGN INFORMATION:
- Campaign Name: {campaign_name}
"""

        if campaign_goal:
            prompt += f"- Campaign Goal: ${campaign_goal:,.2f}\n"

        if campaign_description:
            prompt += f"- Description: {campaign_description}\n"

        if organization_mission:
            prompt += f"- Mission: {organization_mission}\n"

        if deadline:
            prompt += f"- Deadline: {deadline}\n"

        if key_points:
            prompt += "\nKEY TALKING POINTS TO INCLUDE:\n"
            for point in key_points:
                prompt += f"- {point}\n"

        prompt += """
TASK:
Generate a personalized fundraising message with the following components:

1. SUBJECT LINE: A compelling email subject line (5-8 words) that:
   - Captures attention
   - References the campaign or impact
   - Feels personal, not generic
   - Avoids spam-trigger words

2. MESSAGE BODY: A 150-220 word personalized message that:
   - Opens with a warm, personal greeting
   - Acknowledges their past support and relationship (if applicable)
   - Clearly explains the campaign purpose and impact
   - Includes specific, concrete examples of what their gift will achieve
   - Creates emotional connection to the cause
   - Has a clear, actionable call-to-action
   - Closes with gratitude and warmth
   - Sounds authentically human, not AI-generated
   - Uses natural language and avoids clichés
   - References specific details from their constituent record when relevant

IMPORTANT GUIDELINES:
- Write in a conversational, authentic voice
- Use contractions and natural phrasing
- Be specific about impact, not generic
- Show genuine appreciation for their relationship
- Avoid fundraising jargon or corporate language
- Make it feel like a personal note from a real person
- DO NOT include placeholder text like [donor name] - use the actual name provided
- DO NOT include sender signature, address, or contact info - just the message body

OUTPUT FORMAT:
Return your response in this exact format:

SUBJECT: [your subject line here]

MESSAGE:
[your message body here]
"""

        return prompt

    def _build_alternate_prompt(
        self,
        original_prompt: str,
        previous_version: str,
        version_number: int
    ) -> str:
        """Build a prompt for generating an alternate version."""
        return f"""{original_prompt}

ADDITIONAL INSTRUCTION:
This is alternate version #{version_number}. Create a fresh variation that:
- Takes a different approach or angle than the previous version
- Uses different language and phrasing
- Maintains the same core message and tone
- Varies the opening and call-to-action

PREVIOUS VERSION TO VARY FROM:
{previous_version}

Create a distinctly different but equally compelling version.
"""

    def _call_claude(self, prompt: str) -> str:
        """Call the Claude API with the given prompt."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the text content from the response
            return message.content[0].text

        except anthropic.APIError as e:
            raise RuntimeError(f"Claude API error: {str(e)}")

    def _parse_response(self, response: str) -> Dict[str, str]:
        """
        Parse the Claude response to extract subject line and message body.

        Args:
            response: Raw response text from Claude

        Returns:
            Dictionary with 'subject_line' and 'message' keys
        """
        lines = response.strip().split("\n")
        subject_line = ""
        message_lines = []
        in_message = False

        for line in lines:
            if line.strip().startswith("SUBJECT:"):
                subject_line = line.replace("SUBJECT:", "").strip()
            elif line.strip().startswith("MESSAGE:"):
                in_message = True
            elif in_message and line.strip():
                message_lines.append(line.strip())

        # Join message lines
        message = " ".join(message_lines)

        # Fallback: if parsing fails, try to extract intelligently
        if not subject_line or not message:
            # Look for the first line as subject
            if lines:
                subject_line = lines[0].replace("SUBJECT:", "").strip()
                # Everything else is the message
                message = "\n".join(lines[1:]).replace("MESSAGE:", "").strip()

        return {
            "subject_line": subject_line,
            "message": message
        }


def generate_fundraising_message(
    constituent: Dict[str, Any],
    briefing: Dict[str, Any],
    segment_context: Optional[Dict[str, Any]] = None,
    tone: str = "warm, human, relationship-forward",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate a fundraising message.

    Args:
        constituent: Constituent data dictionary
        briefing: Campaign/organizational briefing dictionary
        segment_context: Optional donor segment context
        tone: Desired message tone
        api_key: Optional Anthropic API key

    Returns:
        Dictionary with subject_line, message, and metadata
    """
    generator = MessageGenerator(api_key=api_key)
    return generator.generate(
        constituent=constituent,
        briefing=briefing,
        segment_context=segment_context,
        tone=tone
    )
