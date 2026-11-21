# Approval-Gated Patch Executor Orchestration

## What this stage implements

The new app/patch_executor.py module adds a dependency-injected orchestration layer for a proposed repair patch:

1. Require a repair plan already marked ready_for_owner_approval.
2. Bind the approval receipt to the incident ID, exact base commit, SHA-256 of the complete patch, and exact changed-path set.
3. Re-run the metadata policy and unified-diff content validator.
4. Ask a trusted approval-verifier adapter to validate the owner-issued receipt.
5. Create a dedicated isolated branch, apply the already-proposed diff, and run quality checks through a workspace adapter.
6. Open a draft pull request only if the checks pass.

The orchestration deliberately has no API for provider invocation, main-branch writes, PR merge, or production deployment.

## Trust boundary and required production adapters

This is an orchestration contract, not yet a production-connected executor. The repository does not yet contain concrete implementations of ApprovalVerifier or PatchWorkspace.

Before wiring a production adapter, it must:

- Implement `ApprovalVerifier.verify_and_consume` against trusted server-side storage. Verification and one-time consumption must be atomic, and must enforce owner identity, expiry, revocation, incident, base SHA, patch digest, and exact approved paths. A consumed receipt cannot be replayed, including by concurrent executions.
- Create branches only from the exact approved base SHA and never target main for file writes.
- Apply the exact diff whose digest was approved; do not regenerate or normalize it after approval.
- Run the repository quality workflow in an isolated environment with least-privilege credentials.
- Create draft PRs only. It must not merge, deploy, change secrets, alter permissions, or enable AI providers.
- Preserve audit events for approval verification, branch creation, patch application, test results, and draft PR creation.

The adapter must fail closed on unavailable approval storage, stale base commits, branch conflicts, patch application errors, and failed quality checks.

## Current limitations

- No AI code-generation provider is called; inference remains disabled.
- No concrete GitHub/worktree adapter is connected.
- No patch has been applied to a real repository worktree by this module.
- The unit tests use fake adapters and prove orchestration order, single-use approval behavior, and blocked paths, not live GitHub execution. The verifier contract now requires atomic verify-and-consume semantics; a concrete transactional store is still not connected. Malformed request data and adapter exceptions fail closed; no later stage is called after a failed stage.
- A failed branch operation, patch application, or test run returns a fail-closed result and never creates a draft PR. A partially created isolated branch is left for inspection; no automatic cleanup is performed.
- Human review remains mandatory. Draft PR creation is not merge or deployment authorization.

## Test coverage

tests/test_patch_executor.py covers successful gated orchestration, unverified/failed approval, patch digest and base SHA mismatch, path-scope mismatch, failed quality checks, and blocked repair categories.
