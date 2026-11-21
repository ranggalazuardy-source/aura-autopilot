# Owner-authenticated repair approval endpoint

POST /repair/approvals requires the existing server-side AURA API-key authentication dependency.

Example JSON request:

```json
{
  "incident_id": "incident-123",
  "base_sha": "<40-character-commit-sha>",
  "patch_sha256": "<64-character-patch-sha256>",
  "approved_paths": ["app/agents/example.py"],
  "ttl_seconds": 300,
  "confirm_owner_approval": true
}
```

The route requires a strict JSON boolean confirmation. It derives the owner binding from the server-held AURA_API_KEY; clients cannot submit an owner ID. The service validates the receipt scope and stores a short-lived, single-use D1 receipt. Issuance is written to the audit log.

The endpoint only issues an approval receipt. It does not generate a patch, apply files, create a branch or PR, merge, deploy, or invoke an AI provider. The opaque receipt ID is not returned as a bearer authorization token: execution must still match the exact incident, owner, base SHA, patch digest, and approved paths and consume the receipt atomically.

## Operational boundary

This route uses the existing single-owner API-key model. Rotating the API key changes the derived owner identity, so receipts issued under the old key will not verify under the new key. Keep the key secret and do not put it in URLs or request bodies. The route is not linked from the public dashboard. A production GitHub/worktree adapter and an authenticated execution orchestration route are still absent.
