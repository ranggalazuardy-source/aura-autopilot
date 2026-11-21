# Guarded Repair Planner

The repair planner converts an incident classification and proposed candidate paths into a deterministic repair plan. It is a planning-only component.

## Eligibility

The first iteration can prepare an approval-gated plan only for:
- `automated_test_regression`
- `python_syntax_or_import`

Candidate paths must stay within `app/agents/`, `app/services/`, `tests/`, or `docs/`. The planner rejects unknown categories, dependency/security audits, database/schema work, Cloudflare deployment/configuration, container/runtime incidents, path traversal, empty scopes, and scopes larger than six files.

## No side effects

Even a plan with status `ready_for_owner_approval`:
- does not invoke an AI provider;
- does not change files;
- does not write to GitHub;
- does not create commits or pull requests;
- does not merge or deploy.

Owner approval, provider/data-processing approval, a separately implemented patch executor, diff-policy validation, full CI, and human review are still required before a future patch could be proposed.
