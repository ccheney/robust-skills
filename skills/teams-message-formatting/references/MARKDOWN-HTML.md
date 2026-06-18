# Teams Markdown And HTML Reference

Teams formatting depends on the message surface. This file details the text systems that are most often confused.

## Bot Activity Text

Bot Framework activities can set `textFormat`:

| `textFormat` | Meaning | Use |
|--------------|---------|-----|
| `plain` | Raw text | Untrusted or literal text |
| `markdown` | Teams-supported Markdown subset | Normal bot replies |
| `xml` | Simple XML/HTML markup | Specific rich text requirements |

### Bot Markdown

Supported style varies by client. Stay conservative:

| Style | Syntax | Notes |
|-------|--------|-------|
| Bold | `**bold**` | Supported in text-only bot messages |
| Italic | `_italic_` or `*italic*` | Prefer underscore when adjacent to words |
| Strikethrough | `~~text~~` | Not reliable on every client |
| Link | `[text](https://example.com)` | Prefer explicit links |
| Preformatted | Indented or fenced text | Use short snippets |
| Blockquote | `> quote` | Supported for simple quotes |

Avoid Markdown tables, images, headings, and horizontal rules in bot text. Use an Adaptive Card for layout.

### Bot XML / HTML Subset

Use XML/HTML for surfaces that accept simple markup:

| Style | XML/HTML |
|-------|----------|
| Bold | `<strong>text</strong>` |
| Italic | `<em>text</em>` |
| Header | `<h1>Title</h1>`, `<h2>Title</h2>`, `<h3>Title</h3>` |
| Strikethrough | `<strike>text</strike>` |
| Unordered list | `<ul><li>One</li><li>Two</li></ul>` |
| Ordered list | `<ol><li>One</li><li>Two</li></ol>` |
| Preformatted | `<pre>text</pre>` |
| Blockquote | `<blockquote>text</blockquote>` |
| Link | `<a href="https://example.com">text</a>` |

Do not put unescaped user text inside tags. HTML support differs between Teams desktop, browser, iOS, and Android.

## Adaptive Card Markdown

Adaptive Cards do not use full Markdown. Teams supports Markdown in:

- `TextBlock.text`
- `Fact.title`
- `Fact.value`

HTML is not supported in Adaptive Cards.

### Supported

| Style | Syntax |
|-------|--------|
| Bold | `**Bold**` |
| Italic | `_Italic_` |
| Unordered list | `- Item 1\r- Item 2\r- Item 3` |
| Ordered list | `1. Green\r2. Orange\r3. Blue` |
| Link | `[Title](https://example.com)` |

Use `\r` or `\n` for newlines in lists. Outside lists, use `\n\n` for paragraph breaks.

### Unsupported

| Need | Use instead |
|------|-------------|
| Heading | `TextBlock` with `size`, `weight`, and optional `style: "heading"` |
| Table | Adaptive Card `Table` element |
| Image | Adaptive Card `Image` element |
| Code block | Adaptive Card `CodeBlock` element when available |
| Blockquote | `Container` with subtle styling or plain text |
| HTML | Adaptive Card properties and Markdown only |

### Example

```json
{
  "type": "TextBlock",
  "text": "**Build failed**\n\n- API timeout\r- Database migration pending\r\n\n[Open run](https://example.com/run/123)",
  "wrap": true
}
```

## Connector MessageCard Text

MessageCard is a legacy connector/actionable message format. It supports basic Markdown in text fields and limited HTML in some contexts. Use it only when maintaining an existing connector or when the target workflow explicitly requires MessageCard.

For new Teams integrations, prefer:

- Notification bot plus Adaptive Card
- Workflows webhook that posts an Adaptive Card
- Bot Framework/Teams SDK message with Adaptive Card attachment

## Simple Cards

Hero and thumbnail card text can support limited XML/HTML in the `text` property. Formatting is not supported in `title` or `subtitle`. Rich cards do not support Markdown or table formatting.

Use simple cards sparingly; Adaptive Cards are the preferred structured surface for new Teams work.

## Rendering Checklist

- Keep message text short enough to be useful in notifications.
- Test Adaptive Cards on desktop and mobile when layout matters.
- Prefer explicit elements over formatting syntax for layout.
- Keep URLs valid and encoded.
- Do not use Slack mrkdwn syntax anywhere in Teams payloads.
