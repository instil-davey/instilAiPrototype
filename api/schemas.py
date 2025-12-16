"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field


# Constituent Schemas
class ConstituentBase(BaseModel):
    """Base constituent schema with common fields."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    constituent_type: str = Field(..., pattern="^(donor|volunteer|board_member|staff|other)$")
    status: str = Field(default="active", pattern="^(active|inactive|deceased)$")
    notes: Optional[str] = None


class ConstituentCreate(ConstituentBase):
    """Schema for creating a new constituent."""
    pass


class ConstituentUpdate(BaseModel):
    """Schema for updating a constituent (all fields optional)."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    constituent_type: Optional[str] = Field(None, pattern="^(donor|volunteer|board_member|staff|other)$")
    status: Optional[str] = Field(None, pattern="^(active|inactive|deceased)$")
    notes: Optional[str] = None


class ConstituentResponse(ConstituentBase):
    """Schema for constituent response."""
    constituent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Contribution Schemas
class ContributionBase(BaseModel):
    """Base contribution schema."""
    constituent_id: int
    contribution_date: date
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    contribution_type: str = Field(..., pattern="^(cash|check|credit_card|stock|in_kind|other)$")
    campaign: Optional[str] = Field(None, max_length=100)
    appeal: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class ContributionCreate(ContributionBase):
    """Schema for creating a new contribution."""
    pass


class ContributionUpdate(BaseModel):
    """Schema for updating a contribution."""
    contribution_date: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    contribution_type: Optional[str] = Field(None, pattern="^(cash|check|credit_card|stock|in_kind|other)$")
    campaign: Optional[str] = Field(None, max_length=100)
    appeal: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class ContributionResponse(ContributionBase):
    """Schema for contribution response."""
    contribution_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Interaction Schemas
class InteractionBase(BaseModel):
    """Base interaction schema."""
    constituent_id: int
    interaction_date: datetime
    interaction_type: str = Field(..., pattern="^(email|phone|meeting|event|letter|call|other)$")
    subject: str = Field(..., max_length=200)
    notes: Optional[str] = None
    outcome: Optional[str] = Field(None, max_length=100)


class InteractionCreate(InteractionBase):
    """Schema for creating a new interaction."""
    pass


class InteractionUpdate(BaseModel):
    """Schema for updating an interaction."""
    interaction_date: Optional[datetime] = None
    interaction_type: Optional[str] = Field(None, pattern="^(email|phone|meeting|event|letter|call|other)$")
    subject: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    outcome: Optional[str] = Field(None, max_length=100)


class InteractionResponse(InteractionBase):
    """Schema for interaction response."""
    interaction_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Opportunity Schemas
class OpportunityBase(BaseModel):
    """Base opportunity schema."""
    constituent_id: int
    opportunity_name: str = Field(..., max_length=200)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    probability: int = Field(..., ge=0, le=100)
    stage: str = Field(..., pattern="^(prospecting|qualification|proposal|negotiation|closed_won|closed_lost)$")
    expected_close_date: date
    campaign: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    """Schema for creating a new opportunity."""
    pass


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""
    opportunity_name: Optional[str] = Field(None, max_length=200)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    probability: Optional[int] = Field(None, ge=0, le=100)
    stage: Optional[str] = Field(None, pattern="^(prospecting|qualification|proposal|negotiation|closed_won|closed_lost)$")
    expected_close_date: Optional[date] = None
    campaign: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class OpportunityResponse(OpportunityBase):
    """Schema for opportunity response."""
    opportunity_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardStats(BaseModel):
    """Dashboard statistics schema."""
    total_constituents: int
    active_constituents: int
    total_contributions: Decimal
    contributions_this_year: Decimal
    contributions_this_month: Decimal
    average_contribution: Decimal
    total_opportunities: int
    open_opportunities: int
    pipeline_value: Decimal
    weighted_pipeline: Decimal
    recent_interactions: int


# Pagination
class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List
    total: int
    page: int
    page_size: int
    pages: int
