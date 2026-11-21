# GitHub-Backed Isolated Patch Workspace — Integration Design

## Decision

Do not implement a local Git worktree inside the Cloudflare Worker. The deployed API runs in the Workers Python/ASGI runtime and has no supported persistent Git checkout or general-purpose subprocess workspace. Patch execution must run in an ephemeral GitHub Actions runner, while the Worker remains the policy, approval, and audit control plane.

## Target flow

1. Incident intake creates a normalized incident record. Only allowlisted low-risk categories may enter repair planning.
2. A repair planner proposes candidate paths. It does not infer paths from issue titles, logs, or arbitrary model output.
3. A patch-generation component (not yet configured) produces a unified diff. Deterministic metadata and content gates validate it before approval is requested.
4. The owner reviews the exact incident ID, base commit SHA, patch digest, and changed paths. The owner-authenticated API issues a short-lived, single-use D1 receipt bound to those exact values.
5. A narrowly scoped GitHub App integration or equivalent trusted dispatcher starts a dedicated workflow. The runner retrieves the exact approved patch and receipt context over authenticated channels.
6. The runner revalidates the patch and consumes the D1 receipt atomically before any repository write.
7. The runner creates a branch from the exact approved base SHA, applies only the approved diff, runs the full quality workflow, and opens a draft PR. It cannot merge or deploy.
8. The result and workflow run ID are written to the audit trail. Failures stop the pipeline; a consumed receipt is never restored.

## Required GitHub permissions

Prefer a GitHub App installed only on this repository. Its installation token should be short-lived and limited to:
- Contents: read/write, solely to create a branch and commit a validated patch.
- Pull requests: read/write, solely to open a draft PR.
- Actions: read; add write only if the selected dispatch mechanism demonstrably requires it.

Do not grant Administration, Secrets, Environments, Deployments, Checks write, Workflows write, or organization-wide access. If GitHub's permission model requires broader access for a chosen mechanism, redesign the mechanism rather than silently expanding permissions.

The app private key must be stored as a Cloudflare Worker secret, never in source, D1, logs, issue comments, or user-facing responses. Do not ask the owner to paste credentials into chat. Rotate the key and invalidate outstanding receipts when owner authentication credentials rotate.

## Runner hardening

- Use a dedicated workflow with minimal permissions and pin third-party actions to immutable commit SHAs.
- Accept only an opaque execution request ID; fetch patch content and approval metadata from the authenticated control plane.
- Check out the exact base SHA, not the current default branch.
- Re-run metadata and unified-diff validation in the runner.
- Reject symlinks, submodules, binary patches, mode changes, renames, path traversal, generated secrets, and changes outside the existing allowlist.
- Run tests without repository write credentials. Mint the minimum write credential only after tests pass and only for branch/commit/PR creation.
- Never expose repository write credentials to model-generated code or test processes.
- Never merge, deploy, edit secrets, change permissions, or modify protected workflow/configuration paths.
- Apply concurrency limits, execution timeouts, request expiry, and idempotency keys.
- Preserve failed isolated branches for review only when safe; otherwise record the failure and require a new approval.

## Remaining implementation gates

- No GitHub App or dedicated installation credential is currently configured or confirmed.
- No patch-generation runtime is connected; provider inference remains disabled.
- The current Worker route issues approval receipts only. It is not an execution or dispatch endpoint.
- The async D1 executor bridge is not wired to a real GitHub workspace adapter.
- D1 receipt behavior has fake-binding tests but no live isolated concurrency test.
- A dispatch/runner workflow, authenticated patch retrieval, revocation path, rate limiting, and end-to-end integration tests remain required.

Until every gate is closed and the owner explicitly authorizes the relevant release, keep PR #16 in draft, keep the execution endpoint absent, and do not merge or deploy this work.