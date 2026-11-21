# Persistent repair proposal lifecycle

## Generate and review

The owner-triggered generation endpoint stores the exact validated patch in
`repair_patch_proposals` with immutable base SHA, SHA-256 digest, canonical
approved paths, creation time, and a 30-minute expiry. The returned
`proposal_id` identifies that exact record.

`GET /repair/proposals/{proposal_id}` returns the persisted diff and metadata
for owner review. It never returns the approval receipt.

## Approve

`POST /repair/proposals/{proposal_id}/approve` requires
`{"confirm_owner_approval": true}` and owner API-key authentication. The
Worker atomically claims the proposal for approval, then issues a short-lived
receipt bound to the persisted incident, base SHA, patch digest, and paths.
The caller cannot replace any of those fields.

## Queue

`POST /repair/proposals/{proposal_id}/queue` requires
`{"confirm_owner_queue": true}`. It verifies the same owner's unused,
unexpired receipt and atomically claims the proposal for queueing. The
execution request is built from the exact patch bytes and paths stored in D1;
client-supplied patch content and paths are never accepted.

The receipt is not consumed here. The isolated runner consumes it only after
patch policy and all quality checks pass, immediately before a narrowly scoped
GitHub App write token is minted. The runner creates a Draft PR only. Merge and
deployment remain separate owner decisions.

Proposal states: `proposed → approving → approved → queueing → queued`, with
`expired` and `blocked` terminal safety states. Expired proposals cannot be
approved or queued. A stuck `approving` or `queueing` state fails closed and
requires operator reconciliation rather than replay.
