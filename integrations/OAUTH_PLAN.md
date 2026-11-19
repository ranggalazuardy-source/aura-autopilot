# AURA OAuth Integration Plan

Integrations are not active merely because this plan exists. Each provider requires an owner-created developer app, review/approval where applicable, consent and secret configuration.

## Google / YouTube
- Owner creates Google Cloud project and enables only required APIs.
- Start with read-only channel/video analytics scopes for reporting.
- Add upload/publish permissions only after the owner explicitly enables publishing.
- Store OAuth client secret and refresh token in managed Cloudflare secrets, never in Git.
- OAuth client IDs may be public in some client contexts; client secrets and refresh tokens are always confidential.
- Do not request Gmail or Drive access unless a separately approved feature genuinely needs it.

## TikTok
- Register an app in TikTok for Developers under the owner's account.
- Request only the products/scopes approved for the intended workflow.
- Begin with identity/basic profile and read-only analytics capabilities where available.
- Content publishing requires the relevant TikTok product access, user consent and compliance with current posting rules.
- Do not automate engagement, scraping, unsolicited messaging or actions outside granted scopes.

## Instagram / Meta
- Owner creates a Meta developer app and uses an eligible Instagram professional account.
- Start with the minimum permissions needed for profile/media insights.
- Publishing requires supported account type, product configuration and the relevant publishing permissions/review.
- Keep Facebook Page/Business access and app roles owner-controlled.
- Do not collect personal inbox content unless separately required and approved.

## Affiliate platforms
- Integrate only through official affiliate APIs, approved feeds, or permitted exports.
- Record platform, program ID, disclosure requirements, attribution window, commission terms and payout threshold.
- Do not scrape authenticated pages or automate clicks, purchases, reviews or fake conversions.
- If a platform has no approved API/feed, use a manual import workflow until an official route is available.

## Secret names (values are never committed)
- `GOOGLE_OAUTH_CLIENT_ID` (only if server-side flow requires it)
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REFRESH_TOKEN`
- `TIKTOK_CLIENT_KEY`
- `TIKTOK_CLIENT_SECRET`
- `TIKTOK_ACCESS_TOKEN`
- `META_APP_ID`
- `META_APP_SECRET`
- `META_ACCESS_TOKEN`

Use separate secrets per environment. Rotate/revoke tokens after suspected exposure. Never paste values into chat or GitHub.
