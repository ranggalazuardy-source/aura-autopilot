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


## Authenticated Worker routes

- Owner creates a request through POST /repair/execution-requests with the existing X-AURA-API-Key. The Worker checks that the short-lived receipt exactly matches incident, base SHA, patch digest, and canonical approved paths before persisting the request.
- Runner fetches the one-time patch through GET /repair/runner/{request_id}/patch using X-AURA-Runner-Key. This key is a separate secret and invalid attempts use the Cloudflare auth rate limiter.
- Only after the isolated validation job passes does the publish job call POST /repair/runner/{request_id}/authorize-write. The Worker atomically consumes the exact owner receipt; replay, expiry, revocation, mismatch, and D1 failures block the request.
- The runner workflow then mints a narrowly permissioned GitHub App installation token, creates an aura/repair/<request_id> branch, and opens a Draft PR. It never merges or deploys.

## Required repository configuration before a live run

Configure these GitHub Actions secrets:
- AURA_REPAIR_RUNNER_SECRET: same high-entropy secret as the Cloudflare Worker secret of the same name.
- AURA_REPAIR_APP_ID and AURA_REPAIR_APP_PRIVATE_KEY: a GitHub App installed only on this repository, with Contents: Read & write and Pull requests: Read & write.

Configure repository variable AURA_API_BASE_URL to the deployed AURA Worker base URL. The Cloudflare Worker also needs the separate AURA_REPAIR_RUNNER_SECRET secret. Do not reuse AURA_API_KEY as the runner key.

The workflow is intentionally manual-dispatch at this stage. The request store and authenticated endpoints are implemented, but automatic dispatch from the incident/repair pipeline is not yet connected. No live D1 migration or repository secrets were changed by this code-only PR update. The GitHub App token is not created in the validation job and is not available to patch tests.


## Automatic queue pickup

The guarded runner workflow now has a five-minute scheduled trigger. Its first, read-only job calls POST /repair/runner/next with the dedicated runner secret. D1 atomically reserves the oldest unexpired queued request by changing its status to dispatched and returns only request ID, base SHA, and expiry; it does not return patch bytes. The later validation job retrieves the exact patch once through the authenticated patch endpoint. A single workflow-level concurrency group prevents overlapping queue pollers from reserving work simultaneously.

A manual workflow_dispatch override remains available for an explicitly supplied request ID/base SHA/expiry. If the queue is empty, downstream validation and publish jobs are skipped. The workflow is not active on the default branch until the PR is merged, and production still requires the owner to configure the runner secret, API base URL, and repository-scoped GitHub App credentials.
