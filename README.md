# AURA — Autonomous Unified Revenue Agent

A guarded, multi-channel revenue operations backend. This repository contains the API foundation and a Cloudflare Workers deployment adapter; it is not yet an autonomous publishing or revenue-generating system.

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
- Cloudflare Python Worker adapter and D1 schema
- API-key protection for all write and private-data endpoints

## Not yet included
Platform OAuth, content generation/orchestration, publishing, affiliate feed integrations, scheduler, analytics attribution and web dashboard. These require implementation, platform-specific approval and secure secret configuration.

## Local development
The original local FastAPI app remains available:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs. The local SQLite mode is for development only.

## Cloudflare Workers deployment (Free plan target)
AURA now includes a Python Workers adapter at `cloudflare/worker.py`, configured by `wrangler.jsonc`. Cloudflare documents FastAPI support in Python Workers and D1 database bindings. The Workers Free plan currently has usage limits (including 100,000 requests/day and a 10 ms CPU limit); D1 Free also has daily row read/write limits. Free Workers may be suspended after extended inactivity. This is a prototype hosting target, not a guarantee of uninterrupted production service.

Official references:
- https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- https://developers.cloudflare.com/d1/examples/query-d1-from-python-workers/
- https://developers.cloudflare.com/workers/platform/limits/

### One-time setup
1. Create or sign in to a Cloudflare account and stay on the Free plan. Do not add a paid subscription or enable paid add-ons.
2. Install Python 3.13+ and `uv` on your Windows laptop.
3. In a terminal, clone this repository and enter its folder.
4. Create the D1 database:
   ```bash
   uv run pywrangler d1 create aura-autopilot-db
   ```
5. Copy the database ID returned by Cloudflare and replace the all-zero placeholder in `wrangler.jsonc` with that ID. Do not commit any API key or secret.
6. Apply the database schema:
   ```bash
   uv run pywrangler d1 execute aura-autopilot-db --remote --file=cloudflare/schema.sql
   ```
7. Set the API key as a Cloudflare secret. Generate a strong random value locally, then run:
   ```bash
   uv run pywrangler secret put AURA_API_KEY
   ```
   Paste the secret into the terminal prompt only, never into GitHub or this chat.
8. Deploy:
   ```bash
   uv run pywrangler deploy
   ```
9. Test the public `/health` endpoint. For protected endpoints, send the `X-AURA-API-Key` header.

If Cloudflare asks for payment information or proposes a paid upgrade, stop and do not proceed. No paid resource is authorized. Availability of account signup and Free features can vary by region and account verification.

### API security
- `/`, `/health` and `/config` are public read-only endpoints.
- `/opportunities`, `/approvals` and `/ledger` require the `X-AURA-API-Key` header.
- If `AURA_API_KEY` is not configured, protected endpoints fail closed.
- Do not store the API key in source control, frontend code, screenshots or chat.

## Safety
- Legal and platform-compliant activity only.
- No fake engagement, spam, impersonation, copyright infringement or policy evasion.
- Never commit credentials, passwords, OTPs or recovery codes.
- OAuth must use least-privilege scopes and managed secrets.
- Paid ads, purchases, transfers, withdrawals, security changes, contracts and external commitments require human approval.
- Estimates must be distinguished from confirmed revenue.
- No paid infrastructure or spend is authorized by this repository configuration.
