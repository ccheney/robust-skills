# Responsive Teams Adaptive Card Design

Teams cards render in desktop chats, channels, mobile clients, meeting side panels, and browser clients. Design narrow-first.

## Principles

1. Put the essential message in the first two blocks.
2. Use compact facts before complex grids.
3. Prefer vertical stacking over many columns.
4. Make actions short, explicit, and few.
5. Test any full-width or v1.5 card in narrow surfaces.

## Width

Teams supports a root `msteams.width` hint:

```json
{
  "type": "AdaptiveCard",
  "version": "1.2",
  "msteams": {
    "width": "Full"
  },
  "body": []
}
```

Use full width for dashboards, tables, or dense operational cards. Do not use it to compensate for overcrowded design. Full-width cards still appear in narrow contexts.

## Text

Rules:

- Set `wrap: true` on important `TextBlock` elements.
- Split long prose into multiple `TextBlock` elements.
- Use `isSubtle: true` for metadata, not tiny text.
- Avoid long unbroken strings; URLs should be links with readable labels.
- Use `fallbackText` as a concise summary.

Heading pattern:

```json
{
  "type": "TextBlock",
  "text": "Incident escalated",
  "weight": "Bolder",
  "size": "Medium",
  "wrap": true,
  "style": "heading"
}
```

If targeting v1.2, omit `style: "heading"` and rely on `weight`/`size`.

## Facts And Metadata

Use `FactSet` for compact facts:

```json
{
  "type": "FactSet",
  "facts": [
    { "title": "Severity", "value": "High" },
    { "title": "Owner", "value": "<at>Ada Lovelace</at>" }
  ]
}
```

Use repeated containers when values are long or need status coloring.

## Columns

Safe column patterns:

- Icon/image `auto` column + text `stretch` column.
- Label `auto` column + value `stretch` column.
- Two equal columns for short comparable facts.

Avoid:

- More than three columns.
- Fixed pixel widths.
- Long text in narrow columns.
- Tables made from nested ColumnSets.

## Tables

Use `Table` only when:

- The target client/version supports it.
- Rows and columns are genuinely tabular.
- The card is likely to have enough width.
- A fallback summary is provided.

For mobile, consider replacing tables with:

- `FactSet`
- Repeated `Container` rows
- Link to a full report

## Images

Use images that carry information:

- Status icons.
- Small logos where context matters.
- Charts/screenshots that are readable at card size.

Always include `altText`. Avoid decorative hero images in operational cards.

## Actions

Action layout is constrained. Keep actions short:

| Bad | Better |
|-----|--------|
| `Click here to open the full deployment dashboard` | `Open dashboard` |
| `Approve this request and notify requester` | `Approve` |
| `Reject this request because the evidence is insufficient` | `Reject` |

Use no more than three primary actions in most cards. Move secondary actions behind a link or detail view.

## Accessibility

- Use `label` on inputs for v1.3+ cards.
- For v1.2, place a clear `TextBlock` immediately before each input.
- Do not encode state only through color.
- Include `altText` for images.
- Use clear fallback text.
- Keep mention text meaningful.

## Operational Notification Pattern

```json
{
  "type": "AdaptiveCard",
  "version": "1.2",
  "fallbackText": "API deployment failed in production.",
  "body": [
    {
      "type": "TextBlock",
      "text": "API deployment failed",
      "weight": "Bolder",
      "size": "Medium",
      "color": "Attention",
      "wrap": true
    },
    {
      "type": "FactSet",
      "facts": [
        { "title": "Environment", "value": "Production" },
        { "title": "Commit", "value": "`abc1234`" },
        { "title": "Owner", "value": "<at>Ada Lovelace</at>" }
      ]
    },
    {
      "type": "TextBlock",
      "text": "Rollback is available. Logs are linked below.",
      "wrap": true
    }
  ],
  "actions": [
    { "type": "Action.OpenUrl", "title": "Open run", "url": "https://example.com/run/123" },
    { "type": "Action.OpenUrl", "title": "Open logs", "url": "https://example.com/logs/123" }
  ]
}
```

## Design Review Checklist

- Can a mobile user understand the card without horizontal scanning?
- Does the first block communicate the point?
- Are all actions useful and safe?
- Is any dense data better as a link?
- Does the card still work if images fail?
- Are mentions intentional?
- Does fallback text summarize the card?
