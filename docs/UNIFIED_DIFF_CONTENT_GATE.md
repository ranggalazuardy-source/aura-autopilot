# Unified Diff Content Gate

The content gate complements `app/patch_policy.py`. The existing policy checks
GitHub changed-file metadata; this module also checks the textual unified diff.

It requires a one-to-one match between diff file headers and metadata paths,
matching old/new file paths, textual hunks, and exact addition/deletion counts.
Binary patches, file-mode changes, renames, malformed headers, missing hunks,
and ambiguous content fail closed.

This remains validation-only: it does not fetch diffs, apply patches, write
files, invoke AI providers, create commits or PRs, merge, or deploy. Passing the
gate is not evidence of correctness and does not replace tests, code review,
security review, or explicit owner approval.

The parser intentionally accepts a narrow unified-diff format. If GitHub emits
a diff outside that format, the safe outcome is rejection for manual review.
