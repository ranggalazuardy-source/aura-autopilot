import unittest

from app.services.runner_dispatch_policy import validate_runner_dispatch


class RunnerDispatchPolicyTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "request_id": "a" * 32,
            "repository": "ranggalazuardy-source/aura-autopilot",
            "base_sha": "b" * 40,
            "expires_at": 1600,
        }

    def test_accepts_opaque_short_lived_request(self):
        result = validate_runner_dispatch(self.payload, now=1000)
        self.assertEqual(result.request_id, "a" * 32)
        self.assertEqual(result.base_sha, "b" * 40)

    def test_rejects_extra_fields_including_patch_or_token(self):
        for key, value in (("patch_text", "diff"), ("token", "secret"), ("branch", "main")):
            with self.subTest(key=key):
                payload = {**self.payload, key: value}
                with self.assertRaisesRegex(ValueError, "fields_invalid"):
                    validate_runner_dispatch(payload, now=1000)

    def test_rejects_missing_fields(self):
        payload = dict(self.payload)
        payload.pop("base_sha")
        with self.assertRaisesRegex(ValueError, "fields_invalid"):
            validate_runner_dispatch(payload, now=1000)

    def test_rejects_wrong_repository(self):
        payload = {**self.payload, "repository": "attacker/repository"}
        with self.assertRaisesRegex(ValueError, "repository_invalid"):
            validate_runner_dispatch(payload, now=1000)

    def test_rejects_invalid_request_id_and_sha(self):
        for key, value, reason in (
            ("request_id", "../main", "request_id_invalid"),
            ("base_sha", "B" * 40, "base_sha_invalid"),
        ):
            with self.subTest(key=key):
                payload = {**self.payload, key: value}
                with self.assertRaisesRegex(ValueError, reason):
                    validate_runner_dispatch(payload, now=1000)

    def test_rejects_expired_and_overlong_requests(self):
        for expiry, reason in ((1000, "request_expired"), (1601, "ttl_exceeded")):
            with self.subTest(expiry=expiry):
                payload = {**self.payload, "expires_at": expiry}
                with self.assertRaisesRegex(ValueError, reason):
                    validate_runner_dispatch(payload, now=1000)

    def test_rejects_boolean_timestamp_values(self):
        for field, value in (("now", True), ("expires_at", True)):
            with self.subTest(field=field):
                payload = {**self.payload, "expires_at": value} if field == "expires_at" else self.payload
                with self.assertRaises(ValueError):
                    validate_runner_dispatch(payload, now=value)

    def test_rejects_non_mapping_payload(self):
        with self.assertRaisesRegex(ValueError, "must_be_mapping"):
            validate_runner_dispatch([], now=1000)


if __name__ == "__main__":
    unittest.main()
