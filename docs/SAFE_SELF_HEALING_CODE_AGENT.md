# AURA Safe Self-Healing Code Agent

## Purpose

Turn operational incidents into reproducible, reviewed code repairs while keeping production and spending guarded.

## Autonomy levels

1. **Observe (automatic):** collect workflow outcomes, Worker health, D1 incident/heartbeat data and sanitized error metadata.
2. **Diagnose (automatic):** classify known failure signatures, correlate repeated fingerprints, prepare a repair hypothesis and regression-test proposal.
3. **Prepare (automatic when a code-generation provider is explicitly enabled):** create an isolated repair branch, edit only relevant files, add regression tests, run the complete quality workflow and open a draft pull request.
4. **Review (mandatory):** a human reviews the diff, test results, permissions and blast radius.
5. **Release (owner-controlled):** merge to main and deploy production only after explicit owner authorization.

## Safe repair allowlist

The agent may autonomously:
- Re-run a failed CI job once for likely transient infrastructure failures.
- Create/update incident records and diagnostic reports.
- Create isolated branches and draft PRs for code repairs after an approved code-generation runtime is configured.
- Run unit, architecture, dependency, schema, frontend build and deployment dry-run checks.
- Close its own repair branch without merging if tests fail or a safety check trips.

The agent must not autonomously:
- Merge to `main`, deploy production, or change Cloudflare resources.
- Enable providers, add credentials, spend API quota, purchase services or alter billing.
- Change secrets, permissions, repository security settings, or branch protections.
- Run destructive database migrations, delete user data, or weaken authentication.
- Publish content, contact third parties, or perform financial transactions.

## Repair lifecycle

For each incident:
1. Preserve the original workflow run, commit SHA, job and sanitized logs.
2. Deduplicate using the incident fingerprint/run ID.
3. Classify the failure as transient infrastructure, dependency/audit, syntax/build, test regression, schema, deployment/configuration, security, or unknown.
4. If a known transient CI failure occurs, retry the failed job once.
5. If still failing, create/update a high-signal incident with reproduction details and recommended next diagnostic steps.
6. Once an owner-approved code-generation provider is configured, prepare a branch and draft PR. Never push directly to main.
7. Require all quality checks to pass. Stop on security, auth, billing, secrets, destructive data, or unknown high-risk changes.
8. Record repair outcome and regression test in the incident trail.

## Current implementation boundary

The deployed monitor can record runtime incidents, expose heartbeats, and safely reclaim expired task leases. GitHub Actions can retry a failed quality run once and open an incident ticket after persistent failure. This repository does not yet have an approved autonomous code-generation runtime or a verified patch executor. Therefore arbitrary code bugs are diagnosed/escalated, not silently rewritten. This is intentional until the owner enables a provider and approves its data-processing and quota policy.


Implementation wording: create isolated branches and draft pull request artifacts only after an owner-approved code-generation provider is configured.
