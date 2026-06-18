# Microsoft Graph chatMessage Reference

Use this when constructing Microsoft Graph `chatMessage` payloads for Teams.

## Decision Rules

- Use Graph send only when the user explicitly wants Microsoft Graph or delegated user-send semantics.
- Do not use Graph `chatMessage` send as the default app-only notification path.
- Application permission for normal sends is migration-only (`Teamwork.Migrate.All`); service notifications should usually use a Teams bot/proactive message or Workflows webhook.
- It is against Microsoft guidance to use Teams as a log file; send messages people will read.

## Endpoints

| Scenario | Endpoint |
|----------|----------|
| New channel message | `POST /teams/{team-id}/channels/{channel-id}/messages` |
| Channel reply | `POST /teams/{team-id}/channels/{channel-id}/messages/{message-id}/replies` |
| Existing chat message | `POST /chats/{chat-id}/messages` |

Normal channel sends use delegated `ChannelMessage.Send`. Chat sends use delegated `ChatMessage.Send`. Personal Microsoft accounts are not supported for these Teams APIs.

## Body

`body` is mandatory.

```json
{
  "body": {
    "contentType": "text",
    "content": "Hello world"
  }
}
```

Use `contentType: "html"` for formatting:

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><strong>Build failed</strong><br><a href=\"https://example.com/run/123\">Open run</a></p>"
  }
}
```

Teams clients restrict HTML. Avoid layout tags and inline styles. Prefer simple paragraphs, line breaks, semantic emphasis, links, mentions, codeblock tags, and attachment placeholders.

## Teams-Specific Body Elements

Graph chatMessage bodies can contain Teams-supported non-HTML elements:

| Element | Purpose |
|---------|---------|
| `<at id="0">Name</at>` | References a `chatMessageMention` |
| `<attachment id="card-1"></attachment>` | Places an attachment in the message body |
| `<emoji id="..." alt="..." title="..."></emoji>` | Represents emoji metadata |
| `<customemoji id="..." alt="..." source="..."></customemoji>` | Represents custom emoji metadata |
| `<codeblock class=""><code>...</code></codeblock>` | Represents a plain code block |
| `<codeblock class="Json"><code>...</code></codeblock>` | Represents a language-tagged code block |

Highlighted code blocks are not supported when sending with Graph. Prefer plain code blocks or Adaptive Card `CodeBlock` when a card is appropriate.

Plain code block example:

```json
{
  "body": {
    "contentType": "html",
    "content": "<codeblock class=\"\"><code>npm run verify\nstatus: passed</code></codeblock>"
  }
}
```

## Mentions

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><at id=\"0\">Ada Lovelace</at> please review the incident.</p>"
  },
  "mentions": [
    {
      "id": 0,
      "mentionText": "Ada Lovelace",
      "mentioned": {
        "user": {
          "id": "00000000-0000-0000-0000-000000000000",
          "displayName": "Ada Lovelace",
          "userIdentityType": "aadUser"
        }
      }
    }
  ]
}
```

The body content is always HTML if a chatMessage contains a mention. Keep the numeric IDs synchronized.

## Adaptive Card Attachments

Graph uses a body placeholder plus an attachment object. The attachment `content` is commonly a JSON string.

```json
{
  "body": {
    "contentType": "html",
    "content": "<attachment id=\"incident-card\"></attachment>"
  },
  "attachments": [
    {
      "id": "incident-card",
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Incident opened\",\"weight\":\"Bolder\",\"wrap\":true}]}"
    }
  ]
}
```

Common failures:

- Missing `<attachment id="..."></attachment>` in body.
- Placeholder ID does not match `attachments[].id`.
- `contentType` not set to `application/vnd.microsoft.card.adaptive`.
- Card content supplied as invalid stringified JSON.
- Interactive card actions expected to call a bot when no bot/backend is installed.

## Importance And Summary

`importance` may be `normal`, `high`, or `urgent`. Use `urgent` sparingly; it creates disruptive notifications.

`summary` applies to channel messages and can help notification/fallback views. Keep it short and aligned with the visible message.

## Escaping Checklist

- Escape user text before inserting into HTML.
- Escape code inside `<code>` tags.
- JSON-stringify Adaptive Card attachment content.
- Encode URLs.
- Keep HTML simple; Teams may ignore unsupported tags.

## Anti-Patterns

| Anti-Pattern | Problem | Better |
|--------------|---------|--------|
| App-only Graph send for alerts | Application send is migration-only | Bot proactive messages or Workflows |
| Sending every log line | Teams is not a log sink | Link to logs and summarize |
| Arbitrary HTML/CSS | Teams client restrictions | Simple Teams-compatible HTML |
| Mention text without `mentions` | No real mention | Add `mentions` array |
| Attachment without body placeholder | Card may not render where expected | Add matching `<attachment>` |
