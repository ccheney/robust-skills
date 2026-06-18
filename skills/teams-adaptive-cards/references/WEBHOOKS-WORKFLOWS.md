# Webhooks, Workflows, And Connector Migration

Teams webhook guidance has changed. Treat legacy Office 365 connectors and MessageCards as maintenance paths. For new work, prefer Workflows or a notification bot with Adaptive Cards.

## Incoming Webhook Adaptive Card Payload

The top-level request body is not a raw Adaptive Card. Use the message wrapper:

```json
{
  "type": "message",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": {
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.2",
        "fallbackText": "Build failed for API.",
        "body": [
          {
            "type": "TextBlock",
            "text": "Build failed",
            "weight": "Bolder",
            "color": "Attention",
            "wrap": true
          }
        ],
        "actions": [
          {
            "type": "Action.OpenUrl",
            "title": "Open run",
            "url": "https://example.com/run/123"
          }
        ]
      }
    }
  ]
}
```

Required wrapper fields:

- Top-level `type` must be `message`.
- `attachments` must be an array.
- Each card attachment uses `contentType: "application/vnd.microsoft.card.adaptive"`.
- `content` is the Adaptive Card object.

## Webhook Limits

- Message size limit: 28 KB.
- Around four requests per second can be throttled; implement retry with exponential backoff.
- Webhook cards are best for notifications, not multi-step interactions.
- Use public/accessible URLs for images and links.

## Workflows

The Workflows app can create a webhook URL that receives HTTP requests and posts a message or Adaptive Card to Teams.

Use Workflows when:

- You need user-configurable webhook notifications.
- You want Power Automate transformations before posting.
- The organization prefers no custom Teams app/bot deployment.

Operational constraints:

- Workflows are tied to owner users, not a team/channel object.
- Add co-owners to avoid orphaned flows.
- Flow-bot support differs by channel type; private/shared channel behavior can be limited.
- Posting on behalf of a user can be part of the workflow behavior.

## Connector Retirement And Migration

Office 365 connectors and connector-based webhooks are a legacy/retired path in Teams. New implementations should not depend on connector setup.

Migration paths:

| Existing | Migrate To | Notes |
|----------|------------|-------|
| Incoming Webhook connector | Workflows webhook | Good for simple notifications |
| MessageCard with URL buttons | Adaptive Card with `Action.OpenUrl` | Usually direct conversion |
| MessageCard `HttpPOST` actions | Bot with `Action.Submit` / `Action.Execute` | Requires backend invoke handling |
| Connector configuration UX | Power Automate connector or Teams app config | Depends on product model |
| High-volume alerts | Notification bot plus rate control | Avoid Teams as log sink |

## MessageCard To Adaptive Card Mapping

| MessageCard | Adaptive Card |
|-------------|---------------|
| `summary` | `fallbackText` and notification text |
| `themeColor` | Semantic `color`, icon, or `Container.style` |
| `title` | `TextBlock` `weight: "Bolder"` |
| `text` | `TextBlock` with limited Markdown |
| `sections[].facts` | `FactSet.facts` |
| `activityTitle` | `TextBlock` title |
| `activitySubtitle` | subtle `TextBlock` |
| `activityImage` | `Image` with `altText` |
| `OpenUri` | `Action.OpenUrl` |
| `HttpPOST` | Bot-backed `Action.Submit` or `Action.Execute` |
| `ActionCard` inputs | Adaptive Card `Input.*` elements |

## Webhook Action Guidance

Use:

- `Action.OpenUrl`
- `Action.ToggleVisibility` for local details

Avoid:

- `Action.Submit`
- `Action.Execute`
- Authentication/SSO flows
- Multi-step approvals that require server state changes

If a button must change server state, route the user to a secure web page or build a bot.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| HTTP 400, summary/text required | Posted raw card or MessageCard mismatch | Use message attachment wrapper |
| Card renders but button does nothing useful | Submit/Execute has no backend | Use OpenUrl or bot |
| Card too large | Over 28 KB | Shorten text, remove large base64/images, link out |
| Bursty alerts fail | Throttling | Backoff and aggregate |
| Mentions render as text | Missing `msteams.entities` | Add mention metadata |
| MessageCard button missing in Workflows | Button rendering not supported | Convert to Adaptive Card/OpenUrl or bot |

## Notification Design

Webhook cards should answer:

1. What happened?
2. What is the current state?
3. Who/what is affected?
4. What should the recipient do next?
5. Where can they inspect details?

Keep details behind a link rather than dumping logs into Teams.
