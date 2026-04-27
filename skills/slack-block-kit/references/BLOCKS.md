# Block Types — Complete Property Reference

> Sources:
> - [Block Kit Blocks](https://docs.slack.dev/reference/block-kit/blocks) — Slack
> - [Block Kit Reference](https://docs.slack.dev/reference/block-kit) — Slack
> - [Alert Block](https://docs.slack.dev/reference/block-kit/blocks/alert-block) — Slack
> - [Card Block](https://docs.slack.dev/reference/block-kit/blocks/card-block) — Slack
> - [Carousel Block](https://docs.slack.dev/reference/block-kit/blocks/carousel-block) — Slack

All 18 block types with full property tables, constraints, and surface compatibility.

---

## 1. Header Block

Large, bold text for section titles.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"header"` |
| `text` | text object | Yes | `plain_text` only, max 150 chars |
| `block_id` | string | No | Max 255 chars, unique per message |

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
| `text` | text object | Preferred | Max 3000 chars. Not required if `fields` provided |
| `fields` | text object[] | No | Max 10 items, each max 2000 chars. Can replace or supplement `text` |
| `accessory` | element | No | One compatible element |
| `expand` | boolean | No | Forces full display without "see more" |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

**Compatible accessories:** button, overflow, datepicker, timepicker, select menus, multi-select menus, checkboxes, radio_buttons, image.

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

Callout for status, risk, confirmation, or urgency.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"alert"` |
| `text` | text object | Yes | `plain_text` or `mrkdwn` |
| `level` | string | No | `"default"`, `"info"`, `"warning"`, `"error"`, or `"success"`; defaults to `"default"` |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages

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
| `icon` | image object | No | Small image next to title/subtitle |
| `hero_image` | image object | No | Top image |
| `title` | text object | No | Max 150 chars |
| `subtitle` | text object | No | Max 150 chars |
| `body` | text object | No | Max 200 chars |
| `actions` | button[] | No | Action buttons shown at bottom |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages

At least one of `hero_image`, `title`, `actions`, or `body` is required. There is currently no size attribute.

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

**Surfaces:** Messages

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

## 9. Image Block

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

## 10. Rich Text Block

Formatted text with nested structure. See [RICH-TEXT.md](RICH-TEXT.md) for deep dive.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"rich_text"` |
| `elements` | sub-element[] | Yes | Array of section/list/preformatted/quote |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages, Modals, Home tabs

---

## 11. Table Block

Tabular data display.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"table"` |
| `rows` | cell[][] | Yes | Max 100 rows. Each row is an array of cell objects (max 20 cells). First row = header |
| `column_settings` | setting[] | No | Max 20, with `align` and `is_wrapped` |
| `block_id` | string | No | Max 255 chars |

**Surfaces:** Messages only

**There is no `columns` property.** The first row in `rows` acts as the header row.

**Row structure:** Each row is a flat array of cell objects — NOT an object with a `cells` property.

**Cell types:** `{ "type": "raw_text", "text": "..." }` for plain text, or `{ "type": "rich_text", "elements": [...] }` for formatted content (links, mentions, emoji, bold).

**Column settings:** `align` (`left`/`center`/`right`, default `left`), `is_wrapped` (boolean, default `false`).

**Limit:** One table per message. Multiple tables cause `invalid_attachments` error.

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

## 12. Markdown Block

Standard Markdown rendering, designed for AI app output.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"markdown"` |
| `text` | string | Yes | Standard Markdown, 12,000 chars cumulative per payload |
| `block_id` | string | No | Ignored and not retained |

**Surfaces:** Messages only

**Supports:** bold, italic, strikethrough, links, headers (all header levels render at the same size), ordered/unordered lists, inline code, code blocks with optional syntax highlighting, block quotes, horizontal rules/dividers, tables, task lists, images (as hyperlinks), and character escaping.

**Note:** A single markdown block may translate into multiple Slack blocks after rendering.

**Escaping:** Use backslash to render special characters literally. Supported: `\`, `` ` ``, `*`, `_`, `{`, `}`, `[`, `]`, `(`, `)`, `#`, `+`, `-`, `.`, `!`, `&`.

```json
{ "type": "markdown", "text": "## Status Report\n\n**API** is healthy.\n\n- Latency: 12ms\n- Error rate: 0.01%" }
```

---

## 13. Context Actions Block

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

## 14. Input Block

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

## 15. Video Block

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

## 16. File Block

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

## 17. Plan Block

Container for displaying sequential tasks or workflow steps, designed for AI agent output.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be `"plan"` |
| `title` | string | Yes | Plan title, max 255 chars |
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

## 18. Task Card Block

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
