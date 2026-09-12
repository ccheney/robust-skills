# Slack mrkdwn Syntax

## Contents

- mrkdwn Syntax
- Mentions and References
- Date Formatting
- Escaping

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

## Sources

- https://docs.slack.dev/messaging/formatting-message-text/
