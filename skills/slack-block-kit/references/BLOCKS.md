# Block Types — Complete Property Reference

> Sources:
> - [Block Kit Blocks](https://docs.slack.dev/reference/block-kit/blocks) — Slack
> - [Block Kit Reference](https://docs.slack.dev/reference/block-kit) — Slack

All 21 block types with full property tables, constraints, and surface compatibility.

## Table of Contents

| # | Block | Type string |
|---|-------|-------------|
| 1 | [Header](#1-header-block) | `header` |
| 2 | [Section](#2-section-block) | `section` |
| 3 | [Divider](#3-divider-block) | `divider` |
| 4 | [Context](#4-context-block) | `context` |
| 5 | [Actions](#5-actions-block) | `actions` |
| 6 | [Alert](#6-alert-block) | `alert` |
| 7 | [Card](#7-card-block) | `card` |
| 8 | [Carousel](#8-carousel-block) | `carousel` |
| 9 | [Container](#9-container-block) | `container` |
| 10 | [Image](#10-image-block) | `image` |
| 11 | [Rich Text](#11-rich-text-block) | `rich_text` |
| 12 | [Table](#12-table-block) | `table` |
| 13 | [Data Table](#13-data-table-block) | `data_table` |
| 14 | [Data Visualization](#14-data-visualization-block) | `data_visualization` |
| 15 | [Markdown](#15-markdown-block) | `markdown` |
| 16 | [Context Actions](#16-context-actions-block) | `context_actions` |
| 17 | [Input](#17-input-block) | `input` |
| 18 | [Video](#18-video-block) | `video` |
| 19 | [File](#19-file-block) | `file` |
| 20 | [Plan](#20-plan-block) | `plan` |
| 21 | [Task Card](#21-task-card-block) | `task_card` |

---

## Current surface compatibility

This matrix follows Slack's live block index. Do not infer compatibility from an example rendered on a different surface.

| Block | Messages | Modals | Home tabs |
|---|:---:|:---:|:---:|
| actions, context, divider, header, image, input, rich_text, section, video | Yes | Yes | Yes |
| alert | No | Yes | No |
| card | Yes | Yes | Yes |
| carousel | Yes | No | Yes |
| container | Yes | No | No |
| context_actions | Yes | No | No |
| data_table | Yes | No | Yes |
| data_visualization | Yes | No | No |
| file | Retrieval only | No | No |
| markdown | Yes | No | No |
| plan, task_card | Yes | No | No |
| table | Yes | No | Yes |

The `file` block is returned when retrieving messages with remote files; apps cannot add it directly to a surface.

For every block type, keep `block_id` at 255 characters or fewer, make it unique within the payload, and use a new value for each updated iteration of a message or view. Slack generates one when it is omitted.

---

## 1. Header Block

Large, bold text for section titles.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"header"` |
| `text` | text object | Yes | `plain_text` only, max 150 chars |
| `block_id` | string | No | Max 255 chars, unique per message |
| `level` | integer | No | Heading level 1-4 (H1-H4) |

**Surfaces:** Messages, Modals, Home tabs

```json
{
  "type": "header",
  "text": { "type": "plain_text", "text": "Section Title", "emoji": true }
}
```

---

## 2. Section Block

Primary content block with text, fields, and accessory.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"section"` |
| `text` | text object | Preferred | Min 1, max 3000 chars. Not required if `fields` provided |
| `fields` | text object[] | No | Max 10 items, each max 2000 chars. Can replace or supplement `text` |
| `accessory` | element | No | One compatible element |
| `expand` | boolean | No | Forces full display without "see more" — useful for AI assistant apps posting long messages |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

**Compatible accessories:** button, overflow, datepicker, timepicker, select menus, multi-select menus, checkboxes, radio_buttons, image, workflow_button.

```json
{
  "type": "section",
  "text": { "type": "mrkdwn", "text": "*Status:* Active" },
  "accessory": {
    "type": "button",
    "text": { "type": "plain_text", "text": "View" },
    "action_id": "view_btn",
    "value": "view"
  }
}
```

**Fields layout** renders as two columns:

```json
{
  "type": "section",
  "fields": [
    { "type": "mrkdwn", "text": "*Status:*\nActive" },
    { "type": "mrkdwn", "text": "*Owner:*\nChris" }
  ]
}
```

---

## 3. Divider Block

Horizontal rule separator.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"divider"` |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

```json
{ "type": "divider" }
```

---

## 4. Context Block

Small, muted metadata.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"context"` |
| `elements` | (text object \| image element)[] | Yes | Max 10 elements |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

```json
{
  "type": "context",
  "elements": [
    { "type": "image", "image_url": "https://example.com/pin.png", "alt_text": "pin" },
    { "type": "mrkdwn", "text": "Location: *Dogpatch*" }
  ]
}
```

---

## 5. Actions Block

Container for interactive elements.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"actions"` |
| `elements` | element[] | Yes | Max 25 elements |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

**Compatible elements:** button, select menus, multi-select menus, overflow, datepicker, datetimepicker, timepicker, checkboxes, radio_buttons, workflow_button.

```json
{
  "type": "actions",
  "elements": [
    {
      "type": "datepicker",
      "action_id": "date_pick",
      "initial_date": "2026-02-09",
      "placeholder": { "type": "plain_text", "text": "Select date" }
    },
    {
      "type": "button",
      "text": { "type": "plain_text", "text": "Submit" },
      "style": "primary",
      "action_id": "submit_btn"
    }
  ]
}
```

---

## 6. Alert Block

Callout for status, risk, confirmation, or urgency. **Currently only supported in modals** — do not put alert blocks in messages or Home tabs.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"alert"` |
| `text` | text object | Yes | `plain_text` or `mrkdwn`, max 200 chars |
| `level` | string | No | `"default"`, `"info"`, `"warning"`, `"error"`, or `"success"`; defaults to `"default"` |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Modals only

```json
{
  "type": "alert",
  "text": {
    "type": "mrkdwn",
    "text": "*Dependency conflict detected* before deploy."
  },
  "level": "warning"
}
```

---

## 7. Card Block

Compact, scannable preview for entities, records, summaries, or agent results.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"card"` |
| `icon` | image element | No | Small image next to title/subtitle. URL max 3000 chars, alt_text max 2000 |
| `slack_icon` | Slack icon object | No | Built-in icon next to title/subtitle. Mutually exclusive with `icon` |
| `hero_image` | image element | No | Top image. URL max 3000 chars |
| `title` | text object | No | `plain_text` or `mrkdwn`, max 150 chars |
| `subtitle` | text object | No | `plain_text` or `mrkdwn`, max 150 chars |
| `body` | text object | No | `plain_text` or `mrkdwn`, max 200 chars |
| `subtext` | text object | No | Rendered below body. `plain_text` or `mrkdwn`, max 200 chars |
| `actions` | button[] | No | Max 3 buttons. `danger` buttons left-align; `primary`/unstyled right-align (`primary` furthest right) |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

At least one of `hero_image`, `title`, `actions`, or `body` is required. There is currently no size attribute. For the Slack icon object (`{ "type": "icon", "name": "rocket" }`), see [COMPOSITION.md](COMPOSITION.md#slack-icon-object).

```json
{
  "type": "card",
  "icon": {
    "type": "image",
    "image_url": "https://example.com/icon.png",
    "alt_text": "Icon"
  },
  "title": {
    "type": "mrkdwn",
    "text": "Daily Standup Reminder"
  },
  "subtitle": {
    "type": "mrkdwn",
    "text": "Runs every weekday at *9:00 AM*"
  },
  "body": {
    "type": "mrkdwn",
    "text": "Last run: Today at 9:00 AM. Status: Success"
  },
  "actions": [
    {
      "type": "button",
      "text": { "type": "plain_text", "text": "View Logs" },
      "action_id": "view_logs"
    }
  ]
}
```

---

## 8. Carousel Block

Horizontal group of cards for options, recommendations, search results, or next steps.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"carousel"` |
| `elements` | card[] | Yes | Minimum 1 card, maximum 10 cards |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Home tabs

```json
{
  "type": "carousel",
  "elements": [
    { "type": "card", "title": { "type": "mrkdwn", "text": "Option A" } },
    { "type": "card", "title": { "type": "mrkdwn", "text": "Option B" } }
  ]
}
```

---

## 9. Container Block

Groups related blocks under a title, optionally collapsible. Useful for record previews, bulk-update summaries, and grouped content.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"container"` |
| `title` | text object | Conditional | `plain_text`, max 150 chars. One of `title` or `rich_text_title` is required |
| `rich_text_title` | rich_text object | Conditional | Rich-text title; takes precedence when both title fields are present |
| `child_blocks` | block[] | Yes | Max 10 blocks from the supported list below |
| `subtitle` | text object | No | `plain_text` or `mrkdwn`, max 150 chars |
| `icon` | image element | No | Small image next to title/subtitle. URL max 3000 chars, alt_text max 2000 |
| `width` | string | No | `"narrow"`, `"standard"` (default), `"wide"`, or `"full"` |
| `is_collapsible` | boolean | No | Default `false`. When `true`, the block collapses to show only the title |
| `default_collapsed` | boolean | No | Default `false`. Only applies when `is_collapsible` is `true` |
| `has_header_divider` | boolean | No | Visible divider below header; only applies when not collapsible. Default `false` |
| `block_id` | string | No | Max 255 chars |

**Supported child blocks:** actions, context, divider, file, header, image, input, rich_text, section, table, video. Containers cannot nest containers, cards, or AI blocks (plan, task_card).

```json
{
  "type": "container",
  "title": { "type": "plain_text", "text": "Bulk update: 2 records selected" },
  "subtitle": { "type": "plain_text", "text": "Review changes before confirming" },
  "is_collapsible": true,
  "child_blocks": [
    { "type": "section", "text": { "type": "mrkdwn", "text": "*DCW-1024*\nStatus: Open → Closed" } },
    { "type": "divider" },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": { "type": "plain_text", "text": "Confirm All" },
          "style": "primary",
          "action_id": "bulk_confirm"
        }
      ]
    }
  ]
}
```

---

## 10. Image Block

Standalone image.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"image"` |
| `alt_text` | string | Yes | Max 2000 chars |
| `image_url` | string | No | Max 3000 chars, publicly hosted. Must provide either `image_url` or `slack_file` |
| `slack_file` | object | No | `{ url }` or `{ id }`. Must provide either `image_url` or `slack_file` |
| `title` | text object | No | `plain_text` only, max 2000 chars |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

**Formats:** png, jpg, jpeg, gif

```json
{
  "type": "image",
  "image_url": "https://example.com/chart.png",
  "alt_text": "Sales chart Q4 2025",
  "title": { "type": "plain_text", "text": "Q4 Sales" }
}
```

Using Slack file:

```json
{
  "type": "image",
  "slack_file": { "id": "F0123ABC" },
  "alt_text": "Uploaded screenshot"
}
```

---

## 11. Rich Text Block

Formatted text with nested structure. See [RICH-TEXT.md](RICH-TEXT.md) for deep dive.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"rich_text"` |
| `elements` | sub-element[] | Yes | Array of section/list/preformatted/quote |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

---

## 12. Table Block

Basic static tabular data display. For pagination, sorting, filtering, and clickable cells, use the [data table block](#13-data-table-block) instead.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"table"` |
| `rows` | cell[][] | Yes | Max 100 rows. Each row is an array of max 20 cell objects |
| `column_settings` | setting[] | No | Max 20 items, with `align` and `is_wrapped`. Use `null` to skip a column; columns beyond the array get defaults |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Home tabs. For messages, publish as a top-level table in `blocks` or `attachments`.

**There is no `columns` property.** A static table does not have a dedicated header-row schema; style label cells explicitly when you want a visual header. (The first row is a semantic header only for `data_table`.)

**Row structure:** Each row is a flat array of cell objects — NOT an object with a `cells` property.

**Cell types:** `{ "type": "raw_text", "text": "..." }` for plain text, `{ "type": "raw_number", "value": 42, "text": "42" }` for numeric values, or `{ "type": "rich_text", "elements": [...] }` for formatted content (links, mentions, emoji, bold).

**Column settings:** `align` (`left`/`center`/`right`, default `left`), `is_wrapped` (boolean, default `false`).

**Character limits:** A single table's character count across all cells cannot exceed 10,000 characters, and the aggregate character count across all table cells in a single message also cannot exceed 10,000. Break large tables into separate messages.

```json
{
  "type": "table",
  "rows": [
    [
      { "type": "raw_text", "text": "Service" },
      { "type": "raw_text", "text": "Status" },
      { "type": "raw_text", "text": "Latency" }
    ],
    [
      { "type": "raw_text", "text": "API" },
      { "type": "raw_text", "text": "Healthy" },
      { "type": "raw_text", "text": "12ms" }
    ],
    [
      { "type": "raw_text", "text": "Worker" },
      { "type": "raw_text", "text": "Degraded" },
      { "type": "raw_text", "text": "340ms" }
    ]
  ],
  "column_settings": [
    { "align": "left" },
    { "align": "center" },
    { "align": "right", "is_wrapped": true }
  ]
}
```

---

## 13. Data Table Block

Rich table with pagination, sorting, filtering, and interactivity (clickable links in cells, Work Object flexpanes).

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"data_table"` |
| `rows` | cell[][] | Yes | Min 2 rows (header + 1 data row), max 201 rows (header + 200). All rows must have the same number of cells. 1–20 columns |
| `caption` | string | Yes | Table caption (used as the HTML caption element) |
| `page_size` | integer | No | Rows per page, 1–100. Defaults to 5 |
| `row_header_column_index` | integer | No | 0-based index of the column that uniquely identifies each row (used by screen readers). Defaults to 0 |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Home tabs

**Cell types:** `raw_text`, `raw_number` (`{ "type": "raw_number", "value": 42, "text": "42" }`), `rich_text`. Header row cells cannot be `rich_text`.

**Sorting:** Alphabetical by default; numeric when every cell in a column is `raw_number`.

**Character limits:** 20,000 chars per data table and 20,000 aggregate across all data-table cells per message. This is intentionally double the static table limit.

```json
{
  "type": "data_table",
  "caption": "Department badge levels",
  "rows": [
    [
      { "type": "raw_text", "text": "Name" },
      { "type": "raw_text", "text": "Department" },
      { "type": "raw_text", "text": "Badge" }
    ],
    [
      { "type": "raw_text", "text": "Data Refinement" },
      { "type": "raw_text", "text": "MDR" },
      {
        "type": "rich_text",
        "elements": [
          {
            "type": "rich_text_section",
            "elements": [{ "type": "text", "text": "Blue", "style": { "bold": true } }]
          }
        ]
      }
    ]
  ]
}
```

---

## 14. Data Visualization Block

Renders pie, bar, area, or line charts natively in Slack.

Maximum 2 data visualization blocks per message.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"data_visualization"` |
| `title` | string | Yes | Label above the chart, max 50 chars |
| `chart` | object | Yes | Chart payload — `type` must be `"pie"`, `"bar"`, `"area"`, or `"line"` |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages

**Pie charts** require `segments` (1–12): each `{ "label": "...", "value": n }` with label ≤20 chars and value > 0. Rendered percentage = value / sum of all segment values.

**Bar, area, and line charts** require:
- `series` (1–12 data series): each `{ "name": "...", "data": [...] }`. Name ≤20 chars, unique within the chart. `data` is 1–20 points of `{ "label": "...", "value": n }` (label ≤20 chars; negative values permitted). Area series layer in array order (first at back); bar series group by label.
- `axis_config`: `{ "categories": [...], "x_label": "...", "y_label": "..." }`. `categories` (required) defines valid x-axis labels and their left-to-right order; labels ≤20 chars. `x_label`/`y_label` optional, ≤50 chars.

**Runtime validation rules:**
- Every `data_point.label` in every series must match a value in `axis_config.categories`
- Series cannot omit data points — exactly one entry per category
- Series names must be unique within a chart

```json
{
  "type": "data_visualization",
  "title": "Daily Active Users",
  "chart": {
    "type": "line",
    "series": [
      {
        "name": "Free Tier",
        "data": [
          { "label": "Mon", "value": 12000 },
          { "label": "Tue", "value": 13500 },
          { "label": "Wed", "value": 15200 }
        ]
      }
    ],
    "axis_config": {
      "categories": ["Mon", "Tue", "Wed"],
      "x_label": "Day",
      "y_label": "Users"
    }
  }
}
```

Pie example:

```json
{
  "type": "data_visualization",
  "title": "Ticket Sources",
  "chart": {
    "type": "pie",
    "segments": [
      { "label": "Email", "value": 45 },
      { "label": "Chat", "value": 28 },
      { "label": "Phone", "value": 18 }
    ]
  }
}
```

---

## 15. Markdown Block

Standard Markdown rendering, designed for AI app output.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"markdown"` |
| `text` | string | Yes | Standard Markdown, 12,000 chars cumulative across all markdown blocks per payload |
| `block_id` | string | No | Ignored and not retained |

**Surfaces:** Messages only

**Supports:** bold, italic, strikethrough, links, headers (all header levels render at the same size), ordered/unordered lists, inline code, code blocks with optional syntax highlighting, block quotes, horizontal rules/dividers, tables, task lists, images (rendered as hyperlink text), and character escaping.

**Note:** A single markdown block may translate into multiple Slack blocks after rendering.

**Escaping:** Use backslash to render special characters literally. Supported: `\`, `` ` ``, `*`, `_`, `{`, `}`, `[`, `]`, `(`, `)`, `#`, `+`, `-`, `.`, `!`, `&`.

```json
{ "type": "markdown", "text": "## Status Report\n\n**API** is healthy.\n\n- Latency: 12ms\n- Error rate: 0.01%" }
```

---

## 16. Context Actions Block

Message-level feedback and action buttons.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"context_actions"` |
| `elements` | element[] | Yes | Max 5 elements |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages only

**Compatible elements:** `feedback_buttons`, `icon_button`

```json
{
  "type": "context_actions",
  "elements": [
    {
      "type": "feedback_buttons",
      "action_id": "feedback_1",
      "positive_button": {
        "text": { "type": "plain_text", "text": "Helpful" },
        "value": "positive"
      },
      "negative_button": {
        "text": { "type": "plain_text", "text": "Not helpful" },
        "value": "negative"
      }
    },
    {
      "type": "icon_button",
      "icon": "trash",
      "text": { "type": "plain_text", "text": "Delete" },
      "action_id": "delete_msg",
      "value": "delete"
    }
  ]
}
```

---

## 17. Input Block

Collects user data via form elements.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"input"` |
| `label` | text object | Yes | `plain_text` only, max 2000 chars |
| `element` | element | Yes | One compatible element |
| `block_id` | string | No | Max 255 chars |
| `dispatch_action` | boolean | No | Default `false`. Cannot be `true` with `file_input` |
| `hint` | text object | No | `plain_text` only, max 2000 chars |
| `optional` | boolean | No | Default `false`. Allows empty submission when `true` |

**Surfaces:** Modals, Messages, Home tabs

**Compatible elements:** plain_text_input, number_input, email_text_input, url_text_input, rich_text_input, static_select, external_select, users_select, conversations_select, channels_select, multi_static_select, multi_external_select, multi_users_select, multi_conversations_select, multi_channels_select, datepicker, datetimepicker, timepicker, checkboxes, radio_buttons, file_input.

---

## 18. Video Block

Embedded video player.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"video"` |
| `alt_text` | string | Yes | Tooltip for accessibility |
| `title` | text object | Yes | `plain_text` only, max 200 chars |
| `video_url` | string | Yes | HTTPS, must be in app's unfurl domains |
| `thumbnail_url` | string | Yes | Thumbnail image URL |
| `title_url` | string | Preferred | Non-embeddable URL for the video, HTTPS |
| `description` | text object | Preferred | `plain_text` only, max 200 chars |
| `author_name` | string | No | Max 50 chars |
| `provider_name` | string | No | Originating domain (e.g., "YouTube") |
| `provider_icon_url` | string | No | Provider icon |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

**Requirements:** `links.embed:write` scope, iFrame-embeddable, publicly accessible, cannot point to Slack domains.

---

## 19. File Block

Remote file reference. Read-only — appears when retrieving messages containing remote files.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"file"` |
| `external_id` | string | Yes | External unique ID |
| `source` | string | Yes | Must be `"remote"` |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages only

Cannot be directly added to messages by apps. Shows up when retrieving messages with remote files.

```json
{ "type": "file", "external_id": "ABCD1", "source": "remote" }
```

---

## 20. Plan Block

Container for displaying sequential tasks or workflow steps, designed for AI agent output.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"plan"` |
| `title` | string | Yes | Plan title in plain text. Slack's field table calls it an object, but the official example passes a plain string — follow the example |
| `tasks` | task_card[] | No | Array of task card blocks |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages

```json
{
  "type": "plan",
  "title": "Thinking completed",
  "tasks": [
    {
      "task_id": "call_001",
      "title": "Fetched user profile",
      "status": "complete"
    },
    {
      "task_id": "call_002",
      "title": "Generating report",
      "status": "in_progress",
      "details": {
        "type": "rich_text",
        "elements": [{ "type": "rich_text_section", "elements": [{ "type": "text", "text": "Processing data..." }] }]
      }
    }
  ]
}
```

---

## 21. Task Card Block

Displays a single task with title, status, optional details/output, and source URLs. Used standalone or inside a `plan` block.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"task_card"` |
| `task_id` | string | Yes | Unique task identifier |
| `title` | string | Yes | Task title, plain text |
| `status` | string | No | `"pending"`, `"in_progress"`, `"complete"`, or `"error"` |
| `details` | rich_text object | No | Task details (single rich_text entity) |
| `output` | rich_text object | No | Task output/results (single rich_text entity) |
| `sources` | url element[] | No | Array of `url` source elements (references used to generate response) |
| `block_id` | string | No | Max 255 chars, use unique per message/iteration |

**Surfaces:** Messages

```json
{
  "type": "task_card",
  "task_id": "task_1",
  "title": "Fetching weather data",
  "status": "complete",
  "output": {
    "type": "rich_text",
    "elements": [
      { "type": "rich_text_section", "elements": [{ "type": "text", "text": "Found weather data from 2 sources" }] }
    ]
  },
  "sources": [
    { "type": "url", "url": "https://weather.com/", "text": "weather.com" },
    { "type": "url", "url": "https://accuweather.com/", "text": "accuweather.com" }
  ]
}
```
