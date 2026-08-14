# Composition Objects — Complete Property Reference

> Sources:
> - [Block Kit Composition Objects](https://docs.slack.dev/reference/block-kit/composition-objects) — Slack
> - [Text object](https://docs.slack.dev/reference/block-kit/composition-objects/text-object/) — Slack

Composition objects are reusable JSON patterns used inside blocks and elements.

## Contents

- [Text Object](#text-object)
- [Option Object](#option-object)
- [Option Group Object](#option-group-object)
- [Confirmation Dialog Object](#confirmation-dialog-object)
- [Conversation Filter Object](#conversation-filter-object)
- [Dispatch Action Configuration Object](#dispatch-action-configuration-object)
- [Slack File Object](#slack-file-object)
- [Slack Icon Object](#slack-icon-object)
- [Trigger and Input Parameter Objects](#trigger-object)
- [Workflow Object](#workflow-object)

---

## Text Object

The most common composition object. Appears in nearly every block and element.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"mrkdwn"` or `"plain_text"` |
| `text` | string | Yes | Min 1 char, max 3000 chars |
| `emoji` | boolean | No | `plain_text` only. Indicates that emojis in the field should be escaped into colon emoji format |
| `verbatim` | boolean | No | `mrkdwn` only. Default `false`; `true` skips plain-text preprocessing but still processes mrkdwn and explicit manual parsing strings |

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
| Confirmation dialog (title/confirm/deny) | `plain_text` only |
| Confirmation dialog (text) | Reference field table says `plain_text`; Slack's own current example uses `mrkdwn` (see note below) |
| Option text (select/overflow) | `plain_text` only |
| Option text (checkboxes/radio) | `mrkdwn` or `plain_text` |
| Option description | `plain_text` (or `mrkdwn` for checkboxes/radio buttons) |

### Verbatim Behavior

When `verbatim: false` (default):
- URLs auto-convert to clickable links
- Channel names auto-convert to channel links
- Mentions auto-parse

When `verbatim: true`:
- mrkdwn formatting still processes
- Explicit manual parsing strings still process
- Slack does not modify otherwise plain-text content (for example, it does not auto-link a channel name)
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

Adds a confirmation step to an element that exposes a `confirm` property.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `title` | text object | Yes | `plain_text` only, max 100 chars |
| `text` | text object | Yes | Max 300 chars; see documentation inconsistency below |
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

**Current Slack-doc inconsistency:** the field table calls `text` a `plain_text` object, while Slack's official example uses `mrkdwn`. Prefer `plain_text` when formatting is unnecessary; if following the example, use `mrkdwn` only for this explanatory field, never for `title`, `confirm`, or `deny`.

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

**Known issues:** iOS shows "0 selected" instead of placeholder text when nothing is selected. iOS also has UI inconsistencies when users interact with multi-select menu items.

---

## Dispatch Action Configuration Object

Controls when supported text-like inputs (`plain_text_input`, `rich_text_input`, `number_input`, `email_text_input`, and `url_text_input`) return `block_actions` payloads during input. The composition-object page still describes plain-text input specifically, while each of the other live element pages exposes the same property.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `trigger_actions_on` | string[] | No | One or both of the values below |

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

Provide exactly one of `url` or `id`. The file must be an image, the posting user must have access to it, and Slack currently supports Slack-hosted PNG, JPG/JPEG, and GIF files. Supplying both properties rejects the payload.

```json
{ "url": "https://files.slack.com/files-pri/T0123-F0123/image.png" }
```

```json
{ "id": "F0123ABC456" }
```

**Used in:** image block (`slack_file` property), image element (`slack_file` property).

---

## Slack Icon Object

References a built-in Slack icon for use in card blocks. Renders next to the card's title/subtitle in place of a custom `icon` image (the two are mutually exclusive).

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | Always `"icon"` |
| `name` | string | Yes | One of the built-in icon names below |

**Icon names:** `archive`, `book`, `bookmark`, `bot`, `bug`, `calendar`, `call`, `caret-left`, `caret-right`, `check`, `clipboard`, `code`, `comment`, `compass`, `copy`, `cube`, `download`, `edit`, `email`, `eye-closed`, `eye-open`, `file`, `flag`, `folder`, `gear`, `globe`, `heart`, `help`, `image`, `info`, `key`, `lightbulb`, `link`, `map`, `mobile`, `new-window`, `pin`, `plus`, `refine`, `refresh`, `rocket`, `save`, `screen`, `share`, `sparkle`, `star`, `star-filled`, `tag`, `thumbs-down`, `thumbs-up`, `trash`, `upload`, `user`, `warning`.

```json
{
  "type": "card",
  "slack_icon": { "type": "icon", "name": "rocket" },
  "title": { "type": "mrkdwn", "text": "Deploy complete" }
}
```

**Used in:** card block (`slack_icon` property).

---

## Trigger Object

Contains trigger information for workflow buttons.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `url` | string | Yes | Trigger URL |
| `customizable_input_parameters` | input parameter[] | No | Names must match workflow inputs configured as customizable; values must match those inputs' declared types |

Values can be visible to end users. Never put secrets or other sensitive information in these parameters.

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

## Input Parameter Object

Supplies a customized workflow input inside `trigger.customizable_input_parameters`.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `name` | string | Yes | Must exactly match an input on the workflow behind the link trigger, and that trigger mapping must be marked customizable |
| `value` | value matching workflow input type | Yes | Must match the declared workflow input type; it may be visible client-side |

```json
{ "name": "input_parameter_a", "value": "Value for input param A" }
```

Slack's composition-object index links to a dedicated input-parameter page, but as of the documentation audit that Markdown endpoint returns 404 and the browser route falls back to the docs home page. The trigger-object reference above is therefore the authoritative field description currently available.

---

## Workflow Object

Wraps a trigger object for workflow buttons.

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `trigger` | trigger object | Yes | See trigger object above |

**Used in:** workflow_button element (`workflow` property).
