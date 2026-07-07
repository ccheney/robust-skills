# Teams Message Formatting Cheatsheet

Use this when you need exact syntax quickly. For edge cases, read the surface-specific reference: [MARKDOWN-HTML.md](MARKDOWN-HTML.md), [MENTIONS.md](MENTIONS.md), [GRAPH-CHATMESSAGE.md](GRAPH-CHATMESSAGE.md).

## Surface Matrix

| Surface | Payload field | Markup | Good for | Avoid |
|---------|---------------|--------|----------|-------|
| Bot activity text | `text`, optional `textFormat` | `plain`, `markdown` (default), or `xml` | Conversational replies, links, simple emphasis, mentions | Tables, headings, layout; lists on mobile |
| Adaptive Card text | `TextBlock.text`, `Fact.title`, `Fact.value` | Limited Markdown | Rich notifications, facts, short summaries | HTML, full Markdown |
| Graph chatMessage | `body.content` with `body.contentType` | `text` or Teams-restricted `html` | Delegated user sends, mentions, emoji, code blocks, attachments | App-only notification sending |
| Workflows webhook | `attachments` array wrapping a card | Adaptive Card JSON | External service notifications into a channel/chat | MessageCard except legacy payloads (buttons don't render) |
| Hero/thumbnail cards | `text` property | XML/HTML subset | Simple cards | Markdown; any formatting in `title`/`subtitle` |

Legacy O365 connector Incoming Webhooks (`webhook.office.com` URLs) stopped working with the May 2026 retirement. Anything new goes through a Workflows webhook or a bot.

## Adaptive Card Markdown

| Need | Use | Not |
|------|-----|-----|
| Bold | `**bold**` | `<b>`, `<strong>` |
| Italic | `_italic_` | HTML tags |
| Link | `[text](https://example.com)` | `<https://example.com\|text>` |
| Bullet list | `- Item 1\r- Item 2` | HTML lists |
| Ordered list | `1. First\r2. Second` | Markdown tables |
| Heading | `TextBlock` with `size`/`weight`/`style: "heading"` | `# Heading` |
| Code | `CodeBlock` element | Triple backticks in `TextBlock` |
| Table | `Table` element | Markdown table |

Unsupported in Adaptive Card Markdown: headings, tables, images, preformatted text, blockquotes, and all HTML.

Newlines: `\r` or `\n` between list items; `\n\n` for breaks outside lists. `\n\n` inside a list indents the next item instead of breaking.

## Bot Text Markdown

```json
{
  "type": "message",
  "textFormat": "markdown",
  "text": "**Deploy complete**\n\nView [release notes](https://example.com/releases/42)."
}
```

Safe everywhere: bold, italic, links, preformatted text, blockquotes. Lists render on desktop only; strikethrough is missing on Android; headings, horizontal rules, tables, and image links never render. Use an Adaptive Card for structured layout.

## Bot XML / HTML Subset

```json
{
  "type": "message",
  "textFormat": "xml",
  "text": "<p><strong>Deploy complete</strong></p><p><a href=\"https://example.com/releases/42\">Release notes</a></p>"
}
```

Use XML only when a card type or existing integration requires it. Escape user content before insertion.

## Graph chatMessage HTML

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><strong>Deploy complete</strong><br><a href=\"https://example.com/releases/42\">Release notes</a></p>"
  }
}
```

Graph body HTML is Teams-restricted. Use paragraphs, line breaks, semantic inline tags, links, and the Teams-specific tags (`<at>`, `<attachment>`, `<emoji>`, `<codeblock>`); avoid `<div>`, inline styles, scripts, and layout CSS.

Code block:

```json
{
  "body": {
    "contentType": "html",
    "content": "<codeblock class=\"json\"><code>{ \"status\": \"passed\" }</code></codeblock>"
  }
}
```

Empty or missing `class` means plaintext; a language name (`json`, `python`, `bash`, ...) enables highlighting on render.

## Mentions

| Surface | Visible text | Metadata |
|---------|--------------|----------|
| Bot text | `<at>Ada Lovelace</at>` | Activity `entities` item with `type: "mention"` |
| Adaptive Card | `<at>Ada Lovelace</at>` inside `TextBlock`/`FactSet` | Root `msteams.entities` mention |
| Graph chatMessage | `<at id="0">Ada Lovelace</at>` | `mentions[0]` with matching numeric `id` |

The visible mention text and metadata `text`/`mentionText` must match exactly. IDs can be a Teams user ID (`29:...`), Entra Object ID, or UPN. Details and tag/team/channel mentions: [MENTIONS.md](MENTIONS.md).

## Graph Adaptive Card Attachment Placeholder

```json
{
  "body": {
    "contentType": "html",
    "content": "<attachment id=\"card-1\"></attachment>"
  },
  "attachments": [
    {
      "id": "card-1",
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.5\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Hello\",\"wrap\":true}]}"
    }
  ]
}
```

Graph card `content` is a JSON *string*, not an object. The body must contain a matching `<attachment id="..."></attachment>` placeholder.

## Workflows Webhook Payload

```json
{
  "type": "message",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
          { "type": "TextBlock", "text": "**Deploy complete**", "wrap": true }
        ]
      }
    }
  ]
}
```

Unlike Graph, the Workflows `content` is a JSON object. Messages post as the Flow bot; sender name/icon customization isn't available.

## Escaping

| Context | Escape these first |
|---------|--------------------|
| JSON | `\`, `"`, newlines |
| HTML/XML text | `&`, `<`, `>`, `"`, `'` |
| Markdown literal text | `\`, `*`, `_`, `[`, `]`, `(`, `)`, `#`, `-`, `>` as needed |
| URL in Markdown | Encode spaces and unsafe characters |

## Choosing A Fallback

When uncertain:

1. Use Adaptive Cards for structured notifications.
2. Use bot text Markdown for short conversational replies.
3. Use Graph HTML only when the integration is explicitly Microsoft Graph and delegated send is acceptable.
4. Use Workflows webhooks or notification bots for service notifications.
5. Never start a new MessageCard/connector design; those endpoints are retired.
