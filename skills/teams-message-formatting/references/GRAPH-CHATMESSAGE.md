# Microsoft Graph chatMessage Reference

Use this when constructing Microsoft Graph `chatMessage` payloads for Teams. For mention wire formats see [MENTIONS.md](MENTIONS.md).

## Decision Rules

- Use Graph send only when the integration is explicitly Microsoft Graph and delegated user-send semantics are acceptable.
- Do not use Graph `chatMessage` send as an app-only notification path: the only application permission (`Teamwork.Migrate.All`) is restricted to migration scenarios. Service notifications belong in a bot proactive message or a Workflows webhook.
- It is a violation of the terms of use to use Teams as a log file; send messages people will read and link to the rest.

## Endpoints And Permissions

| Scenario | Endpoint | Delegated permission |
|----------|----------|----------------------|
| New channel message | `POST /teams/{team-id}/channels/{channel-id}/messages` | `ChannelMessage.Send` |
| Channel reply | `POST /teams/{team-id}/channels/{channel-id}/messages/{message-id}/replies` | `ChannelMessage.Send` |
| Chat message | `POST /chats/{chat-id}/messages` | `ChatMessage.Send` |

Personal Microsoft accounts are not supported for these APIs.

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

Use `contentType: "html"` for any formatting:

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><strong>Build failed</strong><br><a href=\"https://example.com/run/123\">Open run</a></p>"
  }
}
```

Teams clients restrict HTML: `<div>` and inline styles may not work as intended, and layout CSS and scripts are out. Stick to paragraphs, `<br>`, semantic emphasis (`<strong>`, `<em>`), links, and the Teams-specific elements below.

## Teams-Specific Body Elements

Graph chatMessage bodies support these non-HTML elements:

| Element | Purpose |
|---------|---------|
| `<at id="0">Name</at>` | References a `chatMessageMention` (user, application, team, channel, or tag) |
| `<attachment id="card-1"></attachment>` | Places an attachment at that position in the body |
| `<emoji id="..." alt="..." title="..."></emoji>` | Standard emoji (on send, `alt` with the Unicode emoji is enough; Teams resolves `id`/`title`) |
| `<customemoji id="..." alt="..." source="..."></customemoji>` | Custom emoji; `source` points at hosted content |
| `<codeblock class="..."><code>...</code></codeblock>` | Code block; `class` names the language |
| `<img src="../hostedContents/1/$value">` | Inline image backed by `hostedContents` with a matching `@microsoft.graph.temporaryId` |

Code block rules:

- Empty or missing `class` renders as plaintext. A language name (lowercase: `bash`, `c`, `cpp`, `csharp`, `css`, `dockerfile`, `go`, `graphql`, `html`, `java`, `javascript`, `json`, `kotlin`, `markdown`, `php`, `powershell`, `python`, `r`, `ruby`, `rust`, `scala`, `shell`, `sql`, `swift`, `typescript`, `xml`, `yaml`, `plaintext`, and more) enables highlighting.
- Do not send pre-highlighted content (`hljs` spans); highlighted code isn't supported on send.
- HTML-escape the code inside `<code>`.

```json
{
  "body": {
    "contentType": "html",
    "content": "<codeblock class=\"shell\"><code>npm run verify\nstatus: passed</code></codeblock>"
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

The body must be HTML whenever the message contains a mention, and `<at id="N">` must match `mentions[N].id`. Team, channel, and tag mention shapes are in [MENTIONS.md](MENTIONS.md).

## Adaptive Card Attachments

Graph uses a body placeholder plus an attachment object. The attachment `content` is a JSON **string** (unlike bot and Workflows payloads, where it is an object).

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
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.5\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Incident opened\",\"weight\":\"Bolder\",\"wrap\":true}]}"
    }
  ]
}
```

Common failures:

- Missing `<attachment id="..."></attachment>` in the body.
- Placeholder ID does not match `attachments[].id` (any unique string works; a GUID is conventional).
- `contentType` not set to `application/vnd.microsoft.card.adaptive`.
- Card supplied as an object instead of stringified JSON, or the string doesn't parse.
- Card actions beyond `Action.OpenUrl`: Graph only supports OpenUrl in sent cards; `Action.Execute`/`Action.Submit` need a bot backend.

File attachments use `contentType: "reference"` with a SharePoint `contentUrl` and `name`.

## Importance And Summary

`importance` may be `normal` (default), `high`, or `urgent`. Use `urgent` sparingly; it produces repeated, disruptive notifications.

`summary` applies to channel messages and feeds notification/fallback views. Keep it short and aligned with the visible message.

## Escaping Checklist

- Escape user text (`&`, `<`, `>`, `"`, `'`) before inserting into HTML.
- Escape code inside `<code>` tags.
- JSON-stringify Adaptive Card attachment content.
- Encode URLs.
- Keep HTML simple; Teams silently drops unsupported tags.

## Anti-Patterns

| Anti-Pattern | Problem | Better |
|--------------|---------|--------|
| App-only Graph send for alerts | Application send is migration-only | Bot proactive messages or Workflows |
| Sending every log line | Teams is not a log sink (terms-of-use violation) | Link to logs and summarize |
| Arbitrary HTML/CSS | Teams client restrictions | Simple Teams-compatible HTML |
| Mention text without `mentions` | No real mention | Add `mentions` array |
| Attachment without body placeholder | Card may not render where expected | Add matching `<attachment>` |
| Pre-highlighted code spans | Rejected/ignored on send | `<codeblock class="lang">` and let Teams highlight |
