"""
Generate sample data for the Nonprofit CRM system.

This script uses Faker to generate realistic sample data for constituents,
contributions, interactions, and opportunities.
"""
import random
from datetime import datetime, timedelta, date
from decimal import Decimal
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Constituent, Contribution, Interaction, Opportunity
from config import settings


# Initialize Faker
fake = Faker()

# Create database engine and session
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def generate_constituents(session, count=50):
    """Generate sample constituent records."""
    print(f"Generating {count} constituents...")
    constituents = []

    constituent_types = ["donor", "volunteer", "board_member", "staff", "other"]
    statuses = ["active", "active", "active", "active", "inactive"]  # Weight toward active

    for _ in range(count):
        constituent = Constituent(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number()[:20],
            address=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr(),
            zip_code=fake.zipcode(),
            constituent_type=random.choice(constituent_types),
            status=random.choice(statuses),
            notes=fake.text(max_nb_chars=200) if random.random() > 0.7 else None,
        )
        session.add(constituent)
        constituents.append(constituent)

    session.commit()
    print(f"✓ Created {count} constituents")
    return constituents


def generate_contributions(session, constituents, count=100):
    """Generate sample contribution records."""
    print(f"Generating {count} contributions...")

    contribution_types = ["cash", "check", "credit_card", "stock", "in_kind"]
    campaigns = ["Annual Fund 2024", "Capital Campaign", "Emergency Relief", "Education Fund", None]
    appeals = ["Direct Mail", "Email Campaign", "Phone-a-thon", "Event", "Online", None]

    for _ in range(count):
        constituent = random.choice(constituents)
        contribution_date = fake.date_between(start_date="-2y", end_date="today")

        # Generate realistic contribution amounts
        amount_ranges = [
            (25, 100, 0.4),    # Small donations (40% chance)
            (100, 500, 0.3),   # Medium donations (30% chance)
            (500, 2000, 0.2),  # Large donations (20% chance)
            (2000, 10000, 0.1) # Major gifts (10% chance)
        ]

        rand = random.random()
        cumulative = 0
        for min_amt, max_amt, probability in amount_ranges:
            cumulative += probability
            if rand <= cumulative:
                amount = Decimal(str(random.randint(min_amt, max_amt)))
                break

        contribution = Contribution(
            constituent_id=constituent.constituent_id,
            contribution_date=contribution_date,
            amount=amount,
            contribution_type=random.choice(contribution_types),
            campaign=random.choice(campaigns),
            appeal=random.choice(appeals),
            notes=fake.sentence() if random.random() > 0.8 else None,
        )
        session.add(contribution)

    session.commit()
    print(f"✓ Created {count} contributions")


def generate_interactions(session, constituents, count=150):
    """Generate sample interaction records."""
    print(f"Generating {count} interactions...")

    interaction_types = ["email", "phone", "meeting", "event", "letter"]
    outcomes = ["Positive", "Neutral", "Follow-up needed", "Not interested", None]

    for _ in range(count):
        constituent = random.choice(constituents)
        interaction_date = fake.date_time_between(start_date="-1y", end_date="now")

        interaction = Interaction(
            constituent_id=constituent.constituent_id,
            interaction_date=interaction_date,
            interaction_type=random.choice(interaction_types),
            subject=fake.sentence(nb_words=6),
            notes=fake.text(max_nb_chars=300) if random.random() > 0.5 else None,
            outcome=random.choice(outcomes),
        )
        session.add(interaction)

    session.commit()
    print(f"✓ Created {count} interactions")


def generate_opportunities(session, constituents, count=30):
    """Generate sample opportunity records."""
    print(f"Generating {count} opportunities...")

    stages = ["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"]
    campaigns = ["Major Gifts 2024", "Capital Campaign", "Planned Giving", "Annual Fund"]

    for _ in range(count):
        constituent = random.choice(constituents)

        # Generate opportunities with realistic amounts and probabilities
        stage = random.choice(stages)
        amount = Decimal(str(random.randint(5000, 100000)))

        # Probability based on stage
        probability_map = {
            "prospecting": random.randint(10, 30),
            "qualification": random.randint(30, 50),
            "proposal": random.randint(50, 70),
            "negotiation": random.randint(70, 90),
            "closed_won": 100,
            "closed_lost": 0,
        }

        probability = probability_map[stage]

        # Expected close date based on stage
        if stage in ["closed_won", "closed_lost"]:
            expected_close_date = fake.date_between(start_date="-6m", end_date="today")
        else:
            expected_close_date = fake.date_between(start_date="today", end_date="+1y")

        opportunity = Opportunity(
            constituent_id=constituent.constituent_id,
            opportunity_name=f"{fake.company()} - {random.choice(campaigns)}",
            amount=amount,
            probability=probability,
            stage=stage,
            expected_close_date=expected_close_date,
            campaign=random.choice(campaigns),
            notes=fake.text(max_nb_chars=200) if random.random() > 0.6 else None,
        )
        session.add(opportunity)

    session.commit()
    print(f"✓ Created {count} opportunities")


def main():
    """Main function to generate all sample data."""
    print("=" * 60)
    print("Nonprofit CRM - Sample Data Generator")
    print("=" * 60)

    # Create tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")

    # Create session
    session = SessionLocal()

    try:
        # Check if data already exists
        existing_constituents = session.query(Constituent).count()
        if existing_constituents > 0:
            response = input(f"\n⚠ Database already contains {existing_constituents} constituents. Delete and recreate? (yes/no): ")
            if response.lower() != "yes":
                print("Aborted.")
                return

            print("\nDeleting existing data...")
            session.query(Opportunity).delete()
            session.query(Interaction).delete()
            session.query(Contribution).delete()
            session.query(Constituent).delete()
            session.commit()
            print("✓ Existing data deleted")

        # Generate data
        print("\nGenerating sample data...\n")
        constituents = generate_constituents(session, count=50)
        generate_contributions(session, constituents, count=100)
        generate_interactions(session, constituents, count=150)
        generate_opportunities(session, constituents, count=30)
        create_segmentation_test_data(session)

        # Print summary
        print("\n" + "=" * 60)
        print("Sample Data Generation Complete!")
        print("=" * 60)
        print(f"✓ Constituents:   {session.query(Constituent).count()}")
        print(f"✓ Contributions:  {session.query(Contribution).count()}")
        print(f"✓ Interactions:   {session.query(Interaction).count()}")
        print(f"✓ Opportunities:  {session.query(Opportunity).count()}")
        print("\nDatabase ready for testing!")
        print(f"Default login: username=admin, password=secret")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def create_segmentation_test_data(session):
    """Create deterministic constituents that satisfy segmentation rules."""
    print("\nAdding curated constituents for segmentation testing...")
    today = datetime.now().date()

    def add_constituent(**kwargs):
        record = Constituent(**kwargs)
        session.add(record)
        session.flush()
        return record

    def add_contributions(cid, entries):
        total = Decimal("0")
        for amount, days_ago in entries:
            contrib_date = today - timedelta(days=days_ago)
            amount_dec = Decimal(str(amount))
            session.add(
                Contribution(
                    constituent_id=cid,
                    contribution_date=contrib_date,
                    amount=amount_dec,
                    contribution_type="check",
                    campaign="Strategic Fund",
                )
            )
            total += amount_dec
        return total

    def add_interactions(cid, days_list):
        for days_ago in days_list:
            interaction_date = datetime.now() - timedelta(days=days_ago)
            session.add(
                Interaction(
                    constituent_id=cid,
                    interaction_date=interaction_date,
                    interaction_type="meeting",
                    subject="Relationship touchpoint",
                    outcome="Positive",
                )
            )

    curated = []

    # High capacity, low recent giving
    donor = add_constituent(
        first_name="Helena",
        last_name="Chambers",
        email="helena.chambers@example.org",
        phone="(555) 123-4567",
        address="400 Legacy Way",
        city="Boston",
        state="MA",
        zip_code="02108",
        constituent_type="donor",
        status="active",
        notes="Long-term major donor with recent lapse.",
    )
    donor.total_lifetime_giving = add_contributions(
        donor.constituent_id,
        [(15000, 400), (20000, 600)],
    )
    add_interactions(donor.constituent_id, [500])
    curated.append(donor)

    # Increasing giving pattern
    donor = add_constituent(
        first_name="Marcus",
        last_name="Lee",
        email="marcus.lee@example.org",
        phone="(555) 234-7890",
        address="88 Momentum Ave",
        city="Seattle",
        state="WA",
        zip_code="98101",
        constituent_type="donor",
        status="active",
    )
    donor.total_lifetime_giving = add_contributions(
        donor.constituent_id,
        [(200, 300), (250, 250), (275, 200), (350, 150), (450, 100), (600, 30)],
    )
    add_interactions(donor.constituent_id, [90, 60, 20])
    curated.append(donor)

    # Declining giving pattern
    donor = add_constituent(
        first_name="Priya",
        last_name="Kumar",
        email="priya.kumar@example.org",
        phone="(555) 777-8888",
        address="12 Horizon Ln",
        city="Austin",
        state="TX",
        zip_code="73301",
        constituent_type="donor",
        status="active",
    )
    donor.total_lifetime_giving = add_contributions(
        donor.constituent_id,
        [(1500, 40), (1200, 80), (900, 120), (700, 160), (500, 200), (300, 240)],
    )
    add_interactions(donor.constituent_id, [150, 120])
    curated.append(donor)

    # No recent contact
    donor = add_constituent(
        first_name="Caleb",
        last_name="Morales",
        email="caleb.morales@example.org",
        phone="(555) 321-5555",
        address="75 Silent Creek Dr",
        city="Denver",
        state="CO",
        zip_code="80202",
        constituent_type="donor",
        status="active",
    )
    donor.total_lifetime_giving = add_contributions(
        donor.constituent_id,
        [(400, 60), (350, 120), (500, 200)],
    )
    add_interactions(donor.constituent_id, [200, 190])
    curated.append(donor)

    # Potential major donor
    donor = add_constituent(
        first_name="Selena",
        last_name="Nguyen",
        email="selena.nguyen@example.org",
        phone="(555) 654-7890",
        address="910 Vista Blvd",
        city="San Jose",
        state="CA",
        zip_code="95112",
        constituent_type="board_member",
        status="active",
    )
    donor.total_lifetime_giving = add_contributions(
        donor.constituent_id,
        [(3000, 90), (3500, 60), (4000, 30), (4500, 10)],
    )
    add_interactions(donor.constituent_id, [70, 50, 30, 10, 5])
    curated.append(donor)

    # Major donor neglected
    donor = add_constituent(
        first_name="Jonathan",
        last_name="Baird",
        email="jonathan.baird@example.org",
        phone="(555) 123-9999",
        address="60 Heritage Path",
        city="Chicago",
        state="IL",
        zip_code="60601",
        constituent_type="board_member",
        status="active",
    )
    donor.total_lifetime_giving = add_contributions(
        donor.constituent_id,
        [(10000, 400), (15000, 200)],
    )
    add_interactions(donor.constituent_id, [400])
    curated.append(donor)

    # Seasonal giver (July focus)
    donor = add_constituent(
        first_name="Amelia",
        last_name="Stone",
        email="amelia.stone@example.org",
        phone="(555) 888-1234",
        address="15 Summer Ridge",
        city="Miami",
        state="FL",
        zip_code="33101",
        constituent_type="donor",
        status="active",
    )
    seasonal_entries = []
    for year_offset in range(0, 3):
        july = date(today.year - year_offset, 7, 15)
        seasonal_entries.append((600 + year_offset * 50, (today - july).days))
        november = date(today.year - year_offset, 11, 20)
        seasonal_entries.append((200, (today - november).days))
    donor.total_lifetime_giving = add_contributions(donor.constituent_id, seasonal_entries)
    add_interactions(donor.constituent_id, [30, 180])
    curated.append(donor)

    session.commit()
    print(f"✓ Added {len(curated)} curated constituents")


if __name__ == "__main__":
    main()
