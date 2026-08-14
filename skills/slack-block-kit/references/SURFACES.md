# Slack Surfaces, Accessibility, and Interactivity

> Current official Slack sources:
> - [Surfaces](https://docs.slack.dev/surfaces)
> - [Messages](https://docs.slack.dev/messaging)
> - [Unfurling links](https://docs.slack.dev/messaging/unfurling-links-in-messages)
> - [Platform security](https://docs.slack.dev/concepts/security)
> - [`chat.postMessage`](https://docs.slack.dev/reference/methods/chat.postMessage)
> - [Modals](https://docs.slack.dev/surfaces/modals) and [modal view schema](https://docs.slack.dev/reference/views/modal-views)
> - [App Home](https://docs.slack.dev/surfaces/app-home)
> - [Developing agents](https://docs.slack.dev/ai/developing-agents)
> - [Canvases](https://docs.slack.dev/surfaces/canvases)
> - [Handling interactions](https://docs.slack.dev/interactivity/handling-user-interaction)
> - [Interaction payloads](https://docs.slack.dev/reference/interaction-payloads)
> - [Socket Mode](https://docs.slack.dev/apis/events-api/using-socket-mode/)
> - [July 2026 notification change](https://docs.slack.dev/changelog/2026/07/13/notification-changes)
> - [Agent context change](https://docs.slack.dev/changelog/2026/07/02/app-context)
> - [Agent messaging experience](https://docs.slack.dev/changelog/2026/06/30/agent-messages-tab)

## Contents

- [Surface overview](#surface-overview)
- [Messages](#messages)
- [Modals](#modals)
- [App Home and agent views](#app-home-and-agent-views)
- [Canvases and Lists](#canvases-and-lists)
- [Interactivity](#interactivity)

## Surface overview

| Surface | Block Kit | Maximum blocks | Primary API |
|---|---:|---:|---|
| Message | Yes | 50 | `chat.postMessage`, `chat.update` |
| Modal | Yes | 100 | `views.open`, `views.update`, `views.push` |
| Home tab | Yes | 100 | `views.publish` |
| Canvas | No through canvas APIs | N/A | `canvases.create`, `canvases.edit` |
| List | No Block Kit document body | N/A | `lists.*` |

Block compatibility is per type, not just per maximum. Read [BLOCKS.md](BLOCKS.md) and [ELEMENTS.md](ELEMENTS.md) before moving a payload between surfaces. For example, `alert` is modal-only; container, markdown, context-actions, plan, and task-card blocks are message-only; card/carousel/table/data-table are available in messages and Home tabs.

## Messages

### Message forms

- A standard message persists until updated or deleted.
- An ephemeral message is visible only to one user, is not persisted across reloads, and cannot be retrieved through the API. Send it in response to a user action rather than unsolicited.
- A threaded reply uses the parent message's `ts` as `thread_ts`. `reply_broadcast: true` also exposes the reply in the channel and should be used sparingly.

### `text`, blocks, notifications, and accessibility

With `blocks`, top-level `text` is optional. Choose one accessible strategy:

1. Include a complete, semantically aligned top-level `text` fallback containing all necessary content for screen-reader users.
2. Omit top-level `text` and let Slack synthesize it from supported blocks.

Do not include a partial top-level fallback: screen readers default to it and do not traverse the interior blocks.

Notification behavior changed on July 13, 2026:

- Desktop clients extract text from supported blocks first and fall back to `message.text` only when no block text can be extracted.
- Mobile clients continue to use `message.text` exclusively.

Therefore include complete top-level `text` when a reliable mobile notification preview matters; omission remains a documented accessibility option when Slack can synthesize the block content.

```json
{
  "channel": "C0123ABC",
  "text": "Deploy complete — all checks passed.",
  "blocks": [
    {
      "type": "section",
      "text": { "type": "mrkdwn", "text": "*Deploy complete* — all checks passed." }
    }
  ]
}
```

`chat.postMessage` also accepts `markdown_text` (standard Markdown, 12,000 characters), but it conflicts with both `text` and `blocks`.

To suppress automatic link/media unfurls in a normal message, set both `unfurl_links: false` and `unfurl_media: false`. Slack specifically recommends considering this for untrusted LLM-generated links because unfurl fetching can create a data-exfiltration path. Streaming messages do not unfurl links.

### Message methods

| Method | Purpose |
|---|---|
| `chat.postMessage` | Publish a normal message |
| `chat.postEphemeral` | Publish a temporary single-user message |
| `chat.update` / `chat.delete` | Modify or remove a message |
| incoming webhook | Publish through a preconfigured URL |
| `response_url` | Respond to an interaction |
| `chat.startStream` / `chat.appendStream` / `chat.stopStream` | Stream agent output; see `SKILL.md` |

## Modals

A modal requires a fresh `trigger_id` from an interaction. It expires after three seconds and may be used only once. Open the modal before starting slow work.

### Modal view schema

| Property | Required | Constraint |
|---|---:|---|
| `type` | Yes | `modal` |
| `title` | Yes | `plain_text`, maximum 24 characters |
| `blocks` | Yes | Maximum 100 |
| `submit` | Conditional | Required when the view contains input blocks; `plain_text`, maximum 24 |
| `close` | No | `plain_text`, maximum 24 |
| `callback_id` | No | Maximum 255 |
| `private_metadata` | No | Maximum 3,000 |
| `clear_on_close` | No | Clear the full stack when closed |
| `notify_on_close` | No | Deliver `view_closed` when canceled |
| `external_id` | No | Unique per team |
| `submit_disabled` | No | Disable submission until Slack considers the inputs complete |

Slack permits at most three views in a modal stack. Use `views.open`, then `views.push` for the stack, and `views.update` to replace an existing view. Supply the current `hash` to `views.update` to reject stale concurrent updates.

### Submission response actions

Acknowledge `view_submission` within three seconds. The acknowledgement body can be:

| Body | Result |
|---|---|
| Empty HTTP 200 | Close current view |
| `{ "response_action": "update", "view": {...} }` | Replace current view |
| `{ "response_action": "push", "view": {...} }` | Push a view |
| `{ "response_action": "clear" }` | Close all views |
| `{ "response_action": "errors", "errors": {"block_id": "message"} }` | Attach validation errors to input blocks |

To preserve user-entered state across a modal view update, deliberately retain identical `block_id` and `action_id` values for each corresponding input. This is a narrow exception to Slack's general instruction to use a new `block_id` for every updated message/view iteration. Outside that state-preservation case, follow the component's update guidance, use fresh block IDs, and keep stable logical routing keys in application code instead of reusing a stale `block_id`.

### Reading submitted state

Use `view.state.values[block_id][action_id]`. Common leaf fields are:

| Element | Submitted property |
|---|---|
| text/number/email/url input | `value` |
| rich-text input | `rich_text_value` |
| file input | `files` |
| single/multi select | `selected_option` / `selected_options` |
| date/time/datetime picker | `selected_date` / `selected_time` / `selected_date_time` |
| users select | `selected_user` / `selected_users` |
| conversations select | `selected_conversation` / `selected_conversations` |
| channels select | `selected_channel` / `selected_channels` |

When a modal input contains a conversations/channels select with `response_url_enabled: true`, its submission can contain `response_urls` for the selected destinations.

## App Home and agent views

### Home tab

Publish a private per-user Home view with `views.publish`. Calling it again replaces the view. Listen for `app_home_opened`; the event reports the user, channel, active tab, and—when available—the view and app context.

```json
{
  "type": "home",
  "callback_id": "home_view",
  "blocks": [
    { "type": "header", "text": { "type": "plain_text", "text": "Welcome back" } }
  ]
}
```

The About tab is populated from app configuration rather than a programmable Block Kit view.

### Current agent messaging experience

Slack introduced two manifest values for the app messaging view:

| Value | Status and behavior |
|---|---|
| `agent_view` | Current and the only choice for new apps. Conversations use the standard Messages tab and can continue in threads. |
| `assistant_view` | Legacy for existing apps. Uses separate Chat and History tabs and is planned for eventual deprecation. |

For `agent_view`, use `app_home_opened` to detect that the user opened the app DM; `assistant_thread_started` no longer signals this. Suggested prompts live at the top of Messages, and `assistant.threads.setSuggestedPrompts` does not require `thread_ts`. Setting a thread status after a new message automatically opens that thread.

### App context

With `agent_view` enabled, subscribe to `app_context_changed` to receive the ordered entities a user is viewing (channel, DM, thread, canvas, or list). When subscribed, Slack also includes `app_context` on `message.im` and the same data under `context` on `app_home_opened`. Treat this as contextual input, not permission to expose content the app or user cannot access.

## Canvases and Lists

### Canvases

Canvas Web API methods do not accept Block Kit. They accept `document_content` with the only current type, `markdown`:

```json
{
  "document_content": {
    "type": "markdown",
    "markdown": "# Project status\n\n**On track**"
  }
}
```

- `document_content.markdown` is limited to 1 MiB (1,048,576 characters). For `canvases.edit`, the limit applies to each change in `changes`.
- Canvas Markdown supports h1-h3, text styles, lists and checklists, callouts, code, quotes, dividers, columns, links, emoji, tables, mentions, images, and several Slack unfurls.
- Canvas tables allow at most 300 cells per table.
- Canvas mentions use `![](@U123)` for a user and `![](#C123)` for a channel.
- Deno Slack built-in canvas functions use an `expanded_rich_text` input instead; do not confuse it with Web API `document_content`.

### Lists

Lists are Slack-native work-management surfaces operated with the `lists.*` methods. They are not Block Kit views. Use their API schemas for fields, records, and views, then use Block Kit messages only for summaries or actions around that data.

## Interactivity

### Required request handling

When an app uses a configured HTTP Request URL, Slack sends interaction payloads as an `application/x-www-form-urlencoded` POST whose `payload` form field contains JSON. Verify the request, parse `payload`, and acknowledge every valid interaction with HTTP 200 within three seconds. With Socket Mode, Slack instead delivers an envelope over the authenticated WebSocket; acknowledge it promptly by returning its `envelope_id` (and a response payload only where supported). The same three-second acknowledgement deadline applies. Defer expensive work until after acknowledgement.

| Payload type | Trigger |
|---|---|
| `block_actions` | User operates a Block Kit interactive element |
| `view_submission` | User submits a modal |
| `view_closed` | User cancels a modal with `notify_on_close: true` |
| `shortcut` / `message_action` | Global or message shortcut |

For `block_actions`, inspect `actions[]` plus its `block_id` and `action_id`; input state is also available for stateful surfaces. Dispatch timing varies by element and surface, so use the current [block-actions payload reference](https://docs.slack.dev/reference/interaction-payloads/block_actions-payload) rather than assuming every input emits on every change.

### Response capabilities and lifetimes

- A `response_url` can be used up to five times within 30 minutes. It does not replace the required three-second acknowledgement.
- Responses default to ephemeral; use `response_type: "in_channel"` for a visible channel response.
- Use `replace_original: true` to update a source app message or `delete_original: true` to delete it, subject to the documented slash-command limitations.
- A `trigger_id` expires after three seconds and is single-use.
- Global shortcuts do not provide `response_url`; a modal with a response-enabled conversations/channels select can generate one at submission time.

Keep action-routing semantics stable, but do not treat a rendered `block_id` as a permanent identifier: use a new block ID for each updated message/view iteration unless retaining matching modal input IDs specifically to preserve entered state. Authorize the acting user and target independently of client-provided values, and make action handlers idempotent because retries and duplicate delivery can occur.
