---
name: slack-block-kit
description: Build or debug Slack Block Kit payloads for messages, modals, App Home, streaming responses, and Work Object unfurls. Use for block layout, elements, or interaction schemas; not plain Slack text formatting alone.
---

# Slack Block Kit

Construct the requested Slack layout or interaction using the receiving surface's schema. The user's explicit instructions take precedence over this skill's guidelines.

## Establish the surface

Use the requested content, interaction, target Slack method/surface, and any existing payload as input. Infer the surface from code when possible; ask if a missing choice changes the payload. Ordinary text replies do not require blocks.

| Work | Reference |
|---|---|
| Message, modal, App Home, or interaction lifecycle | [SURFACES.md](references/SURFACES.md) |
| Block choice, fields, limits, surface compatibility | [BLOCKS.md](references/BLOCKS.md) |
| Buttons, inputs, menus, pickers | [ELEMENTS.md](references/ELEMENTS.md) |
| Text objects, options, confirmation dialogs | [COMPOSITION.md](references/COMPOSITION.md) |
| Structured rich-text nesting and inline elements | [RICH-TEXT.md](references/RICH-TEXT.md) |
| start/append/stop streaming, chunks, SDK differences | [STREAMING.md](references/STREAMING.md) |
| Entity unfurls, flexpanes, edits, comments | [WORK-OBJECTS.md](references/WORK-OBJECTS.md) |
| Compact block/element/limit lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |

Load only the relevant reference or section. Payload construction does not require a Slack connection. Use the separately installed `slack-mrkdwn` skill for detailed text-formatting questions when available; the composition and rich-text references here cover the required object shapes independently.

## Preserve the payload contract

- Choose text syntax per field: `mrkdwn` uses `*bold*` and `<url|label>`; `plain_text` is literal; `markdown` blocks use standard Markdown; `rich_text` uses structured elements.
- Check surface compatibility: for example, alerts are modal-only and message payloads have different limits from modal/Home views.
- Keep top-level fallback text semantically aligned with blocks when provided. Screen readers and mobile notifications can depend on it.
- Escape untrusted text for its receiving field. Preserve supplied IDs and URLs; do not fabricate real channel, user, trigger, or entity identifiers.
- A modal needs a live trigger and interaction handling; a static preview does not prove the lifecycle works. Follow the current method/SDK contract when streaming schemas disagree.

Deliver valid JSON or integration code for the requested surface, with necessary fallback text and any unresolved runtime inputs. Verify payload structure and relevant limits; test live delivery only when requested or already authorized. Creating a payload does not itself authorize posting it.

Use the [Slack Block Kit reference](https://docs.slack.dev/reference/block-kit/) and the exact Web API method/SDK schema for current fields and limits that the bundled reference does not establish.
