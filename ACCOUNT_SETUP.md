# AURA Account Provisioning Checklist

This file is an onboarding register, not proof that accounts exist. All entries begin as **NOT CREATED** until the owner creates them and verifies access.

## Ownership model
- The user is the legal and primary owner of every account and business asset.
- Use the user's real identity where a platform requires a real person or legal business identity.
- Use AURA as the public brand where permitted.
- Keep the primary recovery email, phone, passkeys/2FA and recovery codes under owner control.
- Do not share passwords, OTPs, recovery codes, session cookies or private keys in ChatGPT, GitHub, screenshots or source files.
- Give AURA integrations only scoped OAuth access after reviewing the requested permissions.
- Prefer delegated roles/brand permissions over sharing account passwords.

## Provisioning register

| Platform | Intended use | Suggested public handle | Initial state | Owner action |
|---|---|---|---|---|
| Google Account | Workspace identity, OAuth owner, Analytics/Search Console | `aura.operations` (availability unverified) | NOT CREATED | Owner creates Google account and secures recovery |
| YouTube | Brand channel and video publishing | `AURA Operations` | BLOCKED BY GOOGLE | Create channel under owner-controlled Google account |
| TikTok | Short-form distribution | `@aura.operations` (availability unverified) | NOT CREATED | Owner creates account and completes required verification |
| Instagram | Brand presence and Meta app connection | `@aura.operations` (availability unverified) | NOT CREATED | Owner creates account; switch to professional if eligible |
| Website | Official landing page and owned content | Domain not selected | NOT CREATED | Owner chooses a domain only after checking price/renewal; no purchase without approval |
| Affiliate platforms | Product referrals and commission tracking | Use platform-specific creator identity | NOT CREATED | Owner applies and accepts each platform's terms |

## Safe creation order
1. Create and secure the owner-controlled Google account.
2. Add a unique password and passkey/2-step verification. Store recovery codes offline in the owner's password manager or secure offline storage.
3. Create the YouTube channel under that Google account.
4. Create TikTok and Instagram accounts using the same public brand naming where available.
5. Confirm handle availability and profile links; update this register with verified URLs only.
6. Create the Meta developer app and Google Cloud project only when ready to connect integrations. Do not publish client secrets.
7. Apply to affiliate programs individually; record acceptance, commission rules, payout thresholds and restrictions.
8. Choose and purchase a website domain only after explicit owner approval of the exact provider, first-year price and renewal price.

## Backup register (never put secrets here)

| Item | Where owner stores it | Verified |
|---|---|---|
| Google recovery email | Owner password manager | No |
| Google recovery phone | Owner-controlled device | No |
| Google 2FA/passkey | Owner password manager / authenticator | No |
| Google recovery codes | Offline secure backup | No |
| TikTok recovery method | Owner password manager | No |
| Instagram recovery method | Owner password manager | No |
| Domain registrar recovery | Owner password manager | No |
| OAuth app credentials | Cloudflare secrets only | No |

## Current state
No new third-party accounts have been created by this repository change. No credentials are stored here. Account creation, phone/email verification and acceptance of platform terms must be completed by the owner.
