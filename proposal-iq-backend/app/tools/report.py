"""
Report generation node: turns research + opportunities + mapped solutions
into a short, readable proposal report (markdown, then rendered to simple
HTML for the email body).
"""
import html as html_lib
import json
import re
from xhtml2pdf import pisa
import io
from app.config import call_llm

BOLD_LABEL_LINE = re.compile(r"^\*\*[^*]+\*\*\s*:")
def _inline_format(text: str) -> str:
    escaped = html_lib.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
SYSTEM = (
    "You write concise B2B sales opportunity reports. Tone: professional, "
    "specific, no filler. Use only the facts provided — do not invent "
    "statistics, client names, or claims not present in the input. If the "
    "input is thin, keep the report short rather than padding it."
    " If an opportunity has no corresponding entry in mapped_solutions, "
    "say plainly in that subsection that no catalog solution was a confident fit — do not invent or infer a solution name."
)


def generate_report(
    company_name: str,
    contact_name: str,
    research_notes: str, 
    opportunities: list[dict],
    mapped_solutions: list[dict],
) -> str:
    """Returns the report as markdown text."""
    user = (
        f"Company: {company_name}\n"
        f"Contact: {contact_name}\n\n"
        f"Research notes:\n{research_notes}\n\n"     
        f"Opportunities identified:\n{json.dumps(opportunities, indent=2)}\n\n"
        f"Mapped solutions:\n{json.dumps(mapped_solutions, indent=2)}\n\n"
        "Write a short markdown report with these sections:\n"
        f"# Opportunity Report: {company_name  }\n"
        "## Company Overview (2-3 sentences from the research)\n"
        "## Opportunities & Recommended Solutions (for each opportunity, first "
        "output a line '### <opportunity title>' as its own heading, then "
        "exactly these five lines below it, each starting with '- ' and a bold "
        "label, in this order:\n"
        "- **Opportunity**: <the opportunity, in your own words>\n"
        "- **Evidence**: <the supporting evidence>\n"
        "- **Recommended Solution**: <the solution name>\n"
        "- **Description**: <the solution's description>\n"
        "- **Why It Fits**: <the rationale>\n"
        "Never drop the '- ' prefix on any of these five lines, even if the "
        "content is short. Repeat this heading-plus-five-lines pattern once per "
        "opportunity, with a blank line between each opportunity's block.)\n"
        "## Next Steps (2-3 sentence closing, inviting a follow-up call)\n"
        "Keep the whole report under 400 words."
    )
    return call_llm(SYSTEM, user, max_tokens=1200)


def markdown_to_simple_html(markdown_text: str) -> str:
    """
    Minimal, dependency-free markdown->HTML for email bodies. Not a full
    markdown parser — handles #/##/### headers, blank-line paragraphs, and
    leaves everything else as escaped plain text. Good enough for the LLM's
    consistent report structure; swap in a real markdown lib if you extend
    the report format later.
    """
    lines = markdown_text.strip().splitlines()
    html_parts = [
        '<div style="font-family: Arial, sans-serif; max-width: 640px; '
        'margin: 0 auto; color: #1a1a1a; line-height: 1.5;">'
    ]
    paragraph_buffer: list[str] = []

    def flush_paragraph():
        if paragraph_buffer:
            text = " ".join(paragraph_buffer)
            html_parts.append(f"<p>{_inline_format(text)}</p>") 
            paragraph_buffer.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            html_parts.append(f"<h3>{_inline_format(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            flush_paragraph()
            html_parts.append(f"<h2>{_inline_format(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            flush_paragraph()
            html_parts.append(f"<h1>{_inline_format(stripped[2:])}</h1>")
        elif stripped.startswith(("- ", "* ")):
            flush_paragraph()
            html_parts.append(f"<li>{_inline_format(stripped[2:])}</li>")

        elif BOLD_LABEL_LINE.match(stripped):
            flush_paragraph()
            html_parts.append(f"<li>{_inline_format(stripped)}</li>")
        else:
            paragraph_buffer.append(stripped)

    flush_paragraph()
    html_parts.append("</div>")
    return "\n".join(html_parts)

def html_to_pdf_bytes(html: str) -> bytes:
    buffer = io.BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    return buffer.getvalue()