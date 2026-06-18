---
name: teams-message-formatting
description: Proactively apply when generating Microsoft Teams message text, Bot Framework activities, Teams SDK bot responses, Microsoft Graph chatMessage bodies, Teams Adaptive Card TextBlock or FactSet text, connector MessageCard text, Workflows webhook messages, mentions, emoji, code blocks, links, date/time text, or escaping user content for Teams. Triggers on Teams markdown, Teams Markdown, Teams HTML, Teams bot textFormat, Teams message formatting, Teams mentions, at-mention tags, msteams.entities, Graph chatMessage, contentType html, Adaptive Card Markdown, TextBlock markdown, FactSet markdown, Workflows webhook, Incoming Webhook, MessageCard, connector card, tag mention, channel mention, Teams code block, Teams emoji, and Teams escaping. Use when writing or debugging any Microsoft Teams text rendering issue.
---

# Teams Message Formatting

Microsoft Teams has several incompatible text systems. Pick the surface first, then write the text for that surface.

## CRITICAL: Four Markup Systems

| System | Used In | Bold | Link | Mention |
|--------|---------|------|------|---------|
| Bot text `markdown` | Bot Framework/Teams SDK activity `text` | `**bold**` | `[text](url)` | `<at>Name</at>` plus `entities` |
| Bot text `xml` | Bot activity `textFormat: "xml"` and some rich-card `text` fields | `<strong>bold</strong>` | `<a href="url">text</a>` | `<at>Name</at>` plus `entities` |
| Adaptive Card Markdown | `TextBlock.text`, `Fact.title`, `Fact.value` | `**bold**` | `[text](url)` | `<at>Name</at>` plus root `msteams.entities` |
| Graph `chatMessage` HTML | Microsoft Graph `chatMessage.body.contentType: "html"` | `<strong>bold</strong>` | `<a href="url">text</a>` | `<at id="0">Name</at>` plus `mentions` |

Do not mix them. Slack mrkdwn (`*bold*`, `<url|text>`) is wrong in Teams. Full standard Markdown is also wrong in Adaptive Cards because headings, tables, images, code fences, and blockquotes are not supported in `TextBlock`.

## Quick Decision Tree

```
What are you formatting?
|-- Bot plain reply or proactive message
|   |-- Simple text                         -> `textFormat: "markdown"` or default SDK text
|   |-- Need user/tag mention                -> `<at>...</at>` plus activity `entities`
|   `-- Need rich UI or inputs               -> use $teams-adaptive-cards
|-- Adaptive Card text
|   |-- TextBlock / FactSet                  -> limited Adaptive Card Markdown
|   |-- Header                               -> use TextBlock `size`/`weight`, not `#`
|   |-- Table                                -> use Table element, not Markdown table
|   `-- Code                                 -> use CodeBlock if Teams/card version supports it
|-- Microsoft Graph chatMessage
|   |-- Plain text only                      -> body `contentType: "text"`
|   |-- Formatting, mentions, attachments    -> body `contentType: "html"`
|   `-- Adaptive Card attachment             -> use body `<attachment id="...">` plus attachments
|-- Workflows / Incoming Webhook
|   |-- New implementation                   -> Adaptive Card webhook wrapper
|   `-- Legacy connector                     -> MessageCard only; avoid new connector design
`-- Simple hero/thumbnail card text          -> limited XML/HTML in `text`, not Markdown
```

## Bot Activity Text

Use `textFormat` when constructing raw Bot Framework activities:

```json
{
  "type": "message",
  "textFormat": "markdown",
  "text": "**Build failed** in [CI](https://example.com/run/123)."
}
```

Teams supports only a subset of Markdown across platforms. Use simple bold, italic, links, preformatted text, and blockquotes. Avoid relying on tables, headings, horizontal rules, and image links in text-only bot messages.

For mention text, include both the visible `<at>...</at>` text and a matching `entities` item:

```json
{
  "type": "message",
  "text": "Hey <at>Ada Lovelace</at>, the deployment is ready.",
  "entities": [
    {
      "type": "mention",
      "text": "<at>Ada Lovelace</at>",
      "mentioned": {
        "id": "29:teams-user-id",
        "name": "Ada Lovelace"
      }
    }
  ]
}
```

The `entities[].text` value must exactly match a substring in `text`; otherwise Teams ignores the mention.

## Adaptive Card Text

Use limited Markdown only in `TextBlock.text`, `Fact.title`, and `Fact.value`:

| Format | Syntax | Notes |
|--------|--------|-------|
| Bold | `**bold**` | Standard Markdown bold |
| Italic | `_italic_` | Underscore style is safest |
| Link | `[text](https://example.com)` | URL must be valid and accessible |
| Bullet list | `- Item 1\r- Item 2` | Use `\r` or `\n`; test mobile |
| Ordered list | `1. First\r2. Second` | Keep list text short |
| Line break | `\n\n` outside lists | Single newline can vary by client |

Unsupported in Adaptive Card Markdown: headings, tables, images, preformatted text, and blockquotes. Use Adaptive Card elements instead: `TextBlock` styling for headings, `Table` for tables, `Image` for images, and `CodeBlock` for code when appropriate.

## Graph chatMessage Text

Graph `chatMessage.body` can be `text` or Teams-restricted `html`. Use HTML when the body contains mentions, inline links, attachments, emoji tags, or code blocks:

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><strong>Build failed</strong> in <a href=\"https://example.com/run/123\">CI</a>.</p>"
  }
}
```

Graph supports Teams-specific body elements such as `<at>`, `<attachment>`, `<emoji>`, `<customemoji>`, and `<codeblock>`. The body is not arbitrary browser HTML: avoid `<div>`, inline styles, script-like content, and layout CSS. See [references/GRAPH-CHATMESSAGE.md](references/GRAPH-CHATMESSAGE.md) before building Graph payloads.

## Escaping User Content

Escape based on the destination:

| Destination | Escape |
|-------------|--------|
| JSON string | JSON escaping for backslash, quote, newline |
| Bot XML / Graph HTML | Escape `&`, `<`, `>`, `"`, and `'` when inserted as text |
| Adaptive Card Markdown | Escape or remove Markdown metacharacters when text must render literally |
| Mention display text | Keep the visible `<at>...</at>` text and metadata exactly synchronized |

Never concatenate untrusted user content into Graph HTML, Bot XML, or mention markup without escaping it first.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Slack mrkdwn in Teams | Renders literally or incorrectly | Use Teams Markdown/HTML by surface |
| Markdown table in `TextBlock` | Unsupported | Use Adaptive Card `Table` or concise facts |
| `# Heading` in `TextBlock` | Unsupported | Use `TextBlock` `size`, `weight`, `style` |
| `<b>` in Adaptive Card text | HTML unsupported | Use `**bold**` or TextBlock styling |
| Graph mention without `mentions` array | Renders as text, no notification | Add matching `mentions` entry |
| Bot mention without `entities` | Renders as text, no notification | Add matching activity entity |
| MessageCard for new integrations | Connector path is legacy/retired | Use Workflows or notification bot with Adaptive Cards |
| Graph chatMessage for app-only notifications | Normal sends are delegated; application send is migration-only | Use bot proactive messaging or Workflows |

## Reference Documentation

| File | Purpose |
|------|---------|
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Quick reference for all Teams text systems |
| [references/MARKDOWN-HTML.md](references/MARKDOWN-HTML.md) | Bot Markdown/XML, Adaptive Card Markdown, simple-card HTML |
| [references/MENTIONS.md](references/MENTIONS.md) | Bot, Adaptive Card, Graph, user, tag, channel, and team mentions |
| [references/GRAPH-CHATMESSAGE.md](references/GRAPH-CHATMESSAGE.md) | Microsoft Graph chatMessage body, HTML restrictions, attachments, permissions |

## Sources

- [Format your bot messages](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/format-your-bot-messages) - Microsoft Teams
- [Format text in cards](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-format) - Microsoft Teams
- [Channel and group chat bot conversations](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-and-group-conversations) - Microsoft Teams
- [Send chatMessage in a channel or chat](https://learn.microsoft.com/en-us/graph/api/chatmessage-post) - Microsoft Graph
- [Teams messaging APIs in Microsoft Graph](https://learn.microsoft.com/en-us/graph/teams-messaging-overview) - Microsoft Graph
- [Create an Incoming Webhook](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook) - Microsoft Teams
