"""Claude AI integration for interaction summarisation and merge scoring."""
import json
import re
from difflib import SequenceMatcher
import anthropic
from app.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

PROMPT_VERSION = 1

SYSTEM_PROMPT = """You are a CRM assistant. Process raw interaction notes and extract structured business intelligence.

Rules:
- Write a concise business-focused summary (2-4 sentences)
- REMOVE: personal health info, family matters, opinions about third parties, gossip, exact personal financial details, home addresses, relationship drama
- KEEP: business decisions, deal status, action items, timelines, business context
- Extract concrete action points with dates where mentioned
- If no date mentioned for an action point, leave due_date as null
- Respond ONLY with valid JSON, no markdown, no extra text

Response format:
{
  "summary": "string",
  "action_points": [
    {"text": "string", "due_date": "YYYY-MM-DD or null", "priority": "high|medium|low"}
  ],
  "follow_up_date": "YYYY-MM-DD or null",
  "key_topics": ["string"],
  "sentiment": "positive|neutral|negative"
}"""


def summarise_interaction(raw_content: str, contact_name: str = "", model: str = "claude-haiku-4-5-20251001") -> dict:
    """Call Claude to summarise an interaction. Returns parsed JSON dict."""
    user_message = f"Contact: {contact_name}\n\nInteraction notes:\n{raw_content[:6000]}"

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_response = message.content[0].text
    # Strip potential markdown code fences
    cleaned = re.sub(r"```(?:json)?", "", raw_response).strip()
    result = json.loads(cleaned)
    result["_model_used"] = model
    result["_raw_response"] = raw_response
    return result


def score_merge_candidates(contacts: list) -> list[dict]:
    """
    Compare all contact pairs and return scored merge suggestions.
    Returns list of {contact_a_id, contact_b_id, confidence_score, reasons}.
    """
    suggestions = []
    for i in range(len(contacts)):
        for j in range(i + 1, len(contacts)):
            a, b = contacts[i], contacts[j]
            reasons = []
            score = 0.0

            # Exact email match — high confidence
            if a.email and b.email and a.email.lower() == b.email.lower():
                score = 1.0
                reasons.append("same email")

            # Name similarity
            a_name = f"{a.first_name or ''} {a.last_name or ''}".strip().lower()
            b_name = f"{b.first_name or ''} {b.last_name or ''}".strip().lower()
            name_sim = SequenceMatcher(None, a_name, b_name).ratio()
            if name_sim > 0.85 and score < 1.0:
                score = max(score, 0.75)
                reasons.append(f"similar name ({name_sim:.0%})")

            if score > 0.4:
                suggestions.append({
                    "contact_a_id": str(a.id),
                    "contact_b_id": str(b.id),
                    "confidence_score": score,
                    "reasons": json.dumps(reasons),
                })

    return suggestions
