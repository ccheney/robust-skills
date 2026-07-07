---
name: teams-adaptive-cards
description: Proactively apply when generating Microsoft Teams Adaptive Card JSON, Bot Framework card attachments, Teams SDK card responses, message extension cards, Microsoft Graph chatMessage Adaptive Card attachments, Incoming Webhook or Workflows webhook Adaptive Cards, notification cards, approval cards, form cards, Action.Submit, Action.Execute, Universal Actions, refresh, user-specific views, card mentions, msteams.entities, msteams.width, Teams responsive card layout, CodeBlock, Table, FactSet, ColumnSet, Input.ChoiceSet, People Picker, or debugging Teams card rendering. Use when constructing, validating, wrapping, or migrating Teams card payloads, including MessageCard-to-Adaptive-Card migrations.
---

# Teams Adaptive Cards

Adaptive Cards are the primary rich-message surface for Microsoft Teams. Always choose the transport first, because the same card JSON is wrapped differently for bots, Workflows webhooks, and Microsoft Graph — most broken Teams cards are wrapper mistakes, not card mistakes.

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
`-- Legacy connector/MessageCard payload        -> migrate to Workflows + Adaptive Card
                                                   (O365 connectors stopped working May 2026)
```

### "Which transport wrapper?"

```
Delivery path?
|-- Bot Framework / Teams SDK
|   `-- Activity `attachments[]` with contentType `application/vnd.microsoft.card.adaptive`
|-- Workflows (Power Automate) webhook
|   `-- Top-level `{ "type": "message", "attachments": [...] }`
|       (same wrapper the retired Incoming Webhook connectors used)
|-- Microsoft Graph chatMessage
|   `-- Body `<attachment id="..."></attachment>` plus matching `attachments[]`
|       with the card as a JSON *string* in attachment content
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
    |-- Need Action.Execute / refresh / Universal Actions      -> version "1.4"+, bot-backed
    |-- Need Table / CodeBlock / charts / Icon / targetWidth   -> version "1.5"
    `-- No special features                                    -> version "1.2"
```

Teams supports Adaptive Card schema v1.5 or earlier; Teams does not support v1.6 (that release was scoped to mobile SDK renderers). Newer Teams elements — `CodeBlock`, chart elements (`Chart.Donut`, `Chart.Line`, ...), `Icon`, `CompoundButton`, people picker — are declared in `"version": "1.5"` payloads and gated by host capability, not by a schema bump. Teams mobile reliably supports up to v1.2; later-version features can render incorrectly or inconsistently on mobile, so default to v1.2 and provide `fallback`/`fallbackText` when you go higher.

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

### Workflows Webhook

Office 365 connectors — including connector-based Incoming Webhooks — were disabled by Microsoft in May 2026. Post to a Workflows (Power Automate) webhook URL instead; the message wrapper is identical:

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

Workflows also accepts legacy MessageCard payloads for migration, but interactive MessageCard elements (buttons, inputs) are not supported there — convert to Adaptive Cards. Webhook cards are notification-only: use `Action.OpenUrl`; use a bot when a button must reach a backend.

### Microsoft Graph chatMessage

```json
{
  "body": {
    "contentType": "html",
    "content": "<attachment id=\"74d20c7f-34aa-4a7f-b74e-2b30004247c5\"></attachment>"
  },
  "attachments": [
    {
      "id": "74d20c7f-34aa-4a7f-b74e-2b30004247c5",
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Graph card\",\"wrap\":true}]}"
    }
  ]
}
```

Graph rules that differ from the other transports: attachment `content` is a JSON **string**, not an object; the attachment `id` (a GUID by convention) must exactly match the `<attachment id>` placeholder in `body.content`; and there is no `{ "type": "message" }` wrapper. Normal sends require delegated permissions (`ChannelMessage.Send` / `ChatMessage.Send`) — application permission exists only for migration, so do not choose Graph as an app-only notification channel.

## Layout Guidance

Use Teams-native card structure instead of Markdown tricks:

| Need | Use |
|------|-----|
| Title | `TextBlock` with `weight: "Bolder"`, `size`, optional `style: "heading"` (v1.5) |
| Key-value data | `FactSet` for compact facts; `ColumnSet` for custom layouts |
| Status callout | `Container` with subtle emphasis, icon/image, and concise text |
| Table | `Table` only when v1.5/client support is acceptable |
| Code | `CodeBlock` (v1.5; renders on Teams web/desktop only) |
| Chart | `Chart.Donut`, `Chart.Line`, `Chart.VerticalBar`, etc. (v1.5) |
| Form | `Input.*` elements plus `Action.Submit` or `Action.Execute` |
| People selection | `Input.ChoiceSet` with `choices.data` `Data.Query` people picker |
| Mention | `<at>Name</at>` in text plus root `msteams.entities` |
| Wide desktop card | Root `msteams.width: "Full"`, then test narrow clients |
| Per-width layout | `targetWidth` on elements (`veryNarrow`/`narrow`/`standard`/`wide`) |

Always set `wrap: true` on meaningful `TextBlock` content. Avoid fixed pixel thinking; Teams cards render in chats, channels, meeting side panels, mobile, and desktop.

## Actions

| Action | Use | Teams Notes |
|--------|-----|-------------|
| `Action.OpenUrl` | Open external page/deep link | Safest for webhooks and notifications |
| `Action.Submit` | Submit inputs to bot | Requires bot backend; explicitly unsupported in webhook cards; `isEnabled` unsupported in Teams |
| `Action.Execute` | Universal Actions across Teams/Outlook | v1.4+; bot must handle `adaptiveCard/action` invokes |
| `Action.ToggleVisibility` | Reveal/hide local details | Good for progressive disclosure; works without a backend |
| `Action.ShowCard` | Inline secondary card | Use sparingly; can be confusing on mobile |

Teams ignores positive/destructive action styling in Adaptive Cards. Do not rely on `style: "positive"` or `style: "destructive"` for visual meaning.

## Validate Payloads

Run the bundled linter on any card or wrapped payload (from the skill directory):

```bash
node scripts/check-teams-card.mjs path/to/payload.json                  # auto-detect target
node scripts/check-teams-card.mjs --target card path/to/card.json      # raw Adaptive Card
node scripts/check-teams-card.mjs --target bot path/to/activity.json   # bot activity/attachment
node scripts/check-teams-card.mjs --target webhook path/to/payload.json
node scripts/check-teams-card.mjs --target graph path/to/message.json
```

Output is one `ERROR:`/`WARN:`/`INFO:` line per finding with a JSONPath-style location, plus a summary line. Exit code 0 means no errors (warnings allowed), 1 means at least one error or unparseable JSON, 2 means bad CLI usage. The script catches Teams-specific issues a generic schema validator misses: wrapper mismatches, Graph placeholder/id mismatches, stringified-content problems, unsupported action assumptions, mobile version risk, missing `fallbackText`, missing `msteams.entities` for mentions, and layout hazards.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Posting raw card JSON to a webhook URL | Webhooks expect a message wrapper | Wrap in `{ "type": "message", "attachments": [...] }` |
| Reusing webhook wrapper in Graph | Graph needs body placeholder and stringified attachment content | Use Graph wrapper |
| `Action.Submit` in notification-only webhook | Unsupported; no bot receives it | Use `Action.OpenUrl` or build a bot |
| Version `1.5` by default | Mobile/client feature risk | Default to `1.2` unless a feature needs more |
| Version `1.6` | Not supported by Teams | Use `1.5` with capability-gated elements |
| Markdown table/heading/code fence in TextBlock | Unsupported Markdown subset | Use `Table`, `TextBlock` sizing, or `CodeBlock` |
| Missing `fallbackText` | Poor fallback/accessibility | Add a concise summary |
| Fixed-width multi-column layout | Breaks on mobile/side panels | Design narrow-first; use `targetWidth` |
| Mention text without `msteams.entities` | Renders as literal text, no notification | Add root metadata |
| Connector MessageCard for new work | Connectors retired May 2026 | Use Workflows or notification bot with Adaptive Cards |

## Reference Documentation

| Read | Before |
|------|--------|
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Any card work — wrappers, version policy, limits at a glance |
| [references/ELEMENTS.md](references/ELEMENTS.md) | Choosing body elements: inputs, Table, CodeBlock, charts, people picker, Media |
| [references/ACTIONS.md](references/ACTIONS.md) | Adding buttons: Submit vs Execute, msteams data behaviors, refresh/user-specific views |
| [references/SURFACES.md](references/SURFACES.md) | Picking a delivery path: bots, message extensions, Graph, webhooks |
| [references/WEBHOOKS-WORKFLOWS.md](references/WEBHOOKS-WORKFLOWS.md) | Building webhook notifications or migrating retired connectors/MessageCards |
| [references/GRAPH-ATTACHMENTS.md](references/GRAPH-ATTACHMENTS.md) | Sending cards through Microsoft Graph chatMessage |
| [references/RESPONSIVE-DESIGN.md](references/RESPONSIVE-DESIGN.md) | Designing layout: targetWidth, full width, mobile behavior, accessibility |

## Sources

- [Create and explore card types in Teams](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference) - Microsoft Teams
- [Format text in cards](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-format) - Microsoft Teams
- [Universal Actions for Adaptive Cards](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/universal-actions-for-adaptive-cards/overview) - Microsoft Teams
- [User-specific views](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/universal-actions-for-adaptive-cards/user-specific-views) - Microsoft Teams
- [Retirement of Office 365 connectors within Teams](https://devblogs.microsoft.com/microsoft365dev/retirement-of-office-365-connectors-within-microsoft-teams/) - Microsoft 365 Dev Blog
- [Send chatMessage in a channel or chat](https://learn.microsoft.com/en-us/graph/api/chatmessage-post) - Microsoft Graph
- [Adaptive Cards documentation hub](https://adaptivecards.microsoft.com/) - Microsoft
