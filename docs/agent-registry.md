# AURA Agent Registry

AURA now adopts a curated set of role definitions from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents), grouped into six revenue-focused divisions. The upstream Markdown files are referenced, not blindly executed. Runtime prompts are adapted with AURA's own security, zero-capital and approval controls.

All agents are logical workers inside one orchestrated system, not separate legal persons or account holders.

| Agent | Division | Responsibility | Upstream role | Skill packs |
|---|---|---|---|---|
| Agents Orchestrator | Executive | Assigns priorities, coordinates divisions and manages task handoffs. | [specialized/agents-orchestrator.md](https://github.com/msitarzewski/agency-agents/blob/main/specialized/agents-orchestrator.md) | market-intelligence; platform-engineering-security |
| Business Strategist | Executive | Turns owner goals into a diversified, evidence-backed revenue strategy. | [specialized/business-strategist.md](https://github.com/msitarzewski/agency-agents/blob/main/specialized/business-strategist.md) | market-intelligence; finance-investment-risk |
| Product Trend Researcher | Research & Opportunity | Finds customer needs, market gaps, product trends and low-cost validation tests. | [product/product-trend-researcher.md](https://github.com/msitarzewski/agency-agents/blob/main/product/product-trend-researcher.md) | market-intelligence |
| Growth Hacker | Research & Opportunity | Runs organic acquisition and conversion experiments with measurable hypotheses. | [marketing/marketing-growth-hacker.md](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-growth-hacker.md) | market-intelligence; growth-content-commerce |
| Content Creator | Content & Audience | Creates original scripts, calendars, storytelling and publishing packages. | [marketing/marketing-content-creator.md](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-content-creator.md) | growth-content-commerce |
| TikTok Strategist | Content & Audience | Builds platform-native hooks, retention structures and creative tests. | [marketing/marketing-tiktok-strategist.md](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-tiktok-strategist.md) | growth-content-commerce |
| Instagram Curator | Content & Audience | Plans Reels, carousels, visual identity and community growth. | [marketing/marketing-instagram-curator.md](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-instagram-curator.md) | growth-content-commerce |
| Video Optimization Specialist | Content & Audience | Improves video titles, thumbnails, retention, metadata and repurposing. | [marketing/marketing-video-optimization-specialist.md](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-video-optimization-specialist.md) | growth-content-commerce |
| SEO Specialist | Content & Audience | Builds search-led content, keyword maps and organic traffic plans. | [marketing/marketing-seo-specialist.md](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-seo-specialist.md) | growth-content-commerce; market-intelligence |
| Reddit Community Builder | Content & Audience | Builds trust-led community participation without spam or astroturfing. | [marketing/marketing-reddit-community-builder.md](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-reddit-community-builder.md) | growth-content-commerce; market-intelligence |
| Offer & Lead Gen Strategist | Sales & Monetization | Shapes offers, lead magnets and conversion paths around customer pain. | [sales/sales-offer-lead-gen-strategist.md](https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-offer-lead-gen-strategist.md) | growth-content-commerce; market-intelligence |
| Outbound Strategist | Sales & Monetization | Finds qualified prospects and drafts personalized outreach sequences. | [sales/sales-outbound-strategist.md](https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-outbound-strategist.md) | growth-content-commerce; market-intelligence |
| Sales Outreach | Sales & Monetization | Prepares compliant prospecting, objection responses and follow-ups for review. | [specialized/sales-outreach.md](https://github.com/msitarzewski/agency-agents/blob/main/specialized/sales-outreach.md) | growth-content-commerce |
| Proposal Strategist | Sales & Monetization | Creates service proposals, scopes, deliverables and pricing assumptions. | [sales/sales-proposal-strategist.md](https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-proposal-strategist.md) | growth-content-commerce; finance-investment-risk |
| Finance Tracker | Operations & Finance | Tracks confirmed cash, fees, refunds, approved costs and net margin. | [support/support-finance-tracker.md](https://github.com/msitarzewski/agency-agents/blob/main/support/support-finance-tracker.md) | finance-investment-risk |
| Analytics Reporter | Operations & Finance | Turns validated platform and business metrics into performance reports. | [support/support-analytics-reporter.md](https://github.com/msitarzewski/agency-agents/blob/main/support/support-analytics-reporter.md) | market-intelligence; growth-content-commerce; finance-investment-risk |
| Legal Compliance Checker | Operations & Finance | Reviews platform rules, disclosures, privacy, claims and IP risks; can veto. | [support/support-legal-compliance-checker.md](https://github.com/msitarzewski/agency-agents/blob/main/support/support-legal-compliance-checker.md) | all packs; policy veto |
| AI Engineer | Technology & Automation | Designs model routing, agent workflows, tool boundaries and evaluations. | [engineering/engineering-ai-engineer.md](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-ai-engineer.md) | platform-engineering-security |
| DevOps Automator | Technology & Automation | Maintains CI/CD, deployment, observability, reliability and rollback. | [engineering/engineering-devops-automator.md](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-devops-automator.md) | platform-engineering-security |
| Model QA Specialist | Technology & Automation | Tests model outputs, evidence quality, safety and regression behavior. | [specialized/specialized-model-qa.md](https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-model-qa.md) | all packs; independent QA |

## Division workflow

1. **Executive:** Agents Orchestrator assigns tasks; Business Strategist ranks revenue paths and portfolio priorities.
2. **Research & Opportunity:** Product Trend Researcher gathers demand evidence; Growth Hacker designs free acquisition experiments.
3. **Content & Audience:** Content Creator and channel specialists prepare original content, SEO and community growth packages.
4. **Sales & Monetization:** Offer & Lead Gen, Outbound, Sales Outreach and Proposal specialists prepare qualified, owner-reviewable revenue opportunities.
5. **Operations & Finance:** Finance Tracker and Analytics Reporter reconcile actual performance; Legal Compliance Checker has an independent veto.
6. **Technology & Automation:** AI Engineer and DevOps Automator maintain the system; Model QA Specialist independently checks model and agent quality; IT Service Manager, Site Reliability Engineer, Incident Response Commander and Test Automation Engineer own service continuity, reliability, incident recovery and regression prevention.


| IT Service Manager | Technology & Automation | Owns service health, incident queue, runbooks, access hygiene and operational continuity. | [engineering/engineering-it-service-manager.md](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-it-service-manager.md) | platform-engineering-security |
| Site Reliability Engineer | Technology & Automation | Monitors SLOs, uptime, latency, error budgets and self-healing automation. | [engineering/engineering-sre.md](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-sre.md) | platform-engineering-security |
| Incident Response Commander | Technology & Automation | Leads incident triage, containment, recovery, root-cause analysis and postmortems. | [engineering/engineering-incident-response-commander.md](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-incident-response-commander.md) | platform-engineering-security |
| Test Automation Engineer | Technology & Automation | Builds deterministic regression, integration and end-to-end tests; prevents repeat bugs. | [testing/testing-test-automation-engineer.md](https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-test-automation-engineer.md) | platform-engineering-security |

## IT, AI & Reliability operating mandate

Technology & Automation is AURA's continuous technical operations owner. It monitors system health, CI failures, runtime errors, security/dependency alerts, task queues, provider readiness and operational drift. It detects, classifies, reproduces, fixes, tests, documents and verifies technical faults without waiting for a new owner prompt. AI Engineer owns architecture and agent behavior; DevOps Automator owns CI/CD and deployments; IT Service Manager owns service operations; SRE owns reliability; Incident Response Commander coordinates incidents; Test Automation Engineer adds regression coverage; Model QA independently validates AI/agent behavior.

**Autonomous technical authority:** read logs and telemetry; create internal tickets; run tests and diagnostics; make minimal reversible code/configuration fixes; open/update repair branches and pull requests; run security and regression checks; merge and deploy low-risk fixes when all required checks pass; verify health and roll back a failed release. Every action must be auditable, idempotent, bounded and least-privilege. Never suppress alerts or hide failures to make checks green.

**Owner approval required for spending:** any paid API/model call, paid tool, subscription, ads, purchase, infrastructure upgrade, external contractor or other charge is blocked until the owner approves the exact amount and scope. Free-tier quota exhaustion must pause or skip that provider, never trigger a paid upgrade. Sensitive account/security changes, public communications and external commitments remain subject to platform/account controls; this mandate does not authorize bypassing them.

**Safe repair policy:** prioritize reversible minimal patches; reproduce before editing; add a regression test; run full CI and security checks; deploy gradually where supported; verify health and roll back automatically on regression. If the fault involves data loss/corruption, secrets exposure, suspected compromise, irreversible schema changes, destructive operations, legal/compliance risk or uncertain root cause, contain safely and escalate rather than guessing.

## Autonomy and approval boundaries

- Default capital is Rp0. Paid tools, ads, subscriptions, API usage charges and purchases require approval for the exact amount and duration.
- Drafting and research may be automated within configured read-only scopes. Public posting, external outreach, account changes, contracts and use of third-party IP require explicit owner approval.
- No borrowing, gambling, live trading, transfers, withdrawals or wallet custody.
- Revenue claims must distinguish verified cash received from pending commissions, projections and gross sales.
- Every task carries a task ID, owner, objective, evidence links, assumptions, cost, risk, review status, output and next action.
- Compliance can block work; QA approval is separate from task completion.

## Upstream license and attribution

The upstream repository includes an MIT License. Role names and role-file links are attributed to AgentLand Contributors / msitarzewski/agency-agents. AURA uses its own concise role summaries and guardrailed runtime instructions; it does not redistribute the full upstream Markdown role files. If substantial upstream text is copied in a later change, preserve the upstream copyright and permission notice.
