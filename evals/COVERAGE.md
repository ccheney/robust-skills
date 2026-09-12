# Coverage inventory

112 automated artifact tasks and 226 automatic-selection requests cover all 11 skills. The 11 prompts in `workflows.json` remain separate manual review exercises. Counts describe authored coverage, not model pass rates.

| Skill | Tasks | Development / holdout | Positive controls | Counterexamples | Routing | Grading methods |
|---|---:|---:|---:|---:|---:|---|
| bazel | 10 | 8 / 2 | 12 | 21 | 20 | contract, starlark-runtime |
| clean-ddd-hexagonal | 10 | 7 / 3 | 11 | 23 | 22 | contract, javascript-runtime |
| feature-slicing | 10 | 8 / 2 | 11 | 20 | 21 | contract, fsd |
| mermaid-diagrams | 12 | 8 / 4 | 15 | 24 | 20 | mermaid-runtime |
| modern-css | 10 | 8 / 2 | 17 | 20 | 20 | css-runtime |
| modern-javascript | 10 | 8 / 2 | 14 | 20 | 21 | javascript-runtime |
| postgres-drizzle | 10 | 6 / 4 | 16 | 21 | 20 | drizzle-runtime, postgres-runtime |
| slack-block-kit | 10 | 8 / 2 | 11 | 21 | 21 | contract, slack-contract |
| slack-mrkdwn | 10 | 7 / 3 | 11 | 21 | 20 | contract, javascript-runtime |
| teams-adaptive-cards | 10 | 7 / 3 | 10 | 20 | 21 | teams, teams-contract |
| teams-message-formatting | 10 | 6 / 4 | 12 | 20 | 20 | contract, javascript-runtime, markup-contract |

Routing counts use the owning skill; mixed requests also expect other skills. Each skill has 20 individual routing requests, plus six mixed requests across the inventory.

## Task scenarios

Each linked JSON entry includes its raw inputs, outcome assertions, alternative reference answers, and intended failures for its counterexamples. Grading material is never exposed through the model tools.

### [bazel](tasks/bazel.json)

- `bazel-direct-dependency` — build-graph; development; 4 named task checks.
- `bazel-runtime-data` — runfiles; development; 3 named task checks.
- `bazel-narrow-visibility` — visibility; development; 3 named task checks.
- `bazel-hermetic-tool` — hermeticity; holdout; 5 named task checks.
- `bazel-use-repo` — bzlmod; development; 4 named task checks.
- `bazel-select-branches` — configuration; development; 4 named task checks.
- `bazel-explicit-membership` — package-boundaries; development; 2 named task checks.
- `bazel-configured-query` — diagnostics; development; 3 named task checks.
- `bazel-cache-diagnosis` — cache-correctness; holdout; 4 named task checks.
- `bazel-preserve-version` — scope-preservation; development; 4 named task checks.

### [clean-ddd-hexagonal](tasks/clean-ddd-hexagonal.json)

- `ddd-atomic-transfer` — transaction-boundaries; development; 4 named task checks.
- `ddd-outbox-commit` — reliability; development; 4 named task checks.
- `ddd-dependency-direction` — dependency-boundaries; development; 6 named task checks.
- `ddd-context-translation` — integration; holdout; 5 named task checks.
- `ddd-read-model` — complexity-selection; development; 4 named task checks.
- `ddd-event-replay` — temporal-modeling; holdout; 4 named task checks.
- `ddd-aggregate-size` — scope-preservation; development; 3 named task checks.
- `ddd-missing-refund-rule` — missing-context; development; 4 named task checks.
- `ddd-money-value-object` — domain-behavior; development; 7 named task checks.
- `ddd-order-confirm` — domain-behavior; holdout; 8 named task checks.

### [feature-slicing](tasks/feature-slicing.json)

- `fsd-cross-entity-api` — cross-entity; development; 3 named task checks.
- `fsd-server-client-exports` — framework-compatibility; holdout; 4 named task checks.
- `fsd-public-api` — encapsulation; development; 2 named task checks.
- `fsd-internal-cycle` — cycles; development; 2 named task checks.
- `fsd-shared-segments` — layer-exceptions; development; 2 named task checks.
- `fsd-reused-interaction` — extraction; development; 3 named task checks.
- `fsd-preserve-non-fsd` — scope-preservation; holdout; 4 named task checks.
- `fsd-missing-framework` — missing-context; development; 3 named task checks.
- `checkout-placement` — regression; development; 1 named task checks.
- `cross-slice` — regression; development; 1 named task checks.

### [mermaid-diagrams](tasks/mermaid-diagrams.json)

- `mermaid-reserved-id` — syntax; development; 5 named task checks.
- `mermaid-subgraph-collision` — syntax; development; 6 named task checks.
- `mermaid-decision-branches` — branch-semantics; development; 5 named task checks.
- `mermaid-label-punctuation` — label-escaping; holdout; 5 named task checks.
- `mermaid-sequence-aliases` — interaction-order; development; 5 named task checks.
- `mermaid-sequence-order` — causality; holdout; 3 named task checks.
- `mermaid-er-cardinality` — data-modeling; development; 5 named task checks.
- `mermaid-er-one-to-one` — data-constraints; holdout; 4 named task checks.
- `mermaid-state-lifecycle` — state-machine; development; 8 named task checks.
- `mermaid-state-retry` — state-machine; development; 5 named task checks.
- `mermaid-class-inheritance` — class-modeling; development; 5 named task checks.
- `mermaid-gantt-dependency` — scheduling; holdout; 6 named task checks.

### [modern-css](tasks/modern-css.json)

- `css-responsive-cards` — layout; development; 7 named task checks.
- `css-container-adaptation` — container-queries; development; 4 named task checks.
- `css-cascade-overrides` — cascade; development; 3 named task checks.
- `css-parent-validation` — relational-selectors; development; 2 named task checks.
- `css-theme-override` — theming; holdout; 3 named task checks.
- `css-logical-spacing` — writing-modes; development; 4 named task checks.
- `css-reduced-motion` — accessibility; development; 3 named task checks.
- `css-shrinkable-content` — overflow; development; 3 named task checks.
- `css-keyboard-focus` — accessibility; holdout; 5 named task checks.
- `css-shared-tracks` — subgrid; development; 4 named task checks.

### [modern-javascript](tasks/modern-javascript.json)

- `save-all` — correctness; development; 7 named task checks.
- `rank` — correctness; development; 7 named task checks.
- `javascript-nullish` — semantics; development; 5 named task checks.
- `javascript-own-property` — edge-cases; development; 6 named task checks.
- `javascript-group-identity` — data-integrity; development; 5 named task checks.
- `javascript-group-prototype` — security; holdout; 5 named task checks.
- `javascript-lazy-take` — resource-lifecycle; development; 6 named task checks.
- `javascript-regexp-literal` — security; development; 5 named task checks.
- `javascript-bounded-map` — concurrency; holdout; 7 named task checks.
- `javascript-retry-scope` — error-handling; development; 6 named task checks.

### [postgres-drizzle](tasks/postgres-drizzle.json)

- `postgres-nullable-fk` — schema; development; 6 named task checks.
- `postgres-backfill-required` — migration; development; 3 named task checks.
- `postgres-partial-unique` — indexing; development; 4 named task checks.
- `postgres-keyset-ties` — pagination; holdout; 4 named task checks.
- `postgres-latest-valid-order` — query-semantics; development; 4 named task checks.
- `postgres-join-fanout` — aggregation; development; 4 named task checks.
- `postgres-null-antijoin` — null-semantics; holdout; 4 named task checks.
- `postgres-tenant-rls` — tenant-isolation; development; 6 named task checks.
- `postgres-atomic-reservation` — concurrency; holdout; 5 named task checks.
- `drizzle-stable-schema` — orm-compatibility; holdout; 7 named task checks.

### [slack-block-kit](tasks/slack-block-kit.json)

- `slack-message-alert` — surface-compatibility; development; 2 named task checks.
- `slack-header-renderer` — text-object-types; development; 2 named task checks.
- `slack-modal-input` — interactivity; development; 5 named task checks.
- `slack-table-rows` — tabular-data; development; 2 named task checks.
- `slack-sortable-table` — data-types; development; 8 named task checks.
- `slack-markdown-method` — method-compatibility; holdout; 4 named task checks.
- `slack-streaming-chunks` — streaming; development; 6 named task checks.
- `slack-rich-text-list` — structured-rich-text; development; 5 named task checks.
- `slack-accessible-fallback` — accessibility; holdout; 2 named task checks.
- `slack-button-contract` — actions; development; 3 named task checks.

### [slack-mrkdwn](tasks/slack-mrkdwn.json)

- `slack-escape-untrusted` — escaping; development; 8 named task checks.
- `slack-date-seconds` — date-controls; holdout; 5 named task checks.
- `slack-trusted-mention-boundary` — mention-boundaries; holdout; 5 named task checks.
- `slack-message-renderer` — renderer; development; 2 named task checks.
- `slack-standard-markdown-field` — renderer; development; 3 named task checks.
- `slack-literal-label` — literal-text; development; 3 named task checks.
- `slack-stable-ids` — mentions; development; 3 named task checks.
- `slack-missing-identity` — missing-information; holdout; 3 named task checks.
- `slack-verbatim-controls` — escaping; development; 3 named task checks.
- `slack-notification-content` — accessibility; development; 6 named task checks.

### [teams-adaptive-cards](tasks/teams-adaptive-cards.json)

- `teams-required-input` — forms; development; 7 named task checks.
- `teams-mobile-facts` — client-compatibility; holdout; 3 named task checks.
- `teams-execute-fallback` — actions; development; 6 named task checks.
- `teams-toggle-target` — local-interaction; development; 5 named task checks.
- `teams-card-mention-root` — mentions; development; 3 named task checks.
- `teams-accessible-notification` — accessibility; development; 7 named task checks.
- `teams-messagecard-migration` — migration; holdout; 6 named task checks.
- `teams-unique-input-ids` — forms; holdout; 5 named task checks.
- `graph` — regression; development; 1 named task checks.
- `webhook` — regression; development; 1 named task checks.

### [teams-message-formatting](tasks/teams-message-formatting.json)

- `teams-escape-html` — escaping; development; 7 named task checks.
- `teams-graph-renderer` — renderer; development; 4 named task checks.
- `teams-graph-mention` — mentions; development; 7 named task checks.
- `teams-bot-mention` — mentions; development; 3 named task checks.
- `teams-channel-tag` — mentions; holdout; 2 named task checks.
- `teams-card-text-markdown` — renderer; development; 3 named task checks.
- `teams-missing-user-id` — missing-information; holdout; 4 named task checks.
- `teams-app-only-boundary` — transport-boundaries; holdout; 4 named task checks.
- `teams-literal-mention-looking-text` — escaping; development; 4 named task checks.
- `teams-two-mention-builder` — mention-builder; holdout; 7 named task checks.
