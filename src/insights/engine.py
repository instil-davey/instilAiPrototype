"""
AI-Driven Insights Engine

Uses Claude 3.5 Sonnet to generate strategic donor insights from
segmentation data and database analysis.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from sqlalchemy.orm import Session

from src.segmentation.engine import DonorSegmentationEngine
from src.insights.data_summary import get_database_summary
from src.insights.prompts import (
    SYSTEM_PROMPT,
    generate_insights_prompt,
    generate_followup_prompt
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightGenerationError(Exception):
    """Raised when insight generation fails."""
    pass


class DonorInsightsEngine:
    """
    AI-powered insights engine for donor database analysis.

    Uses Claude 3.5 Sonnet to generate actionable insights about:
    - Giving trends
    - Engagement risks
    - Upgrade opportunities
    - Portfolio suggestions
    """

    def __init__(
        self,
        db_session: Session,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        """
        Initialize the insights engine.

        Args:
            db_session: SQLAlchemy database session
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use (default: claude-3-5-sonnet-20241022)
        """
        self.session = db_session
        self.model = model

        # Initialize Anthropic client
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Anthropic API key must be provided or set in ANTHROPIC_API_KEY environment variable"
            )

        self.client = Anthropic(api_key=self.api_key)

        # Initialize segmentation engine
        self.segmentation_engine = DonorSegmentationEngine(db_session)

    def generate_insights(
        self,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights about the donor database.

        Args:
            max_retries: Maximum number of retries if generation fails

        Returns:
            Dict containing:
            - insights: List of 4-6 insight objects
            - metadata: Generation metadata (model, timestamp, etc.)
            - segmentation_data: Full segmentation analysis
            - database_summary: Database statistics

        Raises:
            InsightGenerationError: If insight generation fails after retries
        """
        logger.info("Starting insight generation...")

        try:
            # Step 1: Run segmentation analysis
            logger.info("Running donor segmentation analysis...")
            segmentation_data = self.segmentation_engine.generate_complete_segments()

            # Step 2: Get database summary
            logger.info("Generating database summary...")
            database_summary = get_database_summary(self.session)

            # Step 3: Generate AI insights
            logger.info("Calling Claude API to generate insights...")
            insights = self._call_claude_api(
                segmentation_data,
                database_summary,
                max_retries
            )

            # Step 4: Validate and format response
            validated_insights = self._validate_insights(insights)

            logger.info(f"Successfully generated {len(validated_insights)} insights")

            return {
                'insights': validated_insights,
                'metadata': {
                    'model': self.model,
                    'insights_count': len(validated_insights),
                    'analysis_date': segmentation_data['analysis_date'],
                    'total_constituents': segmentation_data['total_constituents']
                },
                'segmentation_data': segmentation_data,
                'database_summary': database_summary
            }

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            raise InsightGenerationError(f"Failed to generate insights: {str(e)}")

    def _call_claude_api(
        self,
        segmentation_data: Dict[str, Any],
        database_summary: Dict[str, Any],
        max_retries: int
    ) -> List[Dict[str, Any]]:
        """
        Call Claude API to generate insights.

        Args:
            segmentation_data: Segmentation analysis results
            database_summary: Database statistics
            max_retries: Maximum retry attempts

        Returns:
            List of insight dictionaries

        Raises:
            InsightGenerationError: If API call fails after retries
        """
        # Generate the prompt
        prompt = generate_insights_prompt(segmentation_data, database_summary)

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"API call attempt {attempt + 1}/{max_retries + 1}")

                # Call Claude API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.7,
                    system=SYSTEM_PROMPT,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                # Extract text content
                content = response.content[0].text

                # Parse JSON from response
                insights = self._extract_json_from_response(content)

                if insights and len(insights) >= 4:
                    return insights
                else:
                    logger.warning(f"Received {len(insights)} insights, expected 4-6")
                    if attempt < max_retries:
                        continue
                    else:
                        return insights  # Return what we got on final attempt

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from response: {e}")
                if attempt == max_retries:
                    raise InsightGenerationError(f"Failed to parse insights JSON: {e}")

            except Exception as e:
                logger.error(f"API call failed: {e}")
                if attempt == max_retries:
                    raise InsightGenerationError(f"API call failed: {e}")

        raise InsightGenerationError("Failed to generate insights after all retries")

    def _extract_json_from_response(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract JSON array from Claude's response.

        Claude may wrap JSON in markdown code blocks, so we need to handle that.

        Args:
            content: Raw response text from Claude

        Returns:
            Parsed JSON array
        """
        # Remove markdown code blocks if present
        content = content.strip()

        if content.startswith('```json'):
            content = content[7:]  # Remove ```json
        elif content.startswith('```'):
            content = content[3:]  # Remove ```

        if content.endswith('```'):
            content = content[:-3]  # Remove trailing ```

        content = content.strip()

        # Parse JSON
        return json.loads(content)

    def _validate_insights(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate that insights have required fields and proper structure.

        Args:
            insights: List of insight dictionaries

        Returns:
            Validated insights list

        Raises:
            InsightGenerationError: If validation fails
        """
        required_fields = ['title', 'description', 'impact', 'recommended_action']

        validated = []

        for i, insight in enumerate(insights):
            # Check all required fields are present
            missing_fields = [f for f in required_fields if f not in insight]

            if missing_fields:
                logger.warning(
                    f"Insight {i+1} missing fields: {missing_fields}. Skipping."
                )
                continue

            # Check fields are not empty
            empty_fields = [
                f for f in required_fields
                if not insight[f] or not str(insight[f]).strip()
            ]

            if empty_fields:
                logger.warning(
                    f"Insight {i+1} has empty fields: {empty_fields}. Skipping."
                )
                continue

            validated.append(insight)

        if len(validated) < 4:
            raise InsightGenerationError(
                f"Only {len(validated)} valid insights generated, expected at least 4"
            )

        return validated

    def generate_focused_insight(
        self,
        focus_area: str,
        previous_insights: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate a detailed, focused analysis on a specific area.

        Args:
            focus_area: Area to focus on (e.g., "engagement risks", "upgrade opportunities")
            previous_insights: Optional list of previously generated insights for context

        Returns:
            Detailed analysis text
        """
        logger.info(f"Generating focused insight on: {focus_area}")

        try:
            # Generate follow-up prompt
            prompt = generate_followup_prompt(
                previous_insights or [],
                focus_area
            )

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error generating focused insight: {e}")
            raise InsightGenerationError(f"Failed to generate focused insight: {e}")


def create_insights_engine(
    db_session: Session,
    api_key: Optional[str] = None
) -> DonorInsightsEngine:
    """
    Factory function to create an insights engine instance.

    Args:
        db_session: SQLAlchemy database session
        api_key: Optional Anthropic API key

    Returns:
        DonorInsightsEngine instance
    """
    return DonorInsightsEngine(db_session, api_key)
