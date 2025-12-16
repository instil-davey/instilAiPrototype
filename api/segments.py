"""
Donor Segmentation API

Flask API endpoint for accessing donor segmentation analysis.
"""

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.segments.engine import SegmentationEngine
from models import Base

# Initialize Flask app
app = Flask(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///nonprofit_crm.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def get_db_session():
    """Create a new database session."""
    return SessionLocal()


@app.route('/api/segments', methods=['GET'])
def get_segments():
    """
    GET /api/segments

    Generate and return all donor segments.

    Query Parameters:
        - segment_id (optional): Filter by specific segment ID
        - include_constituents (optional): Include full constituent details (default: false)
        - format (optional): 'summary' or 'detailed' (default: 'detailed')

    Returns:
        JSON response with segment data

    Example:
        GET /api/segments
        GET /api/segments?segment_id=high_capacity_low_giving
        GET /api/segments?format=summary
    """
    try:
        # Get query parameters
        segment_id_filter = request.args.get('segment_id')
        include_constituents = request.args.get('include_constituents', 'false').lower() == 'true'
        format_type = request.args.get('format', 'detailed')

        # Create database session
        session = get_db_session()

        # Initialize segmentation engine
        engine_instance = SegmentationEngine(session)

        # Generate all segments
        segments = engine_instance.generate_all_segments()

        # Filter by segment_id if provided
        if segment_id_filter:
            segments = [s for s in segments if s.segment_id == segment_id_filter]
            if not segments:
                return jsonify({
                    'error': f'Segment not found: {segment_id_filter}',
                    'available_segments': [s.segment_id for s in engine_instance.generate_all_segments()]
                }), 404

        # Format response based on format parameter
        if format_type == 'summary':
            response = {
                'summary': engine_instance.get_segment_summary(segments),
                'segments': [
                    {
                        'segment_id': seg.segment_id,
                        'name': seg.name,
                        'description': seg.description,
                        'count': len(seg.constituent_ids),
                        'metrics': seg.segment_metrics
                    }
                    for seg in segments
                ]
            }
        else:
            # Detailed format
            response = {
                'summary': engine_instance.get_segment_summary(segments),
                'segments': []
            }

            for seg in segments:
                segment_data = {
                    'segment_id': seg.segment_id,
                    'name': seg.name,
                    'description': seg.description,
                    'reasoning_formula': seg.reasoning_formula,
                    'constituent_ids': seg.constituent_ids,
                    'metrics': seg.segment_metrics,
                    'suggested_actions': seg.suggested_actions
                }

                # Optionally include full constituent details
                if include_constituents:
                    segment_data['constituents'] = []
                    for const_id in seg.constituent_ids[:100]:  # Limit to first 100 for performance
                        data = engine_instance.get_constituent_data(const_id)
                        if data:
                            segment_data['constituents'].append({
                                'constituent_id': const_id,
                                'name': data['constituent'].full_name,
                                'email': data['constituent'].email,
                                'type': data['constituent'].constituent_type,
                                'total_lifetime_giving': data['total_lifetime_giving'],
                                'rfm': {
                                    'recency': data['rfm']['recency'],
                                    'frequency': data['rfm']['frequency'],
                                    'monetary': float(data['rfm']['monetary'])
                                },
                                'capacity_score': data['capacity_score'],
                                'engagement_score': data['engagement_score'],
                                'suggested_action': seg.suggested_actions.get(const_id)
                            })

                response['segments'].append(segment_data)

        # Close session
        session.close()

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while generating segments'
        }), 500


@app.route('/api/segments/<segment_id>/constituents/<int:constituent_id>', methods=['GET'])
def get_constituent_segment_detail(segment_id, constituent_id):
    """
    GET /api/segments/<segment_id>/constituents/<constituent_id>

    Get detailed information about a specific constituent in a segment.

    Args:
        segment_id: ID of the segment
        constituent_id: ID of the constituent

    Returns:
        JSON response with detailed constituent data
    """
    try:
        session = get_db_session()
        engine_instance = SegmentationEngine(session)

        # Get constituent data
        data = engine_instance.get_constituent_data(constituent_id)

        if not data:
            return jsonify({
                'error': f'Constituent not found: {constituent_id}'
            }), 404

        # Get all segments to find the requested one
        segments = engine_instance.generate_all_segments()
        segment = next((s for s in segments if s.segment_id == segment_id), None)

        if not segment:
            return jsonify({
                'error': f'Segment not found: {segment_id}'
            }), 404

        if constituent_id not in segment.constituent_ids:
            return jsonify({
                'error': f'Constituent {constituent_id} is not in segment {segment_id}'
            }), 404

        # Build detailed response
        response = {
            'segment': {
                'segment_id': segment.segment_id,
                'name': segment.name,
                'description': segment.description,
                'reasoning_formula': segment.reasoning_formula
            },
            'constituent': {
                'constituent_id': constituent_id,
                'name': data['constituent'].full_name,
                'email': data['constituent'].email,
                'phone': data['constituent'].phone,
                'type': data['constituent'].constituent_type,
                'created_date': data['constituent'].created_date.isoformat(),
                'total_lifetime_giving': data['total_lifetime_giving'],
            },
            'metrics': {
                'rfm': {
                    'recency': data['rfm']['recency'],
                    'frequency': data['rfm']['frequency'],
                    'monetary': float(data['rfm']['monetary']),
                    'avg_gift': float(data['rfm']['avg_gift'])
                },
                'capacity_score': data['capacity_score'],
                'engagement_score': data['engagement_score'],
                'risk_score': data['risk_score'],
                'risk_level': data['risk_level'],
            },
            'trends': {
                'giving_trend': data['trend_analysis']['trend'] if data['trend_analysis'] else None,
                'trend_pct_change': data['trend_analysis']['pct_change'] if data['trend_analysis'] else None,
            },
            'activity': {
                'contribution_count': data['contribution_count'],
                'interaction_count': data['interaction_count'],
                'days_since_last_gift': data['days_since_last_gift'],
                'days_since_last_interaction': data['days_since_last_interaction'] if data['days_since_last_interaction'] != float('inf') else None,
            },
            'seasonal_analysis': data['seasonal_analysis'] if data['seasonal_analysis'] else None,
            'suggested_action': segment.suggested_actions.get(constituent_id),
        }

        session.close()
        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while fetching constituent details'
        }), 500


@app.route('/api/segments/stats', methods=['GET'])
def get_segment_stats():
    """
    GET /api/segments/stats

    Get overall segmentation statistics and performance metrics.

    Returns:
        JSON response with statistics
    """
    try:
        session = get_db_session()
        engine_instance = SegmentationEngine(session)

        # Generate segments
        segments = engine_instance.generate_all_segments()

        # Get summary
        summary = engine_instance.get_segment_summary(segments)

        # Additional statistics
        from models import Constituent, Contribution, Interaction
        from sqlalchemy import func

        total_constituents = session.query(func.count(Constituent.constituent_id)).scalar()
        total_contributions = session.query(func.count(Contribution.contribution_id)).scalar()
        total_interactions = session.query(func.count(Interaction.interaction_id)).scalar()
        total_giving = session.query(func.sum(Contribution.amount)).scalar() or 0

        stats = {
            'database_stats': {
                'total_constituents': total_constituents,
                'total_contributions': total_contributions,
                'total_interactions': total_interactions,
                'total_giving': float(total_giving),
            },
            'segmentation_stats': summary,
            'segment_overlap': {
                'description': 'Constituents may appear in multiple segments',
                'total_segment_placements': sum(len(s.constituent_ids) for s in segments),
                'unique_constituents': summary['total_unique_constituents'],
                'avg_segments_per_constituent': (
                    sum(len(s.constituent_ids) for s in segments) / summary['total_unique_constituents']
                    if summary['total_unique_constituents'] > 0 else 0
                )
            }
        }

        session.close()
        return jsonify(stats), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while generating statistics'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': DATABASE_URL.split('://')[0]  # Just the DB type for security
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server
    print("=" * 80)
    print("🚀 Starting Donor Segmentation API")
    print("=" * 80)
    print(f"Database: {DATABASE_URL}")
    print("\nAvailable endpoints:")
    print("  GET /api/segments")
    print("  GET /api/segments?segment_id=<id>")
    print("  GET /api/segments?format=summary")
    print("  GET /api/segments/<segment_id>/constituents/<constituent_id>")
    print("  GET /api/segments/stats")
    print("  GET /api/health")
    print("=" * 80)
    print("\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
