---
name: slack-block-kit
description: Proactively apply when generating Slack API payloads with blocks, chat.postMessage calls with structured content, streaming AI responses, or views.open/views.publish calls. Triggers on Block Kit, Slack blocks, section block, actions block, header block, context block, alert block, card block, carousel block, container block, table block, data table block, data visualization block, Slack chart, markdown block, rich text block, image block, input block, video block, context_actions block, plan block, task_card block, chat.startStream, chat.appendStream, chat.stopStream, Slack modal, Slack App Home, Slack surfaces, Slack interactive elements, Slack button, select menu, overflow, datepicker, checkboxes, radio buttons, Work Objects, Slack link unfurl, views.open, views.update, views.push, views.publish, Slack composition objects. Use when building Block Kit payloads, blocks arrays, modals, App Home views, interactive elements, link unfurling, streaming agent output, or rich message layouts.
---

# Slack Block Kit

UI framework for building rich, interactive layouts in Slack messages, modals, and App Home.

## CRITICAL: Two Markup Systems

Text inside Block Kit text objects uses Slack mrkdwn syntax (`*bold*`, `<url|text>`), NOT standard Markdown. The only exception is the `markdown` block, which accepts standard Markdown (`**bold**`, `[text](url)`). Mixing these up is the single most common Block Kit generation error.

## Quick Decision Trees

### "Should I use blocks?"

```
Response type?
├─ Conversational reply, short answer, <3 lines   → text only (no blocks)
├─ Multi-section summary, report, dashboard        → blocks
├─ Two-column key-value data                       → blocks (section fields)
├─ Tabular data                                    → blocks (table / data_table)
├─ Charts or metrics visualization                 → blocks (data_visualization)
├─ Code with heading or surrounding context        → blocks
├─ Visual separation needed between topics         → blocks
└─ Feedback buttons or interactive elements        → blocks
```

### "Which block type?"

```
What am I rendering?
├─ Large section title                → header (plain_text, 150 chars max)
├─ Body text or key-value pairs       → section (text + fields + accessory)
├─ Small metadata or secondary info   → context (images + text, 10 max)
├─ Horizontal separator               → divider
├─ Buttons, menus, date pickers       → actions (25 elements max)
├─ Status callout in a MODAL          → alert (modals only, 200 chars)
├─ Compact entity or summary preview  → card (optional image/actions)
├─ Multiple comparable cards/options  → carousel (1-10 cards)
├─ Grouped/collapsible block set      → container (title + ≤10 child blocks)
├─ Standalone image                   → image (image_url or slack_file)
├─ Formatted text with lists, quotes  → rich_text (nested sub-elements)
├─ Simple static table                → table (100 rows, 20 cols)
├─ Sortable/paginated table           → data_table (caption + 200 data rows)
├─ Pie/bar/area/line chart            → data_visualization (native charts)
├─ LLM-generated markdown content     → markdown (standard MD, messages only)
├─ Embedded video player              → video (requires links.embed:write)
├─ Remote file reference              → file (read-only, source: "remote")
├─ Feedback thumbs up/down            → context_actions (messages only)
├─ Collecting user input              → input (label + element)
├─ AI agent task steps                → plan (sequential tasks, messages only)
└─ Single task with status            → task_card (inside plan or standalone)
```

### "mrkdwn or markdown block?"

```
Content source?
├─ Short formatted text, labels, fields     → mrkdwn in section/context
├─ Long-form LLM-generated content          → markdown block (standard MD)
├─ LLM-generated tables/task lists/code     → markdown block
├─ Programmatic tabular data                → table or data_table block
├─ Need headings                            → markdown block or header blocks
└─ Mixed: structured layout + prose         → section/header blocks + markdown block
```

### "table, data_table, or markdown table?"

```
├─ LLM already emitted a Markdown table          → markdown block
├─ Static data, no interaction needed            → table
└─ Users need sorting, paging, or clickable cells → data_table (caption required)
```

## Block Types Overview

Full property tables for all 21 blocks: [references/BLOCKS.md](references/BLOCKS.md). Highlights and sharp edges below.

### header

Large bold text. `plain_text` only—mrkdwn is not supported. Max 150 chars. Optional `level` selects H1-H4.

```json
{ "type": "header", "text": { "type": "plain_text", "text": "Section Title", "emoji": true } }
```

### section

Primary content block. Supports text (3000 chars), two-column `fields` (10 items, 2000 chars each), and one `accessory` element. Either `text` or `fields` is required. Set `expand: true` to prevent "see more" truncation on long AI responses.

```json
{
  "type": "section",
  "fields": [
    { "type": "mrkdwn", "text": "*Status:*\nActive" },
    { "type": "mrkdwn", "text": "*Owner:*\nChris" }
  ]
}
```

Compatible accessories: button, overflow, datepicker, timepicker, select menus, multi-select menus, checkboxes, radio buttons, image, workflow button.

### divider

```json
{ "type": "divider" }
```

### context

Small, muted text for metadata. Elements: mrkdwn text objects or image elements. Max 10 elements.

```json
{ "type": "context", "elements": [{ "type": "mrkdwn", "text": "Last updated: Feb 9, 2026 • deploy-bot" }] }
```

### actions

Interactive elements: buttons, select menus, overflow menus, date pickers. Max 25 elements.

```json
{
  "type": "actions",
  "elements": [
    { "type": "button", "text": { "type": "plain_text", "text": "Approve" }, "style": "primary", "action_id": "approve_action", "value": "approved" }
  ]
}
```

Button styles: `primary` (green), `danger` (red), or omit for default. Use `primary` sparingly—one per set. Slack requires `action_id` uniqueness within the containing block; globally unique IDs within a payload make routing safer.

### alert

Callout for status, risk, or urgency. **Modals only** — putting an alert in a message payload is invalid. Text accepts `plain_text` or `mrkdwn`, max 200 chars. `level`: `default`, `info`, `warning`, `error`, or `success`. For message-surface callouts, use a section block with an emoji or a card instead.

```json
{
  "type": "alert",
  "text": { "type": "mrkdwn", "text": "*Dependency conflict detected* before deploy." },
  "level": "warning"
}
```

### card

Compact, scannable preview for entities, summaries, records, or agent results. At least one of `hero_image`, `title`, `actions`, or `body` is required.

```json
{
  "type": "card",
  "title": { "type": "mrkdwn", "text": "Daily Standup Reminder" },
  "subtitle": { "type": "mrkdwn", "text": "Runs every weekday at *9:00 AM*" },
  "body": { "type": "mrkdwn", "text": "Last run: Today at 9:00 AM. Status: Success" },
  "actions": [
    { "type": "button", "text": { "type": "plain_text", "text": "View Logs" }, "action_id": "view_logs" }
  ]
}
```

Fields: `icon`/`hero_image` (image elements), `slack_icon` (built-in icon, mutually exclusive with `icon`), `title`/`subtitle` (150 chars), `body`/`subtext` (200 chars), `actions` (max 3 buttons; `danger` left-aligns, `primary`/unstyled right-align). No size attribute.

### carousel

Horizontal, scrollable group of card blocks for options, recommendations, search results, or next steps. Must contain 1-10 cards.

```json
{
  "type": "carousel",
  "elements": [
    { "type": "card", "title": { "type": "mrkdwn", "text": "Option A" } },
    { "type": "card", "title": { "type": "mrkdwn", "text": "Option B" } }
  ]
}
```

### container

Groups up to 10 child blocks. At least one title form is required: `title` (`plain_text`, 150 chars) or `rich_text_title` (a rich-text block element); when both are supplied, the rich title wins. Optional fields include `subtitle`, `icon`, `width` (`narrow`/`standard`/`wide`/`full`), collapsing (`is_collapsible`, `default_collapsed`), and `has_header_divider` for non-collapsible containers. Child blocks: actions, context, divider, file, header, image, input, rich_text, section, table, video — no nested containers, cards, or plan blocks.

```json
{
  "type": "container",
  "title": { "type": "plain_text", "text": "Bulk update: 2 records" },
  "is_collapsible": true,
  "child_blocks": [
    { "type": "section", "text": { "type": "mrkdwn", "text": "*DCW-1024*\nStatus: Open → Closed" } }
  ]
}
```

### image

Standalone image with required alt text. Provide either `image_url` (public, max 3000 chars) or `slack_file` object. Formats: png, jpg, jpeg, gif.

```json
{ "type": "image", "image_url": "https://example.com/chart.png", "alt_text": "Deployment success rate chart" }
```

### rich_text

Advanced formatted text with nested elements: styled text, lists, code blocks, quotes. See [references/RICH-TEXT.md](references/RICH-TEXT.md) before writing nested lists or inline mentions — the nesting rules are easy to get wrong.

```json
{
  "type": "rich_text",
  "elements": [
    { "type": "rich_text_section", "elements": [{ "type": "text", "text": "Key findings:", "style": { "bold": true } }] },
    {
      "type": "rich_text_list",
      "style": "bullet",
      "elements": [
        { "type": "rich_text_section", "elements": [{ "type": "text", "text": "Latency reduced by 40%" }] }
      ]
    }
  ]
}
```

Sub-element types: `rich_text_section` (paragraph), `rich_text_list` (`style: "bullet"` or `"ordered"`), `rich_text_preformatted` (code block), `rich_text_quote` (blockquote). Slack currently documents 22 inline element types, including canvas, file, message, workflow, citation, Salesforce, tag/team, and Work Object references. Read [references/RICH-TEXT.md](references/RICH-TEXT.md) for the complete authoring/round-trip and nesting matrix. `rich_text_preformatted` accepts only text and link elements.

### table

Simple tabular data. Each row is a flat array of cell objects (NOT an object with a `cells` property). There is no `columns` property and no dedicated header-row schema; style label cells explicitly when a visual header is needed. Cell types: `raw_text`, `raw_number`, `rich_text`. Max 100 rows, 20 columns, 10,000 chars across all cells (per table AND aggregate per message).

```json
{
  "type": "table",
  "rows": [
    [{ "type": "raw_text", "text": "Service" }, { "type": "raw_text", "text": "Status" }],
    [{ "type": "raw_text", "text": "API" }, { "type": "raw_text", "text": "Healthy" }]
  ],
  "column_settings": [{ "align": "left" }, { "align": "center" }]
}
```

### data_table

Interactive table: pagination, sorting, filtering, clickable cells. Same row shape as `table`, plus a **required** `caption` string. Rows: header + 1–200 data rows (201 total); all rows need equal cell counts; header cells cannot be `rich_text`. Optional `page_size` (1–100, default 5) and `row_header_column_index` (default 0). Numeric sorting applies when a column is all `raw_number` cells. The character limit is 20,000 per data table and 20,000 aggregate across data-table cells per message.

```json
{
  "type": "data_table",
  "caption": "Service health",
  "rows": [
    [{ "type": "raw_text", "text": "Service" }, { "type": "raw_text", "text": "Latency (ms)" }],
    [{ "type": "raw_text", "text": "API" }, { "type": "raw_number", "value": 12, "text": "12" }]
  ]
}
```

### data_visualization

Native pie, bar, area, or line charts. Required: `title` (≤50 chars) and `chart`. Pie: `segments` (1–12, labels ≤20 chars, values > 0). Bar/area/line: `series` (1–12; names ≤20 chars, unique) plus `axis_config.categories` — every data point label must exactly match a category, and no series may omit a category.

```json
{
  "type": "data_visualization",
  "title": "Weekly Sales",
  "chart": {
    "type": "bar",
    "series": [
      { "name": "Online", "data": [{ "label": "Week 1", "value": 32000 }, { "label": "Week 2", "value": 41000 }] }
    ],
    "axis_config": { "categories": ["Week 1", "Week 2"], "y_label": "USD" }
  }
}
```

### markdown

Standard Markdown rendering for AI app output. Messages only.

```json
{ "type": "markdown", "text": "**Bold**, *italic*, [link](https://example.com)\n\n## Heading\n\n- List item" }
```

Supports bold, italic, strikethrough, links, headers (all levels render the same size), lists, code (inline and fenced with syntax highlighting), block quotes, dividers, tables, task lists, and escaping. Images render as hyperlink text. Cumulative 12,000-char limit across all markdown blocks per payload. `block_id` is ignored. One markdown block may translate into multiple Slack blocks.

### context_actions

Feedback and icon buttons for message-level actions. Messages only. Max 5 elements. Compatible elements: `feedback_buttons`, `icon_button` (only icon: `trash`).

### video

Embedded video player. Requires `links.embed:write` scope and a publicly accessible URL in the app's unfurl domains.

### input

Collects user data in modals, messages, and Home tabs. Requires `label` (plain_text, 2000 chars) and one compatible element. See [references/ELEMENTS.md](references/ELEMENTS.md) for all input element types.

### plan

Container for sequential task cards, designed for AI agent output. Messages only.

```json
{
  "type": "plan",
  "title": "Thinking completed",
  "tasks": [
    { "task_id": "t1", "title": "Fetched data", "status": "complete" },
    { "task_id": "t2", "title": "Generating report", "status": "in_progress" }
  ]
}
```

Task status values: `pending`, `in_progress`, `complete`, `error`. Each task is a `task_card` block with optional `details`, `output` (rich_text), and `sources` (url elements).

### file

Remote file reference. Read-only — cannot be directly added to messages by apps.

## Streaming Agent Output

Use `chat.startStream`, `chat.appendStream`, and `chat.stopStream` for live AI responses (all require `chat:write`). Start requires `channel` and `thread_ts`—streamed messages should reply to a user request. Append requires `channel`, the streaming message `ts`, and `markdown_text` even though its reference also accepts optional `chunks`. Stop requires `channel` and `ts`. When streaming to channels, start also requires `recipient_user_id` and `recipient_team_id`.

`chunks` (accepted by all three methods) can include:
- `markdown_text` chunks — `{ "type": "markdown_text", "text": "standard Markdown" }` (the chunk field is `text`, unlike the top-level `markdown_text` argument)
- `task_update` chunks — flat `id`, `title`, `status` (`pending`/`in_progress`/`complete`/`error`), optional string `details`/`output`, and URL `sources`
- `plan_update` chunks — flat `title`
- `blocks` chunks — `blocks` array (max 50; extras are dropped with a warning)

`task_update` and `plan_update` chunk fields are limited to 256 characters.

Set `task_display_mode` on `chat.startStream`:
- `timeline` (default): tasks appear individually in sequence
- `plan`: tasks grouped in one plan; first task placement determines plan placement
- `dense`: consecutive tool calls collapse into a single summarized task card

All three method references accept `blocks` chunks inside `chunks`. Only `chat.stopStream` accepts a top-level `blocks` argument, rendered below the finalized stream. Its separate 50-block limit is distinct from a streamed blocks chunk; do not infer that start/append accept top-level blocks. Rate limits: start/stop Tier 2 (20+/min), append Tier 4 (100+/min).

Streaming messages do not unfurl links.

Slack's current Developing an agent guide has streaming examples that differ from the live method schemas (for example, append chunks without the method reference's required `markdown_text`, and alternate nested chunk shapes). Generate against each Web API method reference and SDK type, and treat the guide examples as conceptual until Slack reconciles them.

## Composition Objects

Option object (used in selects, overflow, checkboxes, radio buttons):

```json
{
  "text": { "type": "plain_text", "text": "Option 1" },
  "value": "opt_1",
  "description": { "type": "plain_text", "text": "Detailed description" }
}
```

Text max 75 chars, `value` max 150 chars, `description` max 75 chars.

Confirmation dialog (add to any interactive element via `confirm`):

```json
{
  "title": { "type": "plain_text", "text": "Are you sure?" },
  "text": { "type": "plain_text", "text": "This action cannot be undone." },
  "confirm": { "type": "plain_text", "text": "Yes, do it" },
  "deny": { "type": "plain_text", "text": "Cancel" },
  "style": "danger"
}
```

Others: conversation filter (`include`: `im`/`mpim`/`private`/`public`), dispatch action config (`on_enter_pressed`, `on_character_entered`), Slack file, Slack icon (card blocks), trigger/workflow (workflow buttons). Full property tables: [references/COMPOSITION.md](references/COMPOSITION.md).

## Limits

| Constraint | Limit |
|-----------|-------|
| Blocks per message | 50 |
| Blocks per modal/Home tab | 100 |
| Section text | 3000 chars |
| Section fields | 10 items, 2000 chars each |
| Header text | 150 chars |
| Context elements | 10 |
| Actions elements | 25 |
| Context actions elements | 5 |
| Alert text (modals only) | 200 chars |
| Card title/subtitle | 150 chars |
| Card body/subtext | 200 chars |
| Card action buttons | 3 |
| Carousel cards | 1-10 |
| Container child blocks | 10 |
| Container title/subtitle | 150 chars |
| Table rows / columns | 100 / 20 |
| Table chars (per table and per message) | 10,000 |
| Data table rows / characters | header + 200 data rows / 20,000 per table and message |
| Data viz series/segments | 1-12 (labels/names 20 chars) |
| Data points per series | 1-20 |
| Data visualization blocks per message | 2 |
| Markdown block text | 12,000 chars cumulative per payload |
| Streaming chunk fields (task/plan update) | 256 chars |
| Modal title / submit / close | 24 chars each |
| Modal views in stack | 3 |
| Modal private_metadata | 3000 chars |
| Button text | 75 chars (displays ~30) |
| Button value | 2000 chars |
| action_id / block_id | 255 chars |
| Overflow options | 5 |
| Select options | 100 |
| Option text | 75 chars |
| Placeholder text | 150 chars |
| File input max file size | 100MB per file |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Partial top-level `text` with blocks | Screen readers use it and skip interior blocks | Include a complete fallback, or omit `text` so Slack can synthesize supported blocks |
| `text` and `blocks` diverge | Notification says one thing, chat shows another | Keep semantically aligned |
| Blocks for simple replies | Visual noise for short responses | Use `text` only for simple replies |
| `alert` block in a message | Alerts are modal-only; payload rejected | Use section + emoji or card in messages |
| Huge tables in one message | Static table 10,000-char or data-table 20,000-char aggregate limit exceeded | Split across multiple messages |
| Rows as `{ "cells": [...] }` objects | Invalid — rows are flat arrays of cells | Each row = array of cell objects |
| `columns` property on table | No such property | Use flat row arrays; style a visual header row yourself |
| Chart labels not matching categories | Runtime validation failure | Every data point label must match `axis_config.categories` |
| `mrkdwn` in header text | Ignored — headers only accept `plain_text` | Use `plain_text` type |
| Standard Markdown in mrkdwn fields | `**bold**` and `[links](url)` render literally | Use `*bold*` and `<url\|text>`, or a markdown block |
| Long header text | Silently truncated at 150 chars | Keep under 150 |
| Missing `alt_text` on images | Accessibility failure, API may reject | Always include alt_text |

## Best Practices

**Use blocks when:** the response has multiple distinct sections; two-column key-value layouts improve readability; a table or chart presents data more clearly than prose; visual separation helps; code needs surrounding context; interactive elements are needed.

**Don't use blocks when:** the response is conversational ("sure, done"), under ~3 lines, or a simple answer to a direct question.

**Always:**
- Either provide a complete, semantically aligned top-level `text` fallback or omit it so Slack can synthesize supported blocks; include it when mobile notification text must be reliable
- Use mrkdwn syntax in text objects, not standard Markdown (except in `markdown` blocks)
- Escape `&`, `<`, `>` in user-generated content

## Surfaces Overview

| Surface | Max Blocks | Key Methods | Notes |
|---------|-----------|-------------|-------|
| Messages | 50 | `chat.postMessage`, `chat.update` | Primary output surface |
| Modals | 100 | `views.open`, `views.update`, `views.push` | Requires `trigger_id` (3s expiry), up to 3 stacked views |
| App Home | 100 | `views.publish` | Private per-user Home view; current agents use `agent_view` Messages |
| Canvases | N/A | `canvases.create`, `canvases.edit` | Markdown only — no Block Kit support |
| Lists | N/A | `lists.*` API methods | Task tracking and project management |

Modals collect input via `input` blocks and return `view_submission` payloads. `private_metadata` (3000 chars) persists context between views. Read [references/SURFACES.md](references/SURFACES.md) before building modal flows or App Home views — it covers the view object schema, response actions, and `view.state.values` extraction paths.

## Work Objects

Work Objects render rich entity previews when links are shared in Slack. They extend link unfurling with structured data, flexpane details, editable fields, and actions. Standard app unfurls instead send a URL-keyed `unfurls` map to `chat.unfurl`; Slack's current guide says that method does not support `rich_text` blocks.

| Type | Entity ID | Purpose |
|------|-----------|---------|
| File | `slack#/entities/file` | Documents, spreadsheets, images |
| Task | `slack#/entities/task` | Tickets, to-dos, work items |
| Incident | `slack#/entities/incident` | Service interruptions, outages |
| Content Item | `slack#/entities/content_item` | Articles, pages, wiki entries |
| Item | `slack#/entities/item` | General-purpose entity |

Work Objects use `chat.unfurl` with `metadata.entities[]`; each entity carries the shared `app_unfurl_url`, canonical `url`, stable `external_ref`, `entity_type`, and `entity_payload`. They also support flexpane details/actions/edits and bidirectional `entity_comments` with events plus `entity.presentComments`/`entity.acknowledgeCommentAction`. Read [references/WORK-OBJECTS.md](references/WORK-OBJECTS.md) before implementing—invalid metadata may fail to render the rich preview.

## Reference Documentation

| Read this | Before doing this |
|-----------|-------------------|
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Quick lookup of any block/element/limit at a glance |
| [references/BLOCKS.md](references/BLOCKS.md) | Building any block payload — all 21 blocks with full property tables |
| [references/ELEMENTS.md](references/ELEMENTS.md) | Adding buttons, selects, inputs, or pickers—current elements and compatibility |
| [references/COMPOSITION.md](references/COMPOSITION.md) | Writing text objects, options, confirm dialogs, filters, Slack icons |
| [references/RICH-TEXT.md](references/RICH-TEXT.md) | Writing rich_text blocks — nesting, inline types, styles |
| [references/SURFACES.md](references/SURFACES.md) | Building messages, modals, App Home/agent views, canvases, or interactive flows |
| [references/WORK-OBJECTS.md](references/WORK-OBJECTS.md) | Implementing link unfurls, flexpanes, editable fields |

## Sources

- [Block Kit Reference](https://docs.slack.dev/reference/block-kit) — Slack
- [Block Kit Blocks](https://docs.slack.dev/reference/block-kit/blocks) — Slack
- [Block Kit Elements](https://docs.slack.dev/reference/block-kit/block-elements) — Slack
- [Composition Objects](https://docs.slack.dev/reference/block-kit/composition-objects) — Slack
- [chat.startStream](https://docs.slack.dev/reference/methods/chat.startStream/) — Slack
- [chat.appendStream](https://docs.slack.dev/reference/methods/chat.appendStream/) — Slack
- [chat.stopStream](https://docs.slack.dev/reference/methods/chat.stopStream/) — Slack
- [Work Objects overview](https://docs.slack.dev/messaging/work-objects-overview/) — Slack
- [Implementing Work Objects](https://docs.slack.dev/messaging/work-objects-implementation/) — Slack
- [Work Object comments](https://docs.slack.dev/messaging/work-objects-comments/) — Slack
- [Surfaces](https://docs.slack.dev/surfaces) — Slack
- [Modal views](https://docs.slack.dev/reference/views/modal-views) — Slack
- [App Home](https://docs.slack.dev/surfaces/app-home) — Slack
- [Developing agents](https://docs.slack.dev/ai/developing-agents) — Slack
- [Notification changes](https://docs.slack.dev/changelog/2026/07/13/notification-changes) — Slack
