"""
Example usage of the Suggested Action Generator

This script demonstrates how to use the generator both directly
and via the API endpoint.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import create_database_engine, get_session
from segments import get_constituent_segment, get_segment_info
from src.actions.generator import generate_suggested_action

# Load environment variables
load_dotenv()


def example_direct_usage():
    """
    Example: Using the generator directly (without API)
    """
    print("=" * 70)
    print("EXAMPLE 1: Direct Generator Usage")
    print("=" * 70)

    # Set up database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nonprofit_crm.db")
    engine = create_database_engine(DATABASE_URL)
    session = get_session(engine)

    try:
        # Example 1: Generate action for constituent ID 1
        constituent_id = 1

        print(f"\nGenerating suggested action for constituent {constituent_id}...")

        # First, let's see what segments this constituent belongs to
        segments = get_constituent_segment(session, constituent_id)
        print(f"\nConstituent Segments: {[s.value for s in segments]}")

        # Generate suggested action
        result = generate_suggested_action(
            session=session,
            constituent_id=constituent_id,
            segment_id=None  # Let it choose the primary segment
        )

        # Display results
        if result["success"]:
            print(f"\n✓ Success!")
            print(f"\nConstituent: {result['constituent_name']}")
            print(f"Target Segment: {result['target_segment']}")
            print(f"\nSuggested Action:")
            print("-" * 70)
            print(result['suggested_action'])
            print("-" * 70)
        else:
            print(f"\n✗ Error: {result['error']}")

    finally:
        session.close()


def example_segment_specific():
    """
    Example: Generate action for a specific segment
    """
    print("\n\n" + "=" * 70)
    print("EXAMPLE 2: Segment-Specific Action")
    print("=" * 70)

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nonprofit_crm.db")
    engine = create_database_engine(DATABASE_URL)
    session = get_session(engine)

    try:
        constituent_id = 2
        target_segment = "lapsed_donor"

        print(f"\nGenerating action for constituent {constituent_id}")
        print(f"Focusing on segment: {target_segment}")

        result = generate_suggested_action(
            session=session,
            constituent_id=constituent_id,
            segment_id=target_segment
        )

        if result["success"]:
            print(f"\n✓ Success!")
            print(f"\nConstituent: {result['constituent_name']}")
            print(f"All Segments: {result['segments']}")
            print(f"Target Segment: {result['target_segment']}")
            print(f"\nSuggested Action:")
            print("-" * 70)
            print(result['suggested_action'])
            print("-" * 70)
        else:
            print(f"\n✗ Error: {result['error']}")

    finally:
        session.close()


def example_batch_processing():
    """
    Example: Process multiple constituents
    """
    print("\n\n" + "=" * 70)
    print("EXAMPLE 3: Batch Processing Multiple Constituents")
    print("=" * 70)

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nonprofit_crm.db")
    engine = create_database_engine(DATABASE_URL)
    session = get_session(engine)

    try:
        # Get first 3 constituents from database
        from models import Constituent

        constituents = session.query(Constituent).limit(3).all()

        print(f"\nProcessing {len(constituents)} constituents...")

        for constituent in constituents:
            print(f"\n{'-' * 70}")
            print(f"Constituent: {constituent.full_name} (ID: {constituent.constituent_id})")

            result = generate_suggested_action(
                session=session,
                constituent_id=constituent.constituent_id
            )

            if result["success"]:
                print(f"Segments: {', '.join(result['segments'])}")
                print(f"Target: {result['target_segment']}")
                print(f"\nAction Preview:")
                # Show first 200 characters of action
                action_preview = result['suggested_action'][:200] + "..."
                print(action_preview)
            else:
                print(f"Error: {result['error']}")

    finally:
        session.close()


def example_api_usage():
    """
    Example: Using the API endpoint (requires API to be running)
    """
    print("\n\n" + "=" * 70)
    print("EXAMPLE 4: API Usage")
    print("=" * 70)

    print("\nTo use the API endpoint:")
    print("-" * 70)

    # Example curl commands
    print("\n1. Start the API server:")
    print("   $ cd api")
    print("   $ python suggested_action.py")
    print("   (or)")
    print("   $ uvicorn suggested_action:app --reload")

    print("\n2. List available segments:")
    print("   $ curl http://localhost:8000/api/segments")

    print("\n3. Generate suggested action:")
    print("""   $ curl -X POST http://localhost:8000/api/suggested-action \\
     -H "Content-Type: application/json" \\
     -d '{
       "constituent_id": 1,
       "segment_id": "major_donor"
     }'""")

    print("\n4. Using Python requests library:")
    print("""
   import requests

   response = requests.post(
       "http://localhost:8000/api/suggested-action",
       json={
           "constituent_id": 1,
           "segment_id": "major_donor"
       }
   )

   result = response.json()
   print(result["suggested_action"])
   """)


def show_available_segments():
    """
    Display all available segments
    """
    from segments import SEGMENT_DEFINITIONS

    print("\n\n" + "=" * 70)
    print("AVAILABLE SEGMENTS")
    print("=" * 70)

    for segment_type, info in SEGMENT_DEFINITIONS.items():
        print(f"\n{info['name']} ({segment_type.value})")
        print(f"  Priority: {info['priority']}")
        print(f"  Description: {info['description']}")


def main():
    """
    Main function to run all examples
    """
    print("\n" + "=" * 70)
    print("NONPROFIT FUNDRAISER SUGGESTED ACTION GENERATOR")
    print("Example Usage Demonstrations")
    print("=" * 70)

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: ANTHROPIC_API_KEY not found in environment")
        print("Please set your API key to run the examples:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nShowing available segments only...\n")
        show_available_segments()
        example_api_usage()
        return

    # Show available segments
    show_available_segments()

    # Run examples (uncomment to run)
    print("\n\n⚠️  Note: The following examples will use your Anthropic API key")
    print("and will incur API costs. Uncomment the lines in main() to run them.")

    # Uncomment these lines to run the examples:
    # example_direct_usage()
    # example_segment_specific()
    # example_batch_processing()
    example_api_usage()

    print("\n\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
