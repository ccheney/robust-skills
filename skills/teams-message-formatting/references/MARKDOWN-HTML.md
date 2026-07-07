# Teams Markdown And HTML Reference

Teams formatting depends on the message surface. This file details the text systems that are most often confused. For mention markup see [MENTIONS.md](MENTIONS.md); for Graph HTML see [GRAPH-CHATMESSAGE.md](GRAPH-CHATMESSAGE.md).

## Bot Activity Text

Bot Framework activities can set `textFormat` (defaults to `markdown`):

| `textFormat` | Meaning | Use |
|--------------|---------|-----|
| `plain` | Raw text, no formatting applied | Untrusted or literal text |
| `markdown` | Teams-supported Markdown subset | Normal bot replies |
| `xml` | Simple XML/HTML markup | Specific rich text requirements |

### Bot Markdown Per-Platform Support

Support differs by platform, so a message that looks fine on desktop can degrade on mobile:

| Style | Syntax | Desktop | iOS | Android |
|-------|--------|---------|-----|---------|
| Bold | `**bold**` | Yes | Yes | Yes |
| Italic | `_italic_` or `*italic*` | Yes | Yes | Yes |
| Strikethrough | `~~text~~` | Yes | Yes | No |
| Link | `[text](https://example.com)` | Yes | Yes | Yes |
| Preformatted text | Indented/fenced text | Yes | Yes | Yes |
| Blockquote | `> quote` | Yes | Yes | Yes |
| Unordered list | `- item` | Yes | No | No |
| Ordered list | `1. item` | Yes | No | No |
| Heading (1-3) | `# Heading` | No | No | No |
| Horizontal rule | `---` | No | No | No |
| Image link | `![alt](url)` | No | No | No |

Text-only bot messages don't support table formatting on any platform. When you need lists on mobile, headings, or tables, send an Adaptive Card instead.

Bot messages have an approximate 100 KB limit including mentions and reactions; keep the message itself under 80 KB or the send fails with `413` / `MessageSizeTooBig`.

### Bot XML / HTML Subset

Use XML/HTML for surfaces that accept simple markup:

| Style | XML/HTML |
|-------|----------|
| Bold | `<strong>text</strong>` (unreliable in hero/thumbnail cards; see below) |
| Italic | `<em>text</em>` |
| Header (levels 1-3) | `<h1>Title</h1>`, `<h2>Title</h2>`, `<h3>Title</h3>` |
| Strikethrough | `<strike>text</strike>` |
| Unordered list | `<ul><li>One</li><li>Two</li></ul>` |
| Ordered list | `<ol><li>One</li><li>Two</li></ol>` |
| Preformatted | `<pre>text</pre>` |
| Blockquote | `<blockquote>text</blockquote>` |
| Link | `<a href="https://example.com">text</a>` |

Do not put unescaped user text inside tags. HTML rendering differs between Teams desktop, browser, iOS, and Android.

## Adaptive Card Markdown

Adaptive Cards do not use full Markdown. Teams supports Markdown only in:

- `TextBlock.text`
- `Fact.title`
- `Fact.value`

HTML is never supported in Adaptive Cards.

### Supported

| Style | Syntax |
|-------|--------|
| Bold | `**Bold**` |
| Italic | `_Italic_` |
| Unordered list | `- Item 1\r- Item 2\r- Item 3` |
| Ordered list | `1. Green\r2. Orange\r3. Blue` |
| Link | `[Title](https://example.com)` |

Newlines: use `\r` or `\n` between list items. Outside lists, use `\n\n` for breaks. Inside a list, `\n\n` indents the next item instead of breaking — stick to `\r` there.

### Unsupported (use elements instead)

| Need | Use instead |
|------|-------------|
| Heading | `TextBlock` with `size`, `weight`, and `style: "heading"` |
| Table | Adaptive Card `Table` element |
| Image | Adaptive Card `Image` element |
| Code block | Adaptive Card `CodeBlock` element |
| Blockquote | `Container` with subtle styling or plain text |
| HTML | Adaptive Card properties and Markdown only |

Markdown is also not supported in bot OAuth sign-in cards.

### Example

```json
{
  "type": "TextBlock",
  "text": "**Build failed**\n\n- API timeout\r- Database migration pending\n\n[Open run](https://example.com/run/123)",
  "wrap": true
}
```

## Legacy Connector MessageCard Text

MessageCard was the legacy O365 connector/actionable-message format. The connector retirement completed in May 2026: `webhook.office.com` connector webhooks no longer accept posts. Workflows webhooks still accept MessageCard-formatted payloads for migration continuity, but action buttons don't render — only the text content.

Touch MessageCard syntax only when reading or migrating an existing payload. It supported basic Markdown (`**bold**`, `*italic*`, `### headings`, `~~strikethrough~~`, lists, `>` blockquotes, links, image links) and a limited HTML equivalent, with `\n\n` for newlines.

For anything new, use:

- Workflows webhook that posts an Adaptive Card
- Notification bot plus Adaptive Card
- Bot Framework/Teams SDK message with Adaptive Card attachment

## Simple Cards (Hero/Thumbnail)

Hero and thumbnail card `text` supports the XML/HTML subset above. No formatting is supported in `title` or `subtitle`, and rich cards do not support Markdown or table formatting.

Cross-platform caveats for rich-card XML: bold is not reliably rendered, and iOS drops bold and italic entirely. Prefer Adaptive Cards for any new structured content.

## Rendering Checklist

- Keep message text short enough to be useful in notifications.
- Test on desktop and mobile when layout matters; the platform tables above are the reason.
- Prefer explicit card elements over formatting syntax for layout.
- Keep URLs absolute, valid, and encoded.
- Do not use Slack mrkdwn syntax anywhere in Teams payloads.
