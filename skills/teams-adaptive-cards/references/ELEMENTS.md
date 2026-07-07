# Adaptive Card Elements For Teams

Use this as a Teams-focused element reference. For exact per-property schema, check the Adaptive Cards documentation hub (adaptivecards.microsoft.com).

## Contents

- [Root AdaptiveCard](#root-adaptivecard)
- [TextBlock](#textblock) / [RichTextBlock](#richtextblock) / [FactSet](#factset)
- [Image And ImageSet](#image-and-imageset)
- [Container](#container) / [ColumnSet And Column](#columnset-and-column) / [Table](#table)
- [CodeBlock](#codeblock) / [Charts](#charts) / [Icon, CompoundButton, And Other v1.5 Elements](#icon-compoundbutton-and-other-v15-elements)
- [Inputs](#inputs) / [ChoiceSet And People Picker](#choiceset-and-people-picker)
- [Elements To Treat Carefully](#elements-to-treat-carefully)

## Root AdaptiveCard

```json
{
  "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.2",
  "fallbackText": "Summary for unsupported clients",
  "body": [],
  "actions": []
}
```

Important root properties:

| Property | Required | Notes |
|----------|----------|-------|
| `type` | Yes | Must be `AdaptiveCard` |
| `version` | Yes | Default to `1.2`; max `1.5` for Teams (`1.6` is not Teams-supported) |
| `$schema` | No but recommended | Helps tooling and validation |
| `fallbackText` | Strongly recommended | Shows when client cannot render card |
| `body` | Usually | Array of visual elements |
| `actions` | No | Keep the count small |
| `refresh` | No | Universal Actions, bot-backed, max 60 `userIds` |
| `authentication` | No | SSO/OAuth scenarios, bot-backed |
| `msteams` | No | Teams-specific width and mentions |

## TextBlock

Primary text element.

```json
{
  "type": "TextBlock",
  "text": "Deployment **succeeded**",
  "wrap": true,
  "weight": "Bolder",
  "size": "Medium"
}
```

Teams guidance:

- Use `wrap: true` for any user-facing sentence.
- Use `weight`, `size`, `color`, and `style` for hierarchy instead of Markdown headings.
- Keep `TextBlock` content short; split paragraphs into multiple blocks.
- Markdown is limited to bold, italic, lists, and links; headings, tables, images, code fences, blockquotes, and HTML do not render.

Useful properties:

| Property | Use |
|----------|-----|
| `text` | Content |
| `wrap` | Allow multi-line rendering |
| `maxLines` | Clamp only when truncation is intentional |
| `weight` | `Lighter`, `Default`, `Bolder` |
| `size` | `Small`, `Default`, `Medium`, `Large`, `ExtraLarge` |
| `color` | Semantic color such as `Good`, `Warning`, `Attention` |
| `isSubtle` | Secondary text |
| `style` | `heading` (v1.5) for accessibility semantics |

## RichTextBlock

Use when mixed inline styles are more important than Markdown convenience.

```json
{
  "type": "RichTextBlock",
  "inlines": [
    { "type": "TextRun", "text": "Status: ", "weight": "Bolder" },
    { "type": "TextRun", "text": "Healthy", "color": "Good" }
  ]
}
```

Use for labels, badges, and inline status text. Keep runs simple for compatibility.

## FactSet

Good for compact metadata.

```json
{
  "type": "FactSet",
  "facts": [
    { "title": "Service", "value": "API" },
    { "title": "Owner", "value": "<at>Ada Lovelace</at>" }
  ]
}
```

Markdown is supported in `Fact.title` and `Fact.value`, and mentions work here too. Use short labels and values. For complex rows, use `ColumnSet` or `Table`.

## Image And ImageSet

```json
{
  "type": "Image",
  "url": "https://example.com/chart.png",
  "altText": "Latency chart for the API service",
  "size": "Stretch"
}
```

Rules:

- Always provide `altText`.
- Use HTTPS URLs; host on a CDN when possible. URLs that redirect to the final image are not supported.
- Max 1024 x 1024 pixels and 1 MB; PNG, JPEG, or GIF. Animated GIF and SVG are not supported.
- Keep images meaningful; avoid decorative images in operational cards.
- Test image dimensions in narrow clients.

## Container

Use to group related elements and apply spacing, separator, style, visibility, or select action.

```json
{
  "type": "Container",
  "style": "emphasis",
  "items": [
    { "type": "TextBlock", "text": "Requires attention", "wrap": true }
  ]
}
```

Avoid deeply nested containers. Cards should remain scannable.

## ColumnSet And Column

Use for side-by-side layout.

```json
{
  "type": "ColumnSet",
  "columns": [
    {
      "type": "Column",
      "width": "auto",
      "items": [{ "type": "TextBlock", "text": "Status", "wrap": true }]
    },
    {
      "type": "Column",
      "width": "stretch",
      "items": [{ "type": "TextBlock", "text": "Healthy", "wrap": true }]
    }
  ]
}
```

Teams guidance:

- Keep to two or three columns for chat/channel cards.
- Prefer `auto` plus `stretch` over fixed pixel widths (Teams design guidance caps explicit widths around 48px, one column max).
- Design narrow-first. Meeting side panels and mobile clients are constrained.
- If the data is just key-value rows, use `FactSet`.

## Table

Use only when actual tabular comparison is necessary; requires v1.5.

```json
{
  "type": "Table",
  "columns": [
    { "width": 1 },
    { "width": 1 }
  ],
  "rows": [
    {
      "type": "TableRow",
      "cells": [
        { "type": "TableCell", "items": [{ "type": "TextBlock", "text": "Service", "wrap": true, "weight": "Bolder" }] },
        { "type": "TableCell", "items": [{ "type": "TextBlock", "text": "Status", "wrap": true, "weight": "Bolder" }] }
      ]
    }
  ]
}
```

For mobile compatibility, prefer `FactSet` or repeated compact `Container` rows unless a table is truly needed.

## CodeBlock

Use for code snippets; requires v1.5 and renders only in Teams web and desktop clients (not mobile) — provide `fallbackText` or a link for mobile users.

```json
{
  "type": "CodeBlock",
  "codeSnippet": "{\n  \"status\": \"ok\"\n}",
  "language": "Json",
  "startLineNumber": 1
}
```

Supported languages include Bash, C, Cpp, CSharp, Css, Go, GraphQL, Html, Java, JavaScript, Json, Perl, Php, PowerShell, Python, Sql, TypeScript, Xml, and PlainText.

Keep snippets short. For long logs or files, link out.

## Charts

Teams supports native chart elements in v1.5 cards (not in Developer Portal previews). Provide a `fallback` element for hosts that lack chart support:

- `Chart.Donut`
- `Chart.Pie`
- `Chart.Gauge`
- `Chart.VerticalBar` / `Chart.VerticalBar.Grouped`
- `Chart.HorizontalBar` / `Chart.HorizontalBar.Stacked`
- `Chart.Line`

```json
{
  "type": "Chart.Donut",
  "title": "Traffic share",
  "data": [
    { "legend": "API", "value": 60 },
    { "legend": "Web", "value": 40 }
  ],
  "fallback": { "type": "TextBlock", "text": "API 60%, Web 40%", "wrap": true }
}
```

## Icon, CompoundButton, And Other v1.5 Elements

These newer elements are documented on the Adaptive Cards hub and supported in Teams via v1.5 payloads with host-capability gating:

| Element | Use |
|---------|-----|
| `Icon` | Fluent icon by `name` (e.g. `"name": "Alert"`), with `size`, `style`, `color` |
| `CompoundButton` | Prompt-starter-style button with icon, title, description, optional badge |
| `Rating` / `Input.Rating` | Read-only or input star ratings |

Always consider a `fallback` for clients that cannot render them, and test on mobile.

## Inputs

Inputs require a submit/execute action and a backend that can process the invoke. Adaptive Cards in Teams do not support file or image uploads.

| Element | Use |
|---------|-----|
| `Input.Text` | Free text, comment, short value |
| `Input.Number` | Numeric entry |
| `Input.Date` | Date entry |
| `Input.Time` | Time entry |
| `Input.Toggle` | Boolean |
| `Input.ChoiceSet` | Single/multiple choice, typeahead, people picker |

Accessibility:

- In schema v1.3+, use input `label`.
- In v1.2 cards, use a preceding `TextBlock` as the label.
- Do not rely only on placeholder text for meaning.
- `isRequired` and `errorMessage` need v1.3+.

## ChoiceSet And People Picker

Static choices:

```json
{
  "type": "Input.ChoiceSet",
  "id": "severity",
  "label": "Severity",
  "style": "expanded",
  "isMultiSelect": false,
  "choices": [
    { "title": "Low", "value": "low" },
    { "title": "High", "value": "high" }
  ]
}
```

Use `style: "compact"` for long lists. `isMultiSelect: true` submits comma-separated values.

People picker — add a `choices.data` `Data.Query` with a predefined Graph dataset (works in v1.2 cards because the host handles the search; bot-backed dynamic typeahead with custom datasets needs v1.5 and a bot):

```json
{
  "type": "Input.ChoiceSet",
  "id": "assignee",
  "label": "Assign to",
  "choices": [],
  "choices.data": {
    "type": "Data.Query",
    "dataset": "graph.microsoft.com/users"
  },
  "isMultiSelect": false
}
```

- Submitted value is the selected user's Entra object ID (comma-separated for multi-select); preselect via `value`.
- Requires a bot-backed card for the submit; works in chats, channels, and dialogs.

## Elements To Treat Carefully

| Element/Feature | Reason |
|-----------------|--------|
| `Media` | Officially supported for OneDrive/SharePoint share links and YouTube/Vimeo/Dailymotion; `mimeType` required on web/desktop; arbitrary MP4 URLs commonly fall back to a link — link out when reliability matters |
| File/image upload | Adaptive Cards in Teams do not support uploads |
| Deep nested `Action.ShowCard` | Hard to use on mobile |
| Many columns | Narrow clients truncate or wrap awkwardly |
| Long single TextBlock | Can become unreadable; split into sections |
| `CodeBlock` on mobile | Not rendered; web/desktop only |
