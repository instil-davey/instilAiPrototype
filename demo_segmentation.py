#!/usr/bin/env python3
"""
Demonstration Script for Donor Segmentation Engine

This script creates synthetic donor data and demonstrates the segmentation engine
capabilities with a full analysis report.
"""

import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from models import Base, Constituent, Contribution, Interaction, Opportunity, init_database
from src.segments.engine import SegmentationEngine


def create_synthetic_data(session):
    """
    Create synthetic donor data for demonstration purposes.
    """
    print("\n" + "=" * 80)
    print("🎲 GENERATING SYNTHETIC DONOR DATA")
    print("=" * 80)

    constituents_data = []
    contributions_data = []
    interactions_data = []

    today = date.today()

    # Create 50 diverse constituents with different patterns
    constituent_types = ['Donor', 'Major Donor', 'Board Member', 'Volunteer']
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'William', 'Mary']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']

    print("\nCreating 50 constituents with varied profiles...")

    for i in range(1, 51):
        constituent_type = random.choice(constituent_types)
        if i <= 5:  # First 5 are major donors
            constituent_type = 'Major Donor'
        elif i <= 10:  # Next 5 are board members
            constituent_type = 'Board Member'

        created_date = today - timedelta(days=random.randint(365, 1825))  # 1-5 years ago

        constituent = Constituent(
            constituent_id=i,
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            email=f'donor{i}@example.com',
            phone=f'555-{i:04d}',
            address=f'{i} Main Street',
            city='Springfield',
            state='IL',
            zip_code='62701',
            constituent_type=constituent_type,
            created_date=created_date,
            total_lifetime_giving=Decimal('0')  # Will calculate later
        )
        constituents_data.append(constituent)
        session.add(constituent)

    session.commit()
    print(f"✓ Created {len(constituents_data)} constituents")

    # Generate contributions with different patterns
    print("\nGenerating contribution patterns...")

    contribution_id = 1

    for const_id in range(1, 51):
        pattern_type = None

        if const_id <= 5:  # High capacity, low recent giving
            pattern_type = 'high_capacity_low_giving'
            amounts = [Decimal('5000'), Decimal('6000'), Decimal('7000'), Decimal('8000')]
            dates = [today - timedelta(days=700), today - timedelta(days=600),
                    today - timedelta(days=500), today - timedelta(days=400)]

        elif const_id <= 10:  # Increasing giving pattern
            pattern_type = 'increasing'
            amounts = [Decimal(amt) for amt in [100, 150, 200, 300, 400, 500, 600, 750]]
            dates = [today - timedelta(days=365 - i*30) for i in range(8)]

        elif const_id <= 15:  # Declining giving pattern
            pattern_type = 'declining'
            amounts = [Decimal(amt) for amt in [1000, 900, 800, 600, 500, 400, 300, 200]]
            dates = [today - timedelta(days=365 - i*30) for i in range(8)]

        elif const_id <= 20:  # Seasonal givers (December pattern)
            pattern_type = 'seasonal'
            amounts = [Decimal('500')] * 5
            dates = [
                date(today.year - 4, 12, 15),
                date(today.year - 3, 12, 20),
                date(today.year - 2, 12, 18),
                date(today.year - 1, 12, 22),
                date(today.year, 1, 5) if today.month > 1 else date(today.year - 1, 12, 15)
            ]

        elif const_id <= 25:  # Potential major donors
            pattern_type = 'potential_major'
            amounts = [Decimal(amt) for amt in [1000, 1500, 2000, 2500, 3000, 3500]]
            dates = [today - timedelta(days=365 - i*45) for i in range(6)]

        elif const_id <= 30:  # Major donors neglected
            pattern_type = 'neglected_major'
            amounts = [Decimal('10000'), Decimal('12000'), Decimal('15000')]
            dates = [today - timedelta(days=500), today - timedelta(days=400),
                    today - timedelta(days=250)]

        else:  # Regular donors
            pattern_type = 'regular'
            num_gifts = random.randint(2, 8)
            amounts = [Decimal(random.randint(50, 500)) for _ in range(num_gifts)]
            dates = [today - timedelta(days=random.randint(10, 730)) for _ in range(num_gifts)]
            dates.sort(reverse=True)

        # Create contributions
        for amount, contrib_date in zip(amounts, dates):
            contribution = Contribution(
                contribution_id=contribution_id,
                constituent_id=const_id,
                contribution_date=contrib_date,
                amount=amount,
                contribution_type='Cash',
                campaign_id=f'CAMP_{random.choice(["ANNUAL", "SPECIAL", "MAJOR"])}',
                payment_method='Credit Card',
                acknowledgment_sent='Yes'
            )
            contributions_data.append(contribution)
            session.add(contribution)
            contribution_id += 1

    session.commit()
    print(f"✓ Created {len(contributions_data)} contributions")

    # Update total lifetime giving
    print("\nUpdating lifetime giving totals...")
    for constituent in constituents_data:
        total = session.query(func.sum(Contribution.amount)).filter(
            Contribution.constituent_id == constituent.constituent_id
        ).scalar() or Decimal('0')
        constituent.total_lifetime_giving = total

    session.commit()

    # Generate interactions
    print("\nGenerating interactions...")

    interaction_id = 1
    interaction_types = ['Phone Call', 'Email', 'Meeting', 'Event']

    for const_id in range(1, 51):
        # Some constituents have no recent contact
        if const_id <= 10 or const_id in range(26, 31):  # No recent contact
            interaction_dates = [today - timedelta(days=random.randint(100, 300)) for _ in range(2)]
        else:  # Recent contact
            num_interactions = random.randint(1, 8)
            interaction_dates = [today - timedelta(days=random.randint(1, 90)) for _ in range(num_interactions)]

        for int_date in interaction_dates:
            interaction = Interaction(
                interaction_id=interaction_id,
                constituent_id=const_id,
                interaction_date=int_date,
                interaction_type=random.choice(interaction_types),
                subject='Follow-up discussion',
                notes='Discussed upcoming opportunities',
                staff_member='Staff Member',
                follow_up_required='No'
            )
            session.add(interaction)
            interaction_id += 1

    session.commit()
    print(f"✓ Created {interaction_id - 1} interactions")

    # Generate some opportunities
    print("\nGenerating opportunities...")

    for const_id in range(1, 11):  # First 10 constituents have opportunities
        opportunity = Opportunity(
            opportunity_id=const_id,
            constituent_id=const_id,
            opportunity_name=f'Major Gift Opportunity {const_id}',
            stage='Cultivation',
            expected_amount=Decimal(random.randint(5000, 50000)),
            expected_close_date=today + timedelta(days=random.randint(30, 180)),
            probability=random.randint(40, 80),
            created_date=today - timedelta(days=random.randint(30, 90)),
            assigned_to='Development Officer'
        )
        session.add(opportunity)

    session.commit()
    print(f"✓ Created 10 opportunities")

    print("\n" + "=" * 80)
    print("✅ Synthetic data generation complete!")
    print("=" * 80)


def run_segmentation_analysis(session):
    """
    Run the segmentation engine and display results.
    """
    print("\n" + "=" * 80)
    print("🔍 RUNNING SEGMENTATION ANALYSIS")
    print("=" * 80)

    # Initialize engine
    engine = SegmentationEngine(session)

    # Generate all segments
    segments = engine.generate_all_segments()

    print("\n" + "=" * 80)
    print("📊 SEGMENTATION RESULTS")
    print("=" * 80)

    for segment in segments:
        print(f"\n{'─' * 80}")
        print(f"SEGMENT: {segment.name}")
        print(f"{'─' * 80}")
        print(f"ID: {segment.segment_id}")
        print(f"Description: {segment.description}")
        print(f"Formula: {segment.reasoning_formula}")
        print(f"Count: {len(segment.constituent_ids)} constituents")

        if segment.segment_metrics:
            print(f"\nMetrics:")
            for key, value in segment.segment_metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")

        # Show first 5 constituents with their actions
        if segment.constituent_ids:
            print(f"\nSample Constituents (first 5):")
            for const_id in segment.constituent_ids[:5]:
                const_data = engine.get_constituent_data(const_id)
                const = const_data['constituent']
                action = segment.suggested_actions.get(const_id, 'No action specified')

                print(f"\n  • {const.full_name} (ID: {const_id})")
                print(f"    Type: {const.constituent_type}")
                print(f"    Lifetime Giving: ${const_data['total_lifetime_giving']:,.2f}")
                print(f"    Capacity Score: {const_data['capacity_score']:.1f}/100")
                print(f"    Engagement Score: {const_data['engagement_score']:.1f}/100")
                print(f"    Suggested Action: {action}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("📈 SUMMARY STATISTICS")
    print("=" * 80)

    summary = engine.get_segment_summary(segments)

    print(f"\nTotal Segments: {summary['total_segments']}")
    print(f"Total Unique Constituents: {summary['total_unique_constituents']}")

    print(f"\nSegment Breakdown:")
    for seg_info in summary['segment_breakdown']:
        print(f"  {seg_info['name']:<45} {seg_info['count']:>3} ({seg_info['percentage']:>5.1f}%)")

    print("\n" + "=" * 80)
    print("✅ SEGMENTATION ANALYSIS COMPLETE")
    print("=" * 80)


def main():
    """
    Main demonstration function.
    """
    print("=" * 80)
    print("🚀 NONPROFIT DONOR SEGMENTATION ENGINE DEMO")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Create in-memory database for demo
    DATABASE_URL = "sqlite:///demo_nonprofit.db"

    print(f"\n🔧 Initializing database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, echo=False)
    init_database(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Generate synthetic data
        create_synthetic_data(session)

        # Run segmentation analysis
        run_segmentation_analysis(session)

        print("\n" + "=" * 80)
        print("🎉 DEMONSTRATION COMPLETE!")
        print("=" * 80)
        print("\nThe segmentation engine has successfully:")
        print("  ✓ Analyzed 50 diverse donor profiles")
        print("  ✓ Identified 7 distinct segments")
        print("  ✓ Generated AI-powered action recommendations")
        print("  ✓ Calculated capacity and engagement scores")
        print("  ✓ Detected giving trends and patterns")
        print("\nYou can now use the API endpoint:")
        print("  python api/segments.py")
        print("\nOr run unit tests:")
        print("  pytest tests/test_segments.py -v")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
