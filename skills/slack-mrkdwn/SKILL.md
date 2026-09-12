---
name: slack-mrkdwn
description: Format or debug Slack message text, mentions, links, dates, and escaping. Use when choosing Slack mrkdwn versus Markdown, rich_text, or plain_text for a receiving field; not Block Kit layout or Slack history retrieval.
---

# Slack Text Formatting

Format the supplied content for the actual receiving field. The user's explicit instructions take precedence over this skill's guidelines.

## Select the renderer

Use the text and destination field/method as input. Infer the destination from the existing payload; if it is unclear and changes the syntax, ask which surface receives the text. For an ordinary Slack message with no other context, state that you are using message `text` and mrkdwn.

| Destination | Format |
|---|---|
| Message `text`, `type: "mrkdwn"` objects | Slack mrkdwn: `*bold*`, `<url|label>` |
| `markdown` block, `markdown_text`, Work Object Markdown fields | Standard Markdown: `**bold**`, `[label](url)` |
| `rich_text` block | Nested elements and style objects, not markup strings |
| Labels or `plain_text` objects | Literal text |

## Preserve content and controls

- Escape untrusted `&`, `<`, and `>` in mrkdwn, in that order. JSON escaping is separate. `verbatim: true` does not neutralize explicit `<...>` controls.
- Use real IDs for mentions and channels. If an ID is missing, leave a clearly labeled template value or ask for it when the output must be ready to send; do not guess from a display name.
- Preserve intended mentions and links without introducing broad notifications. Date controls need a fallback containing timezone information.
- Keep supplied fallback text complete and aligned with block content. Do not assume block rendering supplies mobile notification text.
- Check field-specific limits and method combination rules; non-streaming `markdown_text` cannot be combined with `text` or `blocks` on the documented chat methods.

Return the requested formatted string, text object, or corrected payload. Preserve meaning and explain a renderer mismatch when fixing one. A formatting task can be completed without posting; send only when that action is requested or already authorized.

## References

Read only the part needed for the destination or control syntax.

| Task | Reference |
|---|---|
| Markdown surfaces, text objects, rich text, Work Object text | [RENDERERS.md](references/RENDERERS.md) |
| mrkdwn syntax, mentions, date tokens, escaping | [SYNTAX.md](references/SYNTAX.md) |
| Links/unfurls, parse flags, notifications, legacy attachments | [MESSAGE-BEHAVIOR.md](references/MESSAGE-BEHAVIOR.md) |
| Compact field and syntax lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |

For changing surface support, use Slack's [formatting guide](https://docs.slack.dev/messaging/formatting-message-text/) and the receiving field/method reference.
