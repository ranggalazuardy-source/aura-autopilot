# Persisted triage to IT/AI Engineer repair handoff

`app/services/triaged_ci_repair.py` is the controlled boundary between the
owner's persisted CI triage decision and the existing IT/AI Engineer proposal
adapter.

## Preconditions

- Evidence must be a joined row from `operational_incidents` and
  `operational_incident_evidence`.
- Incident source must be GitHub Actions, repository and workflow must match
  the allowlists, and the incident must remain in `investigating`.
- The persisted triage owner must be `IT_AI_ENGINEER`.
- Only `automated_test_regression` and `python_syntax_or_import` categories
  are eligible, with a full immutable commit SHA and persisted candidate paths.
- The caller must explicitly set `confirm_owner_generation=True` before the
  injected generator is invoked.

## Data and capability boundaries

Only normalized incident ID, source, owner, category, and persisted candidate
paths are passed to the generator. Raw logs, run URLs, credentials, and
untrusted diagnostic text are not forwarded. The existing planner and patch
validators still enforce path and diff policy.

The service is side-effect-free. It does not query D1, instantiate a provider,
write files, queue an execution request, consume an approval receipt, create a
branch or PR, merge, or deploy. The returned proposal still requires a separate
owner approval receipt bound to its exact base SHA, patch digest, and paths.

CI uses a deterministic mock generator. Non-mock generators remain blocked
unless a future owner-authorized runtime explicitly supplies provider inference
approval. No production route or scheduled trigger invokes this service yet.


The regression suite also keeps AST-based route assertions independent of Python's
quote-style formatting so semantic checks remain stable across interpreter versions.
