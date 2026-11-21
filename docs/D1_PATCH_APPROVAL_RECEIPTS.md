# D1-backed patch approval receipts

`app/services/patch_approval_store.py` implements the storage-side verifier contract for a guarded repair receipt.

## Atomic single-use semantics

`D1PatchApprovalStore.verify_and_consume` performs one conditional SQL `UPDATE ... RETURNING id` statement. It binds the receipt ID, owner identity, incident ID, exact base SHA, patch SHA-256, and canonical approved-path list. The update succeeds only while the receipt is unexpired, unrevoked, and unconsumed. The `consumed_at IS NULL` predicate and write are part of the same statement, so concurrent attempts cannot both consume the same row.

The table `patch_approval_receipts` is declared in `cloudflare/schema.sql`. Expiry and consumption timestamps are Unix seconds.

## Explicit limitations

- This change adds the table and verifier only. It does not create, approve, revoke, or list receipts.
- No HTTP route or owner-authenticated approval UI writes receipts.
- The current `execute_approved_patch` orchestration remains synchronous and accepts the verifier protocol; the async D1 store is not yet wired into that call path.
- No concrete GitHub/worktree workspace adapter is connected.
- Tests use a deterministic fake D1 binding. They validate SQL shape, exact bindings, and fail-closed behavior; they do not prove live Cloudflare D1 concurrency behavior.
- The store has no capability to edit files, call AI providers, create branches, open PRs, merge, or deploy.

## Next integration gates

1. Add a separately authenticated owner approval-issuance flow with short expiry and explicit incident/base/diff/path binding.
2. Add owner-only revocation and audit events.
3. Introduce an async executor boundary and wire this verifier without weakening the deterministic patch gates.
4. Prove concurrency behavior against an isolated D1 test database before enabling any production path.
5. Implement a branch-scoped GitHub workspace adapter and keep draft PR creation as the final allowed side effect.
