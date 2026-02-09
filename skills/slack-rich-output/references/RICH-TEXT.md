# Rich Text Block — Deep Dive

> Sources:
> - [Rich Text Block](https://docs.slack.dev/reference/block-kit/blocks/rich-text-block) — Slack

The rich text block is Slack's most expressive formatting system. It's the format Slack's WYSIWYG composer produces and supports deep nesting, styled text, lists, code blocks, quotes, and specialized inline elements.

**Surfaces:** Messages, Modals, Home tabs

---

## Structure

```
rich_text
└── elements[] (sub-elements)
    ├── rich_text_section → elements[] (inline elements)
    ├── rich_text_list → elements[] (rich_text_section items)
    ├── rich_text_preformatted → elements[] (inline elements)
    └── rich_text_quote → elements[] (inline elements)
```

---

## Sub-Element Types

### rich_text_section

Container for a paragraph of inline elements.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"rich_text_section"` |
| `elements` | inline element[] | Yes |

```json
{
  "type": "rich_text_section",
  "elements": [
    { "type": "text", "text": "Hello ", "style": { "bold": true } },
    { "type": "user", "user_id": "U0123ABC" },
    { "type": "text", "text": ", welcome!" }
  ]
}
```

### rich_text_list

Ordered or unordered list. Each item is a `rich_text_section`.

| Property | Type | Required | Details |
|----------|------|----------|---------|
| `type` | string | Yes | `"rich_text_list"` |
| `style` | string | Yes | `"bullet"` or `"ordered"` |
| `elements` | rich_text_section[] | Yes | One section per list item |
| `indent` | integer | No | 0-based nesting level (pixels) |
| `offset` | integer | No | Starting number for ordered lists |
| `border` | integer | No | Border thickness in pixels |

```json
{
  "type": "rich_text_list",
  "style": "ordered",
  "offset": 1,
  "elements": [
    {
      "type": "rich_text_section",
      "elements": [{ "type": "text", "text": "First item" }]
    },
    {
      "type": "rich_text_section",
      "elements": [{ "type": "text", "text": "Second item" }]
    }
  ]
}
```

**Nested lists** use multiple `rich_text_list` elements with increasing `indent` values:

```json
{
  "type": "rich_text",
  "elements": [
    {
      "type": "rich_text_list",
      "style": "bullet",
      "indent": 0,
      "elements": [
        { "type": "rich_text_section", "elements": [{ "type": "text", "text": "Top level" }] }
      ]
    },
    {
      "type": "rich_text_list",
      "style": "bullet",
      "indent": 1,
      "elements": [
        { "type": "rich_text_section", "elements": [{ "type": "text", "text": "Nested item" }] }
      ]
    }
  ]
}
```

### rich_text_preformatted

Code block with monospace font and grey background.

| Property | Type | Required | Details |
|----------|------|----------|---------|
| `type` | string | Yes | `"rich_text_preformatted"` |
| `elements` | inline element[] | Yes | Text content (styling ignored) |
| `border` | integer | No | Border thickness in pixels |

```json
{
  "type": "rich_text_preformatted",
  "elements": [
    { "type": "text", "text": "const x = 42;\nconsole.log(x);" }
  ]
}
```

### rich_text_quote

Indented quote block with left border.

| Property | Type | Required | Details |
|----------|------|----------|---------|
| `type` | string | Yes | `"rich_text_quote"` |
| `elements` | inline element[] | Yes | |
| `border` | integer | No | Border thickness in pixels |

```json
{
  "type": "rich_text_quote",
  "elements": [
    { "type": "text", "text": "The best way to predict the future is to invent it.", "style": { "italic": true } }
  ]
}
```

---

## Inline Element Types

These go inside `rich_text_section`, `rich_text_preformatted`, and `rich_text_quote` `elements` arrays.

### text

Basic text with optional styling.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"text"` |
| `text` | string | Yes |
| `style` | style object | No |

### link

Hyperlink with optional display text.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"link"` |
| `url` | string | Yes |
| `text` | string | No — defaults to URL |
| `unsafe` | boolean | No |
| `style` | style object | No |

### emoji

Standard or custom emoji.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"emoji"` |
| `name` | string | Yes — emoji name without colons |
| `unicode` | string | No — unicode codepoint |

### user

User mention.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"user"` |
| `user_id` | string | Yes |
| `style` | style object | No |

### channel

Channel mention.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"channel"` |
| `channel_id` | string | Yes |
| `style` | style object | No |

### usergroup

User group mention.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"usergroup"` |
| `usergroup_id` | string | Yes |
| `style` | style object | No |

### broadcast

@here, @channel, or @everyone mention.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"broadcast"` |
| `range` | string | Yes — `"here"`, `"channel"`, or `"everyone"` |
| `style` | style object | No |

### date

Localized date display.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"date"` |
| `timestamp` | integer | Yes — Unix timestamp |
| `format` | string | Yes — Token string (e.g., `"{date} at {time}"`) |
| `fallback` | string | No |
| `url` | string | No |
| `style` | style object | No |

Supports 12+ format tokens: `{date}`, `{date_num}`, `{date_short}`, `{date_long}`, `{date_pretty}`, `{date_short_pretty}`, `{date_long_pretty}`, `{time}`, `{time_secs}`, `{ago}`.

### color

Color swatch display.

| Property | Type | Required |
|----------|------|----------|
| `type` | string | Yes — `"color"` |
| `value` | string | Yes — hex color (e.g., `"#FF5733"`) |
| `style` | style object | No |

---

## Style Object

Available on most inline elements. All properties are boolean, default `false`. Not all properties are available on every element type.

| Property | Effect | Available On |
|----------|--------|-------------|
| `bold` | Bold text | All elements |
| `italic` | Italic text | All elements |
| `strike` | Strikethrough | All elements |
| `code` | Inline code (monospace) | `text`, `link` only |
| `underline` | Underlined text | All elements |
| `highlight` | Highlighted background | `user`, `usergroup`, `channel`, `color` |
| `client_highlight` | Client-managed highlight | `user`, `usergroup`, `channel`, `color` |
| `unlink` | Removes link styling | `user`, `usergroup`, `channel` |

Styles can be combined:

```json
{ "type": "text", "text": "Important note", "style": { "bold": true, "italic": true } }
```

---

## Complete Example

A rich text block with heading, paragraph, bulleted list, code block, and quote:

```json
{
  "type": "rich_text",
  "elements": [
    {
      "type": "rich_text_section",
      "elements": [
        { "type": "text", "text": "Deploy Summary", "style": { "bold": true } },
        { "type": "text", "text": "\nVersion 2.4.1 deployed to production.\n\n" }
      ]
    },
    {
      "type": "rich_text_list",
      "style": "bullet",
      "elements": [
        {
          "type": "rich_text_section",
          "elements": [
            { "type": "text", "text": "3 new features" }
          ]
        },
        {
          "type": "rich_text_section",
          "elements": [
            { "type": "text", "text": "12 bug fixes" }
          ]
        },
        {
          "type": "rich_text_section",
          "elements": [
            { "type": "text", "text": "0 breaking changes ", "style": { "bold": true } },
            { "type": "emoji", "name": "tada" }
          ]
        }
      ]
    },
    {
      "type": "rich_text_section",
      "elements": [
        { "type": "text", "text": "\nKey migration command:\n" }
      ]
    },
    {
      "type": "rich_text_preformatted",
      "elements": [
        { "type": "text", "text": "bun run db:migrate --env production" }
      ]
    },
    {
      "type": "rich_text_quote",
      "elements": [
        { "type": "text", "text": "All smoke tests passing. Monitoring dashboards look clean. — " },
        { "type": "user", "user_id": "U0123ABC" }
      ]
    }
  ]
}
```
