"""
Solution mapping node: matches each identified opportunity against the
solutions catalog. Deterministic-ish by design — the LLM picks from a fixed
list rather than inventing solution names, so output stays grounded in what
the company actually offers.
"""
import json
import re
from pathlib import Path

from app.config import call_llm

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "solutions_catalog.json"


def load_catalog() -> list[dict]:
    with open(CATALOG_PATH, "r") as f:
        data = json.load(f)
    return data["solutions"]


SYSTEM = (
    "You match sales opportunities to a fixed catalog of solutions. For each "
    "opportunity, choose the single best-fitting solution from the catalog "
    "below, and explain the fit in one sentence. You MUST only use solution "
    "names exactly as they appear in the catalog — never invent a new "
    "solution name. If no catalog solution genuinely fits an opportunity, "
    " For every opportunity listed, choose the single closest-fitting solution from the catalog below, even if the fit is imperfect — you must map every opportunity to exactly one solution. Copy the solution_name value character-for-character from the catalog. In your rationale, be honest about fit: if the match is a strong fit, say so; if it's a stretch, say plainly why it's still the closest available option rather than overselling it\n\n"
    "Respond with ONLY valid JSON, no markdown fences, in this exact shape:\n"
    '{{"mapped_solutions": [{{"opportunity_title": "...", "solution_name": "...", '
    '"solution_description": "...", "rationale": "..."}}]}}\n\n'
    "Catalog:\n{catalog}"
)


def map_solutions(opportunities: list[dict]) -> dict:
    """
    Returns {"mapped_solutions": list[dict], "error": str|None}
    """
    if not opportunities:
        return {"mapped_solutions": [], "error": "No opportunities to map."}

    catalog = load_catalog()
    catalog_text = "\n".join(f"- {s['name']}: {s['description']}" for s in catalog)

    system = SYSTEM.format(catalog=catalog_text)
    user = "Opportunities:\n" + json.dumps(opportunities, indent=2)

    raw = call_llm(system, user, max_tokens=800)
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(cleaned)
        mapped = parsed.get("mapped_solutions", [])
    except json.JSONDecodeError as e:
        return {
            "mapped_solutions": [],
            "error": f"Could not parse solution mapping JSON from LLM output: {e}",
        }

    # Validation guard: drop any mapping that hallucinated a solution name
    # not actually in the catalog, rather than silently trusting the LLM.
    valid_names = {s["name"] for s in catalog}
    filtered = [m for m in mapped if m.get("solution_name") in valid_names]
    dropped = len(mapped) - len(filtered)

    error = None
    if dropped:
        error = (
            f"Dropped {dropped} mapped solution(s) that referenced a "
            "solution name not in the catalog."
        )

    return {"mapped_solutions": filtered, "error": error}
