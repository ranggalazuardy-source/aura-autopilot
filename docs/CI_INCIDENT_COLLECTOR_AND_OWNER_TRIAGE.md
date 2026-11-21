# AURA CI Incident Collector and Owner Triage

## Collection
- `.github/workflows/incident-intake.yml` observes completed AURA quality/deployment workflows.
- A first quality failure gets the existing single retry. A persistent quality failure or failed deployment opens/reuses a GitHub issue.
- When GitHub Actions secret `AURA_API_KEY` exists, the trusted workflow-run handler posts only workflow name, run ID/attempt, canonical run URL, branch, commit SHA, conclusion and failed job labels to `POST /repair/incidents`.
- Optional repository variable `AURA_API_BASE_URL` selects the Worker API; otherwise the current AURA Worker URL is used.
- If the secret is absent, issue intake remains functional and Worker ingestion is skipped. No credentials are generated or changed by this code.

## Storage and privacy
- The Worker authenticates the intake with the owner API key.
- `operational_incident_evidence` stores sanitized provenance and failed job names only. It does not accept raw logs, patch text, tokens, candidate paths or model prompts.
- Duplicate workflow attempts are deduplicated by repository/run/attempt.
- `GET /repair/incidents` is owner-authenticated and read-only.

## Owner triage
- A human owner must explicitly call `POST /repair/incidents/{incident_id}/triage` with `confirm_owner_triage=true`.
- Only `automated_test_regression` and `python_syntax_or_import` can be considered for guarded repair planning.
- Candidate paths must be explicitly supplied, unique, and pass the existing `build_repair_plan` allowlist. The service never infers paths from logs.
- Dependency/security audit, database schema, Cloudflare config/deployment, container/runtime, and unclassified incidents cannot carry candidate paths and remain manual-only.
- A valid low-risk triage means eligible for proposal planning, not approval to generate/execute a live patch. Owner approval of the exact patch digest, base SHA and paths remains a separate mandatory step.

## Not enabled by this change
- No automatic model/provider inference, background patch generation, file writes, GitHub branch/PR creation, merge, deployment, D1 production migration or secret setup.
- Provider flags remain disabled. The existing guarded runner remains a separate owner-approved execution path.
