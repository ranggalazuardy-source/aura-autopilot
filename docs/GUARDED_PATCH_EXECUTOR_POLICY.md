# Guarded Autonomous Patch Executor — Policy Stage

## Current stage

This change adds a deterministic, fail-closed policy gate for proposed repair diffs. It is a prerequisite for a future patch executor, not a running code-generation agent.

The policy module only evaluates changed-file metadata. It does not call an AI provider, read credentials, create commits, apply patches, merge pull requests, or deploy production.

## Initial repair allowlist

Only small modifications under these prefixes may pass the policy gate:

- `app/agents/`
- `app/services/`
- `tests/`
- `docs/`

The first iteration is deliberately narrow. Cloudflare Worker code, GitHub workflows, infrastructure, migrations, schema, authentication, security, billing, payments, provider routing/configuration, secrets, credentials, and ledger-related paths are blocked.

## Hard limits

- Maximum 6 changed files.
- Maximum 400 additions.
- Maximum 200 deletions.
- Only `modified` files; additions, deletions, renames, and other statuses fail closed.
- Empty diffs, duplicate paths, path traversal, negative change counts, and sensitive file types are rejected.

A passing decision means only that the metadata is within this narrow policy. It does not prove that a patch is correct or safe. Full tests, security review, human review, and explicit owner approval remain mandatory.

## Next integration steps

1. Connect the policy to a dedicated isolated-branch patch executor.
2. Require an explicit owner-approved code-generation runtime and provider/data-processing review before any inference.
3. Validate the actual diff and run regression plus full quality checks.
4. Open a draft PR only; never merge or deploy automatically.
5. Keep production inference disabled until separately authorized.
