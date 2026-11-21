# D1-backed triaged CI repair preparation

`prepare_triaged_ci_repair_from_d1` loads the authoritative incident and CI
evidence in one read-only join. It does not accept caller-supplied evidence,
candidate paths, workflow metadata, or commit hashes.

The loader fails closed when D1 is unavailable, the incident ID is malformed,
the joined evidence is missing, or the database read fails. It then delegates
to the existing provenance, triage-owner, category, SHA, candidate-path,
explicit-confirmation, provider-gate, and unified-diff validations.

The function has no D1 write path, does not issue or consume approval receipts,
does not queue an execution request, and does not write to GitHub. The generator
is injected by a future owner-authorized runtime; CI uses a deterministic mock.
