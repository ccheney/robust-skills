# Slack Block Kit Quick Reference

> Sources:
> - [Block Kit Reference](https://docs.slack.dev/reference/block-kit) — Slack

---

## Block Types

| Block | Type String | Surfaces | Key Limits |
|-------|------------|----------|-----------|
| Header | `header` | Msg, Modal, Home | 150 chars, plain_text only |
| Section | `section` | Msg, Modal, Home | 3000 chars text, 10 fields (2000 each), 1 accessory |
| Divider | `divider` | Msg, Modal, Home | No fields |
| Context | `context` | Msg, Modal, Home | 10 elements (text + image) |
| Actions | `actions` | Msg, Modal, Home | 25 elements |
| Alert | `alert` | Msg | Status/risk callout. Levels: default/info/warning/error/success |
| Card | `card` | Msg | Compact preview. Title/subtitle 150 chars, body 200 chars |
| Carousel | `carousel` | Msg | 1-10 card elements |
| Image | `image` | Msg, Modal, Home | alt_text required, png/jpg/gif |
| Rich Text | `rich_text` | Msg, Modal, Home | Nested sub-elements |
| Table | `table` | Msg only | 100 rows, 20 cols, 1/msg. First row = header. Rows are arrays of `raw_text`/`rich_text` cells. No `columns` prop |
| Markdown | `markdown` | Msg only | 12K chars cumulative, standard MD incl. tables, task lists, dividers, syntax-highlighted code |
| Context Actions | `context_actions` | Msg only | 5 elements |
| Input | `input` | Modal, Msg, Home | label required, many element types |
| Video | `video` | Msg, Modal, Home | links.embed:write scope |
| Plan | `plan` | Msg only | Sequential task cards for AI agent output |
| Task Card | `task_card` | Msg only | Single task with status, details, output, sources |
| File | `file` | Msg only | Read-only, source: "remote" |

---

## Interactive Elements

| Element | Type String | Compatible Blocks |
|---------|------------|-------------------|
| Button | `button` | section, actions, card |
| Overflow Menu | `overflow` | section, actions |
| Select Menu | `static_select` / `external_select` / `users_select` / `conversations_select` / `channels_select` | section, actions, input |
| Multi-Select | `multi_static_select` / `multi_external_select` / `multi_users_select` / `multi_conversations_select` / `multi_channels_select` | section, actions, input |
| Date Picker | `datepicker` | section, actions, input |
| Time Picker | `timepicker` | section, actions, input |
| Datetime Picker | `datetimepicker` | actions, input |
| Checkboxes | `checkboxes` | section, actions, input |
| Radio Buttons | `radio_buttons` | section, actions, input |
| Plain Text Input | `plain_text_input` | input |
| Number Input | `number_input` | input |
| Email Input | `email_text_input` | input |
| URL Input | `url_text_input` | input |
| Rich Text Input | `rich_text_input` | input |
| File Input | `file_input` | input |
| Feedback Buttons | `feedback_buttons` | context_actions |
| Icon Button | `icon_button` | context_actions |
| Image | `image` | section (accessory), context |
| Workflow Button | `workflow_button` | section, actions |
| URL Source | `url` | task_card (sources array) |

---

## Composition Objects

| Object | Used In |
|--------|---------|
| Text (`mrkdwn` / `plain_text`) | Most blocks and elements |
| Option | Select menus, overflow, checkboxes, radio buttons |
| Option Group | Select menus (grouped options) |
| Confirmation Dialog | Any interactive element (via `confirm` property) |
| Conversation Filter | Conversation select menus (via `filter`) |
| Dispatch Action Config | plain_text_input, rich_text_input |
| Slack File | Image block/element (via `slack_file`) |
| Trigger | Workflow button (via `workflow.trigger`) |
| Workflow | Workflow button (wraps trigger object) |

---

## Rich Text Sub-Elements

| Sub-Element | Purpose | Key Properties |
|-------------|---------|----------------|
| `rich_text_section` | Paragraph | `elements` (inline array) |
| `rich_text_list` | Bullet/ordered list | `style`, `indent`, `offset`, `border` |
| `rich_text_preformatted` | Code block | `elements`, `border` |
| `rich_text_quote` | Blockquote | `elements`, `border` |

### Inline Elements (within sections)

| Type | Key Properties |
|------|----------------|
| `text` | `text`, `style: { bold, italic, strike, code, underline, highlight, client_highlight, unlink }` |
| `link` | `url`, `text`, `style` |
| `emoji` | `name` |
| `user` | `user_id` |
| `channel` | `channel_id` |
| `usergroup` | `usergroup_id` |
| `broadcast` | `range` (here/channel/everyone) |
| `date` | `timestamp`, `format`, `fallback` |
| `color` | `value` (hex) |

---

## Button Styles

| Style | Color | Usage |
|-------|-------|-------|
| (default) | Gray | Standard actions |
| `primary` | Green | Affirmation — use sparingly, one per set |
| `danger` | Red | Destructive — use with confirmation dialog |

---

## Limits at a Glance

| What | Limit |
|------|-------|
| Blocks per message | 50 |
| Blocks per modal/Home | 100 |
| Section text | 3000 chars |
| Section fields | 10 items |
| Header text | 150 chars |
| Context elements | 10 |
| Actions elements | 25 |
| Card title / subtitle / body | 150 / 150 / 200 chars |
| Carousel cards | 1-10 |
| Table rows / cols | 100 / 20 |
| Tables per message | 1 |
| Modal title | 24 chars |
| Modal views stack | 3 |
| Button text | 75 chars |
| action_id / block_id | 255 chars |
| Select options | 100 |
| Overflow options | 5 |
| Placeholder text | 150 chars |
| File input max size | 10MB per file |

---

## Surfaces

| Surface | Block Kit | Key Method |
|---------|-----------|------------|
| Messages | Yes (50 blocks) | `chat.postMessage` |
| Modals | Yes (100 blocks) | `views.open` |
| App Home | Yes (100 blocks) | `views.publish` |
| Canvases | No (markdown only) | `canvases.create` |
| Lists | No | `lists.*` |
| Split View | Config-based | Agents & AI Apps |

---

## Work Object Entity Types

| Type | Entity ID |
|------|-----------|
| File | `slack#/entities/file` |
| Task | `slack#/entities/task` |
| Incident | `slack#/entities/incident` |
| Content Item | `slack#/entities/content_item` |
| Item | `slack#/entities/item` |
