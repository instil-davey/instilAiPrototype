"""Agentic orchestration for conversational voice logger."""
from __future__ import annotations

import re
from typing import List

from anthropic import Anthropic, APIError

from config import settings
from api.schemas.voice_agent import (
    VoiceAgentRequest,
    VoiceAgentResponse,
    ConversationTurn,
    SlotState,
    SlotValue,
    ChecklistState,
)

REQUIRED_FIELDS = ["who", "channel", "summary", "sentiment", "next_steps"]
CHANNEL_KEYWORDS = {
    "call": "phone",
    "phone": "phone",
    "zoom": "video",
    "video": "video",
    "in-person": "in-person",
    "in person": "in-person",
    "email": "email",
    "text": "text",
}


class VoiceAgentOrchestrator:
    """Lightweight orchestration around Anthropic for conversational capture."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.confidence_threshold = settings.VOICE_AGENT_CONFIDENCE_THRESHOLD

    def process(self, payload: VoiceAgentRequest) -> VoiceAgentResponse:
        """Process the latest user input and update slot/checklist state."""

        slot_state = payload.slot_state
        # Update slots using heuristic extraction first for robustness
        self._update_slots_from_text(slot_state, payload.latest_user_text, len(payload.conversation))

        conversation = payload.conversation + [ConversationTurn(speaker="User", text=payload.latest_user_text)]

        agent_reply = self._generate_agent_reply(
            conversation=conversation,
            slot_state=slot_state,
            constituent_name=payload.constituent_name or "this constituent",
        )
        conversation.append(ConversationTurn(speaker="AI", text=agent_reply))

        checklist = self._evaluate_checklist(slot_state)
        suggested_followups: List[str] = []
        if not checklist.ready_to_close:
            for field in checklist.missing_fields:
                if field == "channel":
                    suggested_followups.append("Ask how the conversation happened (call, meeting, email, etc.).")
                elif field == "summary":
                    suggested_followups.append("Ask for the key highlights of the conversation.")
                elif field == "sentiment":
                    suggested_followups.append("Ask how the interaction went and how the constituent responded.")
                elif field == "next_steps":
                    suggested_followups.append("Ask if any follow-up tasks or commitments were discussed.")
        else:
            suggested_followups.append("Confirm collected notes and offer to log the interaction.")

        return VoiceAgentResponse(
            agent_reply=agent_reply,
            slot_state=slot_state,
            checklist=checklist,
            suggested_followups=suggested_followups,
        )

    def _update_slots_from_text(self, slot_state: SlotState, text: str, turn_index: int) -> None:
        lower = text.lower()
        # channel heuristics
        for keyword, normalized in CHANNEL_KEYWORDS.items():
            if keyword in lower and slot_state.channel.confidence < 0.5:
                slot_state.channel = SlotValue(
                    value=normalized,
                    confidence=0.7,
                    last_updated_turn=turn_index,
                )
                break
        # sentiment heuristics
        if any(word in lower for word in ["great", "positive", "excited", "happy"]):
            slot_state.sentiment = SlotValue(value="positive", confidence=0.7, last_updated_turn=turn_index)
        elif any(word in lower for word in ["concerned", "worried", "uncertain", "negative"]):
            slot_state.sentiment = SlotValue(value="concerned", confidence=0.65, last_updated_turn=turn_index)
        # next steps heuristics
        if "follow" in lower or "next" in lower or "task" in lower:
            slot_state.next_steps = SlotValue(value=text.strip(), confidence=0.6, last_updated_turn=turn_index)
        # summary fallback
        if len(text.split()) > 5 and slot_state.summary.confidence < 0.5:
            slot_state.summary = SlotValue(value=text.strip(), confidence=0.5, last_updated_turn=turn_index)

    def _generate_agent_reply(self, conversation: List[ConversationTurn], slot_state: SlotState, constituent_name: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI call scribe helping a major gift officer log an interaction. "
                    "Speak naturally, acknowledge what they said, and ask focused follow-ups."
                ),
            }
        ]
        transcript = "\n".join(f"{turn.speaker}: {turn.text}" for turn in conversation[-8:])
        slot_summary = (
            f"Current slots -> who: {slot_state.who.value or constituent_name}, "
            f"channel: {slot_state.channel.value}, summary: {slot_state.summary.value}, "
            f"sentiment: {slot_state.sentiment.value}, next_steps: {slot_state.next_steps.value}"
        )
        user_prompt = (
            f"Transcript so far:\n{transcript}\n\n"
            f"Structured info: {slot_summary}.\n"
            "Respond with a single sentence. If info is missing, ask a specific question to capture it. "
            "If everything is captured, recap and confirm you're ready to log."
        )
        messages.append({"role": "user", "content": user_prompt})

        try:
            completion = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=messages,
                temperature=0.4,
            )
            return completion.content[0].text.strip()
        except APIError as exc:
            return (
                "Thanks for the update. Could you tell me more about the interaction details and next steps so I can log this?"
            )

    def _evaluate_checklist(self, slot_state: SlotState) -> ChecklistState:
        missing = []
        for field in REQUIRED_FIELDS:
            slot = getattr(slot_state, field)
            if slot.confidence < self.confidence_threshold or not slot.value.strip():
                missing.append(field)
        ready = len(missing) == 0
        notes = None
        if missing:
            notes = f"Need better info for: {', '.join(missing)}"
        else:
            notes = "All required info captured."
        return ChecklistState(missing_fields=missing, ready_to_close=ready, notes=notes)
