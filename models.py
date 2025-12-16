"""
Nonprofit CRM ORM Models
SQLAlchemy models for the nonprofit CRM database
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()


class Constituent(Base):
    """
    Represents donors, volunteers, board members, and other constituents
    in the nonprofit CRM system.
    """
    __tablename__ = 'constituents'

    constituent_id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)
    constituent_type = Column(String(50), nullable=False)
    status = Column(String(20), default='active')
    notes = Column(Text, nullable=True)
    created_date = Column(Date, nullable=False, default=func.current_date())
    total_lifetime_giving = Column(Numeric(12, 2), default=Decimal('0.00'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contributions = relationship(
        "Contribution",
        back_populates="constituent",
        cascade="all, delete-orphan"
    )
    interactions = relationship(
        "Interaction",
        back_populates="constituent",
        cascade="all, delete-orphan"
    )
    opportunities = relationship(
        "Opportunity",
        back_populates="constituent",
        cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task",
        back_populates="constituent",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            constituent_type.in_([
                'donor', 'volunteer', 'board_member', 'staff', 'other'
            ]),
            name='chk_constituent_type'
        ),
        CheckConstraint(
            status.in_(['active', 'inactive', 'deceased']),
            name='chk_constituent_status'
        ),
        Index('idx_constituents_email', 'email'),
        Index('idx_constituents_type', 'constituent_type'),
        Index('idx_constituents_created_date', 'created_date'),
        Index('idx_constituents_name', 'last_name', 'first_name'),
    )

    def __repr__(self):
        return f"<Constituent(id={self.constituent_id}, name='{self.first_name} {self.last_name}', type='{self.constituent_type}')>"

    @property
    def full_name(self) -> str:
        """Returns the full name of the constituent."""
        return f"{self.first_name} {self.last_name}"


class Contribution(Base):
    """
    Represents monetary and in-kind contributions from constituents.
    """
    __tablename__ = 'contributions'

    contribution_id = Column(Integer, primary_key=True)
    constituent_id = Column(
        Integer,
        ForeignKey('constituents.constituent_id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    contribution_date = Column(Date, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    contribution_type = Column(String(50), nullable=False)
    campaign = Column(String(100), nullable=True)
    appeal = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    constituent = relationship("Constituent", back_populates="contributions")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            contribution_type.in_([
                'cash', 'check', 'credit_card', 'stock', 'in_kind', 'other'
            ]),
            name='chk_contribution_type'
        ),
        CheckConstraint(
            "amount >= 0",
            name='chk_amount_positive'
        ),
        Index('idx_contributions_constituent', 'constituent_id'),
        Index('idx_contributions_date', 'contribution_date'),
        Index('idx_contributions_campaign', 'campaign'),
        Index('idx_contributions_type', 'contribution_type'),
        Index('idx_contributions_amount', 'amount'),
    )

    def __repr__(self):
        return f"<Contribution(id={self.contribution_id}, constituent_id={self.constituent_id}, amount=${self.amount}, date={self.contribution_date})>"


class Interaction(Base):
    """
    Represents interactions (meetings, calls, emails, events) with constituents.
    """
    __tablename__ = 'interactions'

    interaction_id = Column(Integer, primary_key=True)
    constituent_id = Column(
        Integer,
        ForeignKey('constituents.constituent_id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    interaction_date = Column(DateTime, nullable=False)
    interaction_type = Column(String(50), nullable=False)
    subject = Column(String(200), nullable=False)
    notes = Column(Text, nullable=True)
    outcome = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    constituent = relationship("Constituent", back_populates="interactions")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            interaction_type.in_([
                'email', 'phone', 'meeting', 'event', 'letter', 'call', 'other'
            ]),
            name='chk_interaction_type'
        ),
        Index('idx_interactions_constituent', 'constituent_id'),
        Index('idx_interactions_date', 'interaction_date'),
        Index('idx_interactions_type', 'interaction_type'),
    )

    def __repr__(self):
        return f"<Interaction(id={self.interaction_id}, constituent_id={self.constituent_id}, type='{self.interaction_type}', date={self.interaction_date})>"


class Opportunity(Base):
    """
    Represents fundraising opportunities and pipeline management.
    """
    __tablename__ = 'opportunities'

    opportunity_id = Column(Integer, primary_key=True)
    constituent_id = Column(
        Integer,
        ForeignKey('constituents.constituent_id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    opportunity_name = Column(String(200), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    probability = Column(Integer, nullable=False)
    stage = Column(String(50), nullable=False)
    expected_close_date = Column(Date, nullable=False)
    campaign = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    constituent = relationship("Constituent", back_populates="opportunities")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            stage.in_([
                'prospecting', 'qualification', 'proposal', 'negotiation',
                'closed_won', 'closed_lost'
            ]),
            name='chk_opportunity_stage'
        ),
        CheckConstraint(
            "probability >= 0 AND probability <= 100",
            name='chk_probability_range'
        ),
        CheckConstraint(
            "amount >= 0",
            name='chk_amount_positive'
        ),
        Index('idx_opportunities_constituent', 'constituent_id'),
        Index('idx_opportunities_stage', 'stage'),
        Index('idx_opportunities_close_date', 'expected_close_date'),
        Index('idx_opportunities_amount', 'amount'),
    )

    def __repr__(self):
        return f"<Opportunity(id={self.opportunity_id}, name='{self.opportunity_name}', stage='{self.stage}', amount=${self.amount})>"

    @property
    def weighted_amount(self) -> Optional[Decimal]:
        """Calculate weighted amount based on probability."""
        if self.amount and self.probability:
            return self.amount * Decimal(self.probability) / Decimal(100)
        return None


# =============================================================================
# DATABASE UTILITIES
# =============================================================================

def create_database_engine(database_url: str):
    """
    Create a SQLAlchemy engine for the given database URL.

    Args:
        database_url: Database connection string
                     Examples:
                     - SQLite: 'sqlite:///nonprofit_crm.db'
                     - PostgreSQL: 'postgresql://user:pass@localhost/dbname'

    Returns:
        SQLAlchemy Engine instance
    """
    return create_engine(database_url, echo=False)


def init_database(engine):
    """
    Initialize the database by creating all tables.

    Args:
        engine: SQLAlchemy Engine instance
    """
    Base.metadata.create_all(engine)
    print("✓ Database tables created successfully")


def get_session(engine) -> Session:
    """
    Create a new database session.

    Args:
        engine: SQLAlchemy Engine instance

    Returns:
        SQLAlchemy Session instance
    """
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


# =============================================================================
# QUERY UTILITIES
# =============================================================================

def get_constituent_summary(session: Session, constituent_id: int) -> dict:
    """
    Get a summary of a constituent's giving and interactions.

    Args:
        session: Database session
        constituent_id: ID of the constituent

    Returns:
        Dictionary with constituent summary data
    """
    constituent = session.query(Constituent).filter_by(
        constituent_id=constituent_id
    ).first()

    if not constituent:
        return None

    contribution_count = session.query(func.count(Contribution.contribution_id)).filter(
        Contribution.constituent_id == constituent_id
    ).scalar()

    total_contributions = session.query(func.sum(Contribution.amount)).filter(
        Contribution.constituent_id == constituent_id
    ).scalar() or Decimal('0.00')

    average_contribution = (
        total_contributions / contribution_count if contribution_count > 0 else Decimal('0.00')
    )

    last_contribution = session.query(Contribution).filter(
        Contribution.constituent_id == constituent_id
    ).order_by(Contribution.contribution_date.desc()).first()

    return {
        'constituent_id': constituent.constituent_id,
        'full_name': constituent.full_name,
        'email': constituent.email,
        'constituent_type': constituent.constituent_type,
        'contribution_count': contribution_count,
        'total_contributions': float(total_contributions),
        'average_contribution': float(average_contribution),
        'last_contribution_date': last_contribution.contribution_date if last_contribution else None,
    }


def get_campaign_performance(session: Session) -> List[dict]:
    """
    Get performance metrics for all campaigns.

    Args:
        session: Database session

    Returns:
        List of dictionaries with campaign performance data
    """
    from sqlalchemy import func

    results = session.query(
        Contribution.campaign,
        func.count(Contribution.contribution_id).label('count'),
        func.sum(Contribution.amount).label('total'),
        func.avg(Contribution.amount).label('average')
    ).filter(
        Contribution.campaign.isnot(None)
    ).group_by(
        Contribution.campaign
    ).order_by(
        func.sum(Contribution.amount).desc()
    ).all()

    return [
        {
            'campaign': r.campaign,
            'contribution_count': r.count,
            'total_raised': float(r.total or 0),
            'average_gift': float(r.average or 0)
        }
        for r in results
    ]


# Database session management for FastAPI
from sqlalchemy.orm import sessionmaker

# Create engine (will be initialized by the FastAPI app)
engine = None
SessionLocal = None


def init_db(database_url: str = "sqlite:///nonprofit_crm.db"):
    """
    Initialize the database engine and session factory.

    Args:
        database_url: Database connection string
    """
    global engine, SessionLocal
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function for FastAPI to get database sessions.

    Yields:
        Database session
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class Task(Base):
    """Represents follow-up tasks generated from interactions."""
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True)
    constituent_id = Column(
        Integer,
        ForeignKey('constituents.constituent_id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    description = Column(Text, nullable=False)
    status = Column(String(20), default='pending')
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    constituent = relationship("Constituent", back_populates="tasks")

    __table_args__ = (
        CheckConstraint(
            status.in_(['pending', 'completed']),
            name='chk_task_status'
        ),
        Index('idx_tasks_constituent', 'constituent_id'),
        Index('idx_tasks_status', 'status'),
    )
