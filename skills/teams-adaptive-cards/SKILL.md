---
name: teams-adaptive-cards
description: Proactively apply when generating Microsoft Teams Adaptive Card JSON, Bot Framework card attachments, Teams SDK card responses, message extension cards, Microsoft Graph chatMessage Adaptive Card attachments, Incoming Webhook or Workflows webhook Adaptive Cards, notification cards, approval cards, form cards, Action.Submit, Action.Execute, Universal Actions, refresh, user-specific views, card mentions, msteams.entities, msteams.width, Teams responsive card layout, CodeBlock, Table, FactSet, ColumnSet, Input.ChoiceSet, People Picker, or debugging Teams card rendering. Use when constructing, validating, wrapping, or migrating Teams card payloads, including MessageCard-to-Adaptive-Card migrations.
---

# Teams Adaptive Cards

Adaptive Cards are the primary rich-message surface for Microsoft Teams. Always choose the Teams transport first because the same card JSON is wrapped differently for bots, webhooks, Workflows, and Microsoft Graph.

## Quick Decision Trees

### "Should I use a card?"

```
Response type?
|-- Short conversational reply, <3 lines        -> text only; use $teams-message-formatting
|-- Status notification with facts/actions      -> Adaptive Card
|-- Approval, form, or data collection          -> Adaptive Card through bot/Universal Actions
|-- Search result or message extension response -> Adaptive Card
|-- Service alert to a channel                  -> Workflows webhook or notification bot card
|-- Delegated Graph message with attachment     -> Graph chatMessage card wrapper
`-- Legacy connector payload                    -> migrate MessageCard to Adaptive Card if possible
```

### "Which transport wrapper?"

```
Delivery path?
|-- Bot Framework / Teams SDK
|   `-- Activity `attachments[]` with contentType `application/vnd.microsoft.card.adaptive`
|-- Incoming Webhook / Workflows webhook
|   `-- Top-level `{ "type": "message", "attachments": [...] }`
|-- Microsoft Graph chatMessage
|   `-- Body `<attachment id="..."></attachment>` plus matching `attachments[]`
|-- Message extension result
|   `-- Attachment with Adaptive Card content and preview as required by extension type
`-- Outlook + Teams universal scenario
    `-- Use Universal Actions (`Action.Execute`) with bot backend
```

### "Which card version?"

```
Need maximum Teams mobile compatibility?
|-- Yes -> use version "1.2"
`-- No
    |-- Need Action.Execute / refresh / universal actions -> version "1.4" or newer, bot-backed
    |-- Need Table / CodeBlock / tooltip / isEnabled      -> version "1.5", verify Teams clients
    `-- No special features                               -> version "1.2"
```

Teams supports Adaptive Card v1.5-or-earlier on current platform docs, but Teams mobile support is still called out as safest at v1.2. Default to v1.2 unless the requested feature requires a later version.

## Minimal Card

```json
{
  "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.2",
  "fallbackText": "Deployment succeeded for API.",
  "body": [
    {
      "type": "TextBlock",
      "text": "Deployment succeeded",
      "weight": "Bolder",
      "size": "Medium",
      "wrap": true
    },
    {
      "type": "FactSet",
      "facts": [
        { "title": "Service", "value": "API" },
        { "title": "Duration", "value": "4 min 12 sec" }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View release",
      "url": "https://example.com/releases/42"
    }
  ]
}
```

## Transport Wrappers

### Bot Framework / Teams SDK

```json
{
  "type": "message",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": [
          { "type": "TextBlock", "text": "Hello from a bot", "wrap": true }
        ]
      }
    }
  ]
}
```

### Incoming Webhook / Workflows

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
        "body": [
          { "type": "TextBlock", "text": "Webhook alert", "wrap": true }
        ]
      }
    }
  ]
}
```

Workflows can post Adaptive Cards and MessageCards, but MessageCard button rendering is not supported in the replacement workflow path. Use Adaptive Card `Action.OpenUrl` for notification-only webhooks; use a bot when server-side interaction is required.

### Microsoft Graph chatMessage

```json
{
  "body": {
    "contentType": "html",
    "content": "<attachment id=\"status-card\"></attachment>"
  },
  "attachments": [
    {
      "id": "status-card",
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Graph card\",\"wrap\":true}]}"
    }
  ]
}
```

Graph attachment `id` must match the body placeholder. Graph `chatMessage` sends are delegated for normal use; do not choose Graph as the default app-only notification channel.

## Layout Guidance

Use Teams-native card structure instead of Markdown tricks:

| Need | Use |
|------|-----|
| Title | `TextBlock` with `weight: "Bolder"`, `size`, optional `style: "heading"` |
| Key-value data | `FactSet` for compact facts; `ColumnSet` for custom layouts |
| Status callout | `Container` with subtle emphasis, icon/image, and concise text |
| Table | `Table` only when v1.5/client support is acceptable |
| Code | `CodeBlock` only when v1.5/client support is acceptable |
| Form | `Input.*` elements plus `Action.Submit` or `Action.Execute` |
| Mention | `<at>Name</at>` in text plus root `msteams.entities` |
| Wide desktop card | Root `msteams.width: "Full"`, then test narrow clients |

Always set `wrap: true` on meaningful `TextBlock` content. Avoid fixed pixel thinking; Teams cards render in chats, channels, meeting side panels, mobile, and desktop.

## Actions

| Action | Use | Teams Notes |
|--------|-----|-------------|
| `Action.OpenUrl` | Open external page/deep link | Safest for webhooks and notifications |
| `Action.Submit` | Submit inputs to bot | Requires bot/backend; `isEnabled` unsupported in Teams for Submit |
| `Action.Execute` | Universal Actions across Teams/Outlook | Bot-backed; requires newer schema and invoke handling |
| `Action.ToggleVisibility` | Reveal/hide local details | Good for progressive disclosure |
| `Action.ShowCard` | Inline secondary card | Use sparingly; can be confusing on mobile |

Teams does not support positive/destructive action styling in Adaptive Cards. Do not rely on `style: "positive"` or `style: "destructive"` for visual meaning.

## Validate Payloads

Run the bundled linter for local JSON payloads:

```bash
node skills/teams-adaptive-cards/scripts/check-teams-card.mjs --target webhook path/to/payload.json
node skills/teams-adaptive-cards/scripts/check-teams-card.mjs --target graph path/to/chat-message.json
node skills/teams-adaptive-cards/scripts/check-teams-card.mjs --target bot path/to/activity.json
node skills/teams-adaptive-cards/scripts/check-teams-card.mjs --target card path/to/card.json
```

The script catches Teams-specific issues that a generic Adaptive Card schema validator can miss: wrapper mismatches, Graph attachment placeholders, unsupported action assumptions, mobile version risk, missing fallback text, missing `msteams.entities`, and common layout hazards.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Posting raw card JSON to webhook | Webhooks expect message wrapper | Wrap in `{ "type": "message", "attachments": [...] }` |
| Reusing webhook wrapper in Graph | Graph needs body placeholder and stringified attachment content | Use Graph wrapper |
| `Action.Submit` in notification-only webhook | No bot receives the invoke | Use `Action.OpenUrl` or build a bot |
| Version `1.5` by default | Mobile/client feature risk | Default to `1.2` unless needed |
| Markdown table in TextBlock | Unsupported | Use `Table` or facts |
| Missing `fallbackText` | Poor fallback/accessibility | Add concise fallback |
| Fixed-width multi-column layout | Breaks on mobile/side panels | Design narrow-first, use fewer columns |
| Mention text without `msteams.entities` | No real mention | Add root metadata |
| Connector MessageCard for new work | Connectors are legacy/retired path | Use Workflows or notification bot |

## Reference Documentation

| File | Purpose |
|------|---------|
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Quick reference: wrappers, versions, actions, limits |
| [references/ELEMENTS.md](references/ELEMENTS.md) | Adaptive Card elements, inputs, Teams notes |
| [references/ACTIONS.md](references/ACTIONS.md) | Action.Submit, Action.Execute, Universal Actions, Teams-specific behavior |
| [references/SURFACES.md](references/SURFACES.md) | Bots, message extensions, Graph, webhooks, Workflows, connectors |
| [references/WEBHOOKS-WORKFLOWS.md](references/WEBHOOKS-WORKFLOWS.md) | Incoming Webhook, Workflows, connector retirement/migration |
| [references/GRAPH-ATTACHMENTS.md](references/GRAPH-ATTACHMENTS.md) | Graph chatMessage Adaptive Card attachments |
| [references/RESPONSIVE-DESIGN.md](references/RESPONSIVE-DESIGN.md) | Teams card design, mobile/desktop behavior, width and layout |

## Sources

- [Create and explore card types in Teams](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference) - Microsoft Teams
- [Format text in cards](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-format) - Microsoft Teams
- [Add card actions in a bot](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-actions) - Microsoft Teams
- [Universal Actions for Adaptive Cards](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/universal-actions-for-adaptive-cards/overview) - Microsoft Teams
- [Create an Incoming Webhook](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook) - Microsoft Teams
- [Send chatMessage in a channel or chat](https://learn.microsoft.com/en-us/graph/api/chatmessage-post) - Microsoft Graph
- [Adaptive Card schema explorer](https://learn.microsoft.com/en-us/adaptive-cards/schema-explorer/adaptive-card) - Microsoft
