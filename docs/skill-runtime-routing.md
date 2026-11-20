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

This release performs deterministic routing and persistence only. It does **not** load Markdown instructions into an LLM context, call a model, execute external tools, launch background agents, publish content, or initiate financial activity. The `file` property in the catalogue is a repository reference for the next loader stage; it is not read from the Worker filesystem.

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
