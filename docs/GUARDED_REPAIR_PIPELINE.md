# Guarded incident-to-repair proposal pipeline

`app/services/repair_pipeline.py` joins the normalized incident bridge, repair
planner, injected patch generator, and deterministic diff validators.

## Current behavior

1. Requires an explicit incident ID, eligible incident category, and explicit
   candidate paths. It does not infer files from issue titles or log snippets.
2. Blocks unsupported/high-risk categories before invoking the generator.
3. Requires a full base commit SHA.
4. Invokes only a caller-supplied generator capability. No AI provider is
   configured or called by this module.
5. Validates generated file metadata and unified-diff content with the existing
   fail-closed policy.
6. Requires generated paths to exactly match the incident's planned paths.
7. Returns a proposal with a SHA-256 digest and an explicit owner-approval
   requirement.

## Deliberate limits

This is proposal preparation only. It does not write files, create branches,
consume D1 approval receipts, contact GitHub, open pull requests, merge, deploy,
or publish content. A production generator adapter, incident-to-candidate-path
diagnostics, authenticated execution route, and concrete runner workspace
adapter remain separate integration work. The existing D1 executor bridge is
not invoked here.

Provider inference remains disabled unless separately configured and approved.
The test suite uses a deterministic fake generator and makes no network calls.
