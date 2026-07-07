# Webhooks, Workflows, And Connector Migration

Office 365 connectors — including the classic connector-based Incoming Webhooks — no longer work in Teams. Microsoft disabled them in the May 18–22, 2026 rollout. For webhook-style notifications, use a Workflows (Power Automate) webhook or a notification bot. Any remaining connector/MessageCard payload is a migration task, not a maintenance path.

## Connector Retirement Timeline

| Date | Event |
|------|-------|
| August 2024 | New Office 365 connector creation blocked in Teams |
| January 31, 2025 | Existing connector webhook URLs had to be reissued to keep posting |
| February 2026 | Workflows gained MessageCard payload support to ease migration; deadline extended to April 30, 2026 |
| April 2026 | Private/shared channel support for Workflows webhooks rolled out |
| May 18–22, 2026 | Final rollout: Office 365 connectors disabled; connector webhooks stop working |

Migration driver: Microsoft's Secure Future Initiative. The replacement is Workflows (Power Automate) webhooks, or a Teams notification bot when you need app identity or interactive actions.

## Workflows Webhook Adaptive Card Payload

Create a flow from the "When a Teams webhook request is received" template (or the Workflows app in Teams). POST the same message wrapper the old Incoming Webhooks used — the top-level request body is not a raw Adaptive Card:

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
- `content` is the Adaptive Card object (not stringified — that is a Graph-only rule).

## Webhook Limits And Behavior

- Message size limit: 28 KB (bot messages allow up to ~100 KB; design compactly either way).
- Roughly four requests per second before throttling; implement retry with exponential backoff.
- Messages post under the Workflows "Flow bot" identity; custom bot icon/name is not available.
- Webhook cards are for notifications, not multi-step interactions.
- Use public HTTPS URLs for images and links.
- User mentions work in webhook cards (Entra object ID or UPN in `msteams.entities`); bot mentions do not.

## When To Use Workflows vs A Bot

Use Workflows when:

- The integration is a simple external webhook notification.
- Users should configure the flow themselves in Teams.
- Power Automate should transform incoming data before posting.
- No custom Teams app/bot deployment is warranted.

Operational constraints:

- Workflows are owned by users, not a team/channel object; add co-owners to avoid orphaned flows when someone leaves.
- Private and shared channels are supported (since April 2026), but verify the flow-bot posting mode for the channel type.
- Posting on behalf of a user can be part of the workflow behavior.

Use a notification bot instead when you need app identity, rate control, interactive actions, or product-grade lifecycle management.

## MessageCard To Adaptive Card Mapping

Workflows accepts legacy MessageCard payloads for migration, but interactive MessageCard elements (`HttpPOST` buttons, `ActionCard` inputs) are not supported there. Convert:

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
| `potentialAction` `OpenUri` | `Action.OpenUrl` |
| `HttpPOST` | Bot-backed `Action.Submit` or `Action.Execute` |
| `ActionCard` inputs | Adaptive Card `Input.*` elements plus a bot |

## Webhook Action Guidance

Use:

- `Action.OpenUrl`
- `Action.ToggleVisibility` for local details

Avoid:

- `Action.Submit` (explicitly unsupported in webhook cards)
- `Action.Execute` (Teams docs list it as allowed, but there is no bot to receive the invoke on a plain notification webhook — treat it as unusable unless a bot backs the card)
- Authentication/SSO flows
- Multi-step approvals that require server state changes

If a button must change server state, route the user to a secure web page or build a bot.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Posts stopped after May 2026 | Connector-based webhook retired | Recreate as Workflows webhook; update the URL in the sender |
| HTTP 400, summary/text required | Posted raw card or MessageCard mismatch | Use the message attachment wrapper |
| Card renders but button does nothing useful | Submit/Execute has no backend | Use OpenUrl or a bot |
| Card too large | Over 28 KB | Shorten text, remove large base64/images, link out |
| Bursty alerts fail | Throttling | Backoff and aggregate |
| Mentions render as literal text | Missing `msteams.entities` | Add mention metadata |
| MessageCard buttons missing in Workflows | Interactive MessageCard elements unsupported | Convert to Adaptive Card `Action.OpenUrl` or a bot |
| Message posts as "Flow bot" | Workflows identity is fixed | Expected; use a bot for custom identity |

## Notification Design

Webhook cards should answer:

1. What happened?
2. What is the current state?
3. Who/what is affected?
4. What should the recipient do next?
5. Where can they inspect details?

Keep details behind a link rather than dumping logs into Teams.
