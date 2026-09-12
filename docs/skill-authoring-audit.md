# Skill authoring audit — v4.0.0

Reviewed on September 11, 2026 against OpenAI's
[Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra),
[Build skills](https://developers.openai.com/plugins/build/skills), and
[local skill discovery guidance](https://learn.chatgpt.com/docs/build-skills).
The updated built-in `skill-creator` guidance also informed the review.

## Review criteria

OpenAI recommends short, discriminating descriptions; conditional reference
loading; and instructions that support a concrete outcome without prescribing
an unnecessary itinerary. The description should identify the task before it
can be shortened in a large skill catalog. Detailed procedures belong in the
body or references. Explicit user choices take precedence over skill guidelines.

Applied those criteria to all 11 entrypoints, the three existing
`agents/openai.yaml` files, resource routing, and instruction-bearing guidance
in the references. This is an authoring and behavior review, not a new claim
that every historical technical example or platform-support snapshot has been
revalidated against September 2026 releases.

## Per-skill changes

Character counts are YAML-decoded description lengths. Line counts include
frontmatter. These measurements describe this revision, not mandatory size
limits for future skills.

| Skill | Description chars, before → after | Entrypoint lines, before → after | Principal correction |
|---|---:|---:|---|
| bazel | 573 → 178 | 378 → 52 | Route by graph question; preserve pins; narrow checks to affected targets. |
| clean-ddd-hexagonal | 532 → 229 | 212 → 48 | Select for domain/dependency design; remove size/team thresholds and mandatory pattern progression. |
| feature-slicing | 582 → 198 | 247 → 49 | Require an FSD placement/adoption task; preserve existing frameworks and tooling. |
| mermaid-diagrams | 499 → 215 | 219 → 50 | Select for Mermaid output; preserve format choice and distinguish syntax checks from rendering. |
| modern-css | 884 → 199 | 174 → 50 | Focus on CSS behavior; preserve preprocessors and scope resets to the task. |
| modern-javascript | 539 → 209 | 181 → 45 | Focus on language/async semantics and compatibility; remove blanket test-suite instructions. |
| postgres-drizzle | 495 → 208 | 225 → 41 | Require Postgres/Drizzle work; separate authoring from execution and route migration details conditionally. |
| slack-block-kit | 1,000 → 212 | 490 → 37 | Separate layout/interaction from plain text; move streaming mechanics to a focused reference. |
| slack-mrkdwn | 740 → 218 | 322 → 42 | Select the receiving renderer; split syntax, rendering, and message behavior references. |
| teams-adaptive-cards | 702 → 218 | 242 → 53 | Separate card and transport contracts; preserve the local linter with portable invocation instructions. |
| teams-message-formatting | 822 → 228 | 161 → 43 | Focus on markup/identity; avoid automatic card conversion or transport replacement. |
| **Total** | **7,368 → 2,312 (69% less)** | **2,851 → 510 (82% less)** | |

Every entrypoint states its input context, relevant constraints, output, and
completion expectations. Questions are tied to missing facts that affect the
result rather than blanket approval gates. Skill names and existing UI metadata
are unchanged; automatic invocation remains enabled by default.

All 77 existing technical reference files remain. Four focused references were
added for material previously embedded in Slack entrypoints. Duplicate per-skill
README files for Mermaid and Postgres were removed; the repository README is
the installation/catalog documentation. References no longer point to removed
entrypoint sections for essential guidance.

Supporting instructions were corrected where they could contradict the new
scope: aggregate sizing and cross-aggregate transactions, FSD migration approval,
CSS resets/preprocessor replacement, Drizzle migration editing/recovery, and
MessageCard handling on a working Workflows transport. Wire-format constraints
and version-specific invariants remain in the appropriate references.

## Validation and limits

- OpenAI's installed `skill-creator/scripts/quick_validate.py` passed for all 11
  skills.
- [Repository validation](../scripts/validate_skills.py) passed metadata checks,
  local file-link/reachability checks for all 81 references and the bundled
  Teams script, and coverage of both evaluation inventories. Nine deliberately
  invalid temporary fixtures verified failure reporting, including broken
  links, an unreachable resource, malformed metadata, and missing cases.
- A separate Markdown-anchor inspection covered 559 links, including duplicate
  heading suffixes. This is an audit check; the repository validator checks file
  targets, not fragment anchors or external URLs.
- An independent evaluator received only the catalog descriptions and 55
  numbered prompts, without expected classifications.
  Its selections matched all 55 expectations: 44 selected a skill, 11 selected
  none. These are manual model assessments, not observed activation in a host's
  skill loader or a statistical benchmark.
- A second independent evaluator completed one concrete workflow per skill.
  Review of all 11 outputs confirmed scope preservation, appropriate reference
  selection, and explicit disclosure of unavailable checks. Four generated
  messaging payloads parsed as JSON. The Teams Graph linter reported zero
  errors and zero warnings, with one optional-schema information item.
- The JavaScript exercise verified concurrent starts, waiting for completion,
  result ordering, and empty input on installed Node 24.11.1. Its requested
  Node 20 target was not installed, so target-version execution was not claimed.
- Mermaid rendering, Bazel compilation, CSS browser rendering, database
  execution, and live Slack/Teams delivery were not performed in these bounded
  cases. No dependency installation or live mutation was needed.

The [selection cases](../evals/routing.json) include direct, indirect,
negative, incomplete-input, and scope-boundary requests for each skill. The
[workflow cases](../evals/workflows.json) include their raw artifacts and
instructions so the review can be repeated. Selection case expectations should
be withheld from an evaluator. Explicit-invocation workflow results assess the
loaded instructions, not automatic selection.

## Maintaining the result

When a skill changes, review the actual affected use cases and references.
Shorten descriptions without losing their discriminating use case; do not add
keyword catalogs or arbitrary length targets. Keep shared constraints in the
entrypoint and put conditional mechanics where they are used. Correct observed
failures narrowly, and distinguish a project convention from a technical
requirement. Rerun relevant cases instead of requiring a full audit for every
wording edit.
