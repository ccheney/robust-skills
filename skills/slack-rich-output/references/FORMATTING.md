# Formatting — mrkdwn Syntax, Dates, Mentions, and Escaping

> Sources:
> - [Formatting Message Text](https://docs.slack.dev/messaging/formatting-message-text) — Slack
> - [Block Kit Reference](https://docs.slack.dev/reference/block-kit) — Slack

---

## The Two Markup Systems

Slack has two completely separate markup systems. Never mix them.

| Feature | Slack mrkdwn | Standard Markdown (markdown block) |
|---------|-------------|-----------------------------------|
| Bold | `*text*` | `**text**` |
| Italic | `_text_` | `*text*` or `_text_` |
| Strikethrough | `~text~` | `~~text~~` |
| Link | `<url\|text>` | `[text](url)` |
| Heading | Not supported | `# Heading` |
| Inline code | `` `code` `` | `` `code` `` |
| Code block | ` ```code``` ` | ` ```code``` ` |
| Blockquote | `> text` | `> text` |
| Ordered list | `1. item` (plain text) | `1. item` (rendered) |
| Unordered list | `- item` (rich_text only) | `- item` (rendered) |

**Where each is used:**
- **mrkdwn**: `text` field, text objects with `type: "mrkdwn"`, section fields, context elements
- **Standard Markdown**: `markdown` block only (designed for AI app output)

---

## mrkdwn Text Formatting

### Basic Styles

```
*bold text*
_italic text_
~strikethrough~
`inline code`
```preformatted code block```
> blockquote (prefix each line)
```

### Links

```
<https://example.com>                            Auto-detected URL
<https://example.com|Display Text>               URL with custom text
<mailto:user@example.com|Email Link>             Email link
```

URLs posted in text are auto-linked by Slack. Use `<url|text>` for custom display text.

### Emoji

Include emoji using colon syntax: `:smile:`, `:rocket:`, `:thumbsup:`. Slack converts to rendered emoji. Direct Unicode emoji also works.

### Lists

mrkdwn does not have dedicated list syntax. Use plain text formatting:

```
1. First item
2. Second item
3. Third item
```

For properly rendered bullet/ordered lists, use `rich_text` blocks with `rich_text_list` sub-elements.

---

## Mentions and References

### User Mentions

```
<@U0123ABC456>
```

Triggers a notification for the mentioned user. Auto-converts to display name.

### Channel References

```
<#C0123ABC456>
```

Auto-converts to channel name. Users without access see "private channel".

### User Group Mentions

```
<!subteam^SAZ94GDB8>
```

Notifies all members of the user group.

### Special Mentions

| Syntax | Scope | Caution |
|--------|-------|---------|
| `<!here>` | Active members in channel | Use sparingly |
| `<!channel>` | All channel members | Triggers push notifications for everyone |
| `<!everyone>` | All non-guest workspace members | Very disruptive |

### Best Practice

Always use IDs, not names. IDs are stable; names change:

```
  <@U0123ABC456>       (user ID)
  @chris                (name — may not resolve)

  <#C0123ABC456>       (channel ID)
  #general              (name — may not resolve)
```

To enable name-based parsing, set `link_names: 1` in the API call. However, this is fragile and discouraged.

---

## Date Formatting

Displays dates/times localized to the reader's timezone.

### Syntax

```
<!date^{unix_timestamp}^{token_string}^{optional_link}|{fallback_text}>
```

### Tokens

| Token | Example Output |
|-------|---------------|
| `{date_num}` | 2014-02-18 |
| `{date}` | February 18th, 2014 |
| `{date_short}` | Feb 18, 2014 |
| `{date_long}` | Tuesday, February 18th, 2014 |
| `{date_pretty}` | Yesterday / February 18th, 2014 |
| `{date_short_pretty}` | Yesterday / Feb 18, 2014 |
| `{date_long_pretty}` | Yesterday / Tuesday, February 18th, 2014 |
| `{time}` | 6:39 AM (12h) or 06:39 (24h) |
| `{time_secs}` | 6:39:42 AM |
| `{ago}` | 3 minutes ago / 4 hours ago |

`_pretty` variants use relative terms ("yesterday", "today", "tomorrow") when applicable.

### Examples

```
<!date^1392734382^{date} at {time}|February 18th, 2014 at 6:39 AM PST>
<!date^1392734382^{date_short_pretty} {time}|Feb 18, 2014 6:39 AM>
<!date^1392734382^{ago}|February 18th, 2014>
```

Tokens can be mixed with literal text in the token string. The optional link makes the date clickable. Fallback text (after `|`) displays for older clients.

---

## Escaping

Only three characters require escaping in mrkdwn:

| Character | Escape Sequence |
|-----------|----------------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |

Do NOT encode other characters as HTML entities. Only these three are control characters in Slack's markup system.

When displaying user-generated content that may contain these characters, always escape them to prevent unintended formatting or link injection.

---

## Auto-Parsing Behavior

### Default Behavior (verbatim: false)

When `verbatim` is `false` (the default for mrkdwn text objects):
- URLs auto-convert to clickable links
- Channel names may auto-convert to channel links
- Mentions may auto-parse

### Disabling Auto-Parsing

**In text objects:**
```json
{ "type": "mrkdwn", "text": "Visit http://example.com", "verbatim": true }
```

**In message payloads:**
- Omit `link_names` argument (or set to `0`)
- Set `parse: "none"` to disable all auto-parsing

### Enabling Name-Based Parsing

Add `link_names: 1` to the API call to convert `@username` and `#channel` to linked mentions. This is fragile — prefer using explicit ID syntax.

---

## Disabling Formatting Entirely

| Context | Method |
|---------|--------|
| Text objects | Set `type` to `"plain_text"` |
| Top-level message `text` | Set `mrkdwn: false` |
| Attachments | Exclude field from `mrkdwn_in` array |

---

## Secondary Attachments (Legacy)

The `attachments` array adds secondary content below the main message. Supports:
- `color`: Hex color or `"good"` (green), `"warning"` (yellow), `"danger"` (red)
- `text`: Attachment body
- `fields`: Array of `{ title, value, short }` objects
- `image_url`, `thumb_url`: Images
- `footer`, `footer_icon`, `ts`: Footer metadata

Attachments may be collapsed or truncated by clients. **Prefer Block Kit blocks** over attachments for new development.
