# Opaque Repair Runner Dispatch Contract

## Purpose

This contract is the first runner-facing boundary between a trusted dispatcher
and an ephemeral GitHub Actions job. It deliberately accepts an opaque request
identifier rather than patch content or approval claims.

## Accepted envelope

The validator accepts exactly these four fields:

- `request_id`: 32 lowercase hexadecimal characters.
- `repository`: exactly `ranggalazuardy-source/aura-autopilot`.
- `base_sha`: exactly 40 lowercase hexadecimal characters.
- `expires_at`: Unix timestamp strictly in the future and no more than 600
  seconds after the runner's trusted current time.

Unknown and missing fields are rejected. In particular, dispatch inputs cannot
contain patch text, credentials, branch names, owner identity, approval flags,
or workflow instructions.

## Security properties

- The runner must obtain patch content and approval metadata from the authenticated
  control plane using the opaque request ID.
- The runner must independently verify repository identity, exact base SHA,
  request expiry, and the approval receipt before creating a worktree.
- D1 receipt consumption must happen atomically before any repository write.
- Repository write credentials must not exist in the validation/test job and
  must be minted only after quality checks pass.
- The envelope is not itself proof of owner approval and does not authorize
  repository writes.
- No endpoint, workflow dispatcher, GitHub App, or credential has been connected
  by this change.

## Validation

Unit tests cover exact field allowlisting, malformed identifiers, wrong
repository, expired and overlong requests, invalid clock values, and attempts
to smuggle patch/token/branch fields.
