# Adaptive Card Elements For Teams

Use this as a Teams-focused element reference. For exact schema details, check the Microsoft Adaptive Card schema explorer.

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
| `version` | Yes | Default to `1.2` for broad Teams/mobile support |
| `$schema` | No but recommended | Helps tooling and validation |
| `fallbackText` | Strongly recommended | Shows when client cannot render card |
| `body` | Usually | Array of visual elements |
| `actions` | No | Max practical count should stay small |
| `refresh` | No | Universal Actions, bot-backed |
| `authentication` | No | SSO/OAuth scenarios |
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
- Markdown is limited; do not use tables, images, headings, code fences, or blockquotes.

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
| `style` | `heading` when supported |

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

Markdown is supported in `Fact.title` and `Fact.value`. Use short labels and values. For complex rows, use `ColumnSet` or `Table`.

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
- Use HTTPS URLs unless a specific host supports another source.
- Keep images meaningful; avoid decorative images in operational cards.
- Test image dimensions in narrow clients.
- Animated GIF support and large image behavior vary; prefer static images.

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
- Prefer `auto` plus `stretch` over fixed pixel widths.
- Design narrow-first. Meeting side panels and mobile clients are constrained.
- If the data is just key-value rows, use `FactSet`.

## Table

Use only when actual tabular comparison is necessary and target clients support the required schema version.

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

Use for code snippets when v1.5/client support is acceptable.

```json
{
  "type": "CodeBlock",
  "codeSnippet": "{\n  \"status\": \"ok\"\n}",
  "language": "JSON",
  "startLineNumber": 1
}
```

Teams documents languages such as Bash, C, C++, C#, CSS, Go, GraphQL, HTML, Java, JavaScript, JSON, Perl, PHP, PowerShell, Python, SQL, TypeScript, XML, and PlainText.

Keep snippets short. For long logs or files, link out.

## Inputs

Inputs require a submit/execute action and a backend that can process the invoke.

| Element | Use |
|---------|-----|
| `Input.Text` | Free text, comment, short value |
| `Input.Number` | Numeric entry |
| `Input.Date` | Date entry |
| `Input.Time` | Time entry |
| `Input.Toggle` | Boolean |
| `Input.ChoiceSet` | Single/multiple choice |

Accessibility:

- In schema v1.3+, use input `label`.
- In v1.2 cards, use a preceding `TextBlock` as the label.
- Do not rely only on placeholder text for meaning.
- Use `isRequired` and `errorMessage` only when supported by chosen version/client.

## ChoiceSet

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

Use `style: "compact"` for long lists. Use `isMultiSelect: true` only when the backend expects comma-separated values.

## Elements To Treat Carefully

| Element/Feature | Reason |
|-----------------|--------|
| `Media` | Teams support and playback behavior can vary; link out when reliability matters |
| File/image upload | Adaptive Cards in Teams do not support file or image uploads |
| Deep nested `Action.ShowCard` | Hard to use on mobile |
| Many columns | Narrow clients truncate or wrap awkwardly |
| Long single TextBlock | Can become unreadable; split into sections |
