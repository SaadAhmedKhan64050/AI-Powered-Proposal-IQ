"""
FastAPI interface for Proposal IQ.

Two ways to drive the pipeline:

1. Wizard endpoints (POST /api/runs, then /opportunities, /solutions,
   /send-email) — each stage is a separate call so a human reviews and
   approves before moving on. This is what the Angular frontend uses.

2. One-shot endpoint (POST /api/proposals) — runs the whole pipeline in a
   single call. Useful for the evaluation harness / batch-testing 8-12
   companies without clicking through the wizard each time.

Run locally:
    uvicorn proposal_iq.api:app --reload --port 8000
Then open http://localhost:8000/docs for interactive Swagger UI.
"""
import logging
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from proposal_iq.schemas import (
    ProposalRequest,
    ProposalResponse,
    CreateRunRequest,
    RunResponse,
    SolutionCatalogItem,
    ErrorResponse,
)
from proposal_iq.graph import (
    node_research,
    node_identify_opportunities,
    node_map_solutions,
    node_generate_report,
    node_send_email,
)
from proposal_iq.tools.solutions import load_catalog
from proposal_iq.storage import save_run, load_run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proposal_iq")

app = FastAPI(
    title="Proposal IQ API",
    description=(
        "Takes a company's URL and contact info, researches the company, "
        "identifies opportunities, maps them to solutions, generates a "
        "report, and emails it to the given contact."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _state_to_run_response(state: dict) -> RunResponse:
    return RunResponse(
        run_id=state["run_id"],
        company_name=state.get("company_name", ""),
        contact_name=state.get("contact_name", ""),
        contact_email=state.get("contact_email", ""),
        research_sections=state.get("research_sections", []),    
        research_sources=state.get("research_sources", []),
        opportunities=state.get("opportunities", []),
        mapped_solutions=state.get("mapped_solutions", []),
        report_markdown=state.get("report_markdown", ""),
        report_html=state.get("report_html", ""),
        email_sent=state.get("email_sent", False),
        email_error=state.get("email_error"),
        warnings=state.get("errors", []),
    )


def _load_run_or_404(run_id: str) -> dict:
    state = load_run(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"No run found with id {run_id}")
    return state


@app.get("/health", tags=["meta"])
def health():
    """Basic liveness check."""
    return {"status": "ok"}


@app.get("/api/solutions", response_model=list[SolutionCatalogItem], tags=["meta"])
def get_solutions_catalog():
    """Lists the solutions this system can recommend, for transparency."""
    return load_catalog()


# ---------------------------------------------------------------------------
# Wizard endpoints — one stage per call, state persisted between calls
# ---------------------------------------------------------------------------

@app.post(
    "/api/runs",
    response_model=RunResponse,
    responses={
        502: {"model": ErrorResponse, "description": "Could not research the company"},
        500: {"model": ErrorResponse, "description": "Unexpected internal error"},
    },
    tags=["wizard"],
)
def create_run(request: CreateRunRequest):
    """Stage 1: start a run and research the company."""
    run_id = str(uuid.uuid4())
    state: dict = {
        "company_name": request.company_name,
        "company_url": str(request.company_url),
        "contact_name": request.contact_name,
        "contact_email": request.contact_email,
        "errors": [],
    }

    try:
        state.update(node_research(state))
    except RuntimeError as e:
        logger.exception("Research node failed for run %s", run_id)
        raise HTTPException(status_code=500, detail=str(e))

    save_run(run_id, {**state, "run_id": run_id})

    if not state.get("research_sections"):
        detail = next(iter(state.get("errors", [])), "Could not research the company website.")
        raise HTTPException(status_code=502, detail=detail)

    return _state_to_run_response({**state, "run_id": run_id})


@app.get(
    "/api/runs/{run_id}",
    response_model=RunResponse,
    responses={404: {"model": ErrorResponse, "description": "No run with this id"}},
    tags=["wizard"],
)
def get_run(run_id: str):
    """Fetch the current state of a run — used on page load/refresh."""
    state = _load_run_or_404(run_id)
    return _state_to_run_response(state)


@app.post(
    "/api/runs/{run_id}/opportunities",
    response_model=RunResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["wizard"],
)
def run_opportunities(run_id: str):
    """Stage 2: identify opportunities from the stored research."""
    state = _load_run_or_404(run_id)

    try:
        state.update(node_identify_opportunities(state))
    except RuntimeError as e:
        logger.exception("Opportunities node failed for run %s", run_id)
        raise HTTPException(status_code=500, detail=str(e))

    save_run(run_id, state)
    return _state_to_run_response(state)


@app.post(
    "/api/runs/{run_id}/solutions",
    response_model=RunResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["wizard"],
)
def run_solutions(run_id: str):
    """Stage 3: map opportunities to solutions and generate the report."""
    state = _load_run_or_404(run_id)

    try:
        state.update(node_map_solutions(state))
        state.update(node_generate_report(state))
    except RuntimeError as e:
        logger.exception("Solution mapping/report node failed for run %s", run_id)
        raise HTTPException(status_code=500, detail=str(e))

    save_run(run_id, state)
    return _state_to_run_response(state)


@app.post(
    "/api/runs/{run_id}/send-email",
    response_model=RunResponse,
    responses={
        404: {"model": ErrorResponse},
    },
    tags=["wizard"],
)
def run_send_email(run_id: str):
    """Stage 4: explicitly send the report — only runs on user action."""
    state = _load_run_or_404(run_id)
    state.update(node_send_email(state))
    save_run(run_id, state)
    return _state_to_run_response(state)


# ---------------------------------------------------------------------------
# One-shot endpoint — for batch/evaluation use, not the interactive wizard
# ---------------------------------------------------------------------------

@app.post(
    "/api/proposals",
    response_model=ProposalResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        502: {"model": ErrorResponse, "description": "Could not research the company"},
        500: {"model": ErrorResponse, "description": "Unexpected internal error"},
    },
    tags=["batch"],
)
def create_proposal(request: ProposalRequest):
    """Runs the full pipeline in one call. Intended for batch/eval scripts."""
    run_id = str(uuid.uuid4())
    state: dict = {
        "company_name": request.company_name,
        "company_url": str(request.company_url),
        "contact_name": request.contact_name,
        "contact_email": request.contact_email,
        "errors": [],
    }

    try:
        state.update(node_research(state))
    except RuntimeError as e:
        logger.exception("Research node failed for run %s", run_id)
        raise HTTPException(status_code=500, detail=str(e))

    if not state.get("research_sections"):
        detail = next(iter(state.get("errors", [])), "Could not research the company website.")
        save_run(run_id, {**state, "run_id": run_id})
        raise HTTPException(status_code=502, detail=detail)

    try:
        state.update(node_identify_opportunities(state))
        state.update(node_map_solutions(state))
        state.update(node_generate_report(state))
        if request.send_email:
            state.update(node_send_email(state))
        else:
            state["email_sent"] = False
            state["email_error"] = None
    except RuntimeError as e:
        logger.exception("Pipeline failed for run %s", run_id)
        raise HTTPException(status_code=500, detail=str(e))

    save_run(run_id, {**state, "run_id": run_id})

    return ProposalResponse(
        run_id=run_id,
        company_name=state["company_name"],
        research_sections=state.get("research_sections", []),    
        research_sources=state.get("research_sources", []),
        opportunities=state.get("opportunities", []),
        mapped_solutions=state.get("mapped_solutions", []),
        report_markdown=state.get("report_markdown", ""),
        report_html=state.get("report_html", ""),
        email_sent=state.get("email_sent", False),
        email_error=state.get("email_error"),
        warnings=state.get("errors", []),
    )


@app.get(
    "/api/proposals/{run_id}",
    response_model=ProposalResponse,
    responses={404: {"model": ErrorResponse, "description": "No run with this id"}},
    tags=["batch"],
)
def get_proposal(run_id: str):
    """Fetches a previously generated one-shot report by its run_id."""
    data = _load_run_or_404(run_id)
    return ProposalResponse(
        run_id=run_id,
        company_name=data.get("company_name", ""),
        research_sections=data.get("research_sections", []),    
        research_sources=data.get("research_sources", []),
        opportunities=data.get("opportunities", []),
        mapped_solutions=data.get("mapped_solutions", []),
        report_markdown=data.get("report_markdown", ""),
        report_html=data.get("report_html", ""),
        email_sent=data.get("email_sent", False),
        email_error=data.get("email_error"),
        warnings=data.get("errors", []),
    )
