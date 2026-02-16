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

| Property | Required | Purpose |
|----------|----------|---------|
| `app_unfurl_url` | Yes | The URL the user posted |
| `url` | Yes | Canonical resource URL in external system |
| `entity_type` | Yes | One of the 5 entity types |
| `external_ref` | Yes | Object with `id` (required, must never change) and `type` (optional) identifying the entity |
| `entity_payload.attributes` | Yes | Header info including `title` |
| `entity_payload.fields` | Yes | Object of typed field entries (required even if empty `{}`) |

Slack silently drops the entire metadata payload if any required field is missing — no error, no card, just the bare text message.

**Important:** `external_ref.id` must remain stable across the lifetime of the entity — changing it breaks related conversation tracking.

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
      "display_id": "PROJ-123",
      "display_type": "Bug",
      "product_name": "Jira",
      "product_icon": { "type": "image", "url": "https://example.com/jira-icon.png" },
      "icon": { "type": "image", "url": "https://example.com/icon.png" },
      "full_size_preview": { "preview_url": "https://example.com/preview.pdf" },
      "metadata_last_modified": 1708000000
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

### Attributes Reference

| Property | Required | Purpose |
|----------|----------|---------|
| `title` | Yes | Entity name |
| `subtitle` | No | Secondary text below title |
| `display_id` | No | User-friendly identifier (e.g., "PROJ-123") |
| `display_type` | No | Resource classification label (defaults to entity type name) |
| `product_name` | No | External system name (e.g., "Jira", "GitHub") |
| `product_icon` | No | Custom icon (`{ type: "image", url }` or `{ type: "image", slack_file: { id } }`) |
| `icon` | No | Entity icon |
| `full_size_preview` | No | Image/PDF preview config (see Full-Size Preview section) |
| `metadata_last_modified` | No | Unix timestamp — Slack compares to previous value and skips refresh if unchanged |

### Entity-Type-Specific Fields

Each entity type has standard fields. All are optional and use the data types below.

**File** (`slack#/entities/file`): `preview` (image), `created_by` (user), `date_created` (timestamp), `date_updated` (timestamp), `last_modified_by` (user), `file_size` (string), `mime_type` (string).

**Task** (`slack#/entities/task`): `description` (markdown), `created_by` (user), `assignee` (user), `date_created` (timestamp), `date_updated` (timestamp), `status` (string, supports `tag_color` and `link`), `due_date` (date or timestamp), `priority` (string, supports `icon` and `link`).

**Incident** (`slack#/entities/incident`): `status` (string), `severity` (string), `created_by` (user), `assigned_to` (user), `date_created` (timestamp), `date_updated` (timestamp), `description` (string), `service` (string).

**Content Item** (`slack#/entities/content_item`): `preview` (image), `description` (string), `created_by` (user), `last_modified_by` (user), `date_created` (timestamp), `date_updated` (timestamp).

**Item** (`slack#/entities/item`): No predefined fields — fully custom via `fields` and `custom_fields`.

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

### User Type Properties

When using `slack#/types/user`, the value can include: `user_id` (Slack user ID), `text` (display name), `email`, `url` (external profile link), `icon` (avatar image).

### Boolean Display Modes

Boolean fields support two display modes via a `boolean` property:

- **Checkbox:** `{ "type": "checkbox", "text": "Enable notifications" }`
- **Text (custom labels):** `{ "type": "text", "true_text": "Public", "false_text": "Private" }`

### Entity Reference Properties

When using `slack#/types/entity_ref`, the value includes: `entity_url` (canonical URL), `external_ref` (`{ id, type }`), `title`, `display_type`, `icon`.

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
    "message_ts": "1234567890.123456",
    "thread_ts": "1234567890.123456"
  }
}
```

Note: `external_ref` is not guaranteed to be set in all cases, such as entities from Enterprise Search results.

**Content Refresh TTL:** First open always sends the event. Within 10 minutes, only manual refresh triggers it. After 10 minutes, reopening, tab switching, or manual refresh triggers it. A red dot indicator appears on stale content.

### Responding

Use `entity.presentDetails` with the `trigger_id` from the event to respond with metadata (same schema as `chat.unfurl` minus `entities` array and `app_unfurl_url`):

```json
{
  "trigger_id": "12345.67890",
  "metadata": {
    "entity_type": "slack#/entities/task",
    "external_ref": { "id": "task-123", "type": "task" },
    "entity_payload": { /* same structure as unfurl */ }
  }
}
```

### Custom Partial Views

For restricted access or custom error states, respond with an error object instead:

```json
{
  "trigger_id": "12345.67890",
  "error": {
    "status": "custom_partial_view",
    "custom_title": "Access Restricted",
    "custom_message": "Request access using the button below",
    "message_format": "markdown",
    "actions": [{ "text": "Request Access", "action_id": "request_access", "style": "primary" }]
  }
}
```

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

### Edit Property Configuration

| Property | Purpose |
|----------|---------|
| `enabled` | Boolean — activate editing |
| `placeholder` | Input hint text |
| `hint` | Descriptive text below input |
| `optional` | Allow blank values |
| `select` | Dropdown/multi-select options config |
| `number` | `{ min_value, max_value }` constraints |
| `text` | `{ min_length, max_length }` constraints (0-3000 chars) |
| `boolean` | Input type config (`checkbox`, `radio`, or `select`) |

### Supported Edit Field Types

| Field Type | Block Kit Element | Validation Options |
|------------|------------------|-------------------|
| text | plain_text_input | `min_length`, `max_length` |
| number | number_input | `min_value`, `max_value` |
| date | datepicker | — |
| datetime | datetimepicker | — |
| email | email_text_input | — |
| boolean | checkbox/radio/select | Input type configurable |
| select | static_select | Static options list |
| multi-select | multi_static_select | Static options list |

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

Additional actions in an overflow menu alongside primary actions:

```json
{
  "actions": {
    "primary_actions": [{ "text": "View", "action_id": "view", "style": "primary" }],
    "overflow_actions": [
      { "text": "Edit", "action_id": "edit", "value": "task-123" },
      { "text": "Delete", "action_id": "delete", "value": "task-123" }
    ]
  }
}
```

### Action Properties

| Property | Required | Constraints |
|----------|----------|-------------|
| `text` | Yes | Button label |
| `action_id` | Yes | Interaction identifier |
| `value` | No | Max 2000 chars |
| `style` | No | `"primary"` or `"danger"` |
| `url` | No | External link destination |
| `accessibility_label` | No | Max 75 chars |

### Interaction Handling

When users click action buttons, `block_actions` events are dispatched.

**Unfurl actions:** `container.type: "message_attachment"` with `app_unfurl_url`, `entity_url`, `external_ref`, `message_ts`, `thread_ts`, `channel_id`.

**Flexpane actions:** `container.type: "entity_detail"` with the same fields.

**Response options:** Open a modal, post a thread reply, send a DM, call `chat.unfurl` to refresh the unfurl, or call `entity.presentDetails` to refresh the flexpane.

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

For PDFs and images, provide a preview URL in attributes:

```json
{
  "attributes": {
    "full_size_preview": {
      "is_supported": true,
      "preview_url": "https://example.com/document.pdf",
      "mime_type": "application/pdf"
    }
  }
}
```

| Property | Required | Purpose |
|----------|----------|---------|
| `preview_url` | Yes | URL of the preview file |
| `is_supported` | No | Boolean — set to `false` to disable preview |
| `mime_type` | No | MIME type of the preview file |
| `error` | No | `{ code, message }` for unsupported files (e.g., `"file_not_supported"`) |

**Requirement:** Must include CORS header `access-control-allow-origin: https://app.slack.com`.

**Unfurl thumbnail:** Display a thumbnail in the unfurl via `fields.preview`:

```json
{ "fields": { "preview": { "image_url": "https://example.com/thumb.png", "alt_text": "Preview" } } }
```

---

## Automatic Refresh

Unfurls auto-refresh when:
- User opens, edits, or refreshes flexpane (via `entity.presentDetails` response)
- User clicks an action button (after processing delay)

**Optimization:** Include `metadata_last_modified` Unix timestamp in attributes. Slack compares to the previous value and skips the refresh if unchanged.

---

## View Submission Handling

When users save edits in the flexpane, a `view_submission` event is sent with `view.type: "entity_detail"`:

```json
{
  "type": "view_submission",
  "view": {
    "type": "entity_detail",
    "state": {
      "values": {
        "description": {
          "description.input": { "type": "plain_text_input", "value": "Updated text" }
        }
      }
    },
    "external_ref": { "id": "task-123" },
    "entity_url": "https://example.com/task/123"
  }
}
```

**Respond within 3 seconds:**
- **Success:** Call `entity.presentDetails` with updated metadata
- **Field errors:** Return `{ "response_action": "errors", "errors": { "field_block_id": "Error message" } }`
- **Form errors:** Use `entity.presentDetails` with `edit_error` status

---

## Related Conversations

The flexpane automatically aggregates conversations where the Work Object resource was mentioned, providing cross-conversation context.

---

## Enterprise Search Integration

Apps supporting Enterprise Search must subscribe to `entity_details_requested` and respond with `entity.presentDetails`. Define entity types in Work Object Previews settings. Supports search results, traditional results, and AI answer citations.
