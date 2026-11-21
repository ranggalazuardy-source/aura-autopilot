"""Validate unified-diff content against the guarded patch metadata policy.

This is a validation-only stage. It never applies patches or writes to disk.
"""

import re
from collections.abc import Iterable

from app.patch_policy import ChangedFile, PatchDecision, evaluate_patch


_HUNK_HEADER = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? "
    r"\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@(?: .*)?$"
)


def evaluate_unified_diff(
    patch_text: str,
    files: Iterable[ChangedFile],
) -> PatchDecision:
    """Fail closed unless textual unified-diff headers and counts match metadata."""
    items = tuple(files)
    reasons: list[str] = []

    if not isinstance(patch_text, str) or not patch_text.strip():
        return PatchDecision(False, ("empty_diff_content",))

    lines = patch_text.splitlines()
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in lines:
        if line.startswith("diff --git "):
            if current is not None:
                blocks.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
        elif line.strip():
            reasons.append("content_before_first_file_header")
    if current is not None:
        blocks.append(current)
    if not blocks:
        reasons.append("missing_file_headers")
    if len(blocks) != len(items):
        reasons.append("file_count_mismatch")

    metadata_by_path = {item.filename.replace("\\", "/"): item for item in items}
    seen: set[str] = set()

    for block in blocks:
        header = block[0].split()
        if len(header) != 4 or header[0:2] != ["diff", "--git"]:
            reasons.append("malformed_diff_header")
            continue
        old_header, new_header = header[2], header[3]
        if not old_header.startswith("a/") or not new_header.startswith("b/"):
            reasons.append("invalid_diff_header_paths")
            continue
        old_path, new_path = old_header[2:], new_header[2:]
        if old_path != new_path:
            reasons.append("path_change_not_allowed")
            continue
        path = new_path.replace("\\", "/")
        if path in seen:
            reasons.append("duplicate_diff_file")
        seen.add(path)
        if path not in metadata_by_path:
            reasons.append(f"diff_path_missing_from_metadata:{path}")
            continue

        file_lines = block[1:]
        old_markers = [line[6:] for line in file_lines if line.startswith("--- a/")]
        new_markers = [line[6:] for line in file_lines if line.startswith("+++ b/")]
        if old_markers != [path] or new_markers != [path]:
            reasons.append(f"file_header_mismatch:{path}")
        if any(
            line.startswith((
                "new file mode ", "deleted file mode ", "old mode ",
                "new mode ", "rename from ", "rename to ",
                "copy from ", "copy to ", "Binary files ", "GIT binary patch",
            ))
            for line in file_lines
        ):
            reasons.append(f"non_text_or_mode_change:{path}")

        additions = 0
        deletions = 0
        hunk_seen = False
        in_hunk = False
        old_consumed = 0
        new_consumed = 0
        old_expected = 0
        new_expected = 0

        def finish_hunk() -> None:
            if old_consumed != old_expected or new_consumed != new_expected:
                reasons.append(f"hunk_line_count_mismatch:{path}")

        for line in file_lines:
            if line.startswith("@@"):
                if in_hunk:
                    finish_hunk()
                hunk_seen = True
                in_hunk = True
                match = _HUNK_HEADER.match(line)
                if not match:
                    reasons.append(f"malformed_hunk_header:{path}")
                    old_expected = new_expected = 0
                else:
                    old_expected = int(match.group("old_count") or "1")
                    new_expected = int(match.group("new_count") or "1")
                old_consumed = 0
                new_consumed = 0
                continue
            if not in_hunk:
                continue
            if line.startswith("+"):
                additions += 1
                new_consumed += 1
            elif line.startswith("-"):
                deletions += 1
                old_consumed += 1
            elif line.startswith(" "):
                old_consumed += 1
                new_consumed += 1
            elif line.startswith("\\"):
                continue
            else:
                reasons.append(f"invalid_hunk_line:{path}")
                continue
            if old_consumed > old_expected or new_consumed > new_expected:
                reasons.append(f"hunk_line_count_exceeded:{path}")
        if in_hunk:
            finish_hunk()
        if not hunk_seen:
            reasons.append(f"missing_hunks:{path}")

        metadata = metadata_by_path[path]
        if additions != metadata.additions or deletions != metadata.deletions:
            reasons.append(f"change_count_mismatch:{path}")

    if seen != set(metadata_by_path):
        reasons.append("metadata_diff_path_set_mismatch")

    metadata_decision = evaluate_patch(items)
    reasons.extend(metadata_decision.reasons)
    return PatchDecision(not reasons, tuple(dict.fromkeys(reasons)))
