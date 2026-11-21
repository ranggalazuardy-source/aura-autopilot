# Production Deployment Release Gate

## Dispatch requirements

The production deployment workflow is intentionally manual-only. The deploy job runs only when both conditions are true:

- The selected workflow ref is exactly refs/heads/main.
- The required confirm_production_deploy input is explicitly set to yes.

The input defaults to no. Dispatching the workflow from a feature or pull-request branch skips the production job. Pushes and pull requests do not deploy.

## Operator checklist before dispatch

- Review and merge the approved release PRs into main.
- Confirm the main-branch quality workflow is green for the exact release commit.
- Review the complete diff and confirm no secrets, credentials, or sensitive data are present.
- Confirm Cloudflare account, D1 binding, schema migration, Worker secrets, and rollback/recovery plan.
- Confirm provider eligibility, data-processing terms, and owner approval separately before enabling any inference flags.
- Keep all model/provider flags false unless explicitly authorized; deployment does not itself authorize model inference.
- Verify the production deployment summary and health/authenticated-route probes after deployment.

## Safety boundary

This gate does not merge pull requests, alter production secrets, enable providers, or dispatch a deployment on its own. A human operator must deliberately select the main branch and the explicit yes confirmation in GitHub Actions.
