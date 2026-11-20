# AURA Safety and Operating Policy

1. Legal and platform-compliant activity only.
2. No fake engagement, spam, deceptive claims, impersonation, copyright infringement, scraping behind authentication, or policy evasion.
3. Never store account passwords, OTPs, recovery codes, or payment-card data in the agent database.
4. OAuth tokens must be encrypted at rest and scoped to minimum required permissions.
5. Human approval is required for paid ads, purchases, transfers, withdrawals, account ownership/security changes, contracts, and external messages that create commitments.
6. Every proposed action must declare estimated cost, expected benefit, risk, source, and confidence.
7. Enforce per-day and per-month spending caps. Flexible budget does not mean unlimited budget.
8. Track revenue only when confirmed by platform/merchant reporting; distinguish estimates from received funds.
9. Preserve source attribution and content provenance. Use original or licensed media.
10. Stop an integration on repeated auth failures, policy warnings, unusual spend, or suspicious activity.
11. Production deployment requires authenticated private endpoints, Cloudflare-native throttling of invalid API-key attempts, D1 durable storage with Time Travel recovery, Worker Logs, and secret management.
12. On the Cloudflare Free plan, D1 Time Travel provides up to 7 days of point-in-time recovery for production-storage databases. Cloudflare Observability Free pricing takes effect December 1, 2026, with 0.5 GB/day ingestion and 7-day retention; ingestion pauses when the free allowance is reached, rather than creating overage charges. Until then, the legacy Workers Logs allowance is 200,000 events/day with 3-day retention. These are limited recovery/observability windows, not a substitute for longer-term offsite exports where required.
13. Cloudflare's Rate Limiting API is approximate and regional; it is a protective abuse throttle, not a globally strict quota or financial spending control.
