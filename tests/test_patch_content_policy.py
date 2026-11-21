import unittest

from app.patch_policy import ChangedFile
from app.patch_content_policy import evaluate_unified_diff


class PatchContentPolicyTests(unittest.TestCase):
    def test_matching_textual_diff_passes_metadata_gate(self):
        diff = (
            "diff --git a/app/agents/demo.py b/app/agents/demo.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/app/agents/demo.py\n"
            "+++ b/app/agents/demo.py\n"
            "@@ -1 +1,2 @@ demo\n"
            " old_line\n"
            "+new_line\n"
        )
        result = evaluate_unified_diff(
            diff, [ChangedFile("app/agents/demo.py", "modified", 1, 0, 1)]
        )
        self.assertTrue(result.allowed)

    def test_mismatched_counts_are_rejected(self):
        diff = (
            "diff --git a/tests/test_demo.py b/tests/test_demo.py\n"
            "--- a/tests/test_demo.py\n"
            "+++ b/tests/test_demo.py\n"
            "@@ -1 +1,2 @@\n"
            " old\n"
            "+new\n"
        )
        result = evaluate_unified_diff(
            diff, [ChangedFile("tests/test_demo.py", "modified", 2, 0, 2)]
        )
        self.assertFalse(result.allowed)
        self.assertIn("change_count_mismatch:tests/test_demo.py", result.reasons)

    def test_path_mismatch_and_unlisted_file_are_rejected(self):
        diff = (
            "diff --git a/tests/a.py b/tests/a.py\n"
            "--- a/tests/a.py\n+++ b/tests/a.py\n"
            "@@ -1 +1 @@\n-old\n+new\n"
        )
        result = evaluate_unified_diff(
            diff, [ChangedFile("tests/b.py", "modified", 1, 1, 2)]
        )
        self.assertFalse(result.allowed)

    def test_binary_and_mode_changes_are_rejected(self):
        for marker in ("GIT binary patch", "new file mode 100644", "old mode 100644"):
            with self.subTest(marker=marker):
                diff = (
                    "diff --git a/docs/demo.txt b/docs/demo.txt\n"
                    f"{marker}\n"
                    "--- a/docs/demo.txt\n+++ b/docs/demo.txt\n"
                    "@@ -1 +1 @@\n-old\n+new\n"
                )
                result = evaluate_unified_diff(
                    diff, [ChangedFile("docs/demo.txt", "modified", 1, 1, 2)]
                )
                self.assertFalse(result.allowed)

    def test_empty_or_missing_diff_is_rejected(self):
        self.assertFalse(evaluate_unified_diff("", []).allowed)
        self.assertFalse(evaluate_unified_diff("not a diff", []).allowed)

    def test_deleted_source_line_starting_with_two_dashes_is_counted(self):
        diff = (
            "diff --git a/tests/test_cli.py b/tests/test_cli.py\n"
            "--- a/tests/test_cli.py\n+++ b/tests/test_cli.py\n"
            "@@ -1 +1 @@ function_name\n"
            "--- legacy_option\n"
            "+--new-option\n"
        )
        result = evaluate_unified_diff(
            diff, [ChangedFile("tests/test_cli.py", "modified", 1, 1, 2)]
        )
        self.assertTrue(result.allowed)


if __name__ == "__main__":
    unittest.main()
