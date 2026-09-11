"""
Research node: fetches the company's website and summarizes it into
research notes the later nodes can reason over.

Kept deliberately simple for v1: fetch homepage (+ an "about" page if we can
find one), strip boilerplate, hand the text to the LLM to summarize. No
external search API required, so this works with zero extra API keys beyond
your LLM provider.
"""
import json, re
import requests
from bs4 import BeautifulSoup

from app.config import call_llm, REQUEST_TIMEOUT_SECONDS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ProposalIQBot/0.1; "
        "+https://example.com/bot-info)"
    )
}

# Common "about" style paths worth trying if the homepage doesn't have enough.
ABOUT_PATH_CANDIDATES = ["/about", "/about-us", "/company", "/who-we-are"]
FIXED_HEADINGS = [
    "Company Overview",
    "Products & Services",
    "Market Position",
    "Operations & Supply Chain",
    "Growth & Technology Signals",
]

def _fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        if resp.status_code != 200:
            return None
        return resp.text
    except requests.RequestException:
        return None


def _extract_text(html: str, max_chars: int = 6000) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]

def sections_to_text(sections: list[dict]) -> str:
    """
    Flattens the sectioned research (list of {"heading", "points"} dicts)
    back into a single plain-text block, for prompts (opportunities/report)
    that just need readable text and don't care about the section structure.
    """
    parts = []
    for section in sections:
        heading = section.get("heading", "")
        points = section.get("points", [])
        bullet_lines = "\n".join(f"- {p}" for p in points)
        parts.append(f"{heading}:\n{bullet_lines}")


    return "\n\n".join(parts)

def research_company(company_url: str, company_name: str) -> dict:
    """
Returns {"research_sections": list[dict], "research_sources": list[str], "error": str|None}
    """
    sources = []
    raw_text_chunks = []

    homepage_html = _fetch(company_url)
    if homepage_html is None:
        return {
"research_sections": [{"heading": h, "points": []} for h in FIXED_HEADINGS], 
           "research_sources": [],
            "error": (
                f"Could not fetch {company_url}. It may be down, blocking "
                "automated requests, or the URL may be malformed."
            ),
        }

    sources.append(company_url)
    raw_text_chunks.append(_extract_text(homepage_html))

    # Best-effort: try one "about" page. Not fatal if it fails.
    base = company_url.rstrip("/")
    for path in ABOUT_PATH_CANDIDATES:
        about_html = _fetch(base + path)
        if about_html:
            sources.append(base + path)
            raw_text_chunks.append(_extract_text(about_html))
            break

    combined_text = "\n\n---\n\n".join(raw_text_chunks)
    if not combined_text.strip():
        return {
           "research_sections": [{"heading": h, "points": []} for h in FIXED_HEADINGS],
            "research_sources": sources,
            "error": f"Fetched {company_url} but found no readable text content.",
        }

    system = (
        "You summarize company website content into concise, factual research "
        "points for a B2B sales analyst. Only state what is supported by the "
        "provided text. Organize your findings into exactly these five "
        "sections, in this order: \"Company Overview\", \"Products & "
        "Services\", \"Market Position\", \"Operations & Supply Chain\", "
        "\"Growth & Technology Signals\". "
        "Every section must have at least 1 point — never leave a section's "
        "points list empty. If the source text has no direct information for a "
        "section, write a reasonable inference from context instead (e.g. if "
        "there's no explicit 'Market Position' text but the company describes "
        "itself as an industry leader, use that). Only if there is truly zero "
        "usable context anywhere in the text should a section contain a single "
        "point saying so plainly, e.g. \"No information available from the "
        "source website.\" — never fabricate specific facts, numbers, or claims "
        "not supported by the text. "
        "Respond with "
        "ONLY valid JSON, no markdown, no preamble, in this exact shape: "
        '{"sections": [{"heading": "Company Overview", "points": ["...", '
        '"..."]}, {"heading": "Products & Services", "points": [...]}, '
        '{"heading": "Market Position", "points": [...]}, {"heading": '
        '"Operations & Supply Chain", "points": [...]}, {"heading": "Growth '
        '& Technology Signals", "points": [...]}]}. Each point is one '
        "plain-text sentence, no markdown formatting, no asterisks. 1-4 "
        "points per section."
    )
    user = (
        f"Company name: {company_name}\n"
        f"Website text (from {', '.join(sources)}):\n\n{combined_text}\n\n"
        "Fill in the five fixed sections listed in the system instructions, "
        "based only on what's supported by this text."
    )
    raw = call_llm(system, user, max_tokens=600)
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        sections = json.loads(cleaned).get("sections", [])
    except json.JSONDecodeError:
        sections = [{"heading": h, "points": []} for h in FIXED_HEADINGS]

    for section in sections:
        if not section.get("points"):
            section["points"] = ["No information available from the source website."]
    return {"research_sections": sections, "research_sources": sources, "error": None}
