"""
Flask API for Donor Insights

Provides REST endpoints for generating and accessing AI-powered donor insights.
"""

import os
import logging
from typing import Dict, Any
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from src.insights.engine import create_insights_engine, InsightGenerationError
from src.segmentation.engine import create_segmentation_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///nonprofit_crm.db')
engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(bind=engine))


def get_db_session():
    """Get database session."""
    return SessionLocal()


def cleanup_db_session():
    """Cleanup database session."""
    SessionLocal.remove()


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Cleanup session on app context teardown."""
    cleanup_db_session()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'donor-insights-api'
    }), 200


@app.route('/api/insights', methods=['GET'])
def get_insights():
    """
    Generate AI-powered donor insights.

    Query Parameters:
        - full_data (bool): Include full segmentation and database data (default: false)
        - max_retries (int): Maximum retry attempts for AI generation (default: 2)

    Returns:
        JSON response with:
        - insights: Array of 4-6 insight objects
        - metadata: Generation metadata
        - segmentation_data (optional): Full segmentation results
        - database_summary (optional): Database statistics

    Example Response:
        {
            "insights": [
                {
                    "title": "High-Value Donors at Risk",
                    "description": "3 major donors haven't engaged in 90+ days...",
                    "impact": "At risk of losing $15,000 in annual giving",
                    "recommended_action": "Schedule personalized outreach calls this week"
                }
            ],
            "metadata": {
                "model": "claude-3-5-sonnet-20241022",
                "insights_count": 6,
                "analysis_date": "2025-11-20T...",
                "total_constituents": 10
            }
        }
    """
    try:
        # Parse query parameters
        include_full_data = request.args.get('full_data', 'false').lower() == 'true'
        max_retries = int(request.args.get('max_retries', '2'))

        logger.info(f"Generating insights (full_data={include_full_data})")

        # Get database session
        db_session = get_db_session()

        try:
            # Create insights engine
            insights_engine = create_insights_engine(db_session)

            # Generate insights
            result = insights_engine.generate_insights(max_retries=max_retries)

            # Prepare response
            response = {
                'insights': result['insights'],
                'metadata': result['metadata']
            }

            # Include full data if requested
            if include_full_data:
                response['segmentation_data'] = result['segmentation_data']
                response['database_summary'] = result['database_summary']

            return jsonify(response), 200

        finally:
            cleanup_db_session()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({
            'error': 'Configuration error',
            'message': str(e)
        }), 500

    except InsightGenerationError as e:
        logger.error(f"Insight generation failed: {e}")
        return jsonify({
            'error': 'Insight generation failed',
            'message': str(e)
        }), 500

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/insights/focused', methods=['POST'])
def get_focused_insight():
    """
    Generate a detailed, focused analysis on a specific area.

    Request Body:
        {
            "focus_area": "engagement risks",
            "previous_insights": [...]  // Optional
        }

    Returns:
        JSON response with detailed analysis text
    """
    try:
        # Parse request body
        data = request.get_json()

        if not data or 'focus_area' not in data:
            return jsonify({
                'error': 'Bad request',
                'message': 'focus_area is required'
            }), 400

        focus_area = data['focus_area']
        previous_insights = data.get('previous_insights')

        logger.info(f"Generating focused insight on: {focus_area}")

        # Get database session
        db_session = get_db_session()

        try:
            # Create insights engine
            insights_engine = create_insights_engine(db_session)

            # Generate focused insight
            analysis = insights_engine.generate_focused_insight(
                focus_area,
                previous_insights
            )

            return jsonify({
                'focus_area': focus_area,
                'analysis': analysis
            }), 200

        finally:
            cleanup_db_session()

    except InsightGenerationError as e:
        logger.error(f"Focused insight generation failed: {e}")
        return jsonify({
            'error': 'Insight generation failed',
            'message': str(e)
        }), 500

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/segmentation', methods=['GET'])
def get_segmentation():
    """
    Get donor segmentation analysis without AI insights.

    Returns:
        JSON response with:
        - segments: Array of all constituents with segmentation data
        - segment_summary: Aggregate statistics by segment
        - insights: Basic segment insights
    """
    try:
        logger.info("Generating segmentation analysis")

        # Get database session
        db_session = get_db_session()

        try:
            # Create segmentation engine
            segmentation_engine = create_segmentation_engine(db_session)

            # Generate segments
            result = segmentation_engine.generate_complete_segments()

            return jsonify(result), 200

        finally:
            cleanup_db_session()

    except Exception as e:
        logger.error(f"Segmentation failed: {e}")
        return jsonify({
            'error': 'Segmentation failed',
            'message': str(e)
        }), 500


@app.route('/api/segmentation/rfm', methods=['GET'])
def get_rfm_scores():
    """
    Get RFM (Recency, Frequency, Monetary) scores for all donors.

    Returns:
        JSON response with array of donor RFM scores
    """
    try:
        logger.info("Calculating RFM scores")

        # Get database session
        db_session = get_db_session()

        try:
            # Create segmentation engine
            segmentation_engine = create_segmentation_engine(db_session)

            # Calculate RFM scores
            rfm_scores = segmentation_engine.calculate_rfm_scores()

            return jsonify({
                'rfm_scores': rfm_scores,
                'total_donors': len(rfm_scores)
            }), 200

        finally:
            cleanup_db_session()

    except Exception as e:
        logger.error(f"RFM calculation failed: {e}")
        return jsonify({
            'error': 'RFM calculation failed',
            'message': str(e)
        }), 500


@app.route('/api/segmentation/engagement', methods=['GET'])
def get_engagement():
    """
    Get engagement metrics for all constituents.

    Returns:
        JSON response with engagement scores and levels
    """
    try:
        logger.info("Calculating engagement metrics")

        # Get database session
        db_session = get_db_session()

        try:
            # Create segmentation engine
            segmentation_engine = create_segmentation_engine(db_session)

            # Get engagement metrics
            engagement = segmentation_engine.get_engagement_metrics()

            return jsonify({
                'engagement_metrics': engagement,
                'total_constituents': len(engagement)
            }), 200

        finally:
            cleanup_db_session()

    except Exception as e:
        logger.error(f"Engagement calculation failed: {e}")
        return jsonify({
            'error': 'Engagement calculation failed',
            'message': str(e)
        }), 500


def create_app():
    """Application factory for testing."""
    return app


if __name__ == '__main__':
    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        logger.warning(
            "ANTHROPIC_API_KEY not set. AI insights generation will fail. "
            "Set the environment variable or create a .env file."
        )

    # Run development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    logger.info(f"Starting Donor Insights API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
