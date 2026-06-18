# Teams Message Formatting Cheatsheet

Use this when you need exact syntax quickly. For edge cases, read the surface-specific reference.

## Surface Matrix

| Surface | Payload field | Markup | Good for | Avoid |
|---------|---------------|--------|----------|-------|
| Bot activity text | `text`, optional `textFormat` | `plain`, `markdown`, or `xml` | Conversational replies, links, simple emphasis, mentions | Tables, complex layout |
| Adaptive Card text | `TextBlock.text`, `Fact.title`, `Fact.value` | Limited Markdown | Rich notifications, facts, short summaries | HTML, full Markdown |
| Graph chatMessage | `body.content`, `body.contentType` | `text` or Teams-restricted `html` | User-delegated Teams messages, mentions, attachment placeholders | App-only notification bots |
| Incoming Webhook / Workflows | Message wrapper containing card | Adaptive Card or MessageCard depending flow | External notifications | Connector-only legacy assumptions |
| Hero/thumbnail cards | `text` property | XML/HTML subset | Simple cards | Markdown in title/subtitle |

## Adaptive Card Markdown

| Need | Use | Not |
|------|-----|-----|
| Bold | `**bold**` | `*bold*` |
| Italic | `_italic_` | HTML tags |
| Link | `[text](https://example.com)` | `<https://example.com|text>` |
| Bullet list | `- Item 1\r- Item 2` | HTML lists |
| Ordered list | `1. First\r2. Second` | Markdown tables |
| Heading | `TextBlock` with `size`/`weight` | `# Heading` |
| Code | `CodeBlock` element where supported | Triple backticks in `TextBlock` |
| Table | `Table` element where supported | Markdown table |

Unsupported in Adaptive Card Markdown: headings, tables, images, preformatted text, and blockquotes.

## Bot Text Markdown

```json
{
  "type": "message",
  "textFormat": "markdown",
  "text": "**Deploy complete**\n\nView [release notes](https://example.com/releases/42)."
}
```

Keep bot text Markdown simple. Support varies by client and message type; use Adaptive Cards for structured layout.

## Bot XML / HTML Subset

```json
{
  "type": "message",
  "textFormat": "xml",
  "text": "<p><strong>Deploy complete</strong></p><p><a href=\"https://example.com/releases/42\">Release notes</a></p>"
}
```

Use XML/HTML mainly when required by a card type or SDK path. Escape user content before insertion.

## Graph chatMessage HTML

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><strong>Deploy complete</strong><br><a href=\"https://example.com/releases/42\">Release notes</a></p>"
  }
}
```

Graph body HTML is Teams-restricted. Use semantic inline tags and paragraphs; avoid CSS layout, scripts, and arbitrary web HTML.

## Mentions

| Surface | Visible text | Metadata |
|---------|--------------|----------|
| Bot text | `<at>Ada Lovelace</at>` | Activity `entities` item with `type: "mention"` |
| Adaptive Card | `<at>Ada Lovelace</at>` inside `TextBlock`/`FactSet` | Root `msteams.entities` mention |
| Graph chatMessage | `<at id="0">Ada Lovelace</at>` | `mentions[0]` with matching `id` |

The visible mention text and metadata must match exactly. Prefer stable IDs over display names.

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
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Hello\",\"wrap\":true}]}"
    }
  ]
}
```

Graph card `content` is commonly a JSON string. The body must contain a matching `<attachment id="..."></attachment>` placeholder.

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
4. Use Workflows or notification bots for service notifications.
5. Avoid new MessageCard/connector designs unless maintaining existing legacy payloads.
