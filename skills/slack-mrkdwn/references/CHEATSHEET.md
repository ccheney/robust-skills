# Slack Text Formatting Quick Reference

> Authoritative sources: [Formatting message text](https://docs.slack.dev/messaging/formatting-message-text/), [Markdown block](https://docs.slack.dev/reference/block-kit/blocks/markdown-block/), and [Text object](https://docs.slack.dev/reference/block-kit/composition-objects/text-object/).

## Pick the Right Renderer

| Input surface | Renderer | Bold | Link |
|---|---|---|---|
| Message `text`; text object `type: "mrkdwn"`; enabled attachment fields | Slack mrkdwn | `*bold*` | `<url\|label>` |
| `markdown` block; chat `markdown_text`; Work Object `format: "markdown"` | Standard Markdown | `**bold**` | `[label](url)` |
| `rich_text` block | Structured JSON | Text element `style.bold` | Link element |
| `plain_text` text object | Literal text | None | None |

`*bold*` is italic on standard-Markdown surfaces. Never choose syntax without first checking the destination field.

## mrkdwn Syntax

````text
*bold*                          _italic_
~strikethrough~                 `inline code`
```code block```               >quoted line
<https://url|display text>      <mailto:user@example.com|Email>
<@U0123ABC>                    <#C0123ABC>
:emoji_name:                   \n
<!date^1234567890^{date} at {time}|fallback with timezone>
````

Not mrkdwn: `**bold**`, `[text](url)`, `# heading`, true list syntax, or language-tag syntax highlighting.

## Standard Markdown Surfaces

### `markdown` block

- 12,000 characters cumulative across all `markdown` blocks in a payload.
- A block can translate into multiple output blocks; `block_id` is ignored and not retained.
- Documents bold/italic/strike, links, ordered/unordered lists, block quotes, inline/fenced code, syntax highlighting, headings, dividers, tables, task lists, image-to-link translation, and backslash escapes.
- The block reference says all heading levels render at the same size, but Slack's March 6, 2026 changelog says variable-sized headers are rolling out. Treat heading size as rollout- and client-dependent.

### `markdown_text`

12,000-character standard-Markdown argument on:

- `chat.postMessage`, `chat.postEphemeral`, `chat.scheduleMessage`, `chat.update`
- `chat.startStream`, `chat.appendStream`, `chat.stopStream`

On the four non-streaming methods, do not combine it with `blocks` or `text` (`markdown_text_conflict`). `chat.stopStream` may include final blocks, rendered after the streamed content.

Current streaming-method Markdown chunk shape:

```json
{ "type": "markdown_text", "text": "**Result**" }
```

Streaming messages do not unfurl links.

### Work Objects

```json
{
  "type": "string",
  "value": "**Blocked** — [runbook](https://example.com)",
  "format": "markdown"
}
```

- `format: "markdown"` is for string fields/custom fields and Work Object comments.
- It cannot be combined with a string field's `icon` or `link`.
- Partial-access `custom_message` uses `message_format: "markdown"`.
- A Work Object reference inside `rich_text` uses a `work_object_mention` element, not mrkdwn.

## Mentions

```text
<@U0123ABC>                  User mention; notifies the user
<#C0123ABC>                  Conversation link
<!subteam^SAZ94GDB8>         User group mention; notifies the group
<!here>                      Active channel members
<!channel>                   All channel members
<!everyone>                  Non-guest workspace members through #general
```

Always use IDs. `link_names` currently links user groups only, not users. Use `<@USER_ID>` for users and `<#CONVERSATION_ID>` for conversations.

## Dates

```text
<!date^{unix_timestamp}^{token_string}^{optional_link}|{fallback_text}>
```

| Token | Behavior |
|---|---|
| `{date_num}` | `2014-02-18` |
| `{date}` / `{date_short}` / `{date_long}` | Long, short, or weekday date; year omitted within six months |
| `{date_pretty}` / `{date_short_pretty}` / `{date_long_pretty}` | Date plus yesterday/today/tomorrow where appropriate |
| `{time}` / `{time_secs}` | Viewer-selected 12h/24h format |
| `{ago}` | Human-readable elapsed time |

Slack uses the viewer device's timezone, not the Slack preference timezone. The fallback is required; include its timezone. The optional link must be fully qualified.

## Escaping

Only these Slack control characters use HTML entities:

```text
&  ->  &amp;
<  ->  &lt;
>  ->  &gt;
```

Escape `&` first. Do not encode the whole string. Escape untrusted text before inserting it into a mrkdwn-capable field; `verbatim: true` does not neutralize explicit `<...>` controls.

## Text Objects

```json
[
  { "type": "mrkdwn", "text": "*bold*", "verbatim": true },
  { "type": "plain_text", "text": "literal", "emoji": true }
]
```

- Generic `text`: 1–3,000 characters; containing fields can impose lower limits.
- Section `fields`: up to 10 items, 2,000 characters each.
- `verbatim: false` (default): auto-preprocesses raw URLs, conversation names, and certain mentions.
- `verbatim: true`: skips that preprocessing but still parses mrkdwn and explicit `<...>` constructs.
- `emoji` is only for `plain_text` and controls conversion into colon emoji form.

Common acceptance rules:

| Context | Types |
|---|---|
| Section text/fields; context text | `mrkdwn` or `plain_text` |
| Alert text; card/carousel text fields | `mrkdwn` or `plain_text`, with local limits |
| Checkbox/radio option text and description | `mrkdwn` or `plain_text` |
| Select/multi-select/overflow option text and description | `plain_text` only |
| Header, button, placeholder, input/view chrome | `plain_text` only |

## Top-Level Parsing

| Setting | `chat.postMessage` effect |
|---|---|
| Default | mrkdwn on; raw URLs hyperlinked |
| `parse: "none"` | mrkdwn on; raw URL hyperlinking off |
| `parse: "full"` | mrkdwn ignored |
| `mrkdwn: false` | Top-level `text` does not use mrkdwn |
| `link_names: true` | Links user groups, not users |

Keep top-level `text` under 4,000 characters for best results; Slack truncates over 40,000.

## Accessibility and Notifications

For a message with blocks, either:

1. put all necessary content in top-level `text`, or
2. omit top-level `text` and let Slack attempt to synthesize it from supported blocks.

Screen readers default to top-level `text`. Desktop notifications (since July 13, 2026) extract supported block text first and fall back to `message.text`; mobile notifications exclusively use `message.text`.

## Links and Unfurls

```text
https://example.com
<https://example.com>
<https://example.com|Display Text>
<mailto:user@example.com|Email>
```

- Spaces break URLs.
- Set both `unfurl_links: false` and `unfurl_media: false` to suppress previews.
- For LLM-generated URLs, default both flags to `false`; Slack warns that the preview crawl can complete prompt-injection data exfiltration. If previews are required, allow-list trusted domains.
- `<http://example.com|example.com>` is not unfurled because its label is a complete substring of the URL without the protocol.
- Composer unfurl preview elements with `type: "mrkdwn"` and unfurl Block Kit text objects use mrkdwn; Work Object metadata fields use standard Markdown instead.
- `chat.unfurl` does not currently support rich-text blocks and may return `invalid_blocks` for a Block Kit payload containing a rich-text section element.

## Rich Text

`rich_text` is structured, not a syntax string. Use `rich_text_section`, `rich_text_list`, `rich_text_quote`, or `rich_text_preformatted` and explicit elements/styles. It is Slack's user-composer and `rich_text_input` representation, and is preferred for user-defined formatted content.

## Legacy Attachments

Prefer Block Kit. For existing attachments:

```json
{
  "fallback": "Deployment completed",
  "text": "Deployment *completed*",
  "mrkdwn_in": ["text"]
}
```

Documented mrkdwn-capable legacy content: `text`, `pretext`, and field-object values through `fields`. Field titles and `fallback` are plain text. Without attachment blocks, one of `fallback` or `text` is required. Maximum 20 attachments per message.
