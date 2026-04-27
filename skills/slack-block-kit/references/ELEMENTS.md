# Block Elements — Complete Property Reference

> Sources:
> - [Block Kit Elements](https://docs.slack.dev/reference/block-kit/block-elements) — Slack

All 20 interactive element types with properties, constraints, and compatible blocks.

---

## Button

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"button"` |
| `text` | text object | Yes | `plain_text` only, max 75 chars (displays ~30) |
| `action_id` | string | No | Max 255 chars |
| `url` | string | No | Max 3000 chars, opens in browser |
| `value` | string | No | Max 2000 chars, sent in payload |
| `style` | string | No | `"primary"` (green) or `"danger"` (red) |
| `confirm` | confirm object | No | Confirmation dialog |
| `accessibility_label` | string | No | Screen reader text, max 75 chars |

**Blocks:** section (accessory), actions, card (`actions` array)

---

## Overflow Menu

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"overflow"` |
| `options` | option[] | Yes | Max 5 options |
| `action_id` | string | No | Max 255 chars |
| `confirm` | confirm object | No | Confirmation dialog |

**Blocks:** section (accessory), actions

---

## Select Menus (5 types)

All share: `action_id` (255 chars), `confirm`, `focus_on_load` (boolean), `placeholder` (plain_text, 150 chars).

### Static Select (`static_select`)
- `options`: option[] — max 100. Required unless `option_groups` provided
- `option_groups`: option group[] — max 100 groups
- `initial_option`: option object — pre-selected

### External Select (`external_select`)
- `min_query_length`: integer — chars before typeahead (default 3)
- `initial_option`: option object
- Requires Options Load URL configured in app settings

### Users Select (`users_select`)
- `initial_user`: string — user ID

### Conversations Select (`conversations_select`)
- `initial_conversation`: string — conversation ID
- `default_to_current_conversation`: boolean (default false)
- `filter`: conversation filter object
- `response_url_enabled`: boolean — for modals

### Channels Select (`channels_select`)
- `initial_channel`: string — public channel ID
- `response_url_enabled`: boolean — for modals

**Blocks:** section (accessory), actions, input

---

## Multi-Select Menus (5 types)

All share: `action_id` (255 chars), `confirm`, `focus_on_load`, `placeholder` (150 chars), `max_selected_items` (integer, min 1).

### Multi Static Select (`multi_static_select`)
- `options`: option[] — max 100. Each option max 76 chars
- `option_groups`: option group[] — max 100
- `initial_options`: option[]

### Multi External Select (`multi_external_select`)
- `min_query_length`: integer (default 3)
- `initial_options`: option[]

### Multi Users Select (`multi_users_select`)
- `initial_users`: string[] — user IDs

### Multi Conversations Select (`multi_conversations_select`)
- `initial_conversations`: string[] — conversation IDs
- `default_to_current_conversation`: boolean
- `filter`: conversation filter object

### Multi Channels Select (`multi_channels_select`)
- `initial_channels`: string[] — channel IDs

**Blocks:** section (accessory), actions, input

---

## Date Picker

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"datepicker"` |
| `action_id` | string | No | Max 255 chars |
| `initial_date` | string | No | `YYYY-MM-DD` format |
| `confirm` | confirm object | No | |
| `focus_on_load` | boolean | No | Default false |
| `placeholder` | text object | No | `plain_text`, max 150 chars |

**Blocks:** section (accessory), actions, input

---

## Time Picker

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"timepicker"` |
| `action_id` | string | No | Max 255 chars |
| `initial_time` | string | No | `HH:mm` (24-hour) |
| `timezone` | string | No | IANA timezone (e.g., `"America/Los_Angeles"`) |
| `confirm` | confirm object | No | |
| `focus_on_load` | boolean | No | Default false |
| `placeholder` | text object | No | `plain_text`, max 150 chars |

**Blocks:** section (accessory), actions, input

---

## Datetime Picker

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"datetimepicker"` |
| `action_id` | string | No | Max 255 chars |
| `initial_date_time` | integer | No | Unix timestamp |
| `confirm` | confirm object | No | |
| `focus_on_load` | boolean | No | Default false |

**Blocks:** actions, input

---

## Checkboxes

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"checkboxes"` |
| `options` | option[] | Yes | Max 10 options |
| `action_id` | string | No | Max 255 chars |
| `initial_options` | option[] | No | Must match items in `options` |
| `confirm` | confirm object | No | |
| `focus_on_load` | boolean | No | Default false |

**Blocks:** section (accessory), actions, input

---

## Radio Buttons

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"radio_buttons"` |
| `options` | option[] | Yes | Max 10 options |
| `action_id` | string | No | Max 255 chars |
| `initial_option` | option | No | Must match one item in `options` |
| `confirm` | confirm object | No | |
| `focus_on_load` | boolean | No | Default false |

**Blocks:** section (accessory), actions, input

---

## Plain Text Input

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"plain_text_input"` |
| `action_id` | string | No | Max 255 chars |
| `initial_value` | string | No | Pre-populated text |
| `multiline` | boolean | No | Default false. True = textarea |
| `min_length` | integer | No | 0-3000 |
| `max_length` | integer | No | 1-3000 |
| `dispatch_action_config` | object | No | `trigger_actions_on` array |
| `focus_on_load` | boolean | No | Default false |
| `placeholder` | text object | No | `plain_text`, max 150 chars |

**Blocks:** input

---

## Number Input

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"number_input"` |
| `is_decimal_allowed` | boolean | Yes | Allow decimal numbers |
| `action_id` | string | No | Max 255 chars |
| `initial_value` | string | No | Initial number as string |
| `min_value` | string | No | Minimum allowed |
| `max_value` | string | No | Maximum allowed |
| `dispatch_action_config` | object | No | |
| `focus_on_load` | boolean | No | Default false |
| `placeholder` | text object | No | `plain_text`, max 150 chars |

**Blocks:** input

---

## Email Input

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"email_text_input"` |
| `action_id` | string | No | Max 255 chars |
| `initial_value` | string | No | Pre-populated email |
| `dispatch_action_config` | object | No | |
| `focus_on_load` | boolean | No | Default false |
| `placeholder` | text object | No | `plain_text`, max 150 chars |

**Blocks:** input

---

## URL Input

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"url_text_input"` |
| `action_id` | string | No | Max 255 chars |
| `initial_value` | string | No | Pre-populated URL |
| `dispatch_action_config` | object | No | |
| `focus_on_load` | boolean | No | Default false |
| `placeholder` | text object | No | `plain_text`, max 150 chars |

**Blocks:** input

---

## Rich Text Input

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"rich_text_input"` |
| `action_id` | string | Yes | Max 255 chars |
| `initial_value` | rich text object | No | Pre-populated rich text |
| `dispatch_action_config` | object | No | |
| `focus_on_load` | boolean | No | Default false |
| `placeholder` | text object | No | `plain_text`, max 150 chars |

**Blocks:** input

---

## File Input

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"file_input"` |
| `action_id` | string | No | Max 255 chars |
| `filetypes` | string[] | No | Allowed extensions (e.g., `["jpg", "png"]`). Client-side only — perform server-side validation too |
| `max_files` | integer | No | Max uploadable files (1-10, default 10) |

**Blocks:** input. Note: `dispatch_action: true` is incompatible with file_input.

**Requirements:** App must have `files:read` scope. Max 10MB per file.

---

## Feedback Buttons

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"feedback_buttons"` |
| `positive_button` | button object | Yes | `text` (plain_text, 75 chars), `value` (2000 chars) |
| `negative_button` | button object | Yes | Same as positive |
| `action_id` | string | No | Max 255 chars |

Both buttons support `accessibility_label` (75 chars).

**Blocks:** context_actions

---

## Icon Button

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"icon_button"` |
| `icon` | string | Yes | Only `"trash"` available |
| `text` | text object | Yes | `plain_text` only |
| `action_id` | string | No | Max 255 chars |
| `value` | string | No | Max 2000 chars |
| `confirm` | confirm object | No | |
| `accessibility_label` | string | No | Max 75 chars |
| `visible_to_user_ids` | string[] | No | Only these users see the button |

**Blocks:** context_actions

---

## Image Element

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"image"` |
| `alt_text` | string | Yes | Max 2000 chars |
| `image_url` | string | Conditional | Max 3000 chars. Required unless `slack_file` |
| `slack_file` | object | Conditional | `{ url }` or `{ id }` |

**Blocks:** section (accessory), context (element)

---

## Workflow Button

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"workflow_button"` |
| `text` | text object | Yes | `plain_text` only, max 75 chars |
| `workflow` | workflow object | Yes | Contains trigger URL + input parameters |
| `action_id` | string | Yes | Max 255 chars, unique within block |
| `style` | string | No | `"primary"` or `"danger"` |
| `accessibility_label` | string | No | Max 75 chars |

**Blocks:** section, actions

---

## URL Source Element

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"url"` |
| `url` | string | Yes | Target URL reference |
| `text` | string | Yes | Display text shown to users |

**Blocks:** task_card (sources array only)

```json
{ "type": "url", "url": "https://docs.slack.dev/", "text": "Slack API docs" }
```
