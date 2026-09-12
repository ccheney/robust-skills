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

A free API still requires authentication. Configure:

- Repository secret `GEMINI_API_KEY`: that free-tier project's API key.
- Repository variable `GEMINI_FREE_TIER`: `true`, identifying the designated
  free-tier project.

The variable is a configuration assertion, not an API-level billing check. The
runner cannot verify whether billing has been enabled on the key's project.
Do not reuse a paid-project key for these free runs. The runner uses a fixed
model/endpoint, caps request count and output size, spaces requests, and halts
on quota/auth/network errors without retry or a paid fallback. Google controls
[per-project quotas](https://ai.google.dev/gemini-api/docs/rate-limits), so a
complete suite is not guaranteed to fit a day's free allowance.

Standard GitHub-hosted runner time is free for public repositories; artifact
storage has separate allowances. Copilot in CI uses Copilot credits even with
`GITHUB_TOKEN`, and GitHub Models was retired July 30, 2026. This suite does not
use either service. See [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions),
[Copilot billing in Actions](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/copilot-cli-in-github-actions),
and [GitHub Models retirement](https://docs.github.com/en/github-models).

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
pull and dependency install download public packages. Set `GEMINI_API_KEY` and
`GEMINI_FREE_TIER=true` in your local environment before a live run:

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

## CI behavior

Every relevant PR/push runs deterministic validation and the grader tests.
Live LLM evals run through `workflow_dispatch`, after validation, only when the
free-tier variable is configured. A missing key produces a blocked report with
zero requests. GitHub requires the workflow to exist on the default branch
before its manual dispatch becomes available; then you can select a branch.

Live scores are initially report-only. The job summary and seven-day artifacts
show failed and unscored trials. Infrastructure/quota limits are not counted as
successes, and the workflow's green status is not evidence of a passing LLM
benchmark. Promote stable regression cases to gates after reviewing real runs.

## Reports and interpretation

`results.json` stores per-trial artifacts, tool traces, selected skills, grader
results, elapsed time, available token counts, returned model identifiers, Git
refs, snapshot/case hashes, dirty-tree status, and run limits. `summary.md` gives
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
Provider and billing details were checked September 11, 2026.
