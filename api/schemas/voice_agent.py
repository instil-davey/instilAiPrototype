"""Schemas for conversational voice agent orchestration."""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    """Represents one entry in the conversational transcript."""

    speaker: Literal["AI", "User"]
    text: str = Field(..., min_length=1)


class SlotValue(BaseModel):
    """Represents structured data captured from the conversation."""

    value: str = ""
    confidence: float = 0.0
    last_updated_turn: Optional[int] = None


class SlotState(BaseModel):
    """Collection of all tracked slots for logging an interaction."""

    who: SlotValue = SlotValue()
    channel: SlotValue = SlotValue()
    summary: SlotValue = SlotValue()
    sentiment: SlotValue = SlotValue()
    next_steps: SlotValue = SlotValue()


class ChecklistState(BaseModel):
    """Represents progress toward collecting required information."""

    missing_fields: List[str] = Field(default_factory=list)
    ready_to_close: bool = False
    notes: Optional[str] = None


class VoiceAgentRequest(BaseModel):
    """Incoming request from the frontend when new user input is available."""

    constituent_id: int
    constituent_name: Optional[str] = None
    conversation: List[ConversationTurn] = Field(default_factory=list)
    latest_user_text: str = Field(..., min_length=1)
    slot_state: SlotState = SlotState()


class VoiceAgentResponse(BaseModel):
    """Response returned to the frontend after agent processing."""

    agent_reply: str
    slot_state: SlotState
    checklist: ChecklistState
    suggested_followups: List[str] = Field(default_factory=list)
