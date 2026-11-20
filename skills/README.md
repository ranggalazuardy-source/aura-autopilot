# AURA Agent Skill Packs

AURA's agent roster is based on a curated set of role definitions from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents). Twenty relevant roles are organized into six divisions: Executive, Research & Opportunity, Content & Audience, Sales & Monetization, Operations & Finance, and Technology & Automation.

## Adoption model

- **Curated, not bulk-installed:** AURA selects roles that support diversified, lawful revenue generation. Unrelated roles are excluded.
- **Role references, not blind execution:** the canonical upstream Markdown file for each role is linked in `skills/registry.yaml`. AURA's runtime prompt adds its own task contracts and guardrails.
- **Skill != integration:** a role or skill does not grant API access, credentials, external tools or permission to execute.
- **Evidence-first:** market and performance claims need source links and dates; financial claims need inputs and reconciliation.
- **Zero-capital default:** no paid tools, APIs, ads, subscriptions or purchases unless the owner approves the exact cost.
- **Human gates:** public posting, external outreach, spending, contracts, account/security changes, financial transactions and third-party IP use require explicit owner approval.
- **Least privilege:** read-only access by default; never request passwords, OTPs, recovery codes, private keys or withdrawal-enabled credentials.
- **License and provenance:** upstream role references are attributed to AgentLand Contributors / msitarzewski/agency-agents under its MIT license. AURA does not vendor full role files.

## AURA skill packs

| Pack | Purpose |
|---|---|
| `market-intelligence` | Research, opportunity discovery, validation and prioritization |
| `growth-content-commerce` | Original content, organic growth, affiliate/commerce research, sales and conversion |
| `finance-investment-risk` | Cash accounting, margin analysis, financial reporting and paper-only research |
| `platform-engineering-security` | Cloudflare, agent architecture, testing, security and deployment |

The 20 Agency Agents roles are mapped to these AURA skill packs in `skills/registry.yaml` and `docs/agent-registry.md`.

## Runtime status

The Cloudflare Worker deterministically routes tasks to AURA-authored skill packs and adds the selected Agency Agents role's division, specialty and upstream source to its task context. This does not mean the model is active or that an external action has been executed. Model inference, background scheduling, paid data feeds and public publishing remain disabled until separately configured and approved.
