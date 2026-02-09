# Slack Surfaces — Modals, App Home, Canvases, Lists, Split View

> Sources:
> - [Surfaces](https://docs.slack.dev/surfaces) — Slack
> - [Modals](https://docs.slack.dev/surfaces/modals) — Slack
> - [App Home](https://docs.slack.dev/surfaces/app-home) — Slack
> - [Canvases](https://docs.slack.dev/surfaces/canvases) — Slack
> - [Lists](https://docs.slack.dev/surfaces/lists) — Slack
> - [Split View](https://docs.slack.dev/surfaces/split-view) — Slack
> - [App Design](https://docs.slack.dev/surfaces/app-design) — Slack

---

## Overview

| Surface | Block Kit | Max Blocks | Persistence | Primary Method |
|---------|-----------|-----------|-------------|----------------|
| Messages | Yes | 50 | Permanent (until deleted) | `chat.postMessage` |
| Modals | Yes | 100 | Temporary (until dismissed) | `views.open` |
| App Home | Yes | 100 | Until app updates | `views.publish` |
| Canvases | No (markdown) | N/A | Permanent | `canvases.create` |
| Lists | No | N/A | Permanent | `lists.*` |
| Split View | Config | N/A | Session-based | Agents & AI Apps |

---

## 1. Messages

The primary output surface. Apps send messages via:

| Method | Use Case |
|--------|----------|
| `chat.postMessage` | Standard messages |
| `chat.postEphemeral` | Temporary, visible to one user only |
| `chat.update` | Modify existing messages |
| `chat.delete` | Remove messages |
| Incoming Webhooks | Simple message posting via URL |
| `response_url` | Reply to interactions |

### Message Types

**Standard:** Visible to all conversation members. Persist until deleted.

**Ephemeral:** Visible to one user only. Do not persist across reloads. Cannot be retrieved via API. Only send in response to user actions, never unsolicited.

**Threaded:** Replies under a parent message. Use `thread_ts` parameter. Set `reply_broadcast: true` to also show in channel.

### Payload Structure

```json
{
  "channel": "C0123ABC",
  "text": "Fallback text for notifications",
  "blocks": [ /* Block Kit blocks */ ],
  "thread_ts": "1234567890.123456",
  "mrkdwn": true
}
```

`text` is required — it serves as the notification preview and accessibility fallback, even when `blocks` are present.

---

## 2. Modals

Focused popup dialogs that capture user attention. Requires a `trigger_id` from a user interaction (expires in 3 seconds).

### Lifecycle

```
User interaction → trigger_id → views.open → [views.push] → view_submission → response
```

### View Object

| Property | Type | Required | Constraints |
|----------|------|----------|-------------|
| `type` | string | Yes | `"modal"` |
| `title` | text object | Yes | `plain_text`, max 24 chars |
| `blocks` | block[] | Yes | Max 100 blocks |
| `callback_id` | string | No | Max 255 chars, identifies interactions |
| `submit` | text object | Conditional | Required if `input` blocks exist. `plain_text`, max 24 chars |
| `close` | text object | No | `plain_text`, max 24 chars |
| `private_metadata` | string | No | Max 3000 chars, persists between views |
| `clear_on_close` | boolean | No | Clears entire view stack on close |
| `notify_on_close` | boolean | No | Sends `view_closed` event |
| `external_id` | string | No | Unique per team |
| `submit_disabled` | boolean | No | Disables submit until inputs completed |

### API Methods

| Method | Purpose |
|--------|---------|
| `views.open` | Open initial modal (requires trigger_id) |
| `views.update` | Update any view in stack (requires view_id) |
| `views.push` | Add new view to stack (max 3 total) |

### Response Actions (within 3s of view_submission)

| Action | Effect |
|--------|--------|
| Empty 200 response | Close current view |
| `{ "response_action": "update", "view": {...} }` | Replace current view |
| `{ "response_action": "push", "view": {...} }` | Add view to stack |
| `{ "response_action": "clear" }` | Close all views |
| `{ "response_action": "errors", "errors": {...} }` | Show validation errors |

### Error Handling

```json
{
  "response_action": "errors",
  "errors": {
    "block_id_for_input": "Please enter a valid email address"
  }
}
```

### Race Condition Prevention

Use the `hash` parameter in `views.update` calls. Included in `block_actions` payloads. API rejects outdated hashes.

### Input Data Retrieval

After `view_submission`, input values are in:
```
view.state.values[block_id][action_id].value
```

### Response URLs from Modals

For `conversations_select` or `channels_select` with `response_url_enabled: true`, the `view_submission` payload includes `response_urls` for posting messages to selected conversations.

---

## 3. App Home

Private, per-user space with three tabs: Home, Messages, About.

### Home Tab

Published via `views.publish`. Supports full Block Kit (100 blocks).

```json
{
  "type": "home",
  "blocks": [ /* Block Kit blocks */ ],
  "private_metadata": "optional context string",
  "callback_id": "home_view",
  "external_id": "unique_per_team"
}
```

**API:** `POST views.publish` with `user_id` and `view` parameters.

**Update:** Call `views.publish` again with updated blocks. Replaces existing view.

### Messages Tab

Direct messages between user and app bot. Requires `chat:write` scope. Optionally `im:history` for reading messages.

Subscribe to `message.im` event to receive user messages.

### About Tab

Auto-populated from app's Display Information settings. Not programmatically customizable.

### Events

`app_home_opened` fires when users open App Home. Payload includes `user`, `channel`, `tab` (home/messages/about), and `view`.

### Deep Linking

```
slack://app?team={TEAM_ID}&id={APP_ID}&tab={home|messages|about}
```

### Design Best Practices

- Prioritize relevant content at top
- Expose settings behind buttons, not prominently
- Limit call-to-action density
- Consider overflow menus for secondary actions
- Trigger modals from interactive components for data collection

---

## 4. Canvases

Built-in documents attached to channels or standalone. Use markdown formatting (NOT Block Kit).

### API Methods

| Method | Purpose |
|--------|---------|
| `canvases.create` | Create new canvas |
| `canvases.edit` | Modify existing canvas |
| `files.list` | Search canvases (filter by type "canvas") |

### Content Format

```json
{
  "document_content": {
    "type": "markdown",
    "markdown": "# Title\n\nContent with **bold** and [links](https://example.com)"
  }
}
```

### Supported Markdown

Text styling (bold, italic, strikethrough, code), lists (bulleted, ordered, checklists), headings (h1-h3), code blocks, quote blocks, dividers, emoji (standard + custom), tables (max 300 cells), links, user/channel mentions.

### Mention Syntax (Canvas-specific)

```markdown
User: ![](@U123ABCDEFG)
Channel: ![](#C123ABC456)
```

### Limitations

- No Block Kit support
- Tables limited to 300 cells
- Markdown is the only supported content type

---

## 5. Lists

Work management surfaces for organizing, collaborating, and tracking projects within Slack.

### Use Cases

- Feedback management in channels
- Cross-functional project tracking
- Task assignment and status tracking

### API Access

Lists are managed through the `lists.*` family of Slack Web API methods. Apps can extract data from Lists and post summaries to channels.

### Advantages Over Alternatives

- Custom views within Slack
- Direct @-mentions for stakeholder notification
- Native integration without external tools

---

## 6. Split View

AI chat surface providing side-by-side layout for AI-powered apps.

### Configuration

1. Navigate to "Agents & AI Apps" in app settings
2. Toggle split view on

### Effects

- Top bar entry point appears for app access
- App Home messages tab is replaced with Chat and History tabs
- Chat tab: primary AI conversation interface
- History tab: previous interaction history

### Complementary Features

- Suggested prompts for user guidance
- Loading states for processing indicators
- App threads for organized conversations

---

## App Design Best Practices

### Communication Guidelines

| Principle | Guidance |
|-----------|----------|
| Message frequency | Offer digests over individual alerts |
| Mentions | Avoid @channel, @here, @everyone except for critical outages |
| Channel selection | Segment by type, avoid #general default |
| Ephemeral vs channel | Use ephemeral for single-user responses |
| DMs | Only when user-initiated or confidential |
| Actionable messages | Include interactive elements for immediate action |

### Localization

| Context | Use |
|---------|-----|
| Public content | Channel locale |
| Private interactions | User locale |
| Locale retrieval | `conversations.info` / `users.info` with `include_locale: true` |

### Bot Design

- Descriptive, memorable names (lowercase, <22 chars)
- Brand colors for attachment highlights
- Icons designed for 512x512px scaling down to 36x36px
- Illustrations over photography, minimal text in icons
- Don't round corners — Slack handles this

### Tone

- Brief: every word should facilitate an interaction
- Clear: no jargon, no culturally specific references
- Empathetic: gender-neutral pronouns, diverse emoji skin tones
- Actionable: specific button labels in active voice
