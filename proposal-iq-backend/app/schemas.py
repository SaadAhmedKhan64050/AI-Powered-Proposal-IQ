"""
Pydantic schemas for the FastAPI layer. Kept separate from state.py (the
LangGraph state) since the API's public contract and the graph's internal
state don't have to be identical — this is the boundary that lets you change
internals later without breaking clients.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ProposalRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    company_url: HttpUrl
    contact_name: str = Field(..., min_length=1, max_length=200)
    contact_email: EmailStr
    send_email: bool = Field(
        default=True,
        description="If false, runs research/opportunity/report generation but skips sending the email.",
    )


class CreateRunRequest(BaseModel):
    """Starts a new wizard run: just enough to kick off research."""
    company_name: str = Field(..., min_length=1, max_length=200)
    company_url: HttpUrl
    contact_name: str = Field(..., min_length=1, max_length=200)
    contact_email: EmailStr


class Opportunity(BaseModel):
    title: str
    description: str
    evidence: str


class MappedSolution(BaseModel):
    opportunity_title: str
    solution_name: str
    solution_description: str
    rationale: str

class ResearchSection(BaseModel):
    heading: str
    points: list[str]

class ProposalResponse(BaseModel):
    run_id: str
    company_name: str
    research_sections: list[ResearchSection]                              # in ProposalResponse
    research_sources: list[str]
    opportunities: list[Opportunity]
    mapped_solutions: list[MappedSolution]
    report_markdown: str
    report_html: str
    email_sent: bool
    email_error: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)


class RunResponse(BaseModel):
    """
    Represents a wizard run at any stage. Fields not yet produced by the
    pipeline are empty/false rather than null, so the frontend can render
    the same shape at every stage without null-checking each field.
    """
    run_id: str
    company_name: str
    contact_name: str
    contact_email: str
    research_sections: list[ResearchSection] = Field(default_factory=list) # in RunResponse    research_sources: list[str] = Field(default_factory=list)
    research_sources: list[str] = Field(default_factory=list)
    opportunities: list[Opportunity] = Field(default_factory=list)
    mapped_solutions: list[MappedSolution] = Field(default_factory=list)
    report_markdown: str = ""
    report_html: str = ""
    email_sent: bool = False
    email_error: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)


class SolutionCatalogItem(BaseModel):
    name: str
    description: str


class ErrorResponse(BaseModel):
    detail: str
