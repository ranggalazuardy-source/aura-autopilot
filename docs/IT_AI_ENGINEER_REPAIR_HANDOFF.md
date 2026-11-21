# IT & AI Engineer → Guarded Repair Handoff

## What is connected
- The skill registry assigns AI Engineer, IT Service Manager, SRE, Incident Response Commander and Test Automation Engineer to Technology & Automation.
- `app/services/it_ai_repair_adapter.py` is the first executable handoff boundary for incidents owned by `IT_AI_ENGINEER`.
- It accepts only `github_actions` or `internal_test` incidents and the existing safe repair categories.
- Candidate paths must be explicitly present in incident evidence. The adapter never guesses files from stack traces or logs.
- The existing repair pipeline validates the generated unified diff, exact changed paths, and metadata.

## Provider and execution boundaries
- Deterministic mock generators can exercise the path in tests.
- Non-mock generators are blocked unless an explicit provider-inference approval flag is supplied by a future owner-authorized runtime. No provider adapter is configured here.
- This change does not enable Groq, Gemini, Cloudflare inference, scheduled inference, or any paid service.
- A successful result is only `ready_for_owner_approval`. It does not create an approval receipt, write files, queue D1 execution, create a branch/PR, merge, or deploy.
- The adapter does not yet ingest GitHub Actions events or run as a background agent. Incident ingestion and runtime scheduling remain separate integration work.

## Required next integration
1. A trusted incident collector supplies sanitized source, category, exact base SHA, and evidence-backed candidate paths.
2. IT/AI Engineer invokes this adapter only for eligible incidents.
3. Owner reviews the proposal and approves its exact incident/base/digest/path binding.
4. The existing D1 receipt and isolated runner pipeline remains the only path to a Draft PR.
