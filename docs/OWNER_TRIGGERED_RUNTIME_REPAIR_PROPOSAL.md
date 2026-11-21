# Owner-triggered runtime repair proposal

## Endpoint

`POST /repair/incidents/{incident_id}/generate-proposal`

The endpoint requires the normal owner API key and a strict JSON body:

```json
{
  "confirm_owner_generation": true,
  "confirm_provider_inference": true
}
```

No candidate paths, workflow URL, CI logs, or diagnostics are accepted from the
caller. The Worker reads the incident and CI evidence from D1, verifies the
persisted owner triage and low-risk category, then reads only the persisted
candidate files from the exact failed-run commit SHA.

## Provider gate

Generation is refused unless `AURA_MODEL_ENABLED=true` and at least one
provider is explicitly enabled, has its Free-tier confirmation flag, and has
the required binding/key. The order is Cloudflare Workers AI → Groq → Gemini.
Each attempt reserves against the existing five-calls-per-UTC-day D1 cap.
Failover is limited to quota exhaustion and transient upstream failures;
authentication, billing, configuration, and invalid-request errors stop.

The caller must explicitly confirm provider inference for each request. The
current repository configuration keeps all model execution and provider flags
disabled, so this endpoint does not invoke a provider until the owner changes
those settings in a separately authorized configuration step.

## Proposal boundary

A successful response includes the exact base SHA, unified diff, digest, and
changed paths. It is a proposal only and requires a separate owner approval
receipt. The route does not create an approval receipt, execution request,
branch, or pull request. It never writes files, merges, or deploys.

The async generator reads only persisted allowlisted paths at the immutable
commit SHA. The existing metadata and unified-diff validators remain
authoritative. CI uses fake readers and fake model invokers; no live provider
requests are made.
