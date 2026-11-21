# Async D1-backed patch execution bridge

```python
from app.services.async_patch_execution import execute_approved_patch_with_d1

result = await execute_approved_patch_with_d1(
    request,
    db=request_env.DB,
    workspace=workspace_adapter,
)
```

## Safety sequence

1. Run the existing executor's full deterministic validation against a validation-only workspace. No branch, file, GitHub, or network writes occur in this phase.
2. Atomically consume the exact owner-bound D1 receipt using the conditional `UPDATE ... RETURNING` verifier.
3. Only after successful consumption, run the existing executor against the supplied workspace adapter.
4. The executor creates only an isolated branch and a draft PR after quality checks pass. It never merges or deploys.

Invalid plans, patch metadata, diff content, receipt bindings, expired/revoked receipts, replay, and D1 failures stop before workspace side effects.

A consumed receipt is intentionally not restored if a later workspace step fails. The owner must issue a fresh short-lived approval receipt for a retry.

## Remaining integration boundaries

This bridge is a tested service function, not an HTTP route. It does not authenticate an owner, create approval receipts, implement a GitHub/worktree adapter, or invoke an AI provider. The caller must pass the real Cloudflare D1 binding and an independently reviewed workspace adapter. Do not expose it to requests until owner-only authentication, CSRF/origin protection, audit logging, rate limiting, and a concrete branch-scoped workspace adapter are implemented.
