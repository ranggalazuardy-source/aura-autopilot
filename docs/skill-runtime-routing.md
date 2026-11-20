# Skill Loader & Router

## What is active in this release

The Cloudflare Worker now bundles a deterministic skill catalogue and agent-to-pack bindings. The D1 `task_skill_routes` table records which pack IDs are assigned to each task.

- `GET /skills` lists the four available skill packs and their repository source paths.
- `GET /agents/{agent_name}/skills` lists packs for simple agent names.
- `GET /agent-skills?agent=...` supports all registry names, including names containing slashes such as `E-commerce / Dropship`.
- `POST /agent-tasks` creates a queued task and records its skill routing immediately.
- `POST /agent-tasks/{task_id}/route` re-applies the current registry binding to an existing task.
- `GET /agent-tasks` includes the comma-separated `skill_pack_ids` for each task.

All endpoints require the AURA API key. Unknown agent names are rejected rather than silently routed to an unrelated skill pack. Compliance & Rights and QA / Auditor receive all packs so they can review cross-functional work.

## Runtime boundary

This release performs deterministic routing and can assemble task-scoped contexts from bundled skill instructions. It does **not** call a model, execute external tools, launch background agents, publish content or initiate financial activity. The `file` property in the catalogue remains a human-readable repository reference; runtime instructions are bundled separately in the Worker.

The D1 migration in `cloudflare/schema.sql` must be applied to the Cloudflare D1 database before using task routing in a deployed Worker. Existing task rows are not automatically backfilled; call the route endpoint for each task that needs a recorded binding.

## Next implementation stage

1. Add a controlled prompt/context assembler that retrieves approved skill instructions.
2. Add a model provider adapter with explicit per-agent tool allowlists.
3. Add execution leases, retries, idempotency and bounded task budgets.
4. Keep compliance, QA and owner approval gates outside the executing agent's control.
5. Add integration tests against a staging D1 database before production deployment.


## Skill loader and provider adapter

The Worker now bundles runtime instruction bodies for all four skill packs and assembles a task-scoped context from the agent binding. The instruction bodies are aligned with the human-readable files under `/skills` and packaged in code because a Worker must not assume arbitrary filesystem access at runtime.

- `POST /agent-tasks/{task_id}/prepare` prepares system instructions, task objective and an OpenAI-compatible request preview.
- `GET /runtime/provider` reports provider readiness without exposing secrets.
- The provider adapter builds a request envelope only. It makes no outbound network calls and has no configured model, API key or approved per-task budget.
- Task objectives are kept in a separate user-message field and explicitly treated as untrusted data.

This release does **not** call a model, execute external tools, launch background agents, publish content or initiate financial activity. No paid model use is enabled.


## Bounded task execution and tool registry (v0.7.0)

The Worker now has a lease-based task execution API:

- `GET /tools` lists the deterministic local tools.
- `POST /agent-tasks/claim-next` claims the highest-priority queued task and returns a short-lived worker lease.
- `POST /agent-tasks/{task_id}/heartbeat` renews the lease.
- `POST /agent-tasks/{task_id}/tools` runs an allowlisted local pure function under a valid lease.
- `POST /agent-tasks/{task_id}/complete` records the worker result and evidence, then marks QA as pending.
- `POST /agent-tasks/{task_id}/release` returns an unfinished task to the queue.

The initial tools are `text_stats` and `unit_economics`. They run locally on supplied input; they do not use the network, filesystem, shell, model provider, credentials or financial accounts. Every agent has an explicit allowlist. Lease tokens are generated per claim and required for task operations. Expired leases are reclaimed when another worker requests a task.

This is an execution control plane, not an autonomous AI runtime. No model is called and no agent is running in the background. A worker still needs to be started by an authorized caller. Task results are marked `qa_status=pending_review`; completion is not equivalent to independent QA approval.

Apply the complete `cloudflare/schema.sql` to D1 before deployment. The schema now includes `task_execution_leases` and `task_execution_artifacts`.
