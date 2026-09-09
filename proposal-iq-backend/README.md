# Proposal IQ — Backend

FastAPI + LangGraph pipeline that researches a company, identifies sales
opportunities, maps them to a solutions catalog, drafts a report, and emails
it (as HTML + PDF attachment) to a given contact.

## Prerequisites

- Python 3.10+
- An API key from OpenAI (or Anthropic) — https://platform.openai.com/api-keys
- A free API key from Resend — https://resend.com/api-keys

## Setup

1. **Create and activate a virtual environment**

   Windows (PowerShell):
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

   Mac/Linux:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment file**

   Windows:
   ```powershell
   copy .env.example .env
   ```
   Mac/Linux:
   ```bash
   cp .env.example .env
   ```

   Open `.env` and fill in:
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your-key-here
   RESEND_API_KEY=your-key-here
   ```

4. **Run the server**
   ```bash
   uvicorn proposal_iq.api:app --reload --port 8000
   ```

5. **Confirm it's running** — open http://localhost:8000/health in a browser;
   it should return `{"status": "ok"}`. Interactive API docs are at
   http://localhost:8000/docs.

## How it works

Two ways to drive the pipeline:

- **Wizard endpoints** (`POST /api/runs`, then `/opportunities`, `/solutions`,
  `/send-email`) — one stage per call, so a human reviews and approves
  before moving on. This is what the Angular frontend uses.
- **One-shot endpoint** (`POST /api/proposals`) — runs the whole pipeline in
  a single call. Useful for batch-testing multiple companies without
  clicking through the wizard each time.

## Important: the solutions catalog is a placeholder

`proposal_iq/data/solutions_catalog.json` contains generic, illustrative
solution descriptions — not a real product catalog. Replace it with your own
solution set, written independently, before using this for anything beyond
a demo.

## Troubleshooting

- **"ANTHROPIC_API_KEY is not set" even though you're using OpenAI** — check
  `LLM_PROVIDER=openai` is set correctly in `.env` (no quotes, no spaces
  around `=`), and that you restarted uvicorn after editing `.env`
  (`--reload` does not pick up `.env` changes, only `.py` file changes).
- **502 on `/api/runs`** — the target company's site couldn't be fetched
  (dead URL, blocking automated requests, or malformed URL). Check the
  `detail` field in the error response for specifics.
- **Email doesn't send** — confirm `RESEND_API_KEY` is set and valid; check
  the `email_error` field in the run's response for the exact reason.