"""Deterministic harness tests. Fake completions are not model performance evidence."""

import copy
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from evals.catalog import Catalog, snapshot
from evals.credentials import from_gcloud
from evals.graders import grade
from evals.providers import Gemini, EvalUnavailable
from evals.runner import build_plan, run_trial, summarize, main
from evals.validation import validate

ROOT = Path(__file__).resolve().parents[1]
TEXTS = {
    "skills/example/SKILL.md": "---\nname: example\ndescription: Handle example tasks.\n---\nRead references/details.md when needed.\n",
    "skills/example/references/details.md": "line 1\nline 2\nline 3\n",
}


def completion(content="answer", calls=None, finish=None):
    msg = {"role": "assistant", "content": content}
    if calls is not None:
        msg["tool_calls"] = calls
    return {
        "model": "test-model",
        "choices": [
            {
                "message": msg,
                "finish_reason": finish or ("tool_calls" if calls else "stop"),
            }
        ],
        "usage": {"prompt_tokens": 12, "completion_tokens": 3},
    }


def call(name, args, identity="call-1"):
    return {
        "id": identity,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)},
        "extra_content": {"google": {"thought_signature": "opaque-test-value"}},
    }


class FakeClient:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.inputs = []

    def chat(self, messages, tools):
        self.inputs.append(copy.deepcopy({"messages": messages, "tools": tools}))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class CatalogTests(unittest.TestCase):
    def test_no_answers_or_personal_skills_in_catalog(self):
        _, texts = snapshot(ROOT)
        self.assertTrue(all(p.startswith("skills/") for p in texts))
        self.assertEqual(len(Catalog(texts).entries), 11)

    def test_reference_access_and_ranges(self):
        catalog = Catalog(TEXTS)
        self.assertIn(
            "error",
            catalog.invoke(
                "read_reference", {"skill": "example", "path": "references/details.md"}
            ),
        )
        catalog.invoke("read_skill", {"skill": "example"})
        found = catalog.invoke(
            "read_reference",
            {
                "skill": "example",
                "path": "references/details.md",
                "start_line": 2,
                "line_count": 1,
            },
        )
        self.assertEqual(found["content"], "line 2")
        self.assertEqual(catalog.loaded, {"example"})

    def test_traversal_and_unknown_tools_are_rejected(self):
        catalog = Catalog(TEXTS)
        for path in (
            "../../evals/pilot.json",
            "/tmp/secret",
            "references/../../answers.txt",
        ):
            self.assertIn(
                "error",
                catalog.invoke("read_reference", {"skill": "example", "path": path}),
            )
        self.assertIn("error", catalog.invoke("shell", {"skill": "example"}))
        self.assertIn("error", catalog.invoke("read_skill", {"skill": ["example"]}))


class TrialTests(unittest.TestCase):
    def test_selection_tracks_tools_and_preserves_signatures(self):
        tool = call("read_skill", {"skill": "example"})
        client = FakeClient(completion(calls=[tool]), completion())
        result = run_trial(client, TEXTS, "Actual task")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["selected_skills"], ["example"])
        self.assertEqual(client.inputs[1]["messages"][2]["tool_calls"][0], tool)
        self.assertEqual(result["tokens"]["prompt_tokens"], 24)
        self.assertNotIn("expected_skills", json.dumps(client.inputs))

    def test_reference_calls_do_not_end_selection_early(self):
        client = FakeClient(
            completion(calls=[call("read_skill", {"skill": "example"})]),
            completion(
                calls=[
                    call(
                        "read_reference",
                        {"skill": "example", "path": "references/details.md"},
                    )
                ]
            ),
            completion(),
        )
        self.assertEqual(run_trial(client, TEXTS, "Task")["status"], "completed")
        self.assertEqual(len(client.inputs), 3)

    def test_claimed_skill_use_is_not_observed_activation(self):
        result = run_trial(FakeClient(completion("I used example.")), TEXTS, "Task")
        self.assertEqual(result["selected_skills"], [])

    def test_no_skill_baseline_has_no_catalog_or_tools(self):
        client = FakeClient(completion())
        run_trial(client, {}, "Same user task")
        self.assertEqual(client.inputs[0]["tools"], [])
        self.assertNotIn("example", json.dumps(client.inputs))

    def test_fresh_context_between_trials(self):
        client = FakeClient(
            completion(calls=[call("read_skill", {"skill": "example"})]),
            completion(),
            completion(),
        )
        run_trial(client, TEXTS, "first")
        second = run_trial(client, TEXTS, "second")
        self.assertEqual(second["selected_skills"], [])
        self.assertEqual(len(client.inputs[2]["messages"]), 2)

    def test_blocked_truncated_empty_and_malformed_are_not_passes(self):
        for response, status in [
            (EvalUnavailable("quota"), "blocked"),
            (completion(finish="length"), "inconclusive"),
            (completion(""), "error"),
            ({"choices": [None]}, "error"),
        ]:
            with self.subTest(status=status):
                self.assertEqual(
                    run_trial(FakeClient(response), TEXTS, "task")["status"], status
                )

    def test_turn_limit_is_not_success(self):
        client = FakeClient(
            completion(calls=[call("read_skill", {"skill": "example"})])
        )
        self.assertEqual(run_trial(client, TEXTS, "task", 1)["status"], "inconclusive")

    def test_zero_scored_cases_do_not_report_perfect_accuracy(self):
        rows = [{"variant": "candidate", "kind": "routing", "status": "blocked"}]
        self.assertIsNone(summarize(rows)["candidate"]["routing"]["pass_rate"])


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "fake-not-a-key", "GEMINI_FREE_TIER": "true"},
            clear=True,
        )
        self.environment.start()

    def tearDown(self):
        self.environment.stop()

    def test_key_and_designated_free_project_required(self):
        for name in ("GEMINI_API_KEY", "GEMINI_FREE_TIER"):
            with patch.dict(os.environ, {name: ""}):
                with self.assertRaises(EvalUnavailable):
                    Gemini()

    def test_model_selection_is_explicit_and_restricted_to_free_models(self):
        self.assertEqual(Gemini(model="gemini-3.8-flash").model, "gemini-3.8-flash")
        with self.assertRaises(EvalUnavailable):
            Gemini(model="unverified-paid-model")

    def test_request_budget_and_fixed_endpoint(self):
        client = Gemini(max_requests=1, interval=0)
        client.opener.open = lambda req, timeout: io.BytesIO(
            json.dumps(completion()).encode()
        )
        client.chat([{"role": "user", "content": "Task"}], [])
        with self.assertRaises(EvalUnavailable):
            client.chat([], [])
        self.assertEqual(client.requests, 1)

    def test_quota_halts_without_retry(self):
        client = Gemini(interval=0)
        with patch.object(
            client.opener, "open", side_effect=HTTPError("url", 429, "quota", {}, None)
        ) as opened:
            for _ in range(2):
                with self.assertRaises(EvalUnavailable):
                    client.chat([], [])
            self.assertEqual(opened.call_count, 1)

    def test_provider_result_requires_choices(self):
        client = Gemini(interval=0)
        client.opener.open = lambda req, timeout: io.BytesIO(b'{"choices": []}')
        with self.assertRaises(EvalUnavailable):
            client.chat([], [])

    def test_transient_503_retries_same_request_then_succeeds(self):
        client = Gemini(max_requests=2, interval=0)
        with (
            patch.object(
                client.opener,
                "open",
                side_effect=[
                    HTTPError("url", 503, "overloaded", {}, None),
                    io.BytesIO(json.dumps(completion()).encode()),
                ],
            ) as opened,
            patch("evals.providers.time.sleep"),
        ):
            self.assertEqual(client.chat([], [])["model"], "test-model")
            self.assertEqual(client.requests, 2)
            self.assertIs(
                opened.call_args_list[0].args[0], opened.call_args_list[1].args[0]
            )
            self.assertEqual([e["status"] for e in client.events], [503, 200])

    def test_transient_retries_cannot_exceed_run_budget(self):
        client = Gemini(max_requests=1, interval=0)
        with patch.object(
            client.opener,
            "open",
            side_effect=HTTPError("url", 503, "overloaded", {}, None),
        ) as opened:
            with self.assertRaisesRegex(EvalUnavailable, "budget exhausted"):
                client.chat([], [])
            self.assertEqual(opened.call_count, 1)

    def test_retry_exhaustion_does_not_disable_later_trials(self):
        client = Gemini(interval=0)
        responses = [HTTPError("url", 503, "overloaded", {}, None) for _ in range(3)]
        responses.append(io.BytesIO(json.dumps(completion()).encode()))
        with (
            patch.object(client.opener, "open", side_effect=responses),
            patch("evals.providers.time.sleep"),
        ):
            with self.assertRaisesRegex(EvalUnavailable, "exhausted 2 retries"):
                client.chat([], [])
            self.assertEqual(client.chat([], [])["model"], "test-model")
            self.assertEqual(client.requests, 4)

    def test_auth_errors_are_not_retried_or_logged_with_secrets(self):
        client = Gemini(interval=0)
        with patch.object(
            client.opener,
            "open",
            side_effect=HTTPError("url", 403, "fake-not-a-key", {}, None),
        ) as opened:
            with self.assertRaises(EvalUnavailable) as caught:
                client.chat([], [])
            self.assertNotIn("fake-not-a-key", str(caught.exception))
            self.assertEqual(opened.call_count, 1)


class CredentialTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "local.json"
        self.path.write_text(
            json.dumps(
                {
                    "gcloud_project": "test-project",
                    "gcloud_account": "person@example.com",
                    "gcloud_key": "test-key",
                }
            )
        )

    def tearDown(self):
        self.directory.cleanup()

    def test_gcloud_billing_check_precedes_secret_lookup(self):
        from subprocess import CompletedProcess

        responses = [
            CompletedProcess([], 0, '{"billingEnabled":false}', ""),
            CompletedProcess([], 0, "fake-key\n", ""),
        ]
        with patch("evals.credentials.subprocess.run", side_effect=responses) as run:
            credentials = from_gcloud(self.path)
            self.assertEqual(credentials["key"], "fake-key")
            self.assertEqual(credentials["source"]["billing_enabled"], False)
            self.assertIn("--account=person@example.com", run.call_args_list[0].args[0])
            self.assertIn("billing", run.call_args_list[0].args[0])
            self.assertIn("get-key-string", run.call_args_list[1].args[0])
            self.assertNotIn("fake-key", json.dumps(credentials["source"]))

    def test_billed_project_does_not_retrieve_key(self):
        from subprocess import CompletedProcess

        with patch(
            "evals.credentials.subprocess.run",
            return_value=CompletedProcess([], 0, '{"billingEnabled":true}', ""),
        ) as run:
            with self.assertRaisesRegex(EvalUnavailable, "disabled billing"):
                from_gcloud(self.path)
            self.assertEqual(run.call_count, 1)

    def test_missing_config_uses_environment_path(self):
        with patch("evals.credentials.subprocess.run") as run:
            self.assertIsNone(from_gcloud(self.path.parent / "missing.json"))
            run.assert_not_called()

    def test_invalid_config_fails_without_calling_gcloud(self):
        self.path.write_text("{}")
        with patch("evals.credentials.subprocess.run") as run:
            with self.assertRaises(EvalUnavailable):
                from_gcloud(self.path)
            run.assert_not_called()


class InventoryTests(unittest.TestCase):
    def test_inventory_and_balanced_variants(self):
        self.assertEqual(validate(ROOT), 6)
        plan = build_plan(ROOT, "smoke", ["candidate", "none"], 1, 42)
        self.assertEqual(len(plan), 10)
        for case in ("save-all", "graph", "checkout-placement"):
            self.assertEqual(
                {t["variant"] for t in plan if t["case"]["id"] == case},
                {"candidate", "none"},
            )

    def test_baseline_requires_ref(self):
        with self.assertRaises(ValueError):
            build_plan(ROOT, "smoke", ["baseline"], 1, 42)

    def test_dry_run_makes_no_provider(self):
        with (
            patch("evals.runner.Gemini") as provider,
            patch("evals.runner.from_gcloud") as credentials,
            patch("sys.stdout", new_callable=io.StringIO),
        ):
            self.assertEqual(main(["--dry-run"]), 0)
            provider.assert_not_called()
            credentials.assert_not_called()

    def test_missing_credentials_emit_blocked_report(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict(os.environ, {}, clear=True),
            patch("sys.stdout", new_callable=io.StringIO),
        ):
            self.assertEqual(main(["--output", directory, "--no-local-config"]), 2)
            report = json.loads((Path(directory) / "results.json").read_text())
            self.assertEqual(report["requests"], 0)
            self.assertTrue(all(t["status"] == "blocked" for t in report["trials"]))

    def test_targeted_plan_filters_cases_without_live_calls(self):
        with (
            patch("evals.runner.Gemini") as provider,
            patch("sys.stdout", new_callable=io.StringIO) as output,
        ):
            self.assertEqual(
                main(
                    [
                        "--dry-run",
                        "--case",
                        "checkout-placement",
                        "--variants",
                        "candidate",
                    ]
                ),
                0,
            )
            plan = json.loads(output.getvalue())
            self.assertEqual(len(plan["trials"]), 1)
            self.assertEqual(plan["trials"][0]["id"], "checkout-placement")
            provider.assert_not_called()

    def test_unknown_case_is_a_configuration_error(self):
        with (
            patch("sys.stderr", new_callable=io.StringIO),
            self.assertRaises(SystemExit) as caught,
        ):
            main(["--dry-run", "--case", "does-not-exist"])
        self.assertEqual(caught.exception.code, 2)


class GraderTests(unittest.TestCase):
    def setUp(self):
        self.cases = {
            c["id"]: c for c in json.loads((ROOT / "evals/pilot.json").read_text())
        }

    def test_reference_json_outputs_pass(self):
        for identity in ("graph", "webhook", "checkout-placement", "cross-slice"):
            text = (ROOT / "evals/reference_outputs" / f"{identity}.txt").read_text()
            with self.subTest(identity=identity):
                self.assertEqual(
                    grade(ROOT, self.cases[identity], text)["status"], "pass"
                )

    def test_wrong_wrappers_fail(self):
        for identity in ("graph", "webhook"):
            original = (ROOT / "evals" / self.cases[identity]["input"]).read_text()
            self.assertEqual(
                grade(ROOT, self.cases[identity], original)["status"], "fail"
            )

    def test_cross_slice_and_scope_errors_fail(self):
        bad = {
            "form_path": "src/features/form/ui/form.ts",
            "validation_path": "src/entities/form/model/rules.ts",
            "imports": [],
        }
        self.assertEqual(
            grade(ROOT, self.cases["checkout-placement"], json.dumps(bad))["status"],
            "fail",
        )
        self.assertEqual(
            grade(
                ROOT,
                self.cases["cross-slice"],
                (ROOT / "evals/fixtures/imports.json").read_text(),
            )["status"],
            "fail",
        )

    def test_malformed_output_fails(self):
        for value in ("not json", "[]", '{"imports":[null]}'):
            self.assertEqual(
                grade(ROOT, self.cases["cross-slice"], value)["status"], "fail"
            )

    @unittest.skipUnless(
        os.environ.get("RUN_DOCKER_EVAL_TESTS") == "1",
        "Set RUN_DOCKER_EVAL_TESTS=1 after pulling the pinned Node image",
    )
    def test_javascript_controls(self):
        for identity in ("save-all", "rank"):
            valid = (ROOT / "evals/reference_outputs" / f"{identity}.txt").read_text()
            with self.subTest(identity=identity):
                self.assertEqual(
                    grade(ROOT, self.cases[identity], valid)["status"], "pass"
                )
            original = (ROOT / "evals" / self.cases[identity]["input"]).read_text()
            self.assertEqual(
                grade(ROOT, self.cases[identity], original)["status"], "fail"
            )
        self.assertEqual(
            grade(ROOT, self.cases["rank"], "process.exit(0)")["status"], "fail"
        )


if __name__ == "__main__":
    unittest.main()
