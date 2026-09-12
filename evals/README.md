# Skill evaluations

This directory contains evaluation cases, fixtures, outcome graders, and the
runner. They are maintenance tools, not instructions loaded into installed skills.

## What runs

- `routing.json`: 55 direct, indirect, negative, incomplete, and boundary cases
  across all 11 skills. A trial records actual `read_skill` tool calls in this
  harness; saying a skill was used is not evidence of loading it.
- `pilot.json`: six automated artifact cases for JavaScript, Teams Adaptive
  Cards, and FSD. JavaScript executes behavior assertions in a restricted Node
  container. Teams checks wrapper/content invariants and the bundled linter.
  FSD checks requested placement and dependency edges, not prose wording.
- `workflows.json`: the original 11 manual forward-test prompts, retained for
  broader review. These are not counted as automated task scores.
- `fixtures/`: task inputs visible to the model. `reference_outputs/` and
  `graders/`: held outside model context to test grader correctness.

`smoke` runs four routing cases and three task cases. By default task cases run
with candidate skills and without skills (10 total trials). `full` runs all 55
routing cases and all six automated tasks. An optional baseline arm uses skills
from a specified Git commit, branch, or tag, resolved once at startup.

Every trial starts with fresh messages and a fresh catalog. The model can read
skill entrypoints and bounded reference ranges; it has no shell, network,
credential, home-directory, evaluator, or Git-history tools. Graders evaluate
artifacts after the model finishes. This is an API evaluation harness, not a
replica of Codex, Claude Code, or Copilot's instruction hierarchy or skill loader.
Its selection numbers must not be presented as those hosts' activation rates.

## Model and cost

The default is `gemini-3.8-flash`. Google's current
[pricing page](https://ai.google.dev/gemini-api/docs/pricing) lists free input and
output tokens on the free tier. Use a Google AI Studio project **without Cloud
Billing enabled**. Create its API key in [AI Studio](https://aistudio.google.com/apikey).

A free API still requires authentication. The local runner can retrieve a
Gemini-restricted key through an authenticated `gcloud` account. It checks
`billingEnabled: false` before fetching the key, and keeps the key in memory.
The active Google CLI account/project configuration is not changed.

Create an ignored `evals/local.json` using `local.example.json` as the template:

```json
{
  "gcloud_project": "your-project-with-billing-disabled",
  "gcloud_account": "you@example.com",
  "gcloud_key": "your-gemini-key-id"
}
```

Sign in with `gcloud auth login you@example.com --no-activate`. If you manage
Google CLI through asdf, an optional `gcloud_version` field selects an installed
version for these commands. This config contains identifiers, not the key value.
It is never sent to the model or included in the skill catalog.

Without a local config, environment credentials remain supported:
`GEMINI_API_KEY` plus `GEMINI_FREE_TIER=true`. That environment flag is an
assertion, not a billing lookup; only use it for an unbilled project. Pass
`--no-local-config` to select this mode explicitly.

The runner uses a fixed model/endpoint and never falls back to a paid model.
Transient HTTP 408/500/502/503/504 and network failures get at most two retries,
with exponential backoff and jitter. Every attempt counts toward the run's
request cap. A transient failure that exhausts retries leaves that trial
unscored; independent later trials can continue. Authentication, quota (429),
and other nontransient HTTP errors halt provider requests for the run.
Google controls [per-project quotas](https://ai.google.dev/gemini-api/docs/rate-limits),
so a complete suite is not guaranteed to fit a day's free allowance.

## Run locally

Requirements: Python 3.10+, PyYAML 6.x, Node.js, and Docker for the JavaScript
grader. Node runs generated code in a read-only, network-disabled container with
no credentials, limited memory/CPU/processes, and an execution deadline.

```bash
python3 -m pip install 'PyYAML==6.0.2'
docker pull node:24.11.1-bookworm-slim
python3 scripts/validate_skills.py
python3 -m evals.validation
RUN_DOCKER_EVAL_TESTS=1 python3 -m unittest evals.test_evals -v
python3 -m evals.runner --dry-run
```

The commands above need no model key and make no LLM requests. The Node image
pull and dependency install download public packages. After configuring your
local Google account, run:

```bash
python3 -m evals.runner --profile smoke --max-requests 24
python3 -m evals.runner --profile full --repeats 3 \
  --variants candidate,none,baseline --baseline-ref v4.0.0 \
  --max-requests 100 --output evals/results/comparison
```

The request cap applies to the entire run, including reference-reading turns.
The default is four model turns per trial and 15 seconds between requests.
Trials are shuffled with a recorded seed to reduce ordering bias; this seed
controls scheduling, not the provider's generation randomness. Large suites
need larger quotas or multiple days. There is no background scheduling.

## Local execution only

There is no GitHub Actions evaluation workflow. Run validation and live model
comparisons locally. Results stay in the ignored `evals/results/` directory;
no reports are uploaded automatically. The former CI workflow and its GitHub
secret/variable were removed when evaluations moved to local execution.

## Reports and interpretation

`results.json` stores per-trial artifacts, tool traces, selected skills, grader
results, elapsed time, available token counts, returned model identifiers, Git
refs, snapshot/case hashes, dirty-tree status, credential provenance (without
the key), provider attempts/retries, and run limits. `summary.md` gives
per-variant counts. Routing precision/recall and task pass rates use only scored
trials, alongside explicit unscored counts; a fully blocked run has a null rate.
Exit codes: 0 = all trials pass; 1 = scored failures; 2 = blocked, inconclusive,
or errored trials (possibly alongside failures).

Candidate and no-skill cases receive identical task prompts and raw inputs.
Expected routing labels and reference solutions never reach the model. A
previous-release comparison keeps current cases and graders fixed and changes
only the available skill snapshot. Do not claim a statistically significant
improvement from one successful smoke run. Inspect failed traces and repeat
paired trials before changing instructions. Add unseen real requests and
regressions as the pilot grows; do not tune descriptions against every future
measurement case.

Known limits: FSD grading covers placement, not a compiled frontend; the Teams
linter is not live Teams rendering; the JavaScript fixtures are small modules.
There is no model-based judge, description optimizer, or automatic skill rewrite.

## Basis

The approach follows Anthropic's [skill evaluation announcement](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)
and [agent evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):
compare skill/no-skill outcomes, isolate trials, prefer executable graders, and
record failures and resource use. The transport uses Google's documented
[Chat Completions compatibility endpoint](https://ai.google.dev/gemini-api/docs/openai).
Retry behavior follows Google's [troubleshooting guidance](https://ai.google.dev/gemini-api/docs/troubleshooting).
Provider and billing details were checked September 11, 2026.
