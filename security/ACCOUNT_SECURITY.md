# AURA Account Security Policy

## Non-negotiable controls
1. Human owner retains legal ownership and primary recovery channels.
2. Never store passwords, OTPs, recovery codes, cookies, private keys or OAuth tokens in source control.
3. Never ask the owner to send secrets through chat.
4. Require least-privilege OAuth scopes and explicit consent for each provider.
5. Separate read-only analytics from publishing permissions.
6. Require explicit owner approval before paid ads, purchases, withdrawals, transfers, contracts, domain purchases, paid subscriptions, security changes or external commitments.
7. Log administrative changes and token rotations without logging secret values.
8. Revoke compromised tokens immediately and rotate affected credentials.
9. Use unique credentials per platform and enable passkeys or 2-step verification.
10. Keep at least one offline recovery method controlled by the owner.

## Human approval gates
- Account creation and acceptance of terms: owner action.
- App review, business verification and legal declarations: owner action.
- OAuth consent: owner action.
- Publishing content: approval policy configurable per channel; default is draft-only until explicitly enabled.
- Financial actions: always require fresh explicit approval; an approval record alone never executes a transaction.

## Incident response
- Revoke provider sessions/tokens from the provider's security settings.
- Change affected passwords from a trusted device.
- Regenerate recovery codes and update the owner's offline backup.
- Review recent account activity and AURA audit log.
- Do not send incident secrets or recovery codes to support chats.
