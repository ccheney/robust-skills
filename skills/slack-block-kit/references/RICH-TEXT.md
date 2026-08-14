# Rich Text Block — Complete Reference

> Authoritative Slack sources:
> - [Rich text block](https://docs.slack.dev/reference/block-kit/blocks/rich-text-block/)
> - [Formatting with rich text](https://docs.slack.dev/block-kit/formatting-with-rich-text/)
> - [Block elements index](https://docs.slack.dev/reference/block-kit/block-elements/)
> - Individual element pages linked from the tables below

The `rich_text` block is Slack's structured representation of formatted text and the format produced by Slack's WYSIWYG composer. Prefer it when preserving user-authored Slack content or when exact structured mentions, lists, quotes, and code are needed. It is different from a `mrkdwn` text object and from the standard-Markdown `markdown` block.

**Surfaces:** messages, modals, and Home tabs.

## Contents

- [Structure and nesting](#structure-and-nesting)
- [Four structural elements](#four-structural-elements)
- [Complete inline element index](#complete-inline-element-index)
- [Core element details](#core-element-details)
- [Style objects](#style-objects)
- [Complete authoring example](#complete-authoring-example)
- [Common failures](#common-failures)

## Structure and nesting

```text
rich_text
└── elements[]
    ├── rich_text_section       → inline rich-text elements
    ├── rich_text_list          → rich_text_section[] only
    ├── rich_text_preformatted  → text or link elements only
    └── rich_text_quote         → inline rich-text elements
```

```json
{
  "type": "rich_text",
  "elements": [
    {
      "type": "rich_text_section",
      "elements": [
        { "type": "text", "text": "Hello ", "style": { "bold": true } },
        { "type": "user", "user_id": "U0123ABC" }
      ]
    }
  ]
}
```

## Four structural elements

### `rich_text_section`

Paragraph-like container. `type` and `elements` are required. It accepts every inline type in the complete inline table below.

### `rich_text_list`

| Field | Required | Notes |
|---|---:|---|
| `type: "rich_text_list"` | Yes | |
| `style` | Yes | `bullet` or `ordered` |
| `elements` | Yes | Array of `rich_text_section` objects, one per item |
| `indent` | No | Numeric sub-list indent level |
| `offset` | No | Offset added before the first ordered-list number; `offset: 4` starts at 5 |
| `border` | No | Numeric border on/off value |

Nested lists are represented as adjacent list objects with increasing `indent`, not as a list directly nested inside a section.

### `rich_text_preformatted`

| Field | Required | Notes |
|---|---:|---|
| `type: "rich_text_preformatted"` | Yes | |
| `elements` | Yes | Only `text` and `link` elements |
| `border` | No | Numeric border on/off value |
| `language` | No | Syntax-highlighting hint such as `python`, `javascript`, or `json` |

Do not put mentions, emoji, files, or the other specialized inline types inside a preformatted element.

### `rich_text_quote`

`type` and `elements` are required; optional `border` is numeric. It accepts the same inline types as `rich_text_section`.

## Complete inline element index

Slack's current reference documents 22 inline rich-text element types. All can appear in `rich_text_section`, `rich_text_quote`, and sections inside `rich_text_list`, unless the individual page says otherwise. Only `text` and `link` can appear in `rich_text_preformatted`.

| Type | Required fields | Important optional fields | Official page |
|---|---|---|---|
| `attachment_mention` | `url` | `text`, `app_id`, `entity_id`, `icon_url`, `channel_id`, `ts`, `full_size_preview_enabled`, `icon_name`, `reference_object_type`, `product_name`, `style` | [Attachment mention](https://docs.slack.dev/reference/block-kit/block-elements/attachment-mention-element/) |
| `broadcast` | `range` | `style` | [Broadcast](https://docs.slack.dev/reference/block-kit/block-elements/broadcast-element/) |
| `canvas` | `file_id` | `label`, `hide_title`, `section_id`, `style`, `text`, `url`, `is_skill_invocation` | [Canvas](https://docs.slack.dev/reference/block-kit/block-elements/canvas-element/) |
| `canvas_message_unfurl` | `root_message_ts`, `root_message_channel` | `style` | [Canvas message unfurl](https://docs.slack.dev/reference/block-kit/block-elements/canvas-message-unfurl-element/) |
| `canvas_user_mention` | `user_id` | `thread_id`, `style` | [Canvas user mention](https://docs.slack.dev/reference/block-kit/block-elements/canvas-user-mention-element/) |
| `channel` | `channel_id` | `tab_id`, `style`, `from_llm` | [Channel](https://docs.slack.dev/reference/block-kit/block-elements/channel-element/) |
| `citation` | `url`, `text`, `index`, `details` | `from_llm`, `is_slack_url` | [Citation](https://docs.slack.dev/reference/block-kit/block-elements/citation-element/) |
| `color` | `value` | `style` | [Color](https://docs.slack.dev/reference/block-kit/block-elements/color-element/) |
| `date` | `timestamp`, `format` | `timezone`, `url`, `fallback`, `style` | [Date](https://docs.slack.dev/reference/block-kit/block-elements/date-element/) |
| `emoji` | `name` | `unicode` | [Emoji](https://docs.slack.dev/reference/block-kit/block-elements/emoji-element/) |
| `file` | `file_id` | `style`, `text`, `url`, `is_skill_invocation` | [File](https://docs.slack.dev/reference/block-kit/block-elements/file-element/) |
| `link` | `url` | `text`, `unsafe`, `from_llm`, `is_slack_url`, `truncated`, `style` | [Link](https://docs.slack.dev/reference/block-kit/block-elements/link-element/) |
| `list_record` | `file_id` | `record_id`, `view_id`, `style`, `text`, `url` | [List record](https://docs.slack.dev/reference/block-kit/block-elements/list-record-element/) |
| `message_mention` | `channel_id`, `message_ts` | `author_id`, `thread_ts`, `style`, `text`, `url` | [Message mention](https://docs.slack.dev/reference/block-kit/block-elements/message-mention-element/) |
| `salesforce_data_field` | `salesforce_record_id` | `salesforce_field_label`, `salesforce_field_api_name`, `salesforce_include_field_label`, `style` | [Salesforce data field](https://docs.slack.dev/reference/block-kit/block-elements/salesforce-data-field-element/) |
| `tag` | `text` | `color`, `style` | [Tag](https://docs.slack.dev/reference/block-kit/block-elements/tag-element/) |
| `team` | `team_id` | `style` | [Team](https://docs.slack.dev/reference/block-kit/block-elements/team-element/) |
| `text` | `text` | `style` | [Text](https://docs.slack.dev/reference/block-kit/block-elements/text-element/) |
| `user` | `user_id` | `style`, `from_llm` | [User](https://docs.slack.dev/reference/block-kit/block-elements/user-element/) |
| `usergroup` | `usergroup_id` | `style` | [User group](https://docs.slack.dev/reference/block-kit/block-elements/usergroup-element/) |
| `work_object_mention` | `entity_id`, `app_id`, `text`, `url` | `icon_url`, `full_size_preview_enabled`, `product_name`, `style` | [Work Object mention](https://docs.slack.dev/reference/block-kit/block-elements/work-object-mention-element/) |
| `workflow_mention` | `workflow_id`, `function_trigger_id`, `text` | `url`, `channel_id`, `ts`, `style` | [Workflow mention](https://docs.slack.dev/reference/block-kit/block-elements/workflow-mention-element/) |

The Required/Optional labels above follow each live element page, including some counterintuitive cases (`record_id`, `author_id`, and several display labels are currently marked optional). Do not promote them to required without validating against the live reference.

### Authoring versus round-tripping

Core elements (`text`, `link`, `emoji`, `user`, `channel`, `usergroup`, `broadcast`, `date`, `color`) have clear general-purpose authoring semantics. Slack also documents specialized serializations for canvases, citations, files, list records, message and attachment mentions, Salesforce data, tags, teams, Work Objects, and workflows. Those specialized pages document their JSON shape, but do not promise that every shape is accepted in every arbitrary app-authored message.

For specialized types:

1. Preserve known fields when reading and round-tripping Slack-authored rich text.
2. Use them for app-authored output only when the relevant Slack product flow or builder accepts them.
3. Do not replace a specialized reference with lookalike plain text if fidelity matters.
4. Treat `from_llm`, `is_slack_url`, `unsafe`, `truncated`, `is_skill_invocation`, and location fields as provenance/client metadata unless your integration has a documented reason to set them.

## Core element details

### Text and links

```json
{ "type": "text", "text": "Important", "style": { "bold": true, "italic": true } }
```

```json
{ "type": "link", "url": "https://docs.slack.dev/", "text": "Slack docs" }
```

If `link.text` is omitted, Slack displays the URL.

### Mentions

```json
{ "type": "user", "user_id": "U0123ABC" }
```

```json
{ "type": "channel", "channel_id": "C0123ABC" }
```

```json
{ "type": "usergroup", "usergroup_id": "S0123ABC" }
```

```json
{ "type": "broadcast", "range": "here" }
```

`broadcast.range` is exactly `here`, `channel`, or `everyone`. `everyone` is the broadcast used in `#general`.

### Dates

```json
{
  "type": "date",
  "timestamp": 1767225600,
  "format": "{date_long_pretty} at {time}",
  "fallback": "January 1, 2026 at 12:00 AM"
}
```

Current tokens are:

- `{day_divider_pretty}`
- `{date_num}`, `{date_slash}`
- `{date_long}`, `{date_long_full}`, `{date_long_pretty}`
- `{date}`, `{date_pretty}`
- `{date_short}`, `{date_short_pretty}`
- `{time}`, `{time_secs}`, `{ago}`

`timestamp` is seconds since Unix epoch. Optional `timezone` selects the timezone, `url` links the formatted value, and `fallback` covers rendering failures.

### Tags and citations

`tag.color` can be `gray`, `brown`, `purple`, `indigo`, `blue`, `green`, `yellow`, `orange`, or `red`.

`citation.details` must describe one of five source variants:

| `citation_type` | Additional documented fields |
|---|---|
| `file` | `descriptor`, `file_id` |
| `external` | `app_name`, `app_icon_url` |
| `web` | `display_name`, `title`, `snippet` |
| `message` | `channel`, `message_ts` |
| `memory` | `memory_id` |

## Style objects

The live reference defines styles per element rather than one universal style schema. Only set fields listed for that element.

| Elements | Documented style booleans |
|---|---|
| Most mention/reference elements | `bold`, `italic`, `strike`, `highlight`, `client_highlight`, `underline`, and sometimes `unlink`; follow the individual page |
| `canvas_message_unfurl`, `color`, `date`, `file`, `text` | `bold`, `italic`, `strike`, `highlight`, `client_highlight`, `underline` |

Slack's current element pages do not list a `code` style boolean for the `text` or `link` rich-text elements. Use `rich_text_preformatted` for a code block, or validate any retrieved `code` style before emitting it.

## Complete authoring example

```json
{
  "type": "rich_text",
  "elements": [
    {
      "type": "rich_text_section",
      "elements": [
        { "type": "text", "text": "Deploy summary", "style": { "bold": true } },
        { "type": "text", "text": "\nVersion 2.4.1 deployed.\n" }
      ]
    },
    {
      "type": "rich_text_list",
      "style": "bullet",
      "elements": [
        { "type": "rich_text_section", "elements": [{ "type": "text", "text": "3 features" }] },
        { "type": "rich_text_section", "elements": [{ "type": "text", "text": "12 fixes" }] }
      ]
    },
    {
      "type": "rich_text_preformatted",
      "language": "shell",
      "elements": [{ "type": "text", "text": "npm run deploy" }]
    },
    {
      "type": "rich_text_quote",
      "elements": [
        { "type": "text", "text": "Smoke tests passed — " },
        { "type": "user", "user_id": "U0123ABC" }
      ]
    }
  ]
}
```

## Common failures

- Putting a nested `rich_text_list` inside a list item. Use adjacent lists with `indent`.
- Passing arbitrary inline elements to `rich_text_preformatted`; only `text` and `link` are documented.
- Using `mrkdwn` strings where a rich-text element object is required.
- Assuming every style flag works on every inline type.
- Emitting specialized Slack-client metadata (`from_llm`, `unsafe`, `is_skill_invocation`) without a documented product flow.
- Confusing the rich-text `file` inline element with the top-level `file` block or `file_input` element.
