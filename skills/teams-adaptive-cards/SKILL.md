---
name: teams-adaptive-cards
description: Build, validate, or repair Microsoft Teams Adaptive Card JSON and bot, webhook, or Graph wrappers. Use for card layouts, actions, forms, or MessageCard migration; not Teams text-only formatting or non-Teams card hosts.
---

# Teams Adaptive Cards

Build the requested card for its actual Teams transport and client capabilities. The user's explicit instructions take precedence over this skill's guidelines.

## Select the transport

Use the requested content/actions, delivery code or payload, and target clients as input. A card's JSON and its delivery wrapper are separate contracts.

| Transport | Required shape |
|---|---|
| Bot / Teams SDK | Activity `attachments[]`, card `content` as an object |
| Workflows webhook | `{ "type": "message", "attachments": [...] }` |
| Graph chatMessage | HTML attachment placeholder with matching ID; attachment `content` as a JSON string |
| Message extension | Attachment and preview appropriate to the extension type |

If delivery is unspecified, a raw card can be prepared while clarifying the transport. Do not invent a webhook URL, recipient, or bot backend. An approval/form needs a transport that handles its actions; a notification webhook is not a bot.

## Match capabilities

The references use a Teams baseline of card versions through 1.5, with 1.2 as a conservative mobile fallback. Select the minimum version needed by the requested elements and verify current host support when newer features matter. A schema version alone does not guarantee a Teams client renders an element.

Use card elements for layout: `TextBlock`, `FactSet`, `Table`, inputs, and actions as appropriate. TextBlock Markdown is limited; HTML, Markdown tables, and code fences are not substitutes for supported card elements. Provide wrapping, meaningful fallback text, and consistent mention metadata.

## References

Load only the transport, element, or interaction needed.

| Task | Reference |
|---|---|
| Delivery path, bots, message extensions | [SURFACES.md](references/SURFACES.md) |
| Inputs, tables, code, charts, people picker | [ELEMENTS.md](references/ELEMENTS.md) |
| Submit/Execute, refresh, user-specific views | [ACTIONS.md](references/ACTIONS.md) |
| Webhook notifications or requested connector migration | [WEBHOOKS-WORKFLOWS.md](references/WEBHOOKS-WORKFLOWS.md) |
| Graph attachment IDs, encoding, permissions | [GRAPH-ATTACHMENTS.md](references/GRAPH-ATTACHMENTS.md) |
| Width, mobile layout, accessibility | [RESPONSIVE-DESIGN.md](references/RESPONSIVE-DESIGN.md) |
| Compact wrapper/version/limit lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |

## Validate and deliver

For generated or changed payload files, run [scripts/check-teams-card.mjs](scripts/check-teams-card.mjs) with Node.js. Resolve the script relative to this skill's directory, not the user's working directory:

```bash
node /path/to/teams-adaptive-cards/scripts/check-teams-card.mjs --target webhook /path/to/payload.json
```

Targets: `auto`, `card`, `bot`, `webhook`, `graph`. Exit 0 means no errors (warnings can remain), 1 means errors/invalid JSON, and 2 means invalid CLI usage. Interpret warnings against the requested client/transport; the linter is a local check, not proof of live rendering. If Node is unavailable, inspect the wrapper and fields and state that the linter was not run.

Deliver the requested JSON or integration fix and verification outcome. Test live delivery only when requested or already authorized; payload creation does not require posting. Consult [Teams card documentation](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference) for host capabilities not established by the bundled references.
