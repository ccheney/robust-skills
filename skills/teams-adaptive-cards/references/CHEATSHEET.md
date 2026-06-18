# Teams Adaptive Cards Cheatsheet

## Payload Shapes

### Raw Card

```json
{
  "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.2",
  "fallbackText": "Short summary",
  "body": [
    { "type": "TextBlock", "text": "Hello", "wrap": true }
  ]
}
```

### Bot Activity

```json
{
  "type": "message",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": { "type": "AdaptiveCard", "version": "1.2", "body": [] }
    }
  ]
}
```

### Incoming Webhook / Workflows Webhook

```json
{
  "type": "message",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "contentUrl": null,
      "content": { "type": "AdaptiveCard", "version": "1.2", "body": [] }
    }
  ]
}
```

### Microsoft Graph chatMessage

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
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[]}"
    }
  ]
}
```

## Version Policy

| Version | Use When | Teams Risk |
|---------|----------|------------|
| `1.0` | Very old compatibility | Lacks modern accessibility/input features |
| `1.2` | Default broad Teams/mobile compatibility | Safest default |
| `1.3` | Need input `label`, associated inputs, better accessibility | Test clients |
| `1.4` | Need `Action.Execute`, refresh, authentication | Bot-backed only |
| `1.5` | Need Table, CodeBlock, tooltip, newer behavior | Verify Teams clients/mobile |

Default to `1.2` unless a feature requires a later version.

## Common Elements

| Element | Purpose | Notes |
|---------|---------|-------|
| `TextBlock` | Text, headings, short prose | Use `wrap: true` |
| `RichTextBlock` | Inline text runs with styles | More predictable than Markdown for mixed styling |
| `FactSet` | Compact key-value facts | Good for metadata |
| `Image` | Public image URL or supported data URI path | Always include `altText` |
| `ImageSet` | Multiple related images | Keep small |
| `Container` | Group content with spacing/style/selectAction | Avoid nested visual clutter |
| `ColumnSet` | Horizontal layout | Keep mobile narrow; avoid many columns |
| `Table` | Structured rows/columns | Requires newer support; consider FactSet first |
| `ActionSet` | Inline action group | Use sparingly inside body |
| `CodeBlock` | Code snippets | Requires newer support; include language |
| `Input.Text` | Text entry | Requires submit/execute action |
| `Input.ChoiceSet` | Dropdown/radio/multi-select | Use compact for long lists |
| `Input.Date` / `Input.Time` | Date/time entry | Values are local/input-specific |
| `Input.Toggle` | Boolean | Use clear title |

## Text Formatting

Adaptive Card Markdown supports only:

- `**bold**`
- `_italic_`
- `- bullets` with `\r` or `\n`
- `1. ordered` with `\r` or `\n`
- `[link](url)`

Unsupported in `TextBlock`: headings, tables, images, preformatted text, and blockquotes.

## Actions

| Action | Best Surface | Notes |
|--------|--------------|-------|
| `Action.OpenUrl` | All notification surfaces | Safest, no backend invoke |
| `Action.Submit` | Bot-backed cards | Sends input to bot; no webhook backend |
| `Action.Execute` | Universal Actions | Requires bot invoke handling |
| `Action.ToggleVisibility` | Local details | No backend call |
| `Action.ShowCard` | Small secondary input/details | Test mobile |

Teams ignores positive/destructive action styling. Do not rely on action color for meaning.

## Mentions In Cards

```json
{
  "type": "TextBlock",
  "text": "Owner: <at>Ada Lovelace</at>",
  "wrap": true
}
```

Root metadata:

```json
{
  "msteams": {
    "entities": [
      {
        "type": "mention",
        "text": "<at>Ada Lovelace</at>",
        "mentioned": { "id": "29:user-id", "name": "Ada Lovelace" }
      }
    ]
  }
}
```

## Root `msteams` Properties

| Property | Use |
|----------|-----|
| `msteams.width: "Full"` | Request full-width desktop rendering |
| `msteams.entities` | Mentions |

Full width does not remove the need to design for mobile, meeting panels, and narrow chat views.

## Validate

```bash
node skills/teams-adaptive-cards/scripts/check-teams-card.mjs --target card card.json
node skills/teams-adaptive-cards/scripts/check-teams-card.mjs --target webhook payload.json
node skills/teams-adaptive-cards/scripts/check-teams-card.mjs --target graph chat-message.json
node skills/teams-adaptive-cards/scripts/check-teams-card.mjs --target bot activity.json
```

## Required Final Checks

- Card has `type: "AdaptiveCard"`.
- Card has a version appropriate for the needed features.
- Meaningful text has `wrap: true`.
- Images have `altText`.
- Interactions have an actual backend.
- Mentions include matching metadata.
- Webhook/Graph/Bot wrapper matches the delivery path.
- Payload size is under the target transport limit.
