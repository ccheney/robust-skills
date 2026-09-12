[![skills.sh](https://skills.sh/b/ccheney/robust-skills)](https://skills.sh/ccheney/robust-skills)

# robust-skills

Task-specific engineering skills for Bazel, backend and frontend architecture,
JavaScript, CSS, PostgreSQL/Drizzle, Mermaid, Slack, and Microsoft Teams. Each
skill has a concise entrypoint and links to technical references only when the
task needs them. Version-specific examples are research snapshots; match them
to the project's installed tools and target platforms.

Version 4 changes automatic selection and workflow guidance. See the
[release notes](docs/releases/v4.0.0.md) for migration details and the
[authoring audit](docs/skill-authoring-audit.md) for the OpenAI guidance and
validation results. Skill names and installation selectors are unchanged.

```bash
npx skills add https://github.com/ccheney/robust-skills
```

### bazel

Configure and troubleshoot Bazel builds. Use when editing BUILD or MODULE.bazel files, writing Starlark, diagnosing target, cache, or CI failures, or adopting or upgrading Bazel.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill bazel
```

### clean-ddd-hexagonal

Design or review backend domain and dependency boundaries using DDD, Clean Architecture, and ports/adapters. Use for aggregate modeling, bounded contexts, use-case isolation, or architecture refactoring; not routine CRUD changes.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill clean-ddd-hexagonal
```

### feature-slicing

Organize frontend code with Feature-Sliced Design (FSD). Use when adopting FSD, placing code in an existing FSD project, or fixing slice imports and public APIs; not for every new component or page.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill feature-slicing
```

### modern-javascript

Implement or debug JavaScript language behavior, including promise completion, async iteration, mutation, and runtime compatibility. Use for ECMAScript semantics or polyfill/transform choices; not unrelated framework or TypeScript type design.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill modern-javascript
```

### modern-css

Implement or debug CSS layouts, responsive styles, themes, and motion. Use when choosing native CSS features or replacing legacy styling with browser-compatible CSS; not for unrelated frontend logic.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill modern-css
```

### postgres-drizzle

Write or review PostgreSQL schemas, queries, migrations, and Drizzle ORM code. Use for Postgres/Drizzle relations, indexing, pooling, or query performance; not for unrelated databases or generic backend work.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill postgres-drizzle
```

### mermaid-diagrams

Create or fix Mermaid diagrams in Markdown. Use for requested flowcharts, sequence diagrams, ER diagrams, state machines, or system diagrams when Mermaid is the output format; not every visualization or explanation.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill mermaid-diagrams
```

### slack-mrkdwn

Format or debug Slack message text, mentions, links, dates, and escaping. Use when choosing Slack mrkdwn versus Markdown, rich_text, or plain_text for a receiving field; not Block Kit layout or Slack history retrieval.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill slack-mrkdwn
```

### slack-block-kit

Build or debug Slack Block Kit payloads for messages, modals, App Home, streaming responses, and Work Object unfurls. Use for block layout, elements, or interaction schemas; not plain Slack text formatting alone.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill slack-block-kit
```

### teams-message-formatting

Format or debug Microsoft Teams bot text, Adaptive Card text, and Graph chatMessage bodies. Use for markup, mentions, links, escaping, or client rendering issues; not card layout/actions or ordinary Teams conversation retrieval.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill teams-message-formatting
```

### teams-adaptive-cards

Build, validate, or repair Adaptive Card layouts, actions, forms, and delivery wrappers for Microsoft Teams. Use when Teams is the target host, including bot, webhook, Graph, and MessageCard migration tasks. Exclude Windows/custom card hosts and Teams text-only formatting.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill teams-adaptive-cards
```

## Contributing and validation

The root [evals directory](evals/README.md) contains reusable cases, fixtures,
112 artifact tasks, 226 routing requests, deterministic graders, and a bounded
Gemini 3.8 Flash free-tier runner. Run evaluations
locally with your Google CLI account or an environment key. See the evaluation
guide for setup and limits. No evaluation workflow runs in GitHub Actions.

Use a description that identifies the actual task, and keep conditional detail
in a linked reference. Preserve explicit user choices and keep verification
proportional to the change. The [authoring audit](docs/skill-authoring-audit.md)
explains the scope of the v4 review.

For repository checks, install Python 3.10+ and PyYAML, then run:

```bash
python3 -m pip install 'PyYAML>=6,<7'
python3 scripts/validate_skills.py
```

The validator checks metadata, local resource links, and evaluation coverage.
It does not measure model activation or technical correctness. Use the
[representative prompts](evals/routing.json) and
[workflow cases](evals/workflows.json) to review behavior when changing a
skill. Keep expected routing separate from the evaluator's input.
