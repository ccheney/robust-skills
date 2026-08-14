# Slack Block Kit Quick Reference

> Sources:
> - [Block Kit Reference](https://docs.slack.dev/reference/block-kit) — Slack
> - [Markdown block](https://docs.slack.dev/reference/block-kit/blocks/markdown-block/) — Slack
> - [March 2026 Block Kit rich-text rollout](https://docs.slack.dev/changelog/2026/03/06/block-kit-rich-text/) — Slack
> - [`chat.appendStream`](https://docs.slack.dev/reference/methods/chat.appendStream/) and [Node SDK append arguments](https://docs.slack.dev/tools/node-slack-sdk/reference/web-api/interfaces/ChatAppendStreamArguments/) — Slack

---

## Block Types

| Block | Type String | Surfaces | Key Limits |
|-------|------------|----------|-----------|
| Header | `header` | Msg, Modal, Home | 150 chars, plain_text only; optional level 1-4 |
| Section | `section` | Msg, Modal, Home | 3000 chars text, 10 fields (2000 each), 1 accessory |
| Divider | `divider` | Msg, Modal, Home | No fields |
| Context | `context` | Msg, Modal, Home | 10 elements (text + image) |
| Actions | `actions` | Msg, Modal, Home | 25 elements |
| Alert | `alert` | Modal only | 200 chars. Levels: default/info/warning/error/success |
| Card | `card` | Msg, Modal, Home | Title/subtitle 150, body/subtext 200 chars, max 3 buttons |
| Carousel | `carousel` | Msg, Home | 1-10 card elements |
| Container | `container` | Msg | `title` or `rich_text_title`, max 10 child blocks, collapsible; optional non-collapsible header divider |
| Image | `image` | Msg, Modal, Home | alt_text required, png/jpg/gif |
| Rich Text | `rich_text` | Msg, Modal, Home | Nested sub-elements |
| Table | `table` | Msg, Home | 100 rows, 20 cols. 10K chars/table and per msg. No semantic header schema. Rows are flat cell arrays; no `columns` prop |
| Data Table | `data_table` | Msg, Home | `caption` required. Header + 1-200 rows, 20K chars, page_size 1-100 (default 5). Sortable/paginated |
| Data Visualization | `data_visualization` | Msg only | Title ≤50. pie/bar/area/line. 1-12 series/segments, 1-20 points, labels ≤20 |
| Markdown | `markdown` | Msg only | 12K chars cumulative, standard MD incl. tables, task lists, dividers, syntax-highlighted code; variable header sizes rolling out |
| Context Actions | `context_actions` | Msg only | 5 elements |
| Input | `input` | Modal, Msg, Home | label required, many element types |
| Video | `video` | Msg, Modal, Home | links.embed:write scope |
| Plan | `plan` | Msg only | Sequential task cards for AI agent output |
| Task Card | `task_card` | Msg only | Single task with status, details, output, sources |
| File | `file` | Retrieval only | Read-only, source: "remote"; apps cannot author it |

The current markdown-block reference says all header levels render at the same size, while Slack's March 6, 2026 changelog says variable-sized headers are rolling out. Use semantic levels and expect temporary client/workspace variation.

---

## Interactive Elements

| Element | Type String | Compatible Blocks |
|---------|------------|-------------------|
| Button | `button` | section, actions; card has a separate button-shaped actions array |
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
| Confirmation Dialog | Elements that expose a `confirm` property |
| Conversation Filter | Conversation select menus (via `filter`) |
| Dispatch Action Config | plain/rich/number/email/URL text-like inputs |
| Slack File | Image block/element (via `slack_file`) |
| Slack Icon | Card block (via `slack_icon`) |
| Trigger | Workflow button (via `workflow.trigger`) |
| Input Parameter | Workflow trigger `customizable_input_parameters` |
| Workflow | Workflow button (wraps trigger object) |

---

## Rich Text Sub-Elements

| Sub-Element | Purpose | Key Properties |
|-------------|---------|----------------|
| `rich_text_section` | Paragraph | `elements` (inline array) |
| `rich_text_list` | Bullet/ordered list | `style`, `indent`, `offset`, `border` |
| `rich_text_preformatted` | Code block | `elements`, `border` |
| `rich_text_quote` | Blockquote | `elements`, `border` |

### Inline Elements

| Type | Key Properties |
|------|----------------|
| `text` | `text`, `style: { bold, italic, strike, underline, highlight, client_highlight, unlink }` |
| `link` | `url`, `text`, `style` |
| `emoji` | `name` |
| `user` | `user_id` |
| `channel` | `channel_id` |
| `usergroup` | `usergroup_id` |
| `broadcast` | `range` (here/channel/everyone) |
| `date` | `timestamp`, `format`, `fallback` |
| `color` | `value` (hex) |

The current index also defines `attachment_mention`, `canvas`, `canvas_message_unfurl`, `canvas_user_mention`, `citation`, `file`, `list_record`, `message_mention`, `salesforce_data_field`, `tag`, `team`, `work_object_mention`, and `workflow_mention`. Sections, list-item sections, and quotes accept the broad inline set; `rich_text_preformatted` accepts only `text` and `link`. See [RICH-TEXT.md](RICH-TEXT.md) before authoring specialized/output-oriented types.

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
| Alert text | 200 chars (modals only) |
| Card title / subtitle / body / subtext | 150 / 150 / 200 / 200 chars |
| Card action buttons | 3 |
| Carousel cards | 1-10 |
| Container child blocks / title | 10 / 150 chars |
| Table rows / cols | 100 / 20 |
| Table cell chars (per table & per msg) | 10,000 |
| Data table rows / cell chars | header + 200 / 20,000 per table and per message |
| Data viz series/segments / points | 1-12 / 1-20 |
| Modal title | 24 chars |
| Modal views stack | 3 |
| Button text | 75 chars |
| action_id / block_id | 255 chars |
| Select options | 100 |
| Overflow options | 5 |
| Placeholder text | 150 chars |
| File input max size | 100MB per file |
| Rich text input lines | `min_lines`/`max_lines` 1-100; maximum defaults to 8 |
| Streaming chunk fields (task/plan update) | 256 chars |

---

## Streaming (chat.startStream / appendStream / stopStream)

| What | Detail |
|------|--------|
| Scope | `chat:write` |
| Start requires | `channel`, `thread_ts` (+ `recipient_user_id`, `recipient_team_id` for channels) |
| Append requires | `channel`, streaming message `ts`, plus at least one of `markdown_text` or `chunks` per the official Node SDK contract |
| Stop requires | `channel`, streaming message `ts` |
| Chunk types | `markdown_text` (`text` field), flat `task_update`, flat `plan_update`, `blocks` |
| `task_display_mode` | `timeline` (default), `plan`, `dense` |
| Blocks per chunk array | 50 (extras dropped with warning) |
| Top-level `blocks` | Only stopStream; rendered below final stream, separate 50-block limit |
| Rate limits | start/stop Tier 2 (20+/min), append Tier 4 (100+/min) |

The live Web API field table marks append `markdown_text` required and `chunks` optional. In contrast, the official Node SDK marks both optional but says either is required, the Python SDK accepts both as optional, and the Developing an agent guide shows chunks-only append. For SDK calls, provide at least one; raw-HTTP callers should check the current method schema before omitting `markdown_text` and include it whenever that schema still marks it required. Validate chunk shapes against the current method reference and SDK model.

---

## Surfaces

| Surface | Block Kit | Key Method |
|---------|-----------|------------|
| Messages | Yes (50 blocks) | `chat.postMessage` |
| Modals | Yes (100 blocks) | `views.open` |
| App Home | Yes (100 blocks) | `views.publish` |
| Canvases | No (markdown only) | `canvases.create` |
| Lists | No | `lists.*` |
| Agent Messages | `agent_view` (new apps) | Standard Messages tab with threads |
| Legacy Assistant | `assistant_view` (existing apps) | Chat + History; eventual deprecation |

---

## Work Object Entity Types

| Type | Entity ID |
|------|-----------|
| File | `slack#/entities/file` |
| Task | `slack#/entities/task` |
| Incident | `slack#/entities/incident` |
| Content Item | `slack#/entities/content_item` |
| Item | `slack#/entities/item` |

Unfurl entities live at `metadata.entities[]` and require per-entity `app_unfurl_url`, `url`, `external_ref`, `entity_type`, and `entity_payload`. `entity_comments` is the sibling bidirectional-comments envelope; see [WORK-OBJECTS.md](WORK-OBJECTS.md).
