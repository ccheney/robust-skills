# Slack Rich Output Quick Reference

> Sources:
> - [Block Kit Reference](https://docs.slack.dev/reference/block-kit) — Slack
> - [Formatting Message Text](https://docs.slack.dev/messaging/formatting-message-text) — Slack

---

## mrkdwn Syntax

```
*bold*                          _italic_
~strikethrough~                 `inline code`
```code block```               > blockquote
<https://url|display text>      <@U0123ABC> (mention)
<#C0123ABC> (channel)           :emoji_name:
<!date^1234567890^{date} at {time}|fallback>
```

**NOT standard Markdown:** `**bold**`, `[text](url)`, `# heading` all render literally.

---

## Block Types

| Block | Type String | Surfaces | Key Limits |
|-------|------------|----------|-----------|
| Header | `header` | Msg, Modal, Home | 150 chars, plain_text only |
| Section | `section` | Msg, Modal, Home | 3000 chars text, 10 fields (2000 each), 1 accessory |
| Divider | `divider` | Msg, Modal, Home | No fields |
| Context | `context` | Msg, Modal, Home | 10 elements (text + image) |
| Actions | `actions` | Msg, Modal, Home | 25 elements |
| Image | `image` | Msg, Modal, Home | alt_text required, png/jpg/gif |
| Rich Text | `rich_text` | Msg, Modal, Home | Nested sub-elements |
| Table | `table` | Msg only | 100 rows, 20 cols, 1/msg. First row = header. Rows are arrays of `raw_text`/`rich_text` cells. No `columns` prop |
| Markdown | `markdown` | Msg only | 12K chars cumulative, standard MD |
| Context Actions | `context_actions` | Msg only | 5 elements |
| Input | `input` | Modal, Msg, Home | label required, many element types |
| Video | `video` | Msg, Modal, Home | links.embed:write scope |
| File | `file` | Msg only | Read-only, source: "remote" |

---

## Interactive Elements

| Element | Type String | Compatible Blocks |
|---------|------------|-------------------|
| Button | `button` | section, actions |
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
| `text` | `text`, `style: { bold, italic, strike, code, underline }` |
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

## Date Tokens

| Token | Example Output |
|-------|---------------|
| `{date_num}` | 2014-02-18 |
| `{date}` | February 18th, 2014 |
| `{date_short}` | Feb 18, 2014 |
| `{date_long}` | Tuesday, February 18th, 2014 |
| `{time}` | 6:39 AM |
| `{time_secs}` | 6:39:42 AM |
| `{ago}` | 3 minutes ago |
| `{date_pretty}` | Yesterday (or date if not recent) |
| `{date_short_pretty}` | Yesterday (short format) |
| `{date_long_pretty}` | Yesterday (long format) |

---

## Mentions

```
<@U0123ABC>                  User mention (triggers notification)
<#C0123ABC>                  Channel link
<!subteam^SAZ94GDB8>         User group mention
<!here>                      Active channel members
<!channel>                   All channel members
<!everyone>                  All non-guest workspace members
```

---

## Escaping

Only three characters: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`

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
| Table rows / cols | 100 / 20 |
| Tables per message | 1 |
| Modal title | 24 chars |
| Modal views stack | 3 |
| Button text | 75 chars |
| action_id / block_id | 255 chars |
| Select options | 100 |
| Overflow options | 5 |
| Placeholder text | 150 chars |

---

## Work Object Entity Types

| Type | Entity ID |
|------|-----------|
| File | `slack#/entities/file` |
| Task | `slack#/entities/task` |
| Incident | `slack#/entities/incident` |
| Content Item | `slack#/entities/content_item` |
| Item | `slack#/entities/item` |

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
