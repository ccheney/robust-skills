# Validation evidence — September 12, 2026

This expansion contains 112 artifact tasks (81 development, 31 holdout), 226
routing requests, 140 positive controls, and 231 semantic counterexamples.
The 371 controls verify the graders; they are not 371 successful model trials.

## Local verification

- All 371 controls calibrated successfully across all 112 tasks: each reference
  passed, and each counterexample failed its declared, actually executed checks.
- All 48 harness tests passed with Docker tests enabled. These exercise actual
  executable controls and fake-provider infrastructure paths; fake responses
  are not model-quality evidence.
- Skill metadata/reference validation passed for all 11 skills. Task inventory,
  private fixture paths, assertion IDs, routing labels, splits, and profile
  validation passed. The full/all-splits dry run plans 450 paired/routing trials
  without making provider calls.
- The pinned JavaScript runtime dependency audit reported zero vulnerabilities.
  This is the package audit result at validation time, not a guarantee about all
  runtime software or future advisories.

The final calibration summary and independent artifacts are in
[evidence/2026-09-12](evidence/2026-09-12/). Reproduce the controls with
`python3 -m evals.prepare` followed by `python3 -m evals.calibrate --jobs 3`.

## Independent forward tests

Independent Codex agents received realistic requests, raw inputs and skill paths,
without grader code, reference answers, expected labels or proposed fixes.
Fourteen artifacts across all 11 skills passed the final outcome graders.
This was a diagnostic forward test, not a randomized Gemini comparison.

The first passes exposed four overly narrow evaluation assumptions:

- A Teams HTML answer used valid emphasis without an outer paragraph/div wrapper.
  The grader now measures emphasized content rather than a tag's list index.
- An FSD answer represented an empty wildcard export set as `[]`; the request had
  not required a boolean. Both empty-set and false representations are accepted.
- A Slack answer returned the requested table block directly; the request had
  not required a message envelope. Those table tasks accept either representation.

- A missing-identity answer named the required Slack ID `user_id` rather than
  `slack_user_id`. Both names refer to the same absent identity in this request;
  unrelated missing fields are still rejected.

These became additional positive controls. The Slack table checks were also
strengthened to verify every requested data row and numeric value. PostgreSQL
RLS checks verify an authorized insert as well as rejected cross-tenant writes.
No skill was changed merely to satisfy these checker preferences.

## Skill corrections informed by evals

An earlier completed Gemini 3.5 smoke run exposed two description failures:

| Request | Observed behavior | Skill change |
|---|---|---|
| Async saves inside `forEach` return before completion | No JavaScript skill was loaded | `modern-javascript` now names promise completion, iteration and mutation as concrete language-behavior tasks |
| Adaptive Card for a Windows notification host | Teams card skill loaded despite the host mismatch | `teams-adaptive-cards` now leads with Microsoft Teams as the required target host and explicitly separates Windows/custom hosts |

The earlier no-skill FSD answer also reversed dependency edges; its paired
candidate answer passed, so this did not justify changing the FSD skill.

After the two description edits, a fresh independent manual assessment selected
the expected sets for all 40 requests owned by those skills, including nearby
scope boundaries. The catalog and requests were provided without expected
labels. This supports the clarity of the revised descriptions, but it is **not
an observed Gemini or host activation rate**. The descriptions still need a
completed repeated API comparison when quota is available.

## Live Gemini 3.8 limitation

The new coverage run selected Gemini 3.8 Flash explicitly. The API accepted one
request and then returned HTTP 429 on the next turn, leaving all 11 planned
candidate tasks unscored. A later targeted routing invocation also received 429
and left both selected cases unscored. Neither invocation switched models,
enabled billing or used a paid fallback.

Therefore this expansion makes no claim that Gemini 3.8 passes the full suite,
or that the two description changes improve its measured activation rate.
The prior Gemini 3.5 smoke results are used only as failure evidence, not mixed
into current-suite scores. Run fresh paired development comparisons after the
free quota resets, retaining before/after reports in separate output folders.
