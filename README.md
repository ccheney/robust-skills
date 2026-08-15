[![skills.sh](https://skills.sh/b/ccheney/robust-skills)](https://skills.sh/ccheney/robust-skills)

# robust-skills

Architectural taste for agentic engineering and agents. Backend patterns (DDD, Hexagonal, Clean Architecture), frontend structure (Feature-Sliced Design), modern CSS, database design (Postgres/Drizzle), system visualization (Mermaid), modern JavaScript (ES6-ES2026), Slack Block Kit, Slack mrkdwn formatting, Microsoft Teams Adaptive Cards, and Teams message formatting. Every skill is grounded against current official documentation, with verified examples and accurate version/support claims.

```bash
npx skills add https://github.com/ccheney/robust-skills
```

### clean-ddd-hexagonal

Apply an opinionated synthesis of Clean Architecture + DDD + Hexagonal patterns to backend services. Use when designing APIs, microservices, domain models, aggregates, repositories, bounded contexts, or scalable backend structure. Leads with decision trees for the questions LLMs get wrong — where code belongs, entity vs value object, aggregate boundaries — plus a complexity ladder that says when NOT to use these patterns. Language-agnostic (Go, Rust, Python, TypeScript, Java, C#).

```bash
npx skills add https://github.com/ccheney/robust-skills --skill clean-ddd-hexagonal
```

### feature-slicing

Apply Feature-Sliced Design (FSD v2.1) architecture to frontend projects. Use when creating new features/components/pages, restructuring React/Next.js/Vue/Remix projects, organizing frontend code, setting up project structure, fixing import violations, or migrating legacy codebases. Covers the strict layer hierarchy, the one import rule, public-API patterns, the pages-first philosophy that prevents over-slicing, official Next.js App Router integration, and Steiger linter setup.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill feature-slicing
```

### modern-javascript

Modern JavaScript (ES6-ES2026) patterns and best practices. Use when writing new JavaScript, refactoring legacy code, modernizing codebases, or implementing functional patterns. Pins every feature to its true ECMAScript edition and runtime baseline — including the commonly confused ones (`Array.fromAsync` is ES2026, `using` and Temporal are Stage 4 for ES2027, Records & Tuples was withdrawn). Covers `.at()`, `.toSorted()`, `Object.groupBy()`, iterator helpers, Set methods, optional chaining, nullish coalescing, async/await, and more, with syntax-checked examples verified on Node 24.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill modern-javascript
```

### modern-css

Modern CSS features and best practices for building interfaces with pure native CSS — no preprocessors or frameworks. Use when writing CSS for any web project, choosing layout approaches, building responsive components, implementing dark mode or theming, creating animations, styling form elements, or modernizing legacy stylesheets. Covers Grid, Subgrid, Container Queries, `:has()`, `@layer`, `@scope`, nesting, `@property`, `@function`, `oklch`, `color-mix()`, `light-dark()`, scroll-driven animations, view transitions, anchor positioning, popover, and more — each annotated with accurate mid-2026 Baseline/browser-support status and safe-degradation patterns.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill modern-css
```

### postgres-drizzle

PostgreSQL and Drizzle ORM best practices. Use when writing database schemas, queries, relations, migrations, or any database-related code. Covers the stable drizzle-orm 0.x API while explicitly flagging v1.0 (Relational Queries v2 / `defineRelations`) differences so generated code matches the version a project actually uses, plus PG17/18 features, row-level security, connection pooling, and drizzle-kit workflows. Proactively apply when creating APIs, backends, or data models.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill postgres-drizzle
```

### mermaid-diagrams

Generate Mermaid diagrams in markdown, verified against Mermaid v11.16 — every example in the skill renders cleanly with mermaid-cli. Use when visualizing code, systems, processes, data structures, database schemas, workflows, or API flows. Supports flowcharts, sequence diagrams, ER diagrams, state machines, Gantt charts, mindmaps, C4, class diagrams, git graphs, and 12 more types, with a decision tree for picking the right one and a gotchas list covering the parse errors LLMs most often produce.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill mermaid-diagrams
```

### slack-mrkdwn

Slack mrkdwn text formatting syntax for messages, text objects, and attachments. Use when formatting Slack message text, writing mrkdwn strings, constructing text objects, escaping user content, adding mentions or date formatting, or debugging text rendering issues. Covers the critical mrkdwn vs standard Markdown distinction — including Slack's newer standard-Markdown surfaces (`markdown` blocks and the `markdown_text` streaming argument) — plus mentions, date tokens, escaping, parse/verbatim behavior, and legacy attachments.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill slack-mrkdwn
```

### slack-block-kit

Slack Block Kit UI framework for building rich message layouts, modals, App Home views, and AI agent responses. Use when constructing blocks arrays, creating modals or App Home views, adding interactive elements, implementing link unfurling with Work Objects, streaming agent output via chat.startStream/appendStream/stopStream, or designing rich message layouts. Covers all 21 block types — including the 2026 additions (alert, card, carousel, container, table, data table, data visualization, plan, task card) — plus 20 interactive elements, composition objects, surfaces, and Work Objects, with verified limits and validated JSON examples.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill slack-block-kit
```

### teams-message-formatting

Microsoft Teams text formatting syntax across bot activity text, Adaptive Card Markdown, Microsoft Graph chatMessage HTML, Workflows webhook messages, legacy MessageCards, mentions, emoji, links, code blocks, and escaping. Teams has four mutually incompatible text systems, and this skill routes you to the right markup for the surface, including desktop-vs-mobile support gaps and mention wire formats. Updated for the May 2026 O365 connector retirement. Use when formatting Teams message text, constructing Teams mentions, writing Graph chatMessage bodies, or debugging Teams rendering issues.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill teams-message-formatting
```

### teams-adaptive-cards

Microsoft Teams Adaptive Cards for rich message layouts, notifications, approvals, forms, message extensions, bot responses, Workflows webhooks, and Microsoft Graph chatMessage attachments. Use when constructing, validating, wrapping, or migrating Teams card payloads. Covers version policy (default 1.2, ceiling 1.5 — Teams has no 1.6), Universal Actions with user-specific views, charts, people picker, `targetWidth` responsive layouts, and the post-May-2026 connector retirement migration path. Includes transport-specific wrappers and a bundled linter that catches wrapper mismatches and unsupported features before you ship a card.

```bash
npx skills add https://github.com/ccheney/robust-skills --skill teams-adaptive-cards
```
