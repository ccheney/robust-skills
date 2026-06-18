# Graph chatMessage Adaptive Card Attachments

Microsoft Graph uses a different wrapper from bots and webhooks. A Teams Adaptive Card sent through Graph is a `chatMessage` with an HTML body placeholder and a matching attachment.

## Minimal Graph Card Message

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
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"fallbackText\":\"Status update\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Status update\",\"wrap\":true}]}"
    }
  ]
}
```

## Rules

- `body.contentType` must be `html` when using an attachment placeholder.
- `body.content` must include `<attachment id="..."></attachment>`.
- The placeholder ID must match an `attachments[].id`.
- Adaptive card attachment `contentType` must be `application/vnd.microsoft.card.adaptive`.
- Attachment `content` is commonly JSON-stringified card content.
- Do not use the webhook `{ "type": "message" }` wrapper for Graph.

## With Body Text Around Card

```json
{
  "body": {
    "contentType": "html",
    "content": "<p>Incident update</p><attachment id=\"incident-card\"></attachment>"
  },
  "attachments": [
    {
      "id": "incident-card",
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"API latency is elevated\",\"wrap\":true}]}"
    }
  ],
  "importance": "high"
}
```

Keep body text aligned with the card; notifications and fallback surfaces may expose body/summary separately.

## Graph Permissions

| Path | Least privileged normal send |
|------|------------------------------|
| Channel message | Delegated `ChannelMessage.Send` |
| Chat message | Delegated `ChatMessage.Send` |

Application `Teamwork.Migrate.All` is for migration/import scenarios, not normal app notifications.

## Graph Mentions With Cards

You can include mentions in `body.content` and `mentions` while also including card placeholders.

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><at id=\"0\">Ada Lovelace</at> please review:</p><attachment id=\"card-1\"></attachment>"
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
  ],
  "attachments": [
    {
      "id": "card-1",
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Approval requested\",\"wrap\":true}]}"
    }
  ]
}
```

Card-internal mentions still need card `msteams.entities` inside the Adaptive Card content.

## Validation Checklist

- Parse the JSON payload.
- Extract all `<attachment id="...">` body placeholders.
- Verify every placeholder has a matching attachment.
- Verify every Adaptive Card attachment content parses as JSON.
- Validate each card independently.
- Confirm the send path is delegated and appropriate.
- Keep payload purposeful; do not stream logs to Teams.

## Common Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Card missing | No body placeholder | Add `<attachment id="..."></attachment>` |
| Attachment ignored | ID mismatch | Match placeholder and attachment IDs |
| Bad request | Card content is object where string expected by client/code path | JSON-stringify content for Graph |
| HTML renders oddly | Unsupported Teams HTML | Use simple body HTML |
| Button does not invoke app | Graph is not bot backend | Use bot card for interaction |
| Mention not notifying | Missing `mentions` metadata | Add Graph mention object |

## When Not To Use Graph

Avoid Graph card send when:

- The app needs to send as itself rather than a delegated user.
- The card contains form submit/approval actions that need bot handling.
- The integration will send high-volume operational logs.
- You need proactive install, app identity, or Universal Actions.

Use a Teams bot or Workflows instead.
