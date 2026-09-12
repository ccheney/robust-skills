# Skill evaluations

Run these evaluations locally to find missing skill guidance, routing mistakes,
and regressions. The suite has **112 artifact tasks across all 11 skills**, **226
routing requests**, and **371 grader controls** (alternative correct answers and
deliberate semantic mistakes). See [COVERAGE.md](COVERAGE.md) for every scenario.
There is no CI workflow and no automatic report upload.

## Run locally

Requirements: Python 3.10+, Node.js for the bundled Teams linter, and Docker.
The preparation command downloads the pinned public runtime dependencies; it
does not call a model. The graders run JavaScript, Chromium, Mermaid, Drizzle,
Buildifier and PostgreSQL in disposable containers.

```bash
python3 -m pip install -r evals/requirements.txt
python3 -m evals.prepare
python3 scripts/validate_skills.py
python3 -m evals.validation
RUN_DOCKER_EVAL_TESTS=1 python3 -m unittest evals.test_evals evals.test_contracts
python3 -m evals.calibrate --jobs 3
python3 -m evals.runner --dry-run
```

`calibrate` must accept every reference answer and reject every counterexample
for its declared reason. An unavailable runtime or an assertion that never ran
does not establish that a negative control works. Calibration is grader
verification, not evidence of model performance.

Configure a free-tier Google account as described below, then run:

```bash
# Four routing requests and three paired artifact tasks: 10 trials.
python3 -m evals.runner --profile smoke --output evals/results/smoke

# One development task per skill, paired with no-skill answers: 22 trials.
python3 -m evals.runner --profile coverage --max-requests 100 \
  --output evals/results/coverage

# Focus on a skill; use repeated paired trials before drawing conclusions.
python3 -m evals.runner --profile full --skill modern-javascript --suite task \
  --repeats 3 --max-requests 100 --output evals/results/javascript

# Inspect descriptions independently of task execution.
python3 -m evals.runner --profile full --suite routing --skill slack-mrkdwn \
  --variants candidate --output evals/results/slack-routing

# Keep current fixtures/graders while comparing two skill snapshots.
python3 -m evals.runner --profile coverage --variants candidate,none,baseline \
  --baseline-ref v4.0.0 --output evals/results/comparison
```

Development is the default split. Select `--split holdout` for reserved
measurement cases or `--split all` for the complete inventory. `--case ID` is
repeatable and must name a case in the selected profile. `--skill`, `--suite`
and `--split` combine as filters. The full suite with both splits and the default
candidate/no-skill arms contains 450 trials before repetitions; it is unlikely
to fit a small free quota in one run.

To continue after a quota reset, repeat the same command with `--resume` and the
same output directory. Scored trials are reused, while blocked, inconclusive and
errored trials are attempted again. Model, selected trials, skill snapshot,
fixture/harness fingerprint and turn limit must match. The per-invocation request
budget and spacing can change. To rerun a scored failure after editing a skill,
start a new output directory; never overwrite the before-change evidence.

## What is measured

- **Routing:** the model sees only the skill names/descriptions initially.
  Actual successful `read_skill` calls determine selection, compared against
  expected sets. Cases include direct requests, implicit needs, incomplete
  context, scope boundaries, keyword decoys, similar skills and mixed requests.
- **Artifact quality:** the relevant skill is explicitly supplied in candidate
  and previous-snapshot arms, with optional reference reads. This separates
  quality conditional on skill availability from automatic selection. The
  no-skill arm receives the identical request and raw inputs, without the catalog
  or skill text. `preloaded_skills` and observed `selected_skills` are distinct.
- **Repeat consistency and comparisons:** reports retain all per-assertion
  scores, per-skill/split cells, paired candidate/no-skill/baseline outcomes, and
  whether all or any observed repeated trials pass. Unscored trials remain
  visible. These are empirical counts, not statistical significance claims.

Each trial starts with fresh messages, skill state and grader resources. The
model can read only repository skill Markdown and bounded reference ranges.
It cannot access expected answers, grader code, local credentials, personal
skills, Git history, shell, database or posting tools. Graders execute artifacts
after generation; this is not an interactive coding-agent benchmark. These
numbers describe this API harness, **not Codex, Copilot or Claude Code activation
or end-to-end success rates**.

## Fixtures and graders

`tasks/<skill>.json` owns the task definitions. `fixtures/` contains realistic
raw inputs; `assertions/` contains private executable checks;
`reference_outputs/` holds known-good implementations and semantic mutants.
The model receives only each case's declared `inputs`. There are no reference
answers in prompts. `workflows.json` contains separate manual host-level reviews
and contributes no automated task scores.

| Skill area | Observable checks | Limits |
|---|---|---|
| JavaScript | Completion, ordering, errors, iterator cleanup, identity, nullish defaults, grouping, concurrency and retries | Small Node modules, not application integration |
| CSS | Computed styles and geometry across viewports, containers, RTL, themes, focus and reduced motion | Pinned Chromium; not all browsers or visual aesthetics |
| PostgreSQL / Drizzle | Disposable database migrations, constraints, tenant policies, query mutations, concurrent reservations; schema typecheck and ORM metadata | PostgreSQL 18.6 and pinned Drizzle; not production query plans or migration downtime |
| Mermaid | Actual SVG rendering, normalized nodes/edges, messages, cardinalities, inheritance and task dependencies | Pinned Mermaid; no subjective diagram-quality score |
| Bazel | Buildifier syntax plus declared dependencies, visibility, tools, Bzlmod and configuration decisions | Declarative Starlark subset; does not run a full Bazel build or download toolchains |
| DDD / FSD | Domain behavior modules, dependency graphs, ownership, transactions and explicit structured decisions | Structured architecture exercises, not proof of a complete application design |
| Slack / Teams | Payload invariants, content/identity preservation, escaping, surface/method contracts and Teams linter | Targeted constraints, not complete vendor schemas or live delivery/rendering |

Checks focus on observable results and accept legitimate alternatives: import
aliases, reordered symbol sets, different HTML wrappers, table block versus
message wrapper where unspecified, alternate CSS implementations and equivalent
ER relationships. Exact comparisons are reserved for user-supplied identifiers,
content that must be preserved, required values and genuinely ordered results.
Some architecture exercises intentionally use constrained JSON decision fields;
these are specified in the request, not a universal output format for the skill.

Every case has a category, a development/holdout split and a scenario group.
Keep equivalent examples and paraphrases in one split. Validation detects exact
prompt duplicates, group/split conflicts, invalid paths, absent controls,
unknown assertions and missing skill coverage. Human review must still catch
semantic duplicates and ambiguous tasks. Positive-control calibration of
holdout graders is allowed; reserve holdout model outcomes from instruction
and description tuning. If a holdout failure drives an edit, reclassify that
scenario as development and add a new unseen holdout scenario.

The runtime has no network, host mounts or credentials and uses read-only
filesystems, unprivileged users, resource limits and deadlines. Runtime source
hashes reject stale Docker builds. The Node base and PostgreSQL images are
pinned by digest; package locks pin JavaScript libraries and Buildifier downloads
are checksum-verified. Node container image IDs are recorded for executable outcomes; PostgreSQL uses
the fixed image digest above.
OS packages downloaded during image construction can still change; preserve the
built image when exact reproduction matters. This isolation does not make
in-process JavaScript assertions an adversarially secure grading protocol.

## Use failures to improve skills

1. Inspect the request, raw input, artifact, tool trace and individual failures.
   Reproduce locally with the current grader before changing instructions.
2. Classify the problem: missing/misleading skill guidance, routing ambiguity,
   model error despite adequate guidance, underspecified fixture, overly narrow
   grader, or infrastructure failure. Do not teach a skill an arbitrary checker
   preference.
3. For a skill defect, make a focused correction in its description, entrypoint
   or relevant reference. Add a realistic regression and a nearby negative case
   when the change affects scope. Preserve user intent and valid alternatives.
4. Calibrate changed graders against good and deliberately wrong artifacts.
   Rerun affected development cases, sibling boundaries and repeated paired
   comparisons. Keep before/after reports under separate names.
5. Measure on reserved requests after freezing the change. Record unresolved
   failures and provider limits; do not weaken valid assertions to manufacture a
   pass or promote a blocked trial to success.

[VALIDATION.md](VALIDATION.md) records the actual evidence and skill corrections
for this expansion. There is no automatic skill rewrite or model-based judge.
Human review remains necessary for qualitative outputs and ambiguous routing.

## Model, credentials and free quotas

The default is **`gemini-3.8-flash`**. `--model gemini-3.5-flash` exists only for an
explicit older-model comparison. There is no automatic model switch or paid
fallback. Google's [pricing](https://ai.google.dev/gemini-api/docs/pricing) lists
free input/output for the free tier, but a free API still needs authentication
and is subject to [project quotas](https://ai.google.dev/gemini-api/docs/rate-limits).
Use a Google AI Studio project without Cloud Billing enabled.

The local runner can retrieve a Gemini-restricted key through your authenticated
Google CLI account. Copy `local.example.json` to ignored `evals/local.json`:

```json
{
  "gcloud_project": "your-project-with-billing-disabled",
  "gcloud_account": "you@example.com",
  "gcloud_key": "your-gemini-key-id"
}
```

Sign in with `gcloud auth login you@example.com --no-activate`. An optional
`gcloud_version` selects an installed asdf version. The runner checks
`billingEnabled: false` before retrieving the key, keeps the key in memory and
does not change the active CLI account/project. These identifiers are not
included in model context. The key value never enters reports.

Alternatively set `GEMINI_API_KEY` and `GEMINI_FREE_TIER=true`, then pass
`--no-local-config`. This flag asserts that the key belongs to an unbilled
project; only the Google CLI path verifies billing state automatically.

The default budget is 36 requests, eight turns per trial, and 15 seconds between
requests. Tool reads consume additional turns. The shuffle seed controls order,
not model generation randomness. Transient network and HTTP 408/500/502/503/504
failures receive at most two bounded retries, each charged to the request cap.
Quota/authentication errors stop further requests for that invocation. There is
no background scheduling or automatic quota-reset polling.

`results.json` retains artifacts, tool traces, assertions, skill/fixture hashes,
model IDs, token counts where available, elapsed time, retry events, credential
provenance without keys, and unscored reasons. `summary.md` presents outcome
counts and per-skill cells. Exit codes: 0 all pass; 1 scored failures; 2 unscored
trials, possibly alongside failures. Results remain in ignored `evals/results/`.

## Sources

The suite follows Anthropic's [skill evaluation announcement](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)
and [agent evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):
realistic tasks, executable outcomes, calibrated graders, isolated trials,
skill/no-skill comparisons, repeated measurements and explicit failure analysis.
Skill descriptions and instruction scope follow OpenAI's
[skills and prompting guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
The provider uses Google's [OpenAI compatibility endpoint](https://ai.google.dev/gemini-api/docs/openai)
and [documented retry guidance](https://ai.google.dev/gemini-api/docs/troubleshooting).
Model and provider information was checked September 12, 2026.
