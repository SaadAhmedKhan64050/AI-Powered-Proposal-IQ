# Proposal IQ — Frontend

Angular wizard UI for Proposal IQ: a 5-stage flow (intake → research →
opportunities → solutions → email) that walks a non-developer through
generating and sending a research-backed proposal report.

## Prerequisites

- Node.js 18+ and npm
- The backend running first (see `../proposal-iq/README.md`) — this app
  expects it at `http://localhost:8000`

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Confirm the backend is running** at http://localhost:8000/health
   before starting the frontend.

3. **Run the frontend**
   ```bash
   npx ng serve --port 4200
   ```

4. **Open** http://localhost:4200

## How the wizard works

| Route | Stage |
|---|---|
| `/` | Intake form — company name, URL, contact name, contact email |
| `/runs/:id/research` | Shows research findings, grouped into 5 fixed sections |
| `/runs/:id/opportunities` | Shows opportunities identified from the research |
| `/runs/:id/solutions` | Shows each opportunity mapped to a solution, plus a report preview |
| `/runs/:id/email` | Review the report, then press **Send report** — nothing is sent before this explicit action |

A stepper across the top shows progress and lets you navigate back to any
completed stage. Refreshing or directly opening a stage's URL re-fetches
that run's current state rather than losing progress.

## Configuration

`src/environments/environment.ts` sets the backend URL for local
development (`http://localhost:8000`). Update
`src/environments/environment.prod.ts` before deploying anywhere other than
localhost.

## Troubleshooting

- **"Could not reach the API"** — confirm the backend is running and
  reachable at the URL set in `environment.ts`.
- **TS5011 / rootDir build error** — this is a TypeScript 6.0 compatibility
  issue if a newer global TypeScript/Angular CLI is installed alongside this
  Angular 18 project. Pin TypeScript to the version in this project's
  `package.json`: `npm install typescript@<version-from-package.json> --save-dev`,
  then delete `node_modules`/`package-lock.json` and reinstall.