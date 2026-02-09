# Work Objects — Entity Previews in Slack

> Sources:
> - [Work Objects](https://docs.slack.dev/messaging/work-objects) — Slack

Work Objects standardize how external entities (files, tasks, incidents) appear within Slack conversations. They extend link unfurling with rich, interactive entity previews.

---

## Architecture

```
User shares link → link_shared event → app calls chat.unfurl with metadata
                                       → Unfurl component renders in message
User clicks unfurl → entity_details_requested event → app calls entity.presentDetails
                                                      → Flexpane opens with full details
```

**Unfurl component:** Rich entity preview visible to all participants in the conversation.

**Flexpane component:** Side panel with full details, edit capability, actions, and related conversations.

---

## Entity Types

| Type | Entity ID | Use Case |
|------|-----------|----------|
| File | `slack#/entities/file` | Documents, spreadsheets, images, PDFs |
| Task | `slack#/entities/task` | Tickets, to-dos, work items, issues |
| Incident | `slack#/entities/incident` | Service interruptions, outages, alerts |
| Content Item | `slack#/entities/content_item` | Articles, wiki pages, documentation |
| Item | `slack#/entities/item` | General-purpose entity (anything else) |

---

## Setup

1. Go to app settings at api.slack.com/apps
2. Navigate to "Work Object Previews" in the sidebar
3. Enable the toggle
4. Select desired entity types
5. Save

---

## Unfurl Implementation

### chat.unfurl with Metadata

The `metadata` parameter (URL-encoded) contains the entity definition:

```json
{
  "metadata": {
    "app_unfurl_url": "https://example.com/task/123",
    "entities": [
      {
        "url": "https://example.com/task/123",
        "entity_type": "slack#/entities/task",
        "external_ref": { "id": "task-123", "type": "task" },
        "entity_payload": {
          "attributes": { /* header info */ },
          "fields": { /* entity-specific fields */ },
          "custom_fields": [ /* optional custom fields */ ],
          "display_order": [ /* field display order */ ]
        }
      }
    ]
  }
}
```

### Key Properties

| Property | Purpose |
|----------|---------|
| `app_unfurl_url` | The URL the user posted |
| `url` | Canonical resource URL in external system |
| `entity_type` | One of the 5 entity types |
| `external_ref` | Object with `id` (required) and `type` (optional) identifying the entity. Use the same ID your system uses to retrieve the resource |
| `entity_payload` | Schema defining what's displayed |

### Direct Posting (Without Link Unfurl)

`chat.postMessage` also accepts the `metadata` parameter for posting Work Objects directly:

```json
{
  "channel": "C0123ABC",
  "text": "New task created",
  "metadata": { /* same structure as unfurl */ }
}
```

---

## Entity Payload Schema

```json
{
  "entity_payload": {
    "attributes": {
      "title": "Bug: Login page 500 error",
      "subtitle": "Project Alpha",
      "icon": { "type": "image", "url": "https://example.com/icon.png" },
      "full_size_preview": { "preview_url": "https://example.com/preview.pdf" }
    },
    "fields": {
      "status": {
        "type": "string",
        "value": "In Progress",
        "display_name": "Status"
      },
      "assignee": {
        "type": "slack#/types/user",
        "value": "U0123ABC",
        "display_name": "Assignee"
      },
      "priority": {
        "type": "string",
        "value": "High",
        "display_name": "Priority"
      },
      "due_date": {
        "type": "slack#/types/date",
        "value": "2026-02-15",
        "display_name": "Due Date"
      }
    },
    "custom_fields": [
      {
        "type": "string",
        "key": "sprint",
        "value": "Sprint 14",
        "display_name": "Sprint"
      }
    ],
    "display_order": ["status", "assignee", "priority", "due_date"]
  }
}
```

---

## Data Types

| Type | Format |
|------|--------|
| `string` | Plain text |
| `integer` | Whole number |
| `boolean` | `true` / `false` |
| `array` | Array of values |
| `slack#/types/user` | Slack user ID |
| `slack#/types/channel_id` | Slack channel ID |
| `slack#/types/timestamp` | Unix timestamp |
| `slack#/types/date` | Date string |
| `slack#/types/image` | Image URL |
| `slack#/types/link` | Hyperlink |
| `slack#/types/email` | Email address |
| `slack#/types/entity_ref` | Reference to another Work Object |

---

## Flexpane

### Handling Requests

When users open a flexpane or refresh it, Slack sends an `entity_details_requested` event:

```json
{
  "type": "event_callback",
  "event": {
    "type": "entity_details_requested",
    "user": "U0123ABC",
    "external_ref": { "id": "task-123", "type": "task" },
    "entity_url": "https://example.com/task/123",
    "app_unfurl_url": "https://example.com/task/123",
    "trigger_id": "12345.67890",
    "user_locale": "en-US",
    "channel": "C0123ABC",
    "message_ts": "1234567890.123456"
  }
}
```

Note: `external_ref` is not guaranteed to be set in all cases, such as entities from Enterprise Search results.

### Responding

Use `entity.presentDetails` to respond with metadata (same schema as `chat.unfurl` minus `entities` array and `app_unfurl_url`).

---

## Editable Fields

Fields can be made editable by adding an `edit` property:

```json
{
  "description": {
    "type": "string",
    "value": "Original text",
    "display_name": "Description",
    "edit": {
      "enabled": true,
      "text": {
        "max_length": 500,
        "min_length": 1
      }
    }
  }
}
```

### Supported Edit Field Types

| Type | Validation Options |
|------|-------------------|
| text | `min_length`, `max_length` |
| number | `min_value`, `max_value` |
| date | — |
| datetime | — |
| email | — |
| boolean | — |
| select | Static options list |
| multi-select | Static options list |

### Dynamic Options

Use `fetch_options_dynamically: true` for select/multi-select fields that load options from your server.

### Submission Handling

When users submit edits, a `view_submission` event is sent with changes in `view.state.values`.

### Validation

Three levels:

1. **Client-side:** `edit` property constraints prevent submission
2. **Server-side field-level:** Respond to `view_submission` with field-specific errors
3. **Server-side form-level:** Use `entity.presentDetails` with `edit_error` status

---

## Actions

Apps can add interactive buttons to Work Object previews.

### Primary Actions (max 2)

```json
{
  "actions": {
    "primary_actions": [
      {
        "text": "View Details",
        "action_id": "view_details",
        "style": "primary",
        "value": "task-123"
      },
      {
        "text": "Mark Complete",
        "action_id": "mark_complete",
        "style": "danger",
        "value": "task-123",
        "url": "https://example.com/task/123/complete"
      }
    ]
  }
}
```

### Overflow Actions (max 5)

Additional actions in an overflow menu alongside primary actions.

### Interaction Handling

When users click action buttons, `block_actions` events are dispatched. The container includes `entity_url`, `external_ref`, and `app_unfurl_url` for identification.

---

## Authentication

For sensitive data requiring user authentication:

```json
{
  "user_auth_required": true,
  "user_auth_url": "https://example.com/auth/slack"
}
```

The flexpane shows a sign-in prompt. After authentication, the flexpane refreshes.

---

## Full-Size Preview

For PDFs and images, provide a preview URL:

```json
{
  "attributes": {
    "full_size_preview": {
      "preview_url": "https://example.com/document.pdf"
    }
  }
}
```

**Requirement:** Must include CORS header `access-control-allow-origin: https://app.slack.com`.

---

## Automatic Refresh

Unfurls refresh when:
- Users interact with flexpanes
- Users click action buttons
- `metadata_last_modified` timestamp changes

---

## Related Conversations

The flexpane automatically aggregates conversations where the Work Object resource was mentioned, providing cross-conversation context.
