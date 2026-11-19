# AURA Skill Adoption Plan

**Review date:** 2026-11-20  
**Upstream:** [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)  
**Upstream license:** MIT (see [LICENSE](https://github.com/VoltAgent/awesome-agent-skills/blob/main/LICENSE)).

## What was reviewed

The upstream README describes a curated catalogue of 1,497+ skills, compatible with several coding-agent environments. The catalogue contains capabilities across agent architecture, search/research, marketing, product management, video, crypto data, Cloudflare, security and testing. AURA selected only the capabilities that map to its 15-agent business model and current zero-capital/guarded operating policy.

## Adopted capability groups

| AURA group | Selected upstream references | Why it fits |
|---|---|---|
| Research and opportunity validation | SerpApi search, Brave search, Dean Peters company research, JTBD, PESTEL, opportunity-solution tree, prioritization | Discover many market types, validate demand and rank tests |
| Growth and content | Corey Haines content strategy, copywriting, SEO audit, analytics, CRO, referrals; Kim Barrett offer extraction, scroll-stopping creative, conversion path, language cleanup; Remotion | Build content and customer acquisition systems without limiting the business to one niche |
| Finance and investment research | Dean Peters finance metrics; Binance market rank, token info/audit, trading signal; Coinbase on-chain query | Improve unit economics and research quality; execution tools remain blocked |
| Platform and quality | VoltAgent best practices; Cloudflare Agents SDK, Workers best practices, Wrangler; OpenAI security and threat model; Trail of Bits static analysis/insecure defaults; TestMu Playwright; OpenAI CI repair | Build, secure and test AURA's agent platform and deployment |

## Deliberately excluded or gated

- Binance spot execution and Coinbase wallet/trade/payment skills: no live trading, custody, transfer or payment permission.
- Paid search, ad buying, paid model APIs, scraping services and other metered tools: not activated under Rp0 starting capital without owner approval.
- Provider-specific skills that require a stack AURA does not use (for example unrelated frontend frameworks or database providers) are not loaded just because they exist in the upstream list.
- Browser automation, publishing and account-management capabilities remain gated behind platform authorization and owner approval.

## Implementation in this repository

- `skills/registry.yaml` records selected upstream IDs, links, assigned agents and local skill-pack files.
- `skills/*.md` are AURA-authored operational playbooks inspired by the listed capabilities. They do not reproduce upstream skill source files.
- `docs/agent-registry.md` maps each AURA role to its skill pack.
- `skills/README.md` describes how the packs should be used and their limitations.

## License and attribution

The upstream repository's LICENSE file states MIT License and requires retention of its copyright and permission notice when distributing copies or substantial portions. This AURA implementation links to the upstream catalogue and license and writes original summaries/workflows rather than vendoring the upstream files. If future work copies any upstream skill files or substantial portions, include the original MIT notice and re-check each skill's own source/license and attribution requirements.

## Important runtime limitation

This is a curated skill library in source control. AURA v0.5.0 does not yet dynamically load or execute these packs, and adding a skill does not connect its provider, install an MCP server, provision an API key, or authorize an action. A subsequent runtime implementation must add skill discovery, version/provenance tracking, task-to-skill routing, sandboxed execution, observability, and policy checks before any agent can claim it used a skill.
