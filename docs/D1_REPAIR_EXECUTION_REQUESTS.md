# D1 execution request store

`repair_execution_requests` stores the exact patch bytes, SHA-256, base commit,
incident, approved paths, owner receipt ID, expiry, and one-time claim state.
Request IDs are opaque 128-bit random values. The runner dispatch must carry
only request ID + repository/base SHA/expiry; never patch text or credentials.

`claim_execution_patch` uses one conditional `UPDATE ... RETURNING` so two
runners cannot both claim the same request. The returned patch is re-hashed
before it is exposed. Expired, replayed, malformed, and D1-failed requests
must not reach a workspace.

The service deliberately does not mint GitHub credentials, create branches,
or open PRs. The HTTP layer must authenticate the runner with a dedicated
`AURA_REPAIR_RUNNER_SECRET` (separate from owner API key), rate-limit it,
and verify the associated unconsumed owner receipt before returning patch data.
