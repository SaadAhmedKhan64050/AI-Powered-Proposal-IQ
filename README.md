# Proposal IQ

An AI system that turns a cold prospect (company name, website, contact)
into a researched, evidence-based sales opportunity report — and emails it,
with human review at every stage.

Built as part of a 5-Day Remote AI OS Sprint. Target user: a B2B sales
representative who currently researches prospects manually or via an ad-hoc
ChatGPT session with no fixed structure or guaranteed grounding.

## What it does

1. **Research** — fetches a company's public website (homepage + an About
   page) and summarizes it into 5 fixed sections (Company Overview,
   Products & Services, Market Position, Operations & Supply Chain, Growth
   & Technology Signals).
2. **Opportunities** — identifies concrete opportunities, each grounded in
   specific evidence from the research — no invented claims.
3. **Solution mapping** — maps every opportunity to the closest-fitting
   solution from a catalog (never an invented solution name).
4. **Report** — drafts a short markdown report and renders it to HTML.
5. **Email** — sends the report (HTML body + PDF attachment) to the given
   contact via Resend — only on an explicit "Send" action, never
   automatically.

Each stage is a separate, reviewable step — nothing (especially sending the
email) happens without a human approving that stage first.

## Repository structure

```
Proposal IQ/
├── Proposal IQ_Backend/    FastAPI + LangGraph pipeline
└── Frontend/               Angular wizard UI
```

Each subfolder has its own detailed README with full setup instructions.
This file is the high-level overview; start with the Quick Start below,
or jump straight to whichever subfolder's README you need.

## Quick Start

You'll need: Python 3.10+, Node.js 18+, an OpenAI (or Anthropic) API key,
and a free Resend API key.

**1. Backend**
```bash
cd "Proposal IQ_Backend"
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
copy .env.example .env         # Windows: copy, Mac/Linux: cp
# edit .env and fill in LLM_PROVIDER, OPENAI_API_KEY, RESEND_API_KEY
uvicorn app.api:app --reload
```
Confirm it's running at http://localhost:8000/health

**2. Frontend** (in a separate terminal, backend must already be running)
```bash
cd Frontend
npm install
npx ng serve --port 4200
```
Open http://localhost:4200

Full details, troubleshooting, and API reference are in each subfolder's
README.

## Architecture

- **Backend**: FastAPI + a LangGraph state machine with five nodes
  (research → identify opportunities → map solutions → generate report →
  send email). Two API surfaces: stepwise wizard endpoints
  (`/api/runs`, `/api/runs/{id}/opportunities`, etc.) for the interactive
  UI, and a one-shot endpoint (`/api/proposals`) for batch/evaluation use.
  State is persisted per-run as flat JSON files — no database.
- **Frontend**: Angular, structured as a 5-stage routed wizard rather than
  a single page, so each stage can be reviewed and approved independently.
- **Email**: Resend (not an internal SMTP server) — simple HTTPS API,
  generous free tier, no company mail infrastructure required.

## Important: the solutions catalog is a placeholder

`Proposal IQ_Backend/proposal_iq/data/solutions_catalog.json` contains
generic, illustrative solution descriptions written independently for this
project — not a real company's product catalog. Replace it with your own
solution set before using this beyond a demo.

## Evaluation

See the project's Evaluation Package document for the test case matrix,
baseline comparison, and root-cause analysis of failures found and fixed
during development.

## License / Ownership Note

This project's code and solutions catalog were built independently for
this sprint and do not reuse any employer's proprietary code, data, or
product catalog.
