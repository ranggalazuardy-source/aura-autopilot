# AURA Model Provider Options (Zero-Capital Policy)

**Research date:** 20 November 2026  
**Decision status:** Integration prepared; all providers remain disabled pending owner Free-tier confirmations.

AURA's operating constraint is Rp0 starting capital. No provider call, paid fallback, billing activation, or scheduler activation is authorized by this document.

## Shortlist

| Provider | Free access observed | Fit for AURA | Main caveat |
|---|---|---|---|
| Cloudflare Workers AI | 10,000 Neurons/day on Workers Free | **Best first candidate**: native Worker binding, no external API key, one platform boundary | Neurons are not a request count; model choice affects consumption. On Workers Paid, usage above the daily free allocation is billed. |
| Groq | Free tier exists, but current public rate-limit tables describe Developer-plan limits; Developer tier requires a payment method and is billed per token | **Optional manually selected external alternative**: OpenAI-compatible API | Must remain disabled unless the account is confirmed Free with no payment method. Do not interpret Developer-plan limits as free quotas. |
| Google Gemini API | Selected models such as Gemini 2.5 Flash-Lite have free input/output token access | **Second automatic fallback** after Cloudflare quota exhaustion | Requires `GEMINI_API_KEY`, explicit Free-tier confirmation and data-use acceptance; free-tier content may be used to improve Google products. |
| OpenRouter | Free model variants ending in :free; 20 RPM and 50 requests/day, with a higher daily cap only after a credit purchase | Useful for experiments and model variety | Model availability is dynamic; the higher quota depends on buying credits, which AURA must never do. |
| Cohere | Trial/evaluation keys; 1,000 API calls/month for trial keys | Possible specialist alternative | Small monthly quota for a multi-agent runtime. |
| Mistral | Free mode for some product surfaces | Not selected for API runtime | Current docs say API keys/API use require billing activation and pay-as-you-go. |
| Cerebras | Pricing page currently describes self-serve pay-as-you-go with a free starter credit | Not selected | A one-time starter credit is not a recurring free tier. |

Limits are snapshots, not guarantees. Provider terms, models and quotas can change without notice. Re-check the account's own limits page before enabling anything.

## Recommendation

1. **Prototype on Cloudflare Workers AI first**, if the Cloudflare account is confirmed to be on Workers Free and the selected model is available within the free allocation.
2. Keep **Groq as an optional manually selected adapter**, never an automatic fallback. Enable it only after confirming the Groq account is on the Free tier with no payment method attached, explicitly approving external data processing, and configuring a key.
3. Keep **Gemini optional**, not default, because free-tier data-use terms are less suitable for sending private business context.
4. Do not use OpenRouter's paid-credit quota uplift, paid model variants, Cerebras starter credits, or any paid fallback.

## Required technical guardrails

- AURA_MODEL_ENABLED=false by default.
- AURA_SCHEDULER_ENABLED=false by default.
- No provider call unless both the feature flag and provider-specific owner configuration are present.
- Allowlist model IDs; never accept arbitrary model IDs from task input.
- Hard cap requests, input size, output size, concurrency and daily usage in AURA's own D1 ledger.
- Treat HTTP 429/quota exhaustion as a stop condition. Do not retry against a paid endpoint or silently switch providers.
- Gemini requires both AURA_GEMINI_ENABLED and AURA_GEMINI_FREE_TIER_CONFIRMED plus `GEMINI_API_KEY`. The confirmation is an owner assertion, not an API-verifiable billing check.\n- Groq requires both AURA_GROQ_ENABLED and AURA_GROQ_FREE_TIER_CONFIRMED. The latter is an owner assertion, not an API-verifiable billing check. Keep Groq disabled if a payment method or Developer tier is active.\n- Automatic order is Cloudflare → Gemini → Groq. Failover occurs only on explicit quota/rate-limit exhaustion (HTTP 429 or recognized quota errors). Authentication, billing, configuration, model, and unknown errors stop execution. Each attempted provider consumes one AURA daily call-cap unit.
- If a provider reports billing-required, payment-required, quota-exceeded, or unknown billing state, fail closed and block further inference.
- Never store provider keys in source code, frontend bundles, logs or task artifacts. Use Cloudflare Worker secrets.
- Do not send credentials, personal secrets, financial account identifiers or unnecessary personal data in prompts.
- Model output is untrusted. It may propose work but cannot approve spending, publish, message customers, change account security, or execute financial transactions.
- Keep model calls separate from task claiming until retry, lease, timeout and audit behavior is tested.

## Current AURA state

The Worker has Cloudflare Workers AI, Gemini and Groq adapters with automatic quota-only failover. All model and provider flags default to false; no inference runs until the owner confirms the relevant free tier, accepts data terms, configures keys and enables the feature. The scheduler remains disabled.

## Official references

- Cloudflare Workers AI pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Cloudflare Workers AI bindings: https://developers.cloudflare.com/workers-ai/configuration/bindings/
- Groq rate limits (published table is for Developer plan): https://console.groq.com/docs/rate-limits
- Groq billing FAQs (Developer tier requires a payment method and is billed): https://console.groq.com/docs/billing-faqs
- Gemini API pricing and data-use notes: https://ai.google.dev/gemini-api/docs/pricing
- OpenRouter free models and limits: https://openrouter.ai/collections/free-models/
- Cohere trial rate limits: https://docs.cohere.com/docs/rate-limits
- Mistral usage and API activation: https://docs.mistral.ai/admin/billing-usage/usage-limits
- Cerebras pricing: https://www.cerebras.ai/pricing
