"""
State schema for the Proposal IQ agent graph.

This is the single object that flows through every node. Each node reads
what it needs and returns a partial dict that LangGraph merges into state.
"""
from __future__ import annotations

from typing import TypedDict, Optional


class Opportunity(TypedDict):
    title: str
    description: str
    evidence: str  # what in the research supports this opportunity


class MappedSolution(TypedDict):
    opportunity_title: str
    solution_name: str
    solution_description: str
    rationale: str  # why this solution fits this opportunity


class AgentState(TypedDict, total=False):
    # ---- input ----
    company_name: str
    company_url: str
    contact_name: str
    contact_email: str

    # ---- research stage ----
    research_points: list[str]          # raw scraped/summarized findings
    research_sources: list[str]  # URLs actually used

    # ---- opportunity stage ----
    opportunities: list[Opportunity]

    # ---- solution mapping stage ----
    mapped_solutions: list[MappedSolution]

    # ---- report stage ----
    report_markdown: str
    report_html: str

    # ---- email stage ----
    email_sent: bool
    email_error: Optional[str]

    # ---- run metadata (for eval / logging, not shown to the end user) ----
    errors: list[str]
