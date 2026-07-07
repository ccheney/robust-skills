# Teams Card Surfaces

The same Adaptive Card content appears in different envelopes depending on where it is sent. Choose the surface before writing the final payload.

## Surface Matrix

| Surface | Supports Adaptive Cards | Wrapper | Interactive Backend |
|---------|-------------------------|---------|---------------------|
| Bot Framework / Teams SDK | Yes | Activity attachment | Bot |
| Message extensions | Yes | Extension result attachment | Bot/message extension |
| Workflows webhook | Yes | Top-level message + attachments | Flow actions, not bot card invoke |
| Microsoft Graph chatMessage | Yes as attachment | Body placeholder + attachments | Not a bot invoke path |
| Incoming Webhook (O365 connector) | Retired May 2026 | — | Migrate to Workflows |
| Connectors / MessageCard | Retired May 2026 | — | Migrate to Workflows or bot |
| Tabs | No direct Adaptive Card surface | Use app UI | App frontend |

## Bots

Bot messages are the most capable Teams Adaptive Card path.

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
          { "type": "TextBlock", "text": "Bot card", "wrap": true }
        ]
      }
    }
  ]
}
```

Use bots for:

- Proactive notifications with app identity.
- Forms and approvals using `Action.Submit`.
- Universal Actions with `Action.Execute`.
- User-specific views and refresh.
- SSO-backed cards.
- People picker and dynamic typeahead inputs.

Bot constraints:

- The app must be installed where the bot sends proactive messages.
- Channel/group-chat bots often need to be @mentioned unless RSC permissions are granted.
- Large teams and welcome/proactive messages require anti-spam restraint.
- Bot messages allow up to ~100 KB, larger than webhook limits, but still design compactly.

## Message Extensions

Message extensions can return Adaptive Cards for search results, link unfurling, and action commands.

Use this path when:

- The user explicitly invokes an app command.
- A link should unfurl into a rich preview.
- A compose extension needs selectable results.

Notes:

- Search/link-unfurl cards may have preview card requirements.
- Universal Actions and refresh are supported for specific message-extension scenarios.
- Keep cards self-contained; the user may insert or share them into a conversation.

## Workflows Webhook

Workflows in Teams are powered by Power Automate. A flow created from the "When a Teams webhook request is received" template exposes a URL; POST the message wrapper to it and the flow posts the Adaptive Card into the channel or chat.

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
          { "type": "TextBlock", "text": "Webhook card", "wrap": true }
        ]
      }
    }
  ]
}
```

Use for notification-only cards from external systems.

Constraints:

- Message size limit is 28 KB.
- Rate limit is about four requests per second; use retry/backoff.
- Use `Action.OpenUrl` for actions; `Action.Submit` is unsupported and `Action.Execute` has no bot to reach.
- Messages post under the fixed "Flow bot" identity; no custom icon/name.
- Workflows are owned by users, not the team/channel; assign co-owners for continuity.
- Private/shared channels are supported since April 2026; verify posting mode per channel type.

See [WEBHOOKS-WORKFLOWS.md](WEBHOOKS-WORKFLOWS.md) for the connector retirement timeline and MessageCard migration.

## Microsoft Graph chatMessage

Graph can send a chatMessage with an Adaptive Card attachment:

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

Use Graph when the requirement is truly delegated user-send into existing chats/channels.

Do not use Graph as a shortcut for an app/bot notification service:

- Normal send permissions are delegated (`ChannelMessage.Send` / `ChatMessage.Send`).
- Application permission (`Teamwork.Migrate.All`) is migration-only.
- Graph messages are subject to Teams usage policy; do not send log streams.

See [GRAPH-ATTACHMENTS.md](GRAPH-ATTACHMENTS.md) for the full wrapper rules.

## Connectors And MessageCard (Retired)

Office 365 connectors, connector cards, and connector-based Incoming Webhooks stopped working in May 2026. If you encounter a MessageCard payload or a `webhook.office.com` connector URL:

- Recreate the endpoint as a Workflows webhook and update the sending system's URL.
- Convert MessageCard `sections[].facts` to `FactSet`, `potentialAction.OpenUri` to `Action.OpenUrl`.
- Replace `HttpPOST`/`ActionCard` interactions with bot-backed Adaptive Card actions or a web destination.
- Workflows accepts MessageCard payloads for migration, but interactive MessageCard elements do not work — convert to Adaptive Cards.

## Outgoing Webhooks

Outgoing webhooks receive @mentioned messages and synchronously return a response. Adaptive Card responses can be sent, but card actions are restricted to `openUrl`.

Use outgoing webhooks only for narrow request/response integrations. For richer workflows, use a bot.

## Surface Selection Heuristics

| Scenario | Preferred Surface |
|----------|-------------------|
| Product alert to a channel | Notification bot or Workflows webhook |
| Approval with Approve/Reject buttons | Bot with `Action.Execute` or `Action.Submit` |
| User-delegated manual message | Graph chatMessage |
| Link preview | Message extension link unfurl |
| Search result insertion | Message extension search command |
| Legacy connector/MessageCard migration | Workflows webhook + Adaptive Card |
| External system without Teams app | Workflows webhook |
