# Guarded repair runner: owner setup

This guide configures the AURA repair runner. Keep the runner disabled until every
credential and the updated Worker deployment have been verified.

## Security model

- The queue-polling and patch-download jobs use a dedicated runner secret.
- Patch validation runs with read-only repository permissions and without a
  GitHub App private key or write token.
- Only after validation passes does the publish job consume the single-use owner
  approval receipt and mint a repository-scoped GitHub App token.
- The runner creates a **Draft pull request only**. It never merges or deploys.
- Do not paste secrets or private keys into chat, issues, pull requests, or logs.

## 1. Create a dedicated GitHub App

Create a GitHub App for this repository only. Install it only on
`ranggalazuardy-source/aura-autopilot`.

Required repository permissions:

| Permission | Access |
| --- | --- |
| Contents | Read and write |
| Pull requests | Read and write |
| All other permissions | No access |

Do not grant Administration, Actions, Secrets, Environments, Deployments,
Workflows, or organization permissions. Generate a private key and keep the
downloaded PEM file private. Record the App ID.

## 2. Create the runner shared secret

Generate a high-entropy secret on your own computer. For example:

```bash
openssl rand -hex 32
```

Use the exact same value in both places below. Do not commit it or send it in
chat.

### Cloudflare Worker secret

In Cloudflare Dashboard:

1. Open **Workers & Pages**.
2. Select Worker **aura-autopilot-api**.
3. Open **Settings → Variables and Secrets**.
4. Add a secret named `AURA_REPAIR_RUNNER_SECRET`.
5. Paste the generated value and save.

Alternatively, from the repository root with Wrangler authenticated to the
correct Cloudflare account:

```bash
npx wrangler secret put AURA_REPAIR_RUNNER_SECRET
```

Paste the generated value only into the local terminal prompt.

### GitHub Actions secret

In GitHub, open
**ranggalazuardy-source/aura-autopilot → Settings → Secrets and variables → Actions → New repository secret**.

Create `AURA_REPAIR_RUNNER_SECRET` with the exact same value.

## 3. Add the GitHub App Actions secrets

Under **Settings → Secrets and variables → Actions → Secrets**, add:

- `AURA_REPAIR_APP_ID`: the numeric App ID.
- `AURA_REPAIR_APP_PRIVATE_KEY`: the complete PEM private key contents,
  including the BEGIN/END lines.

Do not upload the PEM into the repository or paste it into ChatGPT.

## 4. Add Actions repository variables

Under **Settings → Secrets and variables → Actions → Variables**, add:

- `AURA_API_BASE_URL` = `https://aura-autopilot-api.ranggalazuardy.workers.dev`
- `AURA_REPAIR_RUNNER_ENABLED` = `false` initially.

Keep the runner disabled until the Worker containing the repair runner routes
has been deployed and its health/authentication checks have passed.

## 5. Verify before enabling

Before changing `AURA_REPAIR_RUNNER_ENABLED` to `true`, verify:

- The latest main commit has been deployed to the intended Cloudflare account.
- The Worker has the same `AURA_REPAIR_RUNNER_SECRET` as GitHub Actions.
- The GitHub App is installed only on this repository with only the two
  permissions above.
- The three Actions secrets and API base URL variable are present.
- No provider inference flags have been enabled as part of this setup.

Then enable the runner by changing the repository variable
`AURA_REPAIR_RUNNER_ENABLED` to `true`.

## 6. First safe test

Do not test with an arbitrary patch. First create a small, owner-reviewed repair
proposal that changes only an allowlisted test or documentation file, approve
that exact proposal through the authenticated AURA API, and queue it. Confirm
that the runner opens a Draft PR and that the PR remains unmerged.

If any secret is missing, the API is unavailable, a receipt is expired, or a
quality check fails, stop and investigate. Do not work around a failed gate by
granting broader permissions or manually creating a write token.
