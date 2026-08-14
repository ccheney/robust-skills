---
name: slack-mrkdwn
description: Proactively apply when generating any Slack text content, message text fields, Block Kit text objects, standard Markdown for Slack, or Work Object text. Triggers on mrkdwn, Slack formatting, Slack markdown, Slack bold, Slack italic, Slack links, mentions, dates, escaping, text objects, verbatim, plain_text, markdown blocks, markdown_text, rich_text, Work Objects, streaming text, notification fallbacks, accessibility, auto-parsing, parse, link_names, unfurls, and mrkdwn_in. Use when formatting Slack messages, composing text objects, escaping user content, choosing between mrkdwn and standard Markdown, adding mentions or localized dates, streaming Markdown, authoring Work Object fields or comments, or debugging Slack text rendering.
---

# Slack mrkdwn

Slack's custom `mrkdwn` syntax is not standard Markdown. First identify the receiving field; the same punctuation can mean something different on another Slack surface.

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

All heading levels currently render at the same size according to the block reference. A single input block may translate into multiple output blocks. The cumulative `text` limit across all `markdown` blocks in one payload is 12,000 characters. A supplied `block_id` is ignored and not retained.

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

## mrkdwn Syntax

| Format | Syntax | Notes |
|---|---|---|
| Bold | `*bold*` | Not `**bold**` |
| Italic | `_italic_` | Not `*italic*` |
| Strikethrough | `~strikethrough~` | Not `~~strikethrough~~` |
| Inline code | `` `code` `` | Other formatting is disabled inside |
| Code block | Triple backticks around the text | No documented language-tag highlighting in mrkdwn |
| Block quote | `>quoted text` | Put `>` at the start of each quoted line |
| Link | `<https://example.com\|display text>` | Not `[text](url)` |
| Emoji | `:emoji_name:` or Unicode | Retrieved messages use colon form |
| Newline | `\n` in a string | Produces a line break |
| List-like text | `- item` / `1. item` plus newlines | mrkdwn has no list syntax; these are text conventions |

Headings are not mrkdwn syntax. Use a `header` block, a standard-Markdown `markdown` block, or structured rich text as appropriate.

For complex combinations, true lists, or user-authored formatting, prefer structured `rich_text` instead of relying on undocumented marker nesting.

## Links and Unfurls

```text
https://example.com
<https://example.com>
<https://example.com|Display text>
<mailto:user@example.com|Email user>
```

Raw URLs in mrkdwn are normally auto-transformed into links. URLs containing spaces break parsing; remove or URL-encode the spaces. When messages are retrieved, Slack returns auto-transformed URLs in angle-bracket form, sometimes with an explicit label.

Slack normally unfurls links posted by users and apps, including media links in Block Kit blocks. For publishing methods that expose these parameters:

| Parameter | Controls |
|---|---|
| `unfurl_links` | Primarily text-based content |
| `unfurl_media` | Media such as images, video, and audio |

Set both to `false` to suppress all link previews. Slack does not unfurl a manually labeled link when the label is a complete substring of the URL after removing the protocol (for example, `<http://example.com|example.com>`). Streaming messages do not unfurl links.

Custom app unfurls use the renderer of each receiving field. Composer preview `elements` can contain an object with `type: "mrkdwn"`; blocks within the unfurl use their normal text-object rules. A `chat.unfurl` `user_auth_message` supports simple Slack formatting, while `user_auth_blocks` supplies a Block Kit alternative. Work Object entity metadata remains a separate standard-Markdown case as described above.

## Mentions and References

### Manual, Stable Syntax

```text
<@U0123ABC456>          user mention
<#C0123ABC456>          conversation link
<!subteam^SAZ94GDB8>    user group mention
<!here>                 active channel members
<!channel>              all channel members
<!everyone>             everyone in #general (non-guest workspace members)
```

An app-published user mention notifies that user. An app-published user group mention notifies the group. Special mentions can notify many people and should be used sparingly.

Use IDs rather than names. User, conversation, and user-group names can change; their IDs are stable. A user who cannot access a referenced private channel sees an unclickable `private channel` label.

The current `chat.postMessage` reference says `link_names` finds and links **user groups** and no longer supports individual users. Do not depend on name auto-parsing for users, conversations, or special mentions. Use the explicit forms above.

## Date Formatting

Slack localizes app-published dates to the timezone setting of the viewer's **device**, not the timezone preference in their Slack client.

```text
<!date^{unix_timestamp}^{token_string}^{optional_link}|{fallback_text}>
```

| Token | Example behavior |
|---|---|
| `{date_num}` | `2014-02-18`, with leading zeros |
| `{date}` | `February 18th, 2014` |
| `{date_short}` | `Feb 18, 2014` |
| `{date_long}` | `Tuesday, February 18th, 2014` |
| `{date_pretty}` | `{date}`, but uses yesterday/today/tomorrow where appropriate |
| `{date_short_pretty}` | `{date_short}`, but uses yesterday/today/tomorrow |
| `{date_long_pretty}` | `{date_long}`, but uses yesterday/today/tomorrow |
| `{time}` | Viewer preference: `6:39 AM` or `18:39` |
| `{time_secs}` | Viewer preference: `6:39:42 AM` or `18:39:42` |
| `{ago}` | Human-readable elapsed time such as `3 minutes ago` |

`{date}`, `{date_short}`, and `{date_long}` omit the year when the date is less than six months in the past or future. The optional third `^`-separated value must be a fully qualified URL and makes the rendered date clickable.

Fallback text is required for older clients. Include a timezone in it because the fallback cannot be localized.

```text
<!date^1392734382^Posted {date_num} {time_secs}|Posted 2014-02-18 6:39:42 AM PST>
<!date^1392734382^{date_short}^https://example.com/|Feb 18, 2014 PST>
```

Slack returns the original `<!date...>` string when messages are retrieved.

## Escaping

Slack reserves exactly three characters for special parsing. When they are data rather than deliberate control syntax, encode them as:

| Character | Entity |
|---|---|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |

Do not HTML-encode the whole string: Slack only decodes these three documented entities. Escape `&` first, then `<` and `>`, to avoid re-encoding the ampersand you just introduced. JSON/string escaping is a separate concern.

Escape untrusted text before placing it in a mrkdwn-capable field. Otherwise it can introduce links, manual mention tokens, or date controls. Prefer `plain_text` when no formatting is needed.

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

## Top-Level Message Text and Parsing

When a message has no `blocks`, top-level `text` is the rendered body and uses mrkdwn by default. When `blocks` are present, top-level `text` is a fallback rather than visible block content.

For `chat.postMessage`:

| Setting | Current documented effect |
|---|---|
| default `parse` | mrkdwn is applied; raw URLs are hyperlinked |
| `parse: "none"` | mrkdwn is still applied; raw URL hyperlinking is disabled |
| `parse: "full"` | mrkdwn formatting is ignored |
| `mrkdwn: false` | Disables mrkdwn processing for top-level `text` |
| `link_names: true` | Finds and links user groups; no individual-user linking |

Use explicit ID-based syntax and disable unwanted preprocessing. Slack's formatting guide recommends manual parsing because names can change and automatic parsing can turn third-party input into unintended notifications.

For best results, keep top-level `text` under 4,000 characters. Slack truncates messages over 40,000 characters. Blocks have their own limits.

## Accessibility and Notification Fallbacks

Screen readers default to the message's top-level `text` and do not read interior blocks directly. With `blocks`, Slack documents two accessible approaches:

1. Include every necessary piece of content in top-level `text`.
2. Omit top-level `text` and let Slack attempt to synthesize it from supported blocks.

Prefer an explicit, complete textual summary when notification and assistive-technology parity matters.

Notification behavior changed in July 2026:

- Desktop notifications extract text from supported blocks first, then fall back to `message.text` if nothing can be extracted.
- Mobile notifications exclusively use `message.text`.

Do not assume a richly formatted block layout will produce a complete mobile notification or screen-reader experience.

## Structured Rich Text

`rich_text` is the structured format produced by Slack's user composer and by `rich_text_input`. Slack's reference strongly prefers it for user-defined formatted text because it is more flexible than mrkdwn.

Use explicit elements such as `rich_text_section`, `rich_text_list`, `rich_text_quote`, and `rich_text_preformatted`, with nested elements/styles for text, links, emoji, users, channels, user groups, broadcasts, dates, and Work Object mentions. Do not put a mrkdwn string into a `rich_text` block and expect it to parse.

## Legacy Secondary Attachments

Secondary attachments are legacy. Prefer Block Kit for new development. Legacy fields can be subject to reduced visibility or functionality.

- `mrkdwn_in` is an array naming attachment fields to format as mrkdwn. The documented mrkdwn-capable legacy content is `text`, `pretext`, and field-object `value`s via `fields`.
- A field-object `title` cannot contain markup and is escaped.
- `fallback` is a plain-text summary for clients that do not show formatted attachment content.
- Without attachment `blocks`, one of `fallback` or `text` is required.
- Attachment `text` collapses at 700+ characters or 5+ line breaks.
- Slack allows no more than 20 attachments in a message.

```json
{
  "fallback": "Deployment completed",
  "text": "Deployment *completed*",
  "mrkdwn_in": ["text"]
}
```

## Common Mistakes

| Mistake | Correction |
|---|---|
| `**bold**` or `[text](url)` in mrkdwn | Use `*bold*` and `<url\|text>` |
| `*bold*` in standard Markdown | It is italic; use `**bold**` |
| `# Heading` in mrkdwn | Use a header block or standard-Markdown surface |
| Passing syntax strings to `rich_text` | Build structured rich-text elements |
| Combining non-streaming `markdown_text` with `text`/`blocks` | Send one system; Slack returns `markdown_text_conflict` |
| Using `link_names` for user mentions | Use `<@USER_ID>`; `link_names` no longer links users |
| Treating `verbatim: true` as escaping | Explicit `<...>` controls still process; escape untrusted `&<>` |
| HTML-encoding every character | Encode only `&`, `<`, and `>` |
| Formatting Work Object fields with mrkdwn | Use standard Markdown plus `format: "markdown"` |
| Assuming block text covers every fallback | Supply deliberate top-level `text` when mobile notifications/a11y require it |

## Reference Documentation

| File | Purpose |
|---|---|
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Compact renderer choice, syntax, mentions, dates, parsing, and fallback rules |

## Official Slack Sources

- [Formatting message text](https://docs.slack.dev/messaging/formatting-message-text/)
- [Text object](https://docs.slack.dev/reference/block-kit/composition-objects/text-object/)
- [Markdown block](https://docs.slack.dev/reference/block-kit/blocks/markdown-block/)
- [Rich text block](https://docs.slack.dev/reference/block-kit/blocks/rich-text-block/)
- [Alert block](https://docs.slack.dev/reference/block-kit/blocks/alert-block/) and [Card block](https://docs.slack.dev/reference/block-kit/blocks/card-block/)
- [Option object](https://docs.slack.dev/reference/block-kit/composition-objects/option-object/)
- [`chat.postMessage`](https://docs.slack.dev/reference/methods/chat.postMessage/), [`chat.postEphemeral`](https://docs.slack.dev/reference/methods/chat.postEphemeral/), [`chat.scheduleMessage`](https://docs.slack.dev/reference/methods/chat.scheduleMessage/), and [`chat.update`](https://docs.slack.dev/reference/methods/chat.update/)
- [`chat.startStream`](https://docs.slack.dev/reference/methods/chat.startStream/), [`chat.appendStream`](https://docs.slack.dev/reference/methods/chat.appendStream/), and [`chat.stopStream`](https://docs.slack.dev/reference/methods/chat.stopStream/)
- [Developing an agent — text streaming](https://docs.slack.dev/ai/developing-agents/#streaming)
- [Implementing Work Objects](https://docs.slack.dev/messaging/work-objects-implementation/) and [Work Object comments](https://docs.slack.dev/messaging/work-objects-comments/)
- [Work object mention element](https://docs.slack.dev/reference/block-kit/block-elements/work-object-mention-element/)
- [Unfurling links in messages](https://docs.slack.dev/messaging/unfurling-links-in-messages/)
- [`chat.unfurl`](https://docs.slack.dev/reference/methods/chat.unfurl/)
- [Legacy secondary message attachments](https://docs.slack.dev/legacy/legacy-messaging/legacy-secondary-message-attachments/)
- [Desktop notification change — July 13, 2026](https://docs.slack.dev/changelog/2026/07/13/notification-changes/)
