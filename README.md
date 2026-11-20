# AURA — Autonomous Unified Revenue Agent

AURA is a guarded revenue-operations platform foundation. It helps record opportunities, route risky actions for human approval, and track confirmed income and expenses. **It does not yet discover opportunities automatically, publish content, connect social accounts, or generate guaranteed revenue.**

## Operating rules
- Opportunity channels: YouTube, TikTok, Google, website, Instagram and marketplace affiliate programs.
- Guarded autonomy: human approval is required before any expenditure or external commitment.
- An approval record is not an instruction to execute a payment. AURA currently does not execute payments.
- Legal, platform-compliant activity only; no spam, fake engagement, impersonation, copyright infringement or policy evasion.
- Estimates and confirmed ledger entries remain separate.

## Current features
- FastAPI API on Cloudflare Python Workers.
- Cloudflare D1 persistence for opportunities, approvals, ledger and audit log.
- Browser dashboard at `/dashboard`.
- API-key protection for private data and write endpoints.
- Opportunity pipeline statuses: proposed, reviewing, shortlisted, rejected and archived.
- Human approval queue with pending, approved and rejected decisions.
- Income/expense ledger and summary.
- Audit trail for key record changes.

## Not implemented yet
Platform OAuth, automated opportunity research, content generation, publishing, affiliate feed integrations, scheduler, analytics attribution, automated revenue optimization and multi-user roles. These require separate implementation, platform-specific approvals and secure credential configuration. The current dashboard is an operations console, not a fully autonomous business agent.

## Cloudflare deployment (Free plan target)

The deployment target is Cloudflare Workers + D1. Free-plan quotas and availability are subject to Cloudflare's current terms and account eligibility; do not enable paid add-ons. No spending is authorized.

Official documentation:
- https://developers.cloudflare.com/workers/languages/python/
- https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- https://developers.cloudflare.com/d1/
- https://developers.cloudflare.com/workers/platform/limits/

### One-time setup from Windows

Prerequisites: Git, Python 3.13+, Node.js LTS and `uv`. Open PowerShell:

```powershell
git clone https://github.com/ranggalazuardy-source/aura-autopilot.git
cd aura-autopilot
```

Authenticate Wrangler with the Cloudflare account:

```powershell
npx wrangler login
```

Create the D1 database:

```powershell
uv run pywrangler d1 create aura-autopilot-db
```

Cloudflare returns a database ID. Replace the all-zero placeholder in `wrangler.jsonc` with that exact ID. Do not guess the ID or commit secrets.

Apply the schema (safe to rerun because tables and indexes use `IF NOT EXISTS`):

```powershell
uv run pywrangler d1 execute aura-autopilot-db --remote --file=cloudflare/schema.sql
```

Create a strong API key locally and set it as a Cloudflare secret. Paste it only into the terminal prompt:

```powershell
uv run pywrangler secret put AURA_API_KEY
```

Deploy:

```powershell
uv run pywrangler deploy
```

Build the Virtual Office assets before deployment using npm install --prefix virtual-office and npm run build --prefix virtual-office.

After deployment, open the Worker URL and visit /health, /dashboard, then /office/ for the interactive 3D agent office. Enter the API key in the dashboard. The key is kept in the current browser session only. Private endpoints reject requests without the key.

If Cloudflare asks for payment information or proposes a paid upgrade, stop. Do not enter payment details or enable paid resources.

### Local development

```powershell
uv sync
uv run pywrangler dev
```

The local SQLite FastAPI app under `app/main.py` is a lightweight development alternative, not feature parity with the Cloudflare Worker. Its private endpoints also require `AURA_API_KEY`. Generate a fresh key in PowerShell, then start it:

```powershell
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements-local.txt
$env:AURA_API_KEY = (python -c "import secrets; print(secrets.token_urlsafe(32))")
uvicorn app.main:app --reload
```

The local app writes to `aura.db` by default and includes a local audit log. Do not use its SQLite database as production storage. The repository's old Render blueprint was removed because it defaulted to an ephemeral SQLite database; Cloudflare Workers + D1 remains the supported deployment target.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Public health check |
| GET | `/config` | Public operating configuration |
| GET | `/dashboard` | Browser operations console |
| GET/POST | `/opportunities` | List/create opportunities |
| POST | `/opportunities/{id}/status` | Update pipeline status |
| GET/POST | `/approvals` | List/create approval requests |
| POST | `/approvals/{id}/decision?decision=approved` | Record approval or rejection |
| GET/POST | `/ledger` | List/create ledger entries |
| GET | `/ledger/summary` | Income, expense and net totals |
| GET | `/audit` | Recent audit events |

All private endpoints require the `X-AURA-API-Key` header. Interactive API documentation is available at `/docs`.

## Security and autonomy boundaries
- Never commit credentials, passwords, OTPs, recovery codes or API keys.
- Keep OAuth scopes least-privilege and store tokens only in managed secrets.
- Paid ads, purchases, transfers, withdrawals, security changes, contracts and external commitments require explicit human approval.
- An approved record does not execute the action; a separate, explicitly authorized integration would be required.
- Confirmed income means a user-recorded ledger entry, not a verified bank settlement.
- No paid infrastructure or expenditure is authorized by this repository.


## Brand and account onboarding
- Brand identity and naming guide: `brand/IDENTITY.md`
- Owner-controlled account setup checklist: `ACCOUNT_SETUP.md`
- Least-privilege provider integration plan: `integrations/OAUTH_PLAN.md`
- Account and credential security policy: `security/ACCOUNT_SECURITY.md`

These documents are preparation only. They do not mean any Google, YouTube, TikTok, Instagram, domain or affiliate account has been created or verified. The owner must create accounts under their own identity, control recovery methods and approve OAuth consent. Suggested handles are unverified until checked directly on each platform.


## Mas Mas Wibu content operations (v0.4.0)

The dashboard now includes a guarded Content tab and D1-backed content queue:
- Create content ideas with platform, format, pillar, hook, script/notes and rights status.
- Move ideas through idea → draft → in_review.
- Approval is blocked unless rights_status is `cleared`.
- Status `approved` is an internal approval only; no video is uploaded or scheduled.
- Initial Mas Mas Wibu starter backlog is seeded by `cloudflare/schema.sql` (14 YouTube Shorts ideas).

After applying the updated schema to D1, the Content tab and API become available. Re-run the full schema safely; table/index creation and seed inserts are idempotent. The new content queue does not connect YouTube OAuth and does not publish content.


## Multi-agent task orchestration (v0.5.0)

AURA now has a persistent agent task queue:
- `POST /agent-tasks` creates a queued task for a named agent.
- `GET /agent-tasks` lists queued and historical tasks.
- `POST /agent-tasks/{id}/status` records a status and result summary.
- The schema seeds initial work items for the 15 defined agent roles.
- `GET /config` reports the owner-approved zero-capital, moderate-risk, 50/50 monthly distribution defaults.

This is a task registry and orchestration foundation, not an autonomous runtime. No agents are running in the background, no external market scans are scheduled, and no integrations or financial transactions are active. Seeded tasks are queued plans, not completed work. Applying the updated D1 schema is required before these endpoints work in production.


## Curated agent skill library

AURA includes four local skill packs curated from relevant capabilities in [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills):
- Market intelligence and opportunity validation
- Growth, content, clipping, affiliate and commerce
- Finance, investment research and risk
- Platform engineering, orchestration and security

See `skills/README.md`, `skills/registry.yaml`, and `docs/skill-adoption-plan.md` for the mapping, provenance, attribution and activation boundaries. These are AURA-authored playbooks and references, not a bulk import of all upstream skills. The Worker bundles the skill instructions for task context preparation; model invocation remains disabled.
\n\n## Skill Loader & Router\n\nThe Worker exposes authenticated skill catalogue and agent-binding endpoints, records deterministic skill-pack routing, and prepares task-scoped contexts. See [`docs/skill-runtime-routing.md`](docs/skill-runtime-routing.md).\n

## Skill context loader and model adapter (v0.7.0)

- `POST /agent-tasks/{id}/prepare` loads assigned skill instructions into a guarded context and returns an OpenAI-compatible request preview.
- `GET /runtime/provider` reports provider readiness.
- The adapter is prepare-only: no provider credentials, model, per-task approved budget or network transport is configured. It cannot call a paid model.
- Task objective is passed as untrusted user input, separate from AURA's system guardrails.
- The D1 routing migration is still required in Cloudflare before deployed task routes work.


## Bounded Agent Execution Engine (v0.7.0)

AURA now supports lease-based task claiming, heartbeats, safe local tool calls, result/evidence recording and task release. The initial tool registry contains pure local `text_stats` and `unit_economics` functions only. No model provider or external side-effect tool is enabled. Completed tasks remain pending QA review.

See `docs/skill-runtime-routing.md` for API behavior and the execution boundary. Apply the complete `cloudflare/schema.sql` to D1 before deployment. CI tests are configured; their latest result has not yet been verified.


## Research Intelligence Engine (v0.8.0)

AURA now includes authenticated research-run tracking, source provenance intake, manual source verification, transparent opportunity scoring, market comparison snapshots, and CEO decision recommendations. The scoring model weights demand, competition, unit economics, zero-capital fit, speed to revenue, skill fit, evidence quality and risk control. Recommendations are advisory only; owner approval remains required.

Research source intake accepts HTTPS URLs and owner/worker-supplied excerpts. It does not crawl or fetch websites, and newly submitted sources remain unverified until manually reviewed. No live search provider, model provider, background worker or paid integration is configured.


## Zero-cost Web Research Adapter (v0.9.0)

AURA adds a public DuckDuckGo HTML search adapter for owner-initiated market research. Results are stored as unverified source leads with excerpts, publisher hostnames and content hashes. Search requests are rate-limited to 10 per 10 minutes globally per deployment. This is a best-effort public HTML integration, not a guaranteed search API; provider markup, availability and terms can change.


The dashboard includes a Research tab for the same workflow: create run → search → inspect and verify source → link source to opportunity → score → compare → record CEO recommendation. All decisions remain advisory and require owner approval.


## 3D Virtual AI Office (v1.0.1)

The /office/ application is a React + Three.js + React Three Fiber isometric office. Each of the 15 registered AURA agents has a persistent visual identity, role, specialty zone and a character that moves between its home workspace, working desk and owner-review area.

The side panel shows the live agent roster, active tasks and audit activity. The browser polls the authenticated GET /office/state endpoint every five seconds. Agent status is derived from D1:
- **Working** only when an in_progress task has a valid, unexpired worker lease.
- **Waiting for input** when the agent has a blocked task.
- **Idle** when there is no active leased task or a task is only queued.
- Expired or missing leases are surfaced as stale; they are not shown as productive work.

The office is a visual operations console, not a simulation of hidden intelligence. It uses the same session API key as /dashboard; the key is kept in sessionStorage, never in the frontend bundle. It does not create background workers or enable model inference.

### Build and preview

Install and start the frontend with:
- npm install --prefix virtual-office
- npm run dev --prefix virtual-office

The Vite app proxies /office/state to http://127.0.0.1:8787 during local development. Start uv run pywrangler dev in a second terminal, and provide the same AURA API key in the dashboard/office login screen.

Create the production bundle before deployment:
- npm run build --prefix virtual-office
- uv run pywrangler deploy

The `assets.base_path` setting requires Wrangler 4.148.0 or newer. Check the Wrangler version used by `pywrangler` before deployment; Cloudflare introduced this subpath feature in Wrangler 4.148.0. Wrangler serves the generated virtual-office/dist bundle under /office. Requests to /office/state miss the static asset manifest and fall through to the authenticated Python Worker API. The D1 schema must already be applied, and the Worker must have AURA_API_KEY configured.

The UI can show real task state only after D1 and the Worker are deployed. When no valid lease exists, it deliberately does not animate an agent as working.


## One-origin production deployment (v1.0.1)

AURA is designed to run on one Cloudflare Worker hostname:
- / — AURA landing page
- /dashboard — main Operations Dashboard
- /office/ — React Three Fiber Virtual Office
- /office/state — authenticated live task and audit telemetry API

Workers.dev is enabled so the first deployment can work without buying a domain. A custom domain can be attached later, but is not required for the single-origin setup.

### One-time GitHub Actions setup

The deployment workflow is .github/workflows/deploy-cloudflare.yml. It provisions or reuses the D1 database named aura-autopilot-db, applies the idempotent SQL schema, sets the Worker API secret, builds the 3D frontend, deploys the Worker, then checks the public health and page routes. It is intentionally manual (workflow_dispatch) until the account secrets have been configured.

1. In Cloudflare, create an API token using the Edit Cloudflare Workers template, then explicitly add Account permission D1: Edit (the template does not include D1 Edit by default). Keep Workers Scripts: Edit, and restrict the token to the one Cloudflare account used for AURA. Cloudflare's GitHub Actions guide uses CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID as CI secrets; never put these values in source code.
2. Get the Cloudflare Account ID from the account overview.
3. Generate a private AURA API key in PowerShell:

   $bytes = New-Object byte[] 32
   $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
   $rng.GetBytes($bytes)
   $rng.Dispose()
   $key = [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+','-').Replace('/','_')
   Set-Clipboard $key

4. In GitHub → Settings → Secrets and variables → Actions, add these repository secrets:
   - CLOUDFLARE_API_TOKEN
   - CLOUDFLARE_ACCOUNT_ID
   - AURA_API_KEY
5. In GitHub → Actions → Deploy AURA to Cloudflare → Run workflow.

The deploy workflow does not create DNS records, purchase a domain, activate paid add-ons, or enable AI model spending. It uses the apac D1 location hint and the existing Workers/D1 account. Check the account's current plan and usage limits; do not approve a paid upgrade or enter payment information.

After a successful deployment, the workflow summary prints the single base URL plus /dashboard and /office/. Use the same AURA API key when signing in to either page. The key is held only in the current browser tab's session storage and is never included in the frontend build.
