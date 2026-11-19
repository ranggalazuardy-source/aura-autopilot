# AURA — Autonomous Unified Revenue Agent

A guarded, multi-channel revenue operations backend. This repository currently contains the API foundation only; it is not yet an autonomous publishing or revenue-generating system.

## Operating profile
- Opportunity discovery: broad, across YouTube, TikTok, Google, website, Instagram and marketplace affiliate programs.
- Autonomy: guarded.
- Spending: every expenditure requires explicit human approval.
- Goal: diversified, legally earned revenue.

## Included
- FastAPI health and configuration endpoints
- Opportunity register
- Human approval queue
- Income and expense ledger

## Not yet included
Platform OAuth, content generation/orchestration, publishing, affiliate feed integrations, scheduler, analytics attribution and web dashboard. These require implementation, platform-specific approval and secure secret configuration.

## Local run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs.

## Deployment note
The included Render Blueprint uses a free web service and SQLite for an initial smoke test. Free instances may sleep and their local filesystem is not durable; do not use this configuration for production data. A persistent database and paid resources must be reviewed and explicitly approved before provisioning.

## Safety
- Legal and platform-compliant activity only.
- No fake engagement, spam, impersonation, copyright infringement or policy evasion.
- Never commit credentials, passwords, OTPs or recovery codes.
- OAuth must use least-privilege scopes and managed secrets.
- Paid ads, purchases, transfers, withdrawals, security changes, contracts and external commitments require human approval.
- Estimates must be distinguished from confirmed revenue.
