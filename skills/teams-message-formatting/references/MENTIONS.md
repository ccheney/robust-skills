# Teams Mentions Reference

Mentions are not just text. Teams requires visible mention markup plus metadata. If the metadata does not exactly match the visible text, Teams renders ordinary text and notifies nobody.

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

- `entities[].text` must exactly match a substring in `text`, including any `@` prefix you choose to show.
- `mentioned.id` accepts a Teams user ID (`29:...`) from the incoming activity or roster, a Microsoft Entra Object ID, or a UPN (`ada@contoso.com`). Entra Object ID and UPN work in bot text, Adaptive Card bodies, and message extension responses, and still trigger activity feed notifications.
- Do not parse display names out of message text to build IDs; users can edit visible text.
- Bots can't mention `@everyone`, and channel/team mentions are not supported in bot messages.

## Bot Tag Mentions

Bots can mention tags in channel text messages and Adaptive Cards. The wire format is a mention entity whose `mentioned` object carries `"type": "tag"` — without it, Teams treats the mention as a user mention and it fails:

```json
{
  "type": "mention",
  "text": "<at>On-Call Team</at>",
  "mentioned": {
    "id": "base64-encoded-tag-id",
    "name": "On-Call Team",
    "type": "tag"
  }
}
```

Get the tag ID from the Microsoft Graph [List teamworkTags](https://learn.microsoft.com/en-us/graph/api/teamworktag-list?view=graph-rest-1.0) API.

Limitations:

- Only in bot-to-client text and Adaptive Card messages, and only in channels.
- Not supported in shared or private channels, in connectors, in the bot invoke flow, or in Teams operated by 21Vianet.
- Throttled: per bot per thread, at most 2 tag-mention messages per 5 seconds (5 per minute), and at most 10 tags per message.

Tag mentions can notify many people; require explicit user intent before sending one.

## Adaptive Card Mentions

Adaptive Cards can mention users in `TextBlock` and `FactSet` content. Include visible `<at>...</at>` text and root-level `msteams.entities`.

```json
{
  "type": "AdaptiveCard",
  "version": "1.5",
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

- Channel and team mentions are not supported in bot messages, card or text.
- Workflows/Incoming Webhook Adaptive Cards support user mentions (including Entra Object ID and UPN), not bot mentions.
- Mentions add metadata weight: stay under 28 KB for webhook cards and 100 KB for bot messages.

## Graph chatMessage Mentions

Graph mentions use indexed `<at id="N">Text</at>` tags in an HTML body and matching `mentions` entries.

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
- The number in `<at id="N">` must equal `mentions[N].id`, and `mentionText` must match the visible text.
- The `mentioned` object holds exactly one identity: `user` (as above), `application` (bots), `tag`, or `conversation` for a team or channel.

Team mention via Graph:

```json
{
  "body": {
    "contentType": "html",
    "content": "<div><at id=\"0\">Platform Team</at> release is out.</div>"
  },
  "mentions": [
    {
      "id": 0,
      "mentionText": "Platform Team",
      "mentioned": {
        "conversation": {
          "id": "68a3e365-f7d9-4a56-b499-24332a9cc572",
          "displayName": "Platform Team",
          "conversationIdentityType": "team"
        }
      }
    }
  ]
}
```

Use `conversationIdentityType: "channel"` with the channel thread ID to mention a channel.

## Mention Safety

| Mistake | Result | Fix |
|---------|--------|-----|
| Visible text only | No notification | Add entities/mentions metadata |
| Metadata only | No visible mention | Add `<at>...</at>` text |
| Mismatched text | Mention ignored | Keep exact text synchronized |
| Display name used as ID | Mention fails | Use Teams ID, Entra Object ID, or UPN |
| Tag entity missing `"type": "tag"` | Treated as (failing) user mention | Add the type to `mentioned` |
| Broad tag/team mention by default | Unwanted notifications | Require explicit user intent |

## Incoming Mentions In Bot Messages

Every channel or group-chat message sent to a bot normally contains an @mention of the bot. Strip the bot mention before interpreting commands:

- C#: `Activity.RemoveRecipientMention()`
- JavaScript: `TurnContext.removeMentionText(activity, activity.recipient.id)`
- Python: `TurnContext.remove_recipient_mention(turn_context.activity)`

Treat the `entities` collection as authoritative for who was mentioned; users can edit the visible text.
