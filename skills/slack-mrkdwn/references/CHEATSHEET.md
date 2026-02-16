# Slack mrkdwn Quick Reference

> Sources:
> - [Formatting Message Text](https://docs.slack.dev/messaging/formatting-message-text) — Slack

---

## mrkdwn Syntax

```
*bold*                          _italic_
~strikethrough~                 `inline code`
```code block```               > blockquote
<https://url|display text>      <@U0123ABC> (mention)
<#C0123ABC> (channel)           :emoji_name:
<mailto:user@example.com|Email>
<!date^1234567890^{date} at {time}|fallback>
```

**NOT standard Markdown:** `**bold**`, `[text](url)`, `# heading` all render literally in mrkdwn.

Inline code disables other formatting within it. Adjacent format markers without spaces (`*bold*_italic_`) are unreliable — add a space between them.

---

## Links

```
<https://example.com>                URL (auto-linked)
<https://example.com|Display Text>   Custom label
<mailto:user@example.com|Email>      Email link
```

Spaces in URLs break parsing. Formatting inside labels (`<url|*bold*>`) works. Control unfurling with `unfurl_links` / `unfurl_media` params.

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

Always use IDs, not names. IDs are stable; names change.

---

## Date Tokens

Syntax: `<!date^{unix_timestamp}^{token_string}^{optional_link}|{fallback}>`

Displays in reader's **device timezone**. Optional link makes date clickable.

| Token | Example Output |
|-------|---------------|
| `{date_num}` | 2014-02-18 |
| `{date}` | February 18th, 2014 (omits year if within ~6 months) |
| `{date_short}` | Feb 18, 2014 |
| `{date_long}` | Tuesday, February 18th, 2014 |
| `{time}` | 6:39 AM (12h) or 06:39 (24h) |
| `{time_secs}` | 6:39:42 AM |
| `{ago}` | 3 minutes ago |
| `{date_pretty}` | Yesterday (or date if not recent) |
| `{date_short_pretty}` | Yesterday (short format) |
| `{date_long_pretty}` | Yesterday (long format) |

---

## Escaping

Only three characters: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`

---

## Text Object Types

| Type | Formatting | Key Properties |
|------|-----------|----------------|
| `mrkdwn` | Slack mrkdwn syntax | `verbatim` (disables auto-link/mention) |
| `plain_text` | No formatting | `emoji` (converts `:emoji:` to rendered) |

Min 1 char, max 3000 chars (section fields: max 2000 each).

---

## Where Each Text Type Is Allowed

| Context | Allowed |
|---------|---------|
| Section text / fields | `mrkdwn` or `plain_text` |
| Context elements | `mrkdwn` or `plain_text` |
| Option description | `mrkdwn` or `plain_text` |
| Header, button, placeholder, label | `plain_text` only |
| Modal title / submit / close | `plain_text` only |
| Option text | `plain_text` only |

---

## Disabling Formatting

| Context | Method |
|---------|--------|
| Text objects | `type: "plain_text"` |
| Message `text` | `mrkdwn: false` |
| Attachments | Exclude from `mrkdwn_in` (accepts: `"text"`, `"pretext"`, `"fields"`) |
| Auto-linking | `verbatim: true` or `parse: "none"` |
| All auto-parsing | `parse: "none"` (default). `parse: "full"` disables mrkdwn, enables auto-parsing |

---

## Legacy Attachment Fields

`fallback` | `color` | `pretext` | `author_name/link/icon` | `title/title_link` | `text` | `fields` | `image_url` | `thumb_url` | `footer/footer_icon/ts` | `mrkdwn_in`
