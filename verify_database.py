#!/usr/bin/env python3
"""
Database Verification Script
Verifies the database structure and displays sample data
"""

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Constituent, Contribution, Interaction, Opportunity

def main():
    print("=" * 80)
    print("🔍 Database Verification")
    print("=" * 80)

    engine = create_engine('sqlite:///nonprofit_crm.db', echo=False)
    inspector = inspect(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # List all tables
    print("\n📋 Database Tables:")
    print("-" * 80)
    tables = inspector.get_table_names()
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n  {table.upper()}")
        print(f"    Columns: {len(columns)}")
        for col in columns[:5]:  # Show first 5 columns
            print(f"      - {col['name']} ({col['type']})")
        if len(columns) > 5:
            print(f"      ... and {len(columns) - 5} more")

    # Show sample data
    print("\n" + "=" * 80)
    print("📊 Sample Data")
    print("=" * 80)

    # Constituents
    print("\n  CONSTITUENTS (first 3):")
    constituents = session.query(Constituent).limit(3).all()
    for c in constituents:
        print(f"    {c.constituent_id}: {c.full_name} ({c.constituent_type}) - ${c.total_lifetime_giving or 0}")

    # Contributions
    print("\n  CONTRIBUTIONS (first 3):")
    contributions = session.query(Contribution).limit(3).all()
    for contrib in contributions:
        print(f"    {contrib.contribution_id}: ${contrib.amount or 0} from constituent {contrib.constituent_id} - {contrib.contribution_date}")

    # Interactions
    print("\n  INTERACTIONS (first 3):")
    interactions = session.query(Interaction).limit(3).all()
    for i in interactions:
        print(f"    {i.interaction_id}: {i.interaction_type} with constituent {i.constituent_id} - {i.interaction_date}")

    # Opportunities
    print("\n  OPPORTUNITIES (first 3):")
    opportunities = session.query(Opportunity).limit(3).all()
    for o in opportunities:
        print(f"    {o.opportunity_id}: {o.opportunity_name} ({o.stage}) - ${o.expected_amount or 0}")

    # Verify relationships
    print("\n" + "=" * 80)
    print("🔗 Relationship Verification")
    print("=" * 80)

    constituent = session.query(Constituent).first()
    if constituent:
        print(f"\n  Testing constituent: {constituent.full_name}")
        print(f"    Contributions: {len(constituent.contributions)}")
        print(f"    Interactions: {len(constituent.interactions)}")
        print(f"    Opportunities: {len(constituent.opportunities)}")

    contribution = session.query(Contribution).first()
    if contribution:
        print(f"\n  Testing contribution ID: {contribution.contribution_id}")
        print(f"    Constituent: {contribution.constituent.full_name if contribution.constituent else 'None'}")

    print("\n" + "=" * 80)
    print("✅ Database verification completed!")
    print("=" * 80)

    session.close()

if __name__ == "__main__":
    main()
