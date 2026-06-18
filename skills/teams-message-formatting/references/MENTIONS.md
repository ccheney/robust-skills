# Teams Mentions Reference

Mentions are not just text. Teams requires visible mention markup plus metadata. If the metadata does not exactly match, Teams renders ordinary text or does not notify the target.

## Bot User Mentions

Bot text messages use `<at>Name</at>` in `text` and a matching entity in `entities`.

```json
{
  "type": "message",
  "text": "Hey <at>Ada Lovelace</at>, please review this.",
  "entities": [
    {
      "type": "mention",
      "text": "<at>Ada Lovelace</at>",
      "mentioned": {
        "id": "29:user-id",
        "name": "Ada Lovelace"
      }
    }
  ]
}
```

Rules:

- `entities[].text` must exactly match a substring in `text`.
- Use the Teams user ID from the incoming activity, roster, or Teams context.
- Do not rely on parsing display names from message text.
- Remove the bot's own recipient mention from incoming channel/group-chat commands before command parsing.

## Bot Tag Mentions

Tag mentions are supported only in bot-to-client text and Adaptive Card messages.

Limitations:

- Not supported in shared channels.
- Not supported in private channels.
- Not supported in connectors.
- Not supported in bot invoke flow.
- Subject to per-thread throttling.

Use tag mentions carefully; they can notify many people.

## Adaptive Card Mentions

Adaptive Cards can mention users in `TextBlock` and `FactSet` content. Include visible `<at>...</at>` text and root-level `msteams.entities`.

```json
{
  "type": "AdaptiveCard",
  "version": "1.2",
  "body": [
    {
      "type": "TextBlock",
      "text": "Assigned to <at>Ada Lovelace</at>",
      "wrap": true
    }
  ],
  "msteams": {
    "entities": [
      {
        "type": "mention",
        "text": "<at>Ada Lovelace</at>",
        "mentioned": {
          "id": "29:user-id",
          "name": "Ada Lovelace"
        }
      }
    ]
  }
}
```

Notes:

- Channel and team mentions are not supported in bot Adaptive Card messages.
- Incoming Webhook Adaptive Cards support user mentions, not bot mentions.
- Message size still matters: mentions add metadata and can push webhooks over the 28 KB limit.

## Graph chatMessage Mentions

Graph mentions use indexed `<at id="N">Text</at>` tags in HTML body and matching `mentions` entries.

```json
{
  "body": {
    "contentType": "html",
    "content": "<p><at id=\"0\">Ada Lovelace</at> please review this.</p>"
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

Rules:

- `body.contentType` must be `html` when mentions are present.
- `<at id="0">...</at>` must correspond to `mentions[0].id`.
- The `mentionText` should match the visible text.
- Graph supports mention entities for users, bots, teams, channels, chats, and tags, but support varies by API path and tenant state.

## Mention Safety

| Mistake | Result | Fix |
|---------|--------|-----|
| Visible text only | No notification | Add entities/mentions metadata |
| Metadata only | No visible mention | Add `<at>...</at>` text |
| Mismatched text | Mention ignored | Keep exact text synchronized |
| Display name used as ID | Mention fails | Use stable Teams/AAD IDs |
| Broad tag/team mention by default | Unwanted notifications | Require explicit user intent |

## Incoming Mentions In Bot Messages

Every channel or group-chat message sent to a bot normally contains an @mention of the bot. Strip the bot mention before interpreting commands:

- C#: `Activity.RemoveRecipientMention()`
- JavaScript: `TurnContext.removeMentionText(activity, recipient.id)`
- Python: `TurnContext.remove_recipient_mention(turn_context.activity)`

Treat the `entities` collection as authoritative for mentioned users; users can edit visible text.
