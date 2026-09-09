"""
Opportunity identification node: turns research notes into a short list of
concrete opportunities, each grounded in something specific from the research
(so the mapping/report stages aren't reasoning over vague guesses).
"""
import json
import re

from proposal_iq.config import call_llm

SYSTEM = (
    "You are a B2B sales analyst for a logistics-technology company. Given "
    "research notes about a prospect, identify 2-4 concrete business "
    "opportunities where logistics/supply-chain technology could help them. "
    "Every opportunity must cite specific evidence from the notes — do not "
    "invent details not present in the research. If the research is too thin "
    "to support any grounded opportunity, return an empty list rather than "
    "guessing.\n\n"
    "Respond with ONLY valid JSON, no markdown fences, no preamble, in this "
    "exact shape:\n"
    '{"opportunities": [{"title": "...", "description": "...", "evidence": "..."}]}'
)


def identify_opportunities(company_name: str, research_notes: str) -> dict:
    """
    Returns {"opportunities": list[dict], "error": str|None}
    """
    if not research_notes.strip():
      return {
            "opportunities": [],
            "error": "No research notes available — skipping opportunity identification.",
        }

    user = f"Company: {company_name}\n\nResearch notes:\n{research_notes}"
    raw = call_llm(SYSTEM, user, max_tokens=800)

    # Defensive parsing: strip accidental code fences if the model adds them.
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(cleaned)
        opportunities = parsed.get("opportunities", [])
        return {"opportunities": opportunities, "error": None}
    except json.JSONDecodeError as e:
        return {
            "opportunities": [],
            "error": f"Could not parse opportunities JSON from LLM output: {e}",
        }
