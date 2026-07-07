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

### Workflows Webhook

Same wrapper the retired Incoming Webhook connectors used (O365 connectors stopped working May 2026 — see [WEBHOOKS-WORKFLOWS.md](WEBHOOKS-WORKFLOWS.md)):

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

Card content is a JSON **string**; attachment `id` (GUID by convention) must match the body placeholder:

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
      "content": "{\"type\":\"AdaptiveCard\",\"version\":\"1.2\",\"body\":[]}"
    }
  ]
}
```

## Version Policy

| Version | Use When | Teams Risk |
|---------|----------|------------|
| `1.2` | Default broad Teams/mobile compatibility | Safest default; Teams mobile reliably supports up to 1.2 |
| `1.3` | Need input `label`, `isRequired`/`errorMessage` | Test clients |
| `1.4` | Need `Action.Execute`, `refresh`, `authentication` | Bot-backed only |
| `1.5` | Need Table, CodeBlock, charts, Icon, `targetWidth`, dynamic typeahead | Verify Teams clients/mobile; add `fallback` |
| `1.6` | Never for Teams | Not supported by Teams (mobile SDK-only release) |

Default to `1.2` unless a feature requires a later version. Newer Teams elements (charts, Icon, CompoundButton, CodeBlock) ship as `"version": "1.5"` payloads gated by host capability.

## Common Elements

| Element | Purpose | Notes |
|---------|---------|-------|
| `TextBlock` | Text, headings, short prose | Use `wrap: true` |
| `RichTextBlock` | Inline text runs with styles | More predictable than Markdown for mixed styling |
| `FactSet` | Compact key-value facts | Markdown works in title/value |
| `Image` | Public image URL | Always include `altText`; max 1024x1024, 1 MB; no animated GIF/SVG |
| `ImageSet` | Multiple related images | Keep small |
| `Container` | Group content with spacing/style/selectAction | Avoid nested visual clutter |
| `ColumnSet` | Horizontal layout | Keep mobile narrow; max ~3 columns |
| `Table` | Structured rows/columns | v1.5; consider FactSet first |
| `ActionSet` | Inline action group | Use sparingly inside body |
| `CodeBlock` | Code snippets | v1.5; Teams web/desktop only; include `language` |
| `Chart.*` | Donut, pie, gauge, bar, line charts | v1.5; provide `fallback` |
| `Icon` | Fluent icon by name | v1.5 |
| `CompoundButton` | Icon + title + description button | v1.5 |
| `Input.Text` | Text entry | Requires submit/execute action |
| `Input.ChoiceSet` | Dropdown/radio/multi-select/people picker | `choices.data` `Data.Query` for people picker |
| `Input.Date` / `Input.Time` | Date/time entry | Values are local/input-specific |
| `Input.Toggle` | Boolean | Use clear title |

## Text Formatting

Adaptive Card Markdown supports only:

- `**bold**`
- `_italic_`
- `- bullets` with `\r` or `\n`
- `1. ordered` with `\r` or `\n`
- `[link](url)`

Unsupported in `TextBlock`: headings, tables, images, preformatted text, blockquotes, and HTML.

## Actions

| Action | Best Surface | Notes |
|--------|--------------|-------|
| `Action.OpenUrl` | All notification surfaces | Safest, no backend invoke |
| `Action.Submit` | Bot-backed cards | Explicitly unsupported in webhook cards; `isEnabled` unsupported in Teams |
| `Action.Execute` | Universal Actions (v1.4+) | Requires bot `adaptiveCard/action` invoke handling |
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

Root metadata (`mentioned.id` accepts the Teams user MRI, Entra object ID, or UPN):

```json
{
  "msteams": {
    "entities": [
      {
        "type": "mention",
        "text": "<at>Ada Lovelace</at>",
        "mentioned": { "id": "ada.lovelace@contoso.com", "name": "Ada Lovelace" }
      }
    ]
  }
}
```

Mentions work in `TextBlock` and `FactSet` title/value. Channel and team mentions are not supported inside bot Adaptive Cards; webhook cards support user mentions only.

## Root `msteams` Properties

| Property | Use |
|----------|-----|
| `msteams.width: "Full"` | Request full-width desktop rendering |
| `msteams.entities` | Mentions |

Full width does not remove the need to design for mobile, meeting panels, and narrow chat views. For per-width layouts, use element-level `targetWidth` (see [RESPONSIVE-DESIGN.md](RESPONSIVE-DESIGN.md)).

## Limits

| Limit | Value |
|-------|-------|
| Webhook message size | 28 KB |
| Bot message size | ~100 KB |
| `refresh.userIds` (user-specific views) | 60 users |
| Cards per carousel/list collection | 10 |
| Inline images | 1024x1024 px, 1 MB, PNG/JPEG/GIF (no animation) |

## Validate

Run from the skill directory; exit 0 = clean/warnings only, 1 = errors, 2 = usage error:

```bash
node scripts/check-teams-card.mjs --target card card.json
node scripts/check-teams-card.mjs --target webhook payload.json
node scripts/check-teams-card.mjs --target graph chat-message.json
node scripts/check-teams-card.mjs --target bot activity.json
```

## Required Final Checks

- Card has `type: "AdaptiveCard"`.
- Card version matches the needed features (never above 1.5).
- Meaningful text has `wrap: true`.
- Images have `altText`.
- Interactions have an actual backend.
- Mentions include matching metadata.
- Webhook/Graph/Bot wrapper matches the delivery path.
- Payload size is under the target transport limit.
