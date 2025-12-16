"""
Test script for the Constituent Briefing Engine

This script demonstrates the briefing engine functionality using sample data
from the nonprofit CRM database.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import required modules
from models import get_session, Constituent
from src.briefing.engine import BriefingEngine


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_briefing(briefing):
    """Pretty print a briefing."""
    print_separator()
    print("CONSTITUENT BRIEFING")
    print_separator()
    print()

    print("📋 SUMMARY")
    print(briefing['summary'])
    print()

    print("💰 GIVING SUMMARY")
    print(briefing['giving_summary'])
    print()

    print("📊 ENGAGEMENT PATTERN")
    print(briefing['engagement_pattern'])
    print()

    print("⭐ WHY THEY MATTER")
    print(briefing['why_they_matter'])
    print()

    print("🏷️  SEGMENT CLASSIFICATION")
    print(briefing['segment_reason'])
    print()

    print("✅ SUGGESTED ACTION")
    print(briefing['suggested_action'])
    print()

    print_separator("-")
    print("METADATA")
    print_separator("-")
    print(f"Constituent ID: {briefing['metadata']['constituent_id']}")
    print(f"Generated: {briefing['metadata']['generated_at']}")
    print(f"Data Points Analyzed:")
    for key, value in briefing['metadata']['data_points'].items():
        print(f"  - {key}: {value}")
    print()


def test_single_briefing(constituent_id, segments=None):
    """Test generating a briefing for a single constituent."""
    print(f"\n{'='*80}")
    print(f"Testing Briefing Generation for: {constituent_id}")
    print(f"{'='*80}\n")

    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  WARNING: ANTHROPIC_API_KEY not set!")
        print("The engine will use fallback mode (basic briefing without AI).")
        print("To use AI features, set your API key:")
        print("  export ANTHROPIC_API_KEY='your_api_key_here'")
        print()

        # Ask user if they want to continue
        response = input("Continue with fallback mode? (y/n): ")
        if response.lower() != 'y':
            print("Test cancelled.")
            return
        print()

    try:
        # Initialize engine
        print("Initializing briefing engine...")
        if api_key:
            engine = BriefingEngine(api_key=api_key)
            print("✓ AI-powered mode enabled (Claude Sonnet 4.5)")
        else:
            # For testing fallback mode
            os.environ['ANTHROPIC_API_KEY'] = 'test_key'
            engine = BriefingEngine(api_key='test_key')
            print("✓ Fallback mode enabled")
        print()

        # Get database session
        print("Connecting to database...")
        session = get_session()
        print("✓ Database connected")
        print()

        # Verify constituent exists
        print(f"Looking up constituent: {constituent_id}")
        constituent = session.query(Constituent).filter(
            Constituent.constituent_id == constituent_id
        ).first()

        if not constituent:
            print(f"❌ Error: Constituent '{constituent_id}' not found in database")
            print()
            print("Available constituents:")
            constituents = session.query(Constituent).all()
            for c in constituents:
                print(f"  - {c.constituent_id}: {c.full_name} ({c.constituent_type})")
            return

        print(f"✓ Found: {constituent.full_name}")
        print(f"  Type: {constituent.constituent_type}")
        print(f"  Lifetime Giving: ${float(constituent.total_lifetime_giving):,.2f}")
        print()

        # Generate briefing
        print("Generating AI-powered briefing...")
        print("(This may take a few seconds...)")
        print()

        briefing = engine.generate_briefing(
            constituent_id=constituent_id,
            db_session=session,
            segment_names=segments
        )

        # Print the briefing
        print_briefing(briefing)

        print("✓ Briefing generated successfully!")
        print()

    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'session' in locals():
            session.close()


def test_multiple_constituents():
    """Test generating briefings for multiple constituents."""
    print(f"\n{'='*80}")
    print("Testing Multiple Constituent Briefings")
    print(f"{'='*80}\n")

    # Get all constituents
    session = get_session()
    constituents = session.query(Constituent).limit(3).all()

    if not constituents:
        print("❌ No constituents found in database")
        return

    print(f"Found {len(constituents)} constituents to test:\n")
    for c in constituents:
        print(f"  - {c.constituent_id}: {c.full_name}")
    print()

    # Test each one
    for constituent in constituents:
        segments = []
        if constituent.constituent_type == "Major Donor":
            segments.append("Major Donors")
        if constituent.constituent_type == "Board Member":
            segments.append("Board Members")

        test_single_briefing(constituent.constituent_id, segments)
        print("\n" + "="*80 + "\n")

    session.close()


def main():
    """Main test function."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               CONSTITUENT BRIEFING ENGINE - TEST SUITE                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Check if database exists
    db_path = 'nonprofit_crm.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print()
        print("Please run the data ingestion script first:")
        print("  python load_data.py")
        return

    print("Choose a test option:")
    print()
    print("1. Test single constituent briefing (CONST003 - Michael Brown)")
    print("2. Test with custom constituent ID")
    print("3. Test multiple constituents (first 3)")
    print("4. Exit")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        test_single_briefing(
            "CONST003",
            segments=["Major Donors", "Board Members"]
        )
    elif choice == "2":
        constituent_id = input("Enter constituent ID (e.g., CONST001): ").strip()
        segments_input = input("Enter segments (comma-separated, or leave blank): ").strip()
        segments = [s.strip() for s in segments_input.split(',')] if segments_input else None
        test_single_briefing(constituent_id, segments)
    elif choice == "3":
        test_multiple_constituents()
    elif choice == "4":
        print("Goodbye!")
    else:
        print("Invalid choice. Please run again.")

    print()
    print("Test complete!")


if __name__ == "__main__":
    main()
