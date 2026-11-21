# Incident-to-Repair-Plan Bridge

The incident repair bridge converts a **normalized incident record** into the
existing deterministic repair planner output. It is a pure, no-side-effect
adapter; it is not yet wired to GitHub issue intake or the production incident
monitor.

## Required evidence

Callers provide `incident_id`, `category`, and explicit `candidate_paths`.
The bridge does not guess paths from an issue title, workflow name, run URL,
branch name, or commit SHA. Missing, malformed, or non-string candidate path
evidence is blocked. High-risk and unknown categories remain blocked by the
underlying planner.

## Safety boundary

A `ready_for_owner_approval` result is only a proposal. It does not authorize
AI inference, file edits, branch creation, commits, pull requests, merge, or
deployment. Provider inference remains disabled. Connecting this adapter to
incident intake requires a separately reviewed integration that can produce
trusted candidate-path evidence and preserve the owner-approval gate.
