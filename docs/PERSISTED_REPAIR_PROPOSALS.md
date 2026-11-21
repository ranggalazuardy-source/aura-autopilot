# Persisted repair proposal approval and queue flow

Repair proposals are persisted in `repair_patch_proposals` with their exact
unified diff, SHA-256 digest, immutable base commit, canonical approved path
list, incident ID, expiry, and lifecycle status.

## Owner review

- `POST /repair/incidents/{incident_id}/generate-proposal` generates and stores
  a proposal only when the owner explicitly confirms generation and provider
  inference, and the existing model/provider gates permit inference.
- `GET /repair/proposals/{proposal_id}` returns the exact stored diff for review.
- Proposals expire after 30 minutes. Expired proposals cannot be approved.

## Approval

`POST /repair/proposals/{proposal_id}/approve` requires the owner API key and
`confirm_owner_approval: true`. The server derives the owner identity from the
authenticated secret; it never accepts an owner ID from the client. A short-lived
receipt is issued and bound to the proposal's incident, base SHA, patch digest,
and exact approved paths.

## Queue

`POST /repair/proposals/{proposal_id}/queue` requires
`confirm_owner_queue: true`, an exact matching owner receipt that is unexpired,
unused and not revoked, and an unchanged stored patch digest. The queue route
copies the exact stored diff and paths into the existing D1 execution-request
store. It does not accept patch text or paths from the caller.

Queueing is not execution approval beyond the receipt already issued, and is not
merge/deploy approval. The isolated runner still verifies the patch, executes
the fixed quality suite, and creates only a Draft PR after successful checks.
No merge or deployment is performed by this flow.

The proposal lifecycle and schema are checked in CI. Tests use AST and schema
contracts only; no live D1 mutation, provider inference, GitHub write, merge,
or deployment is performed in CI.
