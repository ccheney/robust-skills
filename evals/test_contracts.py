"""Regression tests for measurement fairness, isolation, and truthful reporting."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from evals.checks import evaluate, validate_rule
from evals.cases import input_prompt, load_tasks
from evals.graders import grade
from evals.messaging import markup_data
from evals.reporting import breakdown, fingerprint
from evals.runner import run_trial
from evals.test_evals import TEXTS, FakeClient, completion

ROOT = Path(__file__).resolve().parents[1]


class OutcomeTests(unittest.TestCase):
    def test_graph_constraints_reject_extra_edges_and_cycles(self):
        rule = {
            "id": "graph",
            "op": "edges",
            "required": [["a", "b"]],
            "allowed": [["a", "b"], ["b", "c"]],
        }
        self.assertTrue(evaluate([{"from": "a", "to": "b"}], rule))
        self.assertFalse(
            evaluate([{"from": "a", "to": "b"}, {"from": "c", "to": "a"}], rule)
        )
        self.assertFalse(
            evaluate(
                [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}],
                {"id": "cycle", "op": "acyclic"},
            )
        )

    def test_set_equality_accepts_order_but_not_duplicate_substitution(self):
        rule = {"op": "set_equals", "value": ["a", "b"]}
        self.assertTrue(evaluate(["b", "a"], rule))
        self.assertFalse(evaluate(["a", "a"], rule))

    def test_missing_and_null_are_distinct(self):
        rule = {"op": "equals", "path": ["id"], "value": None}
        self.assertTrue(evaluate({"id": None}, rule))
        self.assertFalse(evaluate({}, rule))
        self.assertFalse(evaluate({"id": None}, {"op": "absent", "path": ["id"]}))

    def test_invalid_or_vacuous_configuration_is_rejected(self):
        for rule in [
            {"id": "bad", "op": "all", "checks": []},
            {"id": "bad", "op": "one_of", "value": []},
            {"id": "bad", "op": "length", "min": 3, "max": 1},
            {"id": "bad", "op": "edges", "required": [["a"]]},
        ]:
            with self.subTest(rule=rule), self.assertRaises(ValueError):
                validate_rule(rule)

    def test_markup_emphasis_does_not_require_an_outer_wrapper(self):
        for text in ["<b>Release 42</b>", "<p><strong>Release 42</strong></p>"]:
            self.assertEqual(
                markup_data({"body": text}, {"text_path": ["body"]})["bold_text"],
                "Release 42",
            )
        self.assertEqual(
            markup_data({"body": "&lt;at&gt;Ada&lt;/at&gt;"}, {"text_path": ["body"]})[
                "mentions"
            ],
            [],
        )

    def test_expected_assertions_cannot_silently_disappear(self):
        case = next(c for c in load_tasks(ROOT) if c["id"] == "mermaid-reserved-id")
        with patch(
            "evals.graders.execute",
            return_value={"assertions": [{"id": "diagram-renders", "passed": True}]},
        ):
            out = grade(ROOT, case, "anything")
        self.assertEqual(out["status"], "fail")
        self.assertTrue(
            any(
                a["detail"].startswith("Not reached")
                for a in out["assertions"]
                if not a["passed"]
            )
        )

    def test_unavailable_browser_is_not_a_model_failure(self):
        case = next(c for c in load_tasks(ROOT) if c["id"] == "mermaid-reserved-id")
        with patch(
            "evals.graders.execute",
            return_value={"status": "blocked", "detail": "Browser unavailable"},
        ):
            self.assertEqual(grade(ROOT, case, "anything")["status"], "blocked")

    def test_inputs_exclude_private_grading_material(self):
        for case in load_tasks(ROOT):
            prompt = input_prompt(ROOT, case)
            self.assertNotIn("reference_outputs/", prompt)
            self.assertNotIn("counterexamples", prompt)
        with self.assertRaises(ValueError):
            input_prompt(
                ROOT, {"prompt": "Task", "inputs": ["reference_outputs/private.txt"]}
            )

    def test_task_preload_is_not_counted_as_automatic_selection(self):
        client = FakeClient(completion())
        out = run_trial(client, TEXTS, "Task", preload="example")
        self.assertEqual(out["preloaded_skills"], ["example"])
        self.assertEqual(out["selected_skills"], [])
        self.assertIn(
            "Read references/details.md", client.inputs[0]["messages"][0]["content"]
        )

    def test_blocked_pair_and_partial_repeat_do_not_claim_success(self):
        base = {"id": "case", "skill": "skill", "split": "development", "kind": "task"}
        rows = [
            {**base, "variant": "candidate", "repeat": 1, "status": "pass", "score": 1},
            {**base, "variant": "none", "repeat": 1, "status": "blocked"},
            {**base, "variant": "candidate", "repeat": 2, "status": "blocked"},
        ]
        report = breakdown(rows)
        self.assertEqual(
            report["paired_task_outcomes"]["none"]["candidate_only_pass"], 0
        )
        self.assertIsNone(report["repeat_consistency"][0]["all_pass"])
        self.assertEqual(report["cells"][0]["unscored"], 1)

    def test_fingerprint_includes_fixture_content_but_ignores_local_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evals/fixtures").mkdir(parents=True)
            f = root / "evals/fixtures/input.txt"
            f.write_text("first")
            before = fingerprint(root)
            (root / "evals/local.json").write_text("private identifier")
            self.assertEqual(fingerprint(root), before)
            f.write_text("second")
            self.assertNotEqual(fingerprint(root), before)


class ResumeTests(unittest.TestCase):
    def test_resume_skips_scored_trials_without_a_provider(self):
        import io
        from evals.runner import main

        with tempfile.TemporaryDirectory() as directory:
            args = [
                "--case",
                "modern-javascript-negative",
                "--variants",
                "candidate",
                "--output",
                directory,
                "--no-local-config",
            ]
            client = FakeClient(completion())
            client.requests = 1
            client.events = []
            with (
                patch("evals.runner.Gemini", return_value=client),
                patch("sys.stdout", new_callable=io.StringIO),
            ):
                self.assertEqual(main(args), 0)
            with (
                patch("evals.runner.Gemini") as provider,
                patch("sys.stdout", new_callable=io.StringIO),
            ):
                self.assertEqual(main(args + ["--resume"]), 0)
                provider.assert_not_called()
            with (
                patch("sys.stderr", new_callable=io.StringIO),
                self.assertRaises(SystemExit) as error,
            ):
                main(args + ["--resume", "--model", "gemini-3.5-flash"])
            self.assertEqual(error.exception.code, 2)

    def test_empty_artifacts_do_not_pass_any_task(self):
        # Contract checks run here; executable controls are covered by calibrate.
        for case in load_tasks(ROOT):
            if case["grader"] in (
                "contract",
                "slack-contract",
                "teams-contract",
                "markup-contract",
                "teams",
                "fsd",
            ):
                with self.subTest(case=case["id"]):
                    self.assertEqual(grade(ROOT, case, "{}")["status"], "fail")


if __name__ == "__main__":
    unittest.main()
