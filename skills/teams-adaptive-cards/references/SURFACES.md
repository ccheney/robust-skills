# Teams Card Surfaces

The same Adaptive Card content appears in different envelopes depending on where it is sent. Choose the surface before writing the final payload.

## Surface Matrix

| Surface | Supports Adaptive Cards | Wrapper | Interactive Backend |
|---------|-------------------------|---------|---------------------|
| Bot Framework / Teams SDK | Yes | Activity attachment | Bot |
| Message extensions | Yes | Extension result attachment | Bot/message extension |
| Incoming Webhook | Yes for card wrapper | Top-level message + attachments | No bot invoke |
| Workflows webhook | Yes when flow posts Adaptive Card | Usually message wrapper or flow-specific body | Flow actions, not bot card invoke |
| Microsoft Graph chatMessage | Yes as attachment | Body placeholder + attachments | Not a bot invoke path |
| Connectors | Connector cards/MessageCard legacy | MessageCard | Legacy actionable message path |
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

Bot constraints:

- The app must be installed where the bot sends proactive messages.
- Channel/group-chat bots often need to be @mentioned unless RSC permissions are granted.
- Large teams and welcome/proactive messages require anti-spam restraint.
- Message size can be larger than webhook limits, but still design compactly.

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

## Incoming Webhook

Incoming webhook card payloads use the message attachment wrapper:

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
- Use `Action.OpenUrl` for actions.
- Do not rely on `Action.Submit` or `Action.Execute` without a bot.
- Microsoft has moved the strategic path to Workflows/Power Automate and notification bots.

## Workflows

Workflows in Teams are powered by Power Automate. They can receive webhook requests and then post messages or Adaptive Cards to Teams channels/chats.

Use Workflows when:

- The integration is a simple external webhook notification.
- Users should configure the flow in Teams.
- The flow needs to transform incoming data before posting.
- No custom Teams bot is warranted.

Limitations:

- Workflows are owned by users, not the team/channel; assign co-owners for continuity.
- Private-channel flow-bot support can be limited; posting on behalf of a user may be used.
- MessageCard button rendering is not supported in the Workflows replacement path.
- For robust product integrations, consider a notification bot.

## Microsoft Graph chatMessage

Graph can send a chatMessage with an Adaptive Card attachment:

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
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[{\"type\":\"TextBlock\",\"text\":\"Graph card\",\"wrap\":true}]}"
    }
  ]
}
```

Use Graph when the requirement is truly delegated user-send into existing chats/channels.

Do not use Graph as a shortcut for an app/bot notification service:

- Normal send permissions are delegated (`ChannelMessage.Send` / `ChatMessage.Send`).
- Application permission is migration-only.
- Graph messages are subject to Teams usage policy; do not send log streams.

## Connectors And MessageCard

Connector cards/MessageCards are legacy. Maintain existing payloads only when required.

Migration guidance:

- Convert MessageCard `sections[].facts` to `FactSet`.
- Convert `potentialAction.OpenUri` to `Action.OpenUrl`.
- Replace `HttpPOST`/`ActionCard` interactions with bot-backed Adaptive Card actions or a web destination.
- Move external incoming webhooks to Workflows or notification bots.

## Outgoing Webhooks

Outgoing webhooks receive @mentioned messages and synchronously return a response. Adaptive Card responses can be sent, but card actions are restricted to `openURL`.

Use outgoing webhooks only for narrow request/response integrations. For richer workflows, use a bot.

## Surface Selection Heuristics

| Scenario | Preferred Surface |
|----------|-------------------|
| Product alert to a channel | Notification bot or Workflows webhook |
| Approval with Approve/Reject buttons | Bot with `Action.Execute` or `Action.Submit` |
| User-delegated manual message | Graph chatMessage |
| Link preview | Message extension link unfurl |
| Search result insertion | Message extension search command |
| Legacy connector migration | Workflows or bot Adaptive Card |
| External system without Teams app | Workflows webhook |
