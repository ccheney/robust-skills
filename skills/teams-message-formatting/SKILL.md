---
name: teams-message-formatting
description: Proactively apply when generating Microsoft Teams message text, Bot Framework activities, Teams SDK bot responses, Microsoft Graph chatMessage bodies, Teams Adaptive Card TextBlock or FactSet text, Workflows webhook messages, legacy connector MessageCard text, mentions, emoji, code blocks, links, date/time text, or escaping user content for Teams. Triggers on Teams markdown, Teams Markdown, Teams HTML, Teams bot textFormat, Teams message formatting, Teams mentions, at-mention tags, msteams.entities, Graph chatMessage, contentType html, Adaptive Card Markdown, TextBlock markdown, FactSet markdown, Workflows webhook, Incoming Webhook, MessageCard, connector card, tag mention, channel mention, Teams code block, Teams emoji, and Teams escaping. Use when writing or debugging any Microsoft Teams text rendering issue.
---

# Teams Message Formatting

Microsoft Teams has several incompatible text systems. Pick the surface first, then write the text for that surface — most rendering bugs come from using one surface's syntax on another.

## CRITICAL: Four Markup Systems

| System | Used In | Bold | Link | Mention |
|--------|---------|------|------|---------|
| Bot text `markdown` | Bot Framework/Teams SDK activity `text` (default) | `**bold**` | `[text](url)` | `<at>Name</at>` plus activity `entities` |
| Bot text `xml` | Bot activity `textFormat: "xml"` and hero/thumbnail card `text` | `<strong>bold</strong>` | `<a href="url">text</a>` | `<at>Name</at>` plus activity `entities` |
| Adaptive Card Markdown | `TextBlock.text`, `Fact.title`, `Fact.value` | `**bold**` | `[text](url)` | `<at>Name</at>` plus root `msteams.entities` |
| Graph `chatMessage` HTML | Microsoft Graph `chatMessage.body.contentType: "html"` | `<strong>bold</strong>` | `<a href="url">text</a>` | `<at id="0">Name</at>` plus `mentions` array |

Do not mix them. Slack mrkdwn (`*bold*`, `<url|text>`) is wrong everywhere in Teams. Full standard Markdown is also wrong in Adaptive Cards: headings, tables, images, preformatted text, and blockquotes are not supported in `TextBlock`.

## Quick Decision Tree

```
What are you formatting?
|-- Bot reply or proactive bot message
|   |-- Simple text                          -> textFormat "markdown" (or SDK default)
|   |-- User/tag mention                     -> <at>...</at> plus activity entities
|   `-- Rich UI, inputs, buttons             -> Adaptive Card ($teams-adaptive-cards)
|-- Adaptive Card text
|   |-- TextBlock / FactSet                  -> limited Adaptive Card Markdown only
|   |-- Heading                              -> TextBlock size/weight/style, never `#`
|   |-- Table                                -> Table element, never Markdown table
|   `-- Code                                 -> CodeBlock element, never backticks
|-- Microsoft Graph chatMessage (delegated send)
|   |-- Plain text                           -> body contentType "text"
|   |-- Formatting, mentions, emoji, code    -> body contentType "html"
|   `-- Adaptive Card                        -> <attachment id> placeholder + attachments
|-- Service-to-channel webhook
|   |-- Anything new                         -> Workflows webhook + Adaptive Card wrapper
|   `-- Legacy webhook.office.com URL        -> retired May 2026; migrate to Workflows
`-- Hero/thumbnail card                      -> XML/HTML subset in `text` only; no Markdown,
                                                no formatting in title/subtitle
```

## Bot Activity Text

Set `textFormat` when constructing raw Bot Framework activities (`markdown` is the default):

```json
{
  "type": "message",
  "textFormat": "markdown",
  "text": "**Build failed** in [CI](https://example.com/run/123)."
}
```

Bot text Markdown support varies by client, so stay inside the safe subset:

- Safe on desktop, iOS, and Android: bold, italic, links, preformatted text, blockquotes.
- Desktop only: ordered and unordered lists.
- Not on Android: strikethrough.
- Never supported in text-only bot messages: headings, horizontal rules, tables, image links. Use an Adaptive Card for those.

Bot messages have an approximate 100 KB limit (text, mentions, reactions); stay under 80 KB or the send fails with `413 MessageSizeTooBig`.

For mentions, include both the visible `<at>...</at>` text and a matching `entities` item:

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

The `entities[].text` value must exactly match a substring of `text` (including any `@` prefix); otherwise Teams ignores the mention. The `mentioned.id` accepts a Teams user ID (`29:...`), a Microsoft Entra Object ID, or a UPN. See [references/MENTIONS.md](references/MENTIONS.md) for tag, team, and channel mentions.

## Adaptive Card Text

Use limited Markdown only in `TextBlock.text`, `Fact.title`, and `Fact.value`:

| Format | Syntax | Notes |
|--------|--------|-------|
| Bold | `**bold**` | Standard Markdown bold |
| Italic | `_italic_` | Underscore style is what the Teams docs show |
| Link | `[text](https://example.com)` | URL must be absolute |
| Bullet list | `- Item 1\r- Item 2` | `\r` or `\n` between items |
| Ordered list | `1. First\r2. Second` | Keep list text short |
| Line break | `\n\n` outside lists | `\n\n` inside a list indents the next item — use `\r` there |

Unsupported in Adaptive Card Markdown: headings, tables, images, preformatted text, and blockquotes. HTML is never supported in Adaptive Cards. Use card elements instead: `TextBlock` `size`/`weight`/`style: "heading"` for headings, `Table` for tables, `Image` for images, `CodeBlock` for code.

## Graph chatMessage Text

Graph `chatMessage.body` is `text` or Teams-restricted `html`. Use HTML whenever the body contains mentions, links, emphasis, attachments, emoji tags, or code blocks:

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><strong>Build failed</strong> in <a href=\"https://example.com/run/123\">CI</a>.</p>"
  }
}
```

Graph supports Teams-specific body elements: `<at id="N">`, `<attachment id="...">`, `<emoji>`, `<customemoji>`, and `<codeblock class="..."><code>`. The body is not arbitrary browser HTML — `<div>`, inline styles, and layout CSS may be ignored or break rendering. Normal sends are delegated-only (`ChannelMessage.Send` / `ChatMessage.Send`); application-permission send is migration-only. Read [references/GRAPH-CHATMESSAGE.md](references/GRAPH-CHATMESSAGE.md) before building Graph payloads.

## Escaping User Content

Escape based on the destination, innermost format first:

| Destination | Escape |
|-------------|--------|
| JSON string | JSON escaping for backslash, quote, newline |
| Bot XML / Graph HTML | `&`, `<`, `>`, `"`, `'` when inserted as text |
| Adaptive Card Markdown | Escape or strip Markdown metacharacters when text must render literally |
| Mention display text | Keep the visible `<at>...</at>` text and metadata exactly synchronized |

Never concatenate untrusted user content into Graph HTML, Bot XML, or mention markup without escaping it first — unescaped `<` or `&` corrupts the whole body.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Slack mrkdwn in Teams | Renders literally or incorrectly | Use the markup for the target surface |
| Markdown table or `# heading` in `TextBlock` | Unsupported, renders as literal text | `Table` element; `TextBlock` `size`/`weight`/`style` |
| `<b>` or any HTML in Adaptive Card text | HTML unsupported in cards | `**bold**` or TextBlock styling |
| Triple-backtick code in `TextBlock` | Preformatted text unsupported | `CodeBlock` element |
| Graph mention without `mentions` array | Renders as text, no notification | Add matching `mentions` entry |
| Bot mention without `entities` | Renders as text, no notification | Add matching activity entity |
| New MessageCard/connector integration | O365 connectors retired May 2026 | Workflows webhook or notification bot with Adaptive Cards |
| Graph chatMessage for app-only notifications | Application send is migration-only | Bot proactive messaging or Workflows |
| Lists or strikethrough in bot text for mobile users | Lists desktop-only; strikethrough missing on Android | Adaptive Card, or restructure the text |

## Reference Documentation

| Read | When |
|------|------|
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | You need exact syntax for any surface fast |
| [references/MARKDOWN-HTML.md](references/MARKDOWN-HTML.md) | Bot Markdown/XML per-platform support, Adaptive Card Markdown detail, hero-card HTML, MessageCard legacy |
| [references/MENTIONS.md](references/MENTIONS.md) | Any mention: bot, Adaptive Card, Graph, user, tag, team, channel, or stripping incoming bot mentions |
| [references/GRAPH-CHATMESSAGE.md](references/GRAPH-CHATMESSAGE.md) | Building Graph chatMessage payloads: HTML restrictions, codeblock/emoji tags, attachments, permissions |

## Sources

- [Format your bot messages](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/format-your-bot-messages) - Microsoft Teams
- [Format text in cards](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-format) - Microsoft Teams
- [Channel and group chat bot conversations](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-and-group-conversations) - Microsoft Teams
- [Send chatMessage in a channel or chat](https://learn.microsoft.com/en-us/graph/api/chatmessage-post?view=graph-rest-1.0) - Microsoft Graph
- [Teams messaging APIs in Microsoft Graph](https://learn.microsoft.com/en-us/graph/teams-messaging-overview) - Microsoft Graph
- [Create an Incoming Webhook (Workflows)](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook) - Microsoft Teams
- [Retirement of Office 365 connectors within Microsoft Teams](https://devblogs.microsoft.com/microsoft365dev/retirement-of-office-365-connectors-within-microsoft-teams/) - Microsoft 365 Dev Blog
