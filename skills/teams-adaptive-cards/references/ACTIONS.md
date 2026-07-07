# Teams Adaptive Card Actions

Actions are the highest-risk part of Teams cards because support depends on transport and backend.

## Action Selection

| Need | Use |
|------|-----|
| Open a URL or deep link | `Action.OpenUrl` |
| Submit form inputs to a bot | `Action.Submit` |
| Cross-host Teams/Outlook invoke with refresh | `Action.Execute` |
| Show/hide local details | `Action.ToggleVisibility` |
| Reveal a small inline card | `Action.ShowCard` |

## Transport Compatibility

| Transport | `OpenUrl` | `Submit` | `Execute` | Notes |
|-----------|-----------|----------|-----------|-------|
| Bot Framework / Teams SDK | Yes | Yes | Yes, with Universal Actions handling | Best for interaction |
| Message extension | Yes | Depends on extension/action flow | Yes for supported Universal Actions scenarios | Match extension type |
| Workflows webhook | Yes | No — explicitly unsupported | Docs list it as allowed, but no bot receives the invoke; treat as unusable | Use notification-only cards |
| Graph chatMessage attachment | Renders card attachment | Do not assume bot invoke | Do not assume bot invoke | Graph sends a message, not a bot backend |
| Outgoing Webhook response | `OpenUrl` only | No | No | Teams outgoing webhooks restrict card actions |

## Action.OpenUrl

```json
{
  "type": "Action.OpenUrl",
  "title": "View incident",
  "url": "https://example.com/incidents/123"
}
```

Best practices:

- Use HTTPS URLs.
- For Teams deep links, generate valid Teams deep-link URLs.
- Keep titles short.
- Do not use URL actions for destructive operations without confirmation on the destination page.

## Action.Submit

Submits input values and optional hidden `data` to the bot.

```json
{
  "type": "Action.Submit",
  "title": "Approve",
  "data": {
    "action": "approve",
    "requestId": "REQ-123"
  }
}
```

Teams behavior:

- The bot does not receive input changes until the user selects a submit button.
- The bot has a short response window for invoke handling.
- Positive/destructive action styling is not supported in Teams.
- `isEnabled` for `Action.Submit` is not supported in Teams.

### Teams `msteams` Submit Behaviors

Teams supports Bot Framework action behavior through `data.msteams`.

#### messageBack

```json
{
  "type": "Action.Submit",
  "title": "Comment",
  "data": {
    "msteams": {
      "type": "messageBack",
      "displayText": "Added a comment",
      "text": "comment",
      "value": "{\"requestId\":\"REQ-123\"}"
    }
  }
}
```

Use when the bot should receive structured action data and optionally show user-visible display text.

#### imBack

```json
{
  "type": "Action.Submit",
  "title": "Run status",
  "data": {
    "msteams": {
      "type": "imBack",
      "value": "status REQ-123"
    }
  }
}
```

Use sparingly; it echoes text back into chat.

#### signin

```json
{
  "type": "Action.Submit",
  "title": "Sign in",
  "data": {
    "msteams": {
      "type": "signin",
      "value": "https://example.com/auth/start"
    }
  }
}
```

Prefer Teams SSO/OAuth patterns when building production apps.

#### task/fetch or invoke

```json
{
  "type": "Action.Submit",
  "title": "Open dialog",
  "data": {
    "msteams": {
      "type": "task/fetch",
      "data": { "requestId": "REQ-123" }
    }
  }
}
```

Use for dialog/task-module flows when the bot handles invoke activities.

## Action.Execute

Universal Actions use `Action.Execute` and send an `adaptiveCard/action` invoke to the bot. They are intended for cross-host scenarios such as Teams and Outlook.

```json
{
  "type": "Action.Execute",
  "title": "Approve",
  "verb": "approveRequest",
  "data": {
    "requestId": "REQ-123"
  }
}
```

Requirements:

- Use schema version `1.4` or newer.
- Implement bot invoke handling for `adaptiveCard/action`.
- Return updated cards where appropriate.
- Include fallback behavior if older clients may see the card.
- For Outlook actionable messages, the card also needs the registered `originator` GUID; Teams-only bot cards do not.

The bot answers the invoke with a card or message response:

```json
{
  "statusCode": 200,
  "type": "application/vnd.microsoft.card.adaptive",
  "value": { "type": "AdaptiveCard", "version": "1.4", "body": [] }
}
```

## Refresh And User-Specific Views

Refresh lets a card update for specific users, so approvers can see buttons while other viewers see read-only state.

```json
{
  "refresh": {
    "action": {
      "type": "Action.Execute",
      "verb": "refresh",
      "data": { "requestId": "REQ-123" }
    },
    "userIds": [
      "8:orgid:00000000-0000-0000-0000-000000000000"
    ]
  }
}
```

Rules (verified against Teams user-specific views docs):

- `userIds` entries are Teams user MRIs (for example `8:orgid:<Entra object ID>`).
- Maximum 60 users can receive a user-specific view per card. For larger groups, rotate IDs in and out of `userIds` (for example, drop the earliest responder when the 61st responds) and rely on manual refresh for the rest.
- If `userIds` is omitted, Teams auto-triggers refresh for everyone only when the conversation has 60 or fewer members; beyond that, users must pick "Refresh" from the message options menu.
- Automatic refresh triggers only if the card from the last invoke is older than about a minute.
- Teams caches up to 50 user-specific cards per user; older cards are evicted.
- Refresh invokes the bot; no bot means no refresh.
- Keep refreshed cards consistent with the action result to avoid stale decisions; update the base card with a message update when the shared state changes.

## Action.ToggleVisibility

```json
{
  "type": "Action.ToggleVisibility",
  "title": "Show details",
  "targetElements": ["details"]
}
```

Target elements need `id` values:

```json
{
  "type": "Container",
  "id": "details",
  "isVisible": false,
  "items": [
    { "type": "TextBlock", "text": "More details", "wrap": true }
  ]
}
```

Do not hide required inputs behind toggle actions unless the validation behavior is clear and tested.

## Action.ShowCard

Use for small inline secondary forms or details. Avoid deeply nested ShowCards. Inputs in ShowCards have parent/child submit behavior that can surprise users and backend code.

## Confirmation And Destructive Actions

Teams has no built-in confirm prompt or destructive styling for card actions. For destructive actions:

- Make the button text unambiguous ("Delete pipeline", not "OK").
- Make the backend idempotent.
- Include an operation ID in `data`.
- Return an updated card that clearly shows final state.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `Action.Submit` in webhook card | Explicitly unsupported; no bot receives it | Use `OpenUrl` or a bot |
| `Action.Execute` without bot invoke handler | Button fails | Implement Universal Actions handling |
| Relying on `style: "destructive"` | Teams does not support action styling | Use clear text and idempotent backend |
| Missing hidden IDs in `data` | Backend cannot correlate action | Include stable IDs |
| Updating state only in chat text | Card remains stale | Update/replace card or use refresh |
| More than 60 `userIds` in refresh | Extra IDs beyond the limit get no user-specific view | Rotate the list; provide manual refresh |
