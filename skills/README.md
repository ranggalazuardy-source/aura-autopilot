# AURA Agent Skill Packs

AURA uses a curated, capability-based skill layer informed by [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills). The upstream repository indexes 1,497+ skills across official teams and community maintainers; AURA does **not** install all of them. It selects relevant capabilities, adapts their workflows to AURA's agents, and keeps provider-specific execution disabled until the matching integration is deliberately configured.

## Adoption model

- **Reference, don't blindly copy:** each upstream skill is linked by canonical identifier and source URL. AURA's local files are original orchestration playbooks, not verbatim copies of upstream skill files.
- **Skill != integration:** a skill describes how an agent should reason and prepare work. It does not grant API access, credentials, or permission to execute.
- **Evidence-first:** market claims need dated sources; financial claims need explicit assumptions and calculation inputs.
- **Zero-capital default:** do not choose a paid tool, API, subscription, ad campaign, or hosted model unless the owner approves the exact cost first.
- **Human gates:** spending, trades, transfers, withdrawals, public posting, legal commitments, account/security changes and use of third-party IP require explicit owner approval.
- **Least privilege:** read-only access by default; never request passwords, OTPs, recovery codes, private keys, or withdrawal-enabled credentials.
- **License and provenance:** upstream skill names and links are attributed to their maintainers. See `docs/skill-adoption-plan.md` and the upstream MIT license. Re-check upstream terms before vendoring any skill file.

## Local skill packs

| Pack | Primary agents | Purpose |
|---|---|---|
| `market-intelligence` | Market Intelligence, CEO | Research, opportunity discovery, validation and prioritization |
| `growth-content-commerce` | Content, Clipping, Affiliate, E-commerce, Service Sales, SEO, Digital Products | Original content, marketing, funnel, sales and unit economics |
| `finance-investment-risk` | Finance, Equity Research, Crypto Research, Trading Risk Manager | Cash accounting, paper research, risk controls and no-live-trading boundary |
| `platform-engineering-security` | CEO, QA, platform operators | Cloudflare, agent architecture, testing, security and deployment |

## Runtime status

These packs are documentation and agent instruction assets. The Worker now bundles AURA-authored runtime instruction bodies and assembles task-scoped context from the agent-to-pack registry. The human-readable files under `/skills` remain the reviewable source documents; the Worker does not read arbitrary files at runtime. Context preparation is active, while model invocation, external tools, paid data feeds and broker connections remain disabled.
