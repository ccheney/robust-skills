# Composition Objects — Complete Property Reference

> Sources:
> - [Block Kit Composition Objects](https://docs.slack.dev/reference/block-kit/composition-objects) — Slack

Composition objects are reusable JSON patterns used inside blocks and elements.

---

## Text Object

The most common composition object. Appears in nearly every block and element.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"mrkdwn"` or `"plain_text"` |
| `text` | string | Yes | Min 1 char, max 3000 chars |
| `emoji` | boolean | No | `plain_text` only. Converts `:emoji:` to rendered emoji |
| `verbatim` | boolean | No | `mrkdwn` only. Default `false`. When `true`, disables auto-link conversion and mention parsing |

### Type Rules

| Context | Allowed Types |
|---------|--------------|
| Header block text | `plain_text` only |
| Section text / fields | `mrkdwn` or `plain_text` |
| Context elements | `mrkdwn` or `plain_text` |
| Button text | `plain_text` only |
| Placeholder | `plain_text` only |
| Input label | `plain_text` only |
| Input hint | `plain_text` only |
| Modal title / submit / close | `plain_text` only |
| Confirmation dialog fields | `plain_text` only |
| Option text | `plain_text` only |
| Option description | `mrkdwn` or `plain_text` |

### Verbatim Behavior

When `verbatim: false` (default):
- URLs auto-convert to clickable links
- Channel names auto-convert to channel links
- Mentions auto-parse

When `verbatim: true`:
- Markdown formatting still processes
- No auto-linking or mention parsing
- Useful for displaying raw URLs or text containing `@` or `#` that aren't mentions

```json
{ "type": "mrkdwn", "text": "Check the log at http://example.com/debug", "verbatim": true }
```

---

## Option Object

Represents a single selectable item.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `text` | text object | Yes | `plain_text` for select/overflow menus; `mrkdwn` allowed for checkboxes/radio buttons. Max 75 chars |
| `value` | string | Yes | Unique identifier, max 150 chars |
| `description` | text object | No | `plain_text` (or `mrkdwn` for checkboxes/radio buttons only), max 75 chars |
| `url` | string | No | Overflow menus only, max 3000 chars |

**Used in:** static_select, multi_static_select, external_select, multi_external_select, overflow, checkboxes, radio_buttons.

```json
{
  "text": { "type": "plain_text", "text": "High Priority" },
  "value": "high",
  "description": { "type": "mrkdwn", "text": "Critical issues only" }
}
```

---

## Option Group Object

Groups related options in select menus for visual organization.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `label` | text object | Yes | `plain_text` only, max 75 chars |
| `options` | option[] | Yes | Max 100 options per group |

**Used in:** static_select, multi_static_select, external_select, multi_external_select.

Max 100 option groups per menu.

```json
{
  "label": { "type": "plain_text", "text": "Engineering" },
  "options": [
    { "text": { "type": "plain_text", "text": "Backend" }, "value": "backend" },
    { "text": { "type": "plain_text", "text": "Frontend" }, "value": "frontend" }
  ]
}
```

---

## Confirmation Dialog Object

Adds a confirmation step to any interactive element.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `title` | text object | Yes | `plain_text` only, max 100 chars |
| `text` | text object | Yes | `plain_text` only, max 300 chars |
| `confirm` | text object | Yes | `plain_text` only, max 30 chars |
| `deny` | text object | Yes | `plain_text` only, max 30 chars |
| `style` | string | No | `"primary"` (green) or `"danger"` (red). Default `"primary"` |

Desktop: `danger` = red background, `primary` = green background.
Mobile: `danger` = red text, `primary` = blue text.

```json
{
  "title": { "type": "plain_text", "text": "Delete item?" },
  "text": { "type": "plain_text", "text": "This cannot be undone." },
  "confirm": { "type": "plain_text", "text": "Delete" },
  "deny": { "type": "plain_text", "text": "Keep" },
  "style": "danger"
}
```

**Used in:** Any element that accepts a `confirm` property (buttons, select menus, overflow, datepicker, timepicker, checkboxes, radio buttons).

---

## Conversation Filter Object

Filters the options in conversation select menus.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `include` | string[] | No | `"im"`, `"mpim"`, `"private"`, `"public"`. Array cannot be empty |
| `exclude_external_shared_channels` | boolean | No | Default `false` |
| `exclude_bot_users` | boolean | No | Default `false` |

At least one property must be supplied.

```json
{
  "include": ["public", "private"],
  "exclude_bot_users": true
}
```

**Used in:** conversations_select, multi_conversations_select (via `filter` property).

**Known issues:** iOS shows "0 selected" instead of placeholder text when nothing is selected.

---

## Dispatch Action Configuration Object

Controls when plain_text_input or rich_text_input elements return `block_actions` payloads during input.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `trigger_actions_on` | string[] | Yes | One or both of the values below |

**Trigger values:**

| Value | Behavior |
|-------|----------|
| `on_enter_pressed` | Dispatches when user presses Enter. Shows hint text prompting the user |
| `on_character_entered` | Dispatches on every character add/remove |

Requires `dispatch_action: true` on the parent input block.

```json
{
  "type": "input",
  "dispatch_action": true,
  "element": {
    "type": "plain_text_input",
    "action_id": "search_input",
    "dispatch_action_config": {
      "trigger_actions_on": ["on_character_entered"]
    }
  },
  "label": { "type": "plain_text", "text": "Search" }
}
```

---

## Slack File Object

References a Slack-hosted file for use in image blocks or image elements.

Provide either `url` or `id` (not both):

```json
{ "url": "https://files.slack.com/files-pri/T0123-F0123/image.png" }
```

```json
{ "id": "F0123ABC456" }
```

**Used in:** image block (`slack_file` property), image element (`slack_file` property).

---

## Trigger Object

Contains trigger information for workflow buttons.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `url` | string | Yes | Trigger URL |
| `customizable_input_parameters` | param[] | No | Input parameters for the workflow |

Each parameter: `{ name: string, value: string }`.

```json
{
  "trigger": {
    "url": "https://slack.com/shortcuts/Ft0123ABC/launch",
    "customizable_input_parameters": [
      { "name": "input_param_a", "value": "Value for param A" }
    ]
  }
}
```

---

## Workflow Object

Wraps a trigger object for workflow buttons.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `trigger` | trigger object | Yes | See trigger object above |

**Used in:** workflow_button element (`workflow` property).
