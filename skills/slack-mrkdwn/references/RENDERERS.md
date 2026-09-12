# Slack Text Renderers

## Contents

- Choose the Rendering System
- Standard Markdown Surfaces
- Text Objects
- Structured Rich Text

## Choose the Rendering System

| System | Common surfaces | Example |
|---|---|---|
| Slack `mrkdwn` | Top-level message `text` (default), Block Kit text objects with `type: "mrkdwn"`, composer/classic unfurl blocks, legacy attachment fields enabled by `mrkdwn_in` | `*bold* <https://example.com\|link>` |
| Standard Markdown | `markdown` block; `markdown_text` chat method arguments; Work Object string fields/comments with `format: "markdown"`; Work Object partial-view messages with `message_format: "markdown"` | `**bold** [link](https://example.com)` |
| Structured `rich_text` | Slack's WYSIWYG/user-message representation and `rich_text_input` values | Explicit nested JSON elements and style objects |
| `plain_text` | Labels, buttons, placeholders, view titles, and any text object that must render literally | No formatting syntax |

Do not translate by punctuation alone. For example, `*bold*` in mrkdwn is italic in standard Markdown. A `rich_text` block does not parse either syntax; construct its elements explicitly.

## Standard Markdown Surfaces

### Markdown Block

```json
{
  "type": "markdown",
  "text": "## Result\n\n**Complete** — see [details](https://example.com)."
}
```

Slack's `markdown` block explicitly documents support for:

- bold, italic, nested bold/italic, and strikethrough
- ordered and unordered lists
- links, block quotes, inline code, and fenced code blocks
- language-tagged fenced code blocks with syntax highlighting
- headings, horizontal dividers, tables, and task lists
- images, translated to hyperlink text using the image alt text
- backslash escaping of documented special characters

The current block reference says all heading levels render at the same size, while Slack's March 6, 2026 changelog says variable-sized headers are being rolled out. Treat heading size as rollout- and client-dependent rather than relying on a specific visual hierarchy until the references converge. A single input block may translate into multiple output blocks. The cumulative `text` limit across all `markdown` blocks in one payload is 12,000 characters. A supplied `block_id` is ignored and not retained.

### `markdown_text` Chat Arguments

The following current Web API methods accept a standard-Markdown `markdown_text` argument with a 12,000-character limit:

| Methods | Combination rules |
|---|---|
| `chat.postMessage`, `chat.postEphemeral`, `chat.scheduleMessage`, `chat.update` | Do not combine `markdown_text` with `blocks` or `text`; Slack returns `markdown_text_conflict` |
| `chat.startStream`, `chat.appendStream`, `chat.stopStream` | Accept Markdown during a stream; `chat.stopStream` can also append final `blocks`, rendered after streamed Markdown/chunks |

Streaming methods also accept `chunks`. In the current method references, a Markdown chunk is:

```json
{ "type": "markdown_text", "text": "**Streaming** response" }
```

`chunks` can also carry task updates, plan updates, and block chunks. Consult the individual streaming method reference for the exact request fields and current limits. Link unfurling is disabled in streaming messages.

### Work Objects

Work Objects do not use mrkdwn for their metadata string formatting:

```json
{
  "type": "string",
  "value": "**Blocked** — see [runbook](https://example.com/runbook)",
  "format": "markdown"
}
```

- A Work Object `fields` or `custom_fields` property of type `string` can set `format: "markdown"`. This is incompatible with that field's `icon` or `link` properties.
- Work Object comments can provide `{ "value": "...", "format": "markdown" }`; comments may alternatively provide structured rich-text blocks.
- A custom partial-access message can set `message_format: "markdown"` for its `custom_message`.
- To reference a Work Object inside `rich_text`, use a structured `work_object_mention` element (including `entity_id`, `app_id`, `text`, and `url`), not a made-up mrkdwn token.
- Block Kit text objects embedded in composer or classic link unfurls still follow their own `mrkdwn`/`plain_text` rules.

## Text Objects

```json
[
  { "type": "mrkdwn", "text": "*bold* and _italic_", "verbatim": true },
  { "type": "plain_text", "text": "No formatting", "emoji": true }
]
```

The generic text object allows 1–3,000 characters. A containing block or element may impose a smaller limit; for example, section `fields` allow up to 10 objects of 2,000 characters each.

- `verbatim` is valid only for `mrkdwn`.
- `emoji` is valid only for `plain_text` and controls whether Slack escapes recognized emoji into colon format. It does not enable mrkdwn.

### `verbatim`

| Value | Behavior |
|---|---|
| `false` (default) | Preprocesses plain content: raw URLs become links, conversation names may be linked, and certain mentions may be parsed |
| `true` | Skips that preprocessing, while still processing mrkdwn and explicit manual constructs such as `<@U…>` or `<url\|label>` |

Use `verbatim: true` when content contains raw `@`, `#`, or URLs that should not be automatically rewritten. It is not a way to neutralize deliberate angle-bracket control syntax; escape untrusted `<` and `>`.

### Common Field Rules

This is a practical summary, not a substitute for the receiving component's reference:

| Context | Accepted text-object types |
|---|---|
| Section `text` and `fields` | `mrkdwn` or `plain_text` |
| Context text elements | `mrkdwn` or `plain_text` |
| Alert `text` (modal only, max 200) | `mrkdwn` or `plain_text` |
| Card/carousel-card `title`, `subtitle`, `body`, `subtext` | `mrkdwn` or `plain_text`; field-specific 150/200 limits apply |
| Checkbox/radio option `text` and `description` | `mrkdwn` or `plain_text` |
| Select, multi-select, and overflow option `text`/`description` | `plain_text` only |
| Header text, button text, placeholders, input labels/hints, view title/submit/close | `plain_text` only |

Slack adds Block Kit components over time. Verify the exact field reference before choosing a text type or limit.

## Structured Rich Text

`rich_text` is the structured format produced by Slack's user composer and by `rich_text_input`. Slack's reference strongly prefers it for user-defined formatted text because it is more flexible than mrkdwn.

Use explicit elements such as `rich_text_section`, `rich_text_list`, `rich_text_quote`, and `rich_text_preformatted`, with nested elements/styles for text, links, emoji, users, channels, user groups, broadcasts, dates, and Work Object mentions. Do not put a mrkdwn string into a `rich_text` block and expect it to parse.

## Sources

- https://docs.slack.dev/reference/block-kit/composition-objects/text-object/
- https://docs.slack.dev/reference/block-kit/blocks/markdown-block/
- https://docs.slack.dev/messaging/work-objects-implementation/
