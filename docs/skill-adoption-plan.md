# Agency Agents Adoption Plan

**Review date:** 2026-11-20  
**Upstream:** [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)  
**License:** MIT ([LICENSE](https://github.com/msitarzewski/agency-agents/blob/main/LICENSE)).

## Selection rationale

AURA's objective is to identify and build multiple lawful revenue streams with zero initial capital, moderate risk and owner approval before spending or external commitments. The upstream catalogue is broad; AURA adopts only 20 roles that directly support opportunity research, audience growth, content production, sales, financial operations, compliance and platform reliability.

## Selected divisions

- Executive: Agents Orchestrator, Business Strategist.
- Research & Opportunity: Product Trend Researcher, Growth Hacker.
- Content & Audience: Content Creator, TikTok Strategist, Instagram Curator, Video Optimization Specialist, SEO Specialist, Reddit Community Builder.
- Sales & Monetization: Offer & Lead Gen Strategist, Outbound Strategist, Sales Outreach, Proposal Strategist.
- Operations & Finance: Finance Tracker, Analytics Reporter, Legal Compliance Checker.
- Technology & Automation: AI Engineer, DevOps Automator, Model QA Specialist.

Canonical upstream role paths and the responsibility of each role are recorded in `skills/registry.yaml` and `docs/agent-registry.md`.

## Runtime implementation

- The Worker registry and 3D office roster use the same 20 role names and six division assignments.
- Each role is mapped to one or more existing AURA skill packs. The role's specialty and canonical upstream file are injected into the task-scoped system context.
- The office groups agents by division and displays live task status above each avatar.
- Role descriptions are adapted into AURA-authored summaries; upstream skill files are not copied wholesale.
- The 3D office uses a 16:9 landscape viewport, dark theme and blocky toy-like avatars.

## Exclusions and safety gates

- No role can grant itself new permissions or credentials.
- No paid ads, subscriptions, paid model APIs, data services or purchases under the Rp0 default without exact owner approval.
- No auto-sending outreach, public posting, contracts, account changes, payments, transfers or withdrawals.
- Affiliate claims must be truthful and disclosed; third-party media must be owner-created, licensed or explicitly authorized.
- Finance reports separate gross sales, pending commissions, refunds, fees, actual cash and net distributable cash.
- Live trading, wallet custody and financial execution remain disabled.
- Compliance has veto authority; Model QA is an independent review role.

## License and attribution

The upstream LICENSE is MIT and names AgentLand Contributors, copyright 2025. This implementation links to the original role files and uses concise original summaries rather than redistributing the full files. Any future substantial copied text must retain the upstream copyright and permission notice.
