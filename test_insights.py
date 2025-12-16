#!/usr/bin/env python3
"""
Test script for the Donor Insights Engine

This script tests the segmentation engine and data summary functions
without requiring an Anthropic API key.
"""

import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.segmentation.engine import create_segmentation_engine
from src.insights.data_summary import (
    get_database_summary,
    get_giving_trends,
    get_engagement_analysis,
    get_opportunity_analysis
)
from src.insights.prompts import generate_insights_prompt


def test_segmentation(session):
    """Test the segmentation engine."""
    print("\n" + "="*60)
    print("TESTING DONOR SEGMENTATION ENGINE")
    print("="*60)

    engine = create_segmentation_engine(session)

    # Test RFM calculation
    print("\n1. Calculating RFM scores...")
    rfm_scores = engine.calculate_rfm_scores()
    print(f"   ✓ Calculated RFM scores for {len(rfm_scores)} constituents")

    # Show a sample
    if rfm_scores:
        sample = rfm_scores[0]
        print(f"\n   Sample RFM Score:")
        print(f"   - Name: {sample['first_name']} {sample['last_name']}")
        print(f"   - Segment: {sample['segment']}")
        print(f"   - RFM Score: {sample['rfm_score']}")
        print(f"   - Monetary: ${sample['monetary']:,.2f}")
        print(f"   - Frequency: {sample['frequency']} gifts")
        print(f"   - Recency: {sample['recency_days']} days")

    # Test engagement metrics
    print("\n2. Calculating engagement metrics...")
    engagement = engine.get_engagement_metrics()
    print(f"   ✓ Calculated engagement for {len(engagement)} constituents")

    if engagement:
        sample = engagement[0]
        print(f"\n   Sample Engagement:")
        print(f"   - Constituent ID: {sample['constituent_id']}")
        print(f"   - Engagement Score: {sample['engagement_score']}/100")
        print(f"   - Engagement Level: {sample['engagement_level']}")
        print(f"   - Interactions: {sample['interaction_count']}")

    # Test opportunity pipeline
    print("\n3. Analyzing opportunity pipeline...")
    pipeline = engine.get_opportunity_pipeline()
    print(f"   ✓ Analyzed pipeline for {len(pipeline)} constituents")

    # Test complete segmentation
    print("\n4. Generating complete segmentation...")
    complete = engine.generate_complete_segments()
    print(f"   ✓ Generated complete segmentation")
    print(f"   - Total Constituents: {complete['total_constituents']}")
    print(f"   - Segments: {len(complete['segment_summary'])}")

    # Display segment summary
    print("\n   Segment Distribution:")
    for segment, metrics in sorted(
        complete['segment_summary'].items(),
        key=lambda x: x[1]['count'],
        reverse=True
    ):
        print(f"   - {segment}: {metrics['count']} constituents "
              f"(${metrics['total_monetary']:,.2f} lifetime giving)")

    return complete


def test_data_summary(session):
    """Test the data summary functions."""
    print("\n" + "="*60)
    print("TESTING DATA SUMMARY FUNCTIONS")
    print("="*60)

    # Test database summary
    print("\n1. Generating database summary...")
    summary = get_database_summary(session)
    print(f"   ✓ Database summary generated")
    print(f"   - Total Constituents: {summary['total_constituents']}")
    print(f"   - Total Contributions: {summary['total_contributions']}")
    print(f"   - Total Giving: ${summary['total_contribution_amount']:,.2f}")
    print(f"   - Average Gift: ${summary['average_gift']:,.2f}")
    print(f"   - Total Interactions: {summary['total_interactions']}")
    print(f"   - Total Opportunities: {summary['total_opportunities']}")

    # Test giving trends
    print("\n2. Analyzing giving trends...")
    trends = get_giving_trends(session)
    print(f"   ✓ Giving trends analyzed")
    print(f"   - Months with data: {len(trends['monthly_data'])}")
    print(f"   - Contribution types: {len(trends['by_type'])}")
    print(f"   - Payment methods: {len(trends['by_payment_method'])}")

    # Test engagement analysis
    print("\n3. Analyzing engagement patterns...")
    engagement = get_engagement_analysis(session)
    print(f"   ✓ Engagement analysis complete")
    print(f"   - Interaction types: {len(engagement['by_interaction_type'])}")
    print(f"   - Follow-ups required: {engagement['followup_required_count']}")

    # Test opportunity analysis
    print("\n4. Analyzing opportunities...")
    opportunities = get_opportunity_analysis(session)
    print(f"   ✓ Opportunity analysis complete")
    print(f"   - Pipeline stages: {len(opportunities['by_stage'])}")

    return summary


def test_prompt_generation(segmentation_data, database_summary):
    """Test prompt generation."""
    print("\n" + "="*60)
    print("TESTING PROMPT GENERATION")
    print("="*60)

    print("\n1. Generating AI prompt...")
    prompt = generate_insights_prompt(segmentation_data, database_summary)
    print(f"   ✓ Prompt generated ({len(prompt)} characters)")

    # Show a preview
    preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
    print(f"\n   Prompt Preview:")
    print("   " + "-"*56)
    for line in preview.split('\n')[:10]:
        print(f"   {line}")
    print("   ...")
    print("   " + "-"*56)

    return prompt


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("DONOR INSIGHTS ENGINE - TEST SUITE")
    print("="*60)

    # Check database exists
    db_path = 'nonprofit_crm.db'
    if not os.path.exists(db_path):
        print(f"\n❌ ERROR: Database '{db_path}' not found!")
        print("   Please run load_data.py first to create the database.")
        sys.exit(1)

    # Connect to database
    print(f"\n✓ Found database: {db_path}")
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Run tests
        segmentation_data = test_segmentation(session)
        database_summary = test_data_summary(session)
        prompt = test_prompt_generation(segmentation_data, database_summary)

        # Success summary
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print("\n✓ All tests passed successfully!")
        print("\nThe insights engine is ready to use.")
        print("\nNext steps:")
        print("1. Set your ANTHROPIC_API_KEY environment variable")
        print("2. Install requirements: pip install -r requirements.txt")
        print("3. Start the API: python api/insights.py")
        print("4. Access insights: curl http://localhost:5000/api/insights")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        session.close()


if __name__ == '__main__':
    main()
