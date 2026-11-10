import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from idea_engine import acquisition, core, providers
from idea_engine.__main__ import main


class PlanningTests(unittest.TestCase):
    def test_ten_modes_including_surprise(self):
        self.assertEqual(len(core.modes()), 10)
        self.assertIn("surprise", [m["id"] for m in core.modes()])

    def test_reproducible_random_plan_and_explicit_status(self):
        self.assertEqual(core.make_plan(random_seed=31), core.make_plan(random_seed=31))
        self.assertEqual(core.make_plan()["status"], "planned_not_researched")
        self.assertNotEqual(core.make_plan(random_seed=2)["direction"], core.make_plan(random_seed=31)["direction"])

    def test_deeper_plan_is_bounded(self):
        plan = core.make_plan(depth="deep")
        self.assertLessEqual(len(plan["source_ids"]), plan["limits"]["max_pages"])
        self.assertEqual(plan["limits"]["max_model_calls"], 6)

    def test_required_seed_and_invalid_mode(self):
        for call in [lambda: core.make_plan("repo"), lambda: core.compile_prompt("repo"), lambda: core.make_plan("other")]:
            with self.assertRaises(ValueError):
                call()

    def test_source_layers_and_search(self):
        found = core.find_sources("markdown", "acquisition")
        self.assertIn("markdown-new", [s["id"] for s in found])
        self.assertTrue(all(s["layer"] == "acquisition" for s in found))

    def test_prompt_carries_supplied_evidence_without_claiming_browsing(self):
        result = core.compile_prompt("expand", "test app", [{"id": "e1", "excerpt": "manual task"}])
        self.assertIn('"id": "e1"', result)
        self.assertIn("untrusted data", result)


class GateTests(unittest.TestCase):
    def candidate(self):
        return {"gates": {g: {"status": "pass", "evidence_ids": ["e1"]} for g in ["behavior", "buyer", "outcome", "delivery", "distribution", "economics", "experiment"]}}

    def test_unknown_is_not_failure_or_success(self):
        result = core.evaluate_candidate({})
        self.assertEqual(result["decision"], "needs_evidence")
        self.assertEqual(result["gate"], "behavior")

    def test_first_failure_stops(self):
        item = self.candidate()
        item["gates"]["buyer"] = {"status": "fail", "reason": "No buying authority"}
        item["score"] = 10
        self.assertEqual(core.evaluate_candidate(item)["gate"], "buyer")
        self.assertEqual(core.evaluate_candidate(item)["decision"], "stop")

    def test_unsupported_pass_does_not_advance(self):
        item = self.candidate()
        item["gates"]["behavior"]["evidence_ids"] = []
        self.assertEqual(core.evaluate_candidate(item)["decision"], "needs_evidence")

    def test_abandon_condition_is_prerequisite(self):
        item = self.candidate()
        self.assertEqual(core.evaluate_candidate(item)["decision"], "needs_evidence")
        item["experiment"] = dict(claim="Three qualified buyers purchase", measurement="Paid pilots", deadline="two weeks", currency="USD", abandon_condition="No purchases after qualified exposure")
        self.assertEqual(core.evaluate_candidate(item)["decision"], "ready_to_test")


class CaptureTests(unittest.TestCase):
    def test_unsafe_urls_rejected(self):
        for url in ["http://example.com", "file:///etc/passwd", "https://user:pass@example.com", "https://127.0.0.1", "https://[::1]", "https://localhost", "https://example.com?token=secret", "https://example.com:8080", "https://x.internal"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                acquisition.validate_public_url(url)

    @patch("idea_engine.acquisition.socket.getaddrinfo")
    def test_dns_private_rejected(self, dns):
        dns.return_value = [(2, 1, 6, "", ("10.0.0.1", 443))]
        with self.assertRaises(ValueError):
            acquisition.validate_public_url("https://looks-public.example")

    @patch("idea_engine.acquisition.post_json")
    @patch("idea_engine.acquisition.validate_public_url")
    def test_markdown_capture_contract(self, validate, post):
        post.return_value = ("# A page", {"Content-Type": "text/markdown", "Set-Cookie": "private"})
        text, headers = acquisition.capture_markdown("https://example.com", True)
        self.assertEqual(text, "# A page")
        self.assertNotIn("Set-Cookie", headers)
        self.assertEqual(post.call_args.args[1]["method"], "auto")
        self.assertFalse(post.call_args.args[1]["retain_images"])

    def test_explicit_public_confirmation(self):
        with self.assertRaises(ValueError):
            acquisition.capture_markdown("https://example.com")

    @patch("idea_engine.acquisition.post_json")
    @patch("idea_engine.acquisition.validate_public_url")
    def test_html_and_empty_rejected(self, validate, post):
        for result in [("<html>Blocked</html>", {"Content-Type": "text/html"}), ("", {"Content-Type": "text/markdown"})]:
            post.return_value = result
            with self.assertRaises(acquisition.AcquisitionError):
                acquisition.capture_markdown("https://example.com", True)

    def test_snapshot_provenance_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = core.evidence_record("https://example.com", "# Page", "browser", "first")
            path = core.save_capture(tmp, record, "# Page")
            later = dict(record, retrieved_at="later")
            core.save_capture(tmp, later, "# Page")
            self.assertEqual(json.loads(Path(path).read_text())["retrieved_at"], "first")
            self.assertEqual(record["evidence_status"], "captured_unreviewed")
            self.assertEqual(record["supports"], [])

    def test_redirect_rejected(self):
        with self.assertRaises(acquisition.AcquisitionError):
            acquisition.NoRedirect().redirect_request(None, None, 302, "", {}, "https://127.0.0.1")


class ProviderTests(unittest.TestCase):
    def test_live_calls_opt_in(self):
        for call in [lambda: providers.synthesize("text"), lambda: providers.screen_evidence("text")]:
            with self.assertRaises(ValueError):
                call()

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-secret", "OPENROUTER_MODEL": "test-model"})
    @patch("idea_engine.providers.post_json")
    def test_openrouter_contract_and_unverified_label(self, post):
        post.return_value = (json.dumps({"choices": [{"message": {"content": "hypothesis"}, "finish_reason": "stop"}], "usage": {"total_tokens": 15}}), {})
        result = providers.synthesize("supplied evidence", True)
        self.assertEqual(result["status"], "hypothesis_unverified")
        self.assertEqual(post.call_args.args[1]["model"], "test-model")
        self.assertNotIn("test-secret", json.dumps(result))

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-secret", "OPENROUTER_MODEL": "test-model"})
    @patch("idea_engine.providers.post_json")
    def test_invalid_or_truncated_model_output_is_error(self, post):
        for value in [{"error": "failure"}, {"choices": [{"message": {"content": "partial"}, "finish_reason": "length"}]}]:
            post.return_value = (json.dumps(value), {})
            with self.assertRaises(acquisition.AcquisitionError):
                providers.synthesize("text", True)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-secret", "OPENROUTER_MODEL": "test-model"})
    @patch("idea_engine.providers.post_json")
    def test_oversized_prompt_never_sent(self, post):
        with self.assertRaises(ValueError):
            providers.synthesize("x" * (providers.MAX_INPUT_CHARS + 1), True)
        post.assert_not_called()

    def test_cli_writes_offline_plan_and_preserves_old_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "plan.json")
            self.assertEqual(main(["plan", "--out", path]), 0)
            self.assertEqual(json.loads(Path(path).read_text())["status"], "planned_not_researched")
            self.assertEqual(main(["plan", "--out", path]), 2)


if __name__ == "__main__":
    unittest.main()
