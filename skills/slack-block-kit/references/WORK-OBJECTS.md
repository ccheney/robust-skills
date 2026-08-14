# Work Objects — Complete Implementation Reference

> Authoritative Slack sources:
> - [Work Objects overview](https://docs.slack.dev/messaging/work-objects-overview/)
> - [Implementing Work Objects](https://docs.slack.dev/messaging/work-objects-implementation/)
> - [Bidirectional comments](https://docs.slack.dev/messaging/work-objects-comments/)
> - [`chat.unfurl`](https://docs.slack.dev/reference/methods/chat.unfurl/)
> - [`entity.presentDetails`](https://docs.slack.dev/reference/methods/entity.presentDetails/)
> - [`entity.presentComments`](https://docs.slack.dev/reference/methods/entity.presentComments/)
> - [`entity.acknowledgeCommentAction`](https://docs.slack.dev/reference/methods/entity.acknowledgeCommentAction/)

Work Objects are structured entities attached to Slack link unfurls or app-posted notifications. They provide a conversation-visible unfurl, a per-user flexpane with details and editing, related-conversation aggregation, actions, previews, and optional bidirectional comments.

## Contents

- [Architecture](#architecture)
- [Supported entity types](#supported-entity-types)
- [Standard app unfurls versus Work Objects](#standard-app-unfurls-versus-work-objects)
- [Link-unfurl flow](#link-unfurl-flow)
- [Entity payload](#entity-payload)
- [Field schema and data types](#field-schema-and-data-types)
- [Images, Slack files, and full-size previews](#images-slack-files-and-full-size-previews)
- [Flexpane details](#flexpane-details)
- [Editable fields](#editable-fields)
- [Work Object actions](#work-object-actions)
- [Bidirectional comments](#bidirectional-comments)
- [Related conversations, search, and mentions](#related-conversations-search-and-mentions)
- [Validation checklist](#validation-checklist)

## Architecture

```text
link_shared
  └─ chat.unfurl(metadata.entities[])          → conversation-visible unfurl
       ├─ entity_details_requested
       │    └─ entity.presentDetails(metadata) → per-user details flexpane
       └─ entity_comments_requested
            └─ entity.presentComments(...)     → ephemeral comments tab

flexpane edit/post-comment → view_submission
delete comment             → block_actions
comment mutation result    → entity.acknowledgeCommentAction
```

Unfurl content is visible to everyone in the conversation. Put sensitive or user-specific content behind flexpane authentication.

## Supported entity types

| Display type | `entity_type` | Recommended use |
|---|---|---|
| File | `slack#/entities/file` | Documents, spreadsheets, images, PDFs |
| Task | `slack#/entities/task` | Tickets, to-dos, issues |
| Incident | `slack#/entities/incident` | Incidents and service interruptions |
| Content Item | `slack#/entities/content_item` | Pages, articles, wiki content |
| Item | `slack#/entities/item` | General-purpose entities using custom fields |

Enable the desired types under **Work Object Previews** in app settings. For link unfurls, also configure link-unfurl domains, subscribe to `link_shared`, and grant `links:read` plus `links:write`.

## Standard app unfurls versus Work Objects

Both flows begin with a matching-domain `link_shared` event and end with `chat.unfurl`, but they use different content arguments:

| Flow | `chat.unfurl` content |
|---|---|
| Standard app unfurl | `unfurls`, a map keyed by each exact shared URL whose values contain blocks or a legacy attachment |
| Work Object | `metadata.entities[]`, the structured entity schema in this document |

Configure up to five app-unfurl domains, request `links:read` to receive the matching link data and `links:write` to publish the unfurl, and subscribe to `link_shared`. The event supplies only link/message context, not the original message. Acknowledge it promptly, then do lookups and call `chat.unfurl` asynchronously.

`chat.unfurl` accepts either `channel` + `ts`, or `unfurl_id` + `source`. `source` is `composer` for an in-composer preview or `conversations_history` for a posted link. For standard composer unfurls, optional `preview` controls composer title/icon treatment; it is ignored on posted messages.

Slack's current unfurling guide says `chat.unfurl` does not support rich-text blocks even though they work in other Web API messages. Use supported message blocks in standard `unfurls`, and use Work Object metadata rather than attempting to embed `rich_text` in an unfurl.

## Link-unfurl flow

Call `chat.unfurl` with the source `channel` + `ts` (or composer `unfurl_id` + `source`) and `metadata`. Send it as an object with JSON transport; URL-encode it only for form-encoded transport. `chat.unfurl` requires `links:write` and is Tier 3 (50+ per minute).

```json
{
  "channel": "C0123ABC",
  "ts": "1760000000.000100",
  "metadata": {
    "entities": [
      {
        "app_unfurl_url": "https://example.com/task/123?from=slack",
        "url": "https://example.com/task/123",
        "external_ref": { "id": "task-123", "type": "task" },
        "entity_type": "slack#/entities/task",
        "entity_payload": {
          "attributes": {
            "title": { "text": "Fix login page error" },
            "display_id": "PROJ-123",
            "product_name": "Issue Tracker"
          },
          "fields": {
            "status": { "value": "In progress", "tag_color": "blue" }
          },
          "display_order": ["status"]
        }
      }
    ]
  }
}
```

### Entity envelope

| Property | Required for unfurl | Meaning |
|---|---:|---|
| `app_unfurl_url` | Yes | Exact URL from `link_shared`; belongs inside each entity, not at `metadata` top level |
| `url` | Yes | Canonical resource URL in the external system |
| `external_ref.id` | Yes | Stable, opaque resource identifier |
| `external_ref.type` | No | Internal type needed when the ID is not globally unique |
| `entity_type` | Yes | One of Slack's five Work Object types |
| `entity_payload` | Yes | Attributes, recommended fields, custom fields, display order, and actions |
| `entity_comments` | No | Comment count/timestamp and comments-tab capability; sibling of `entity_payload` |

`metadata.entities` may contain multiple entities for multiple shared URLs. Keep `external_ref` stable forever: Slack uses it for related-conversation tracking, and changing its format or ID breaks continuity. Do not encode unrelated or sensitive data in it.

Slack may discard invalid Work Object metadata without producing the rich preview. Log the API response, preserve the original `app_unfurl_url`, and validate the full entity envelope before calling the method.

### Direct app-posted Work Objects

`chat.postMessage` can reuse the same `metadata.entities` schema for a notification that is not responding to a shared link. In that case `app_unfurl_url` is not required. SDK naming may differ; for example, the Java SDK exposes `eventAndEntityMetadata`.

## Entity payload

```json
{
  "entity_payload": {
    "attributes": {
      "title": { "text": "Fix login page error" }
    },
    "fields": {},
    "custom_fields": [],
    "display_order": [],
    "actions": {
      "primary_actions": [],
      "overflow_actions": []
    }
  }
}
```

`attributes.title.text` is the required title shape. It is not a bare string. `fields`, `custom_fields`, and `display_order` are optional, though Slack recommends the standard fields so downstream features work correctly. The general-purpose Item type has no standard `fields`; put all Item properties in `custom_fields`.

### Attributes

| Property | Required | Shape / behavior |
|---|---:|---|
| `title` | Yes | `{ "text": "..." }`; may also contain `edit` |
| `display_id` | No | Human-readable ID |
| `display_type` | No | Resource label; defaults from entity type |
| `product_name` | No | Product/system name; defaults to app name |
| `product_icon` | No | Icon object: `alt_text` plus exactly one of public `url` or `slack_file` |
| `full_size_preview` | No | Image/PDF preview descriptor |
| `metadata_last_modified` | No | Unix seconds; refresh only when greater than stored value; Slack falls back to `date_updated` when absent |

Do not use the Block Kit image-element wrapper (`{ "type": "image" }`) for `product_icon`. Work Object icon objects use `alt_text` plus `url` or `slack_file`.

### Standard fields by type

| Entity | Recommended `fields` keys |
|---|---|
| File | `preview`, `created_by`, `date_created`, `date_updated`, `last_modified_by`, `file_size`, `mime_type`; optional entity-level `slack_file` |
| Task | `description`, `created_by`, `date_created`, `date_updated`, `assignee`, `status`, `due_date`, `priority` |
| Incident | `status`, `severity`, `created_by`, `assigned_to`, `date_created`, `date_updated`, `description`, `service` |
| Content Item | `preview`, `description`, `created_by`, `date_created`, `date_updated`, `last_modified_by` |
| Item | No `fields` object; use `custom_fields` |

Use the exact recommended key. Slack says a substitute such as `creator` instead of `created_by` may validate but will not power downstream features correctly.

Common standard-field shapes:

| Field family | Shape |
|---|---|
| `preview` | `{ "type": "slack#/types/image", "alt_text": "...", "image_url": "..." }` or `slack_file` instead of `image_url` |
| `created_by`, `last_modified_by`, `assignee`, `assigned_to` | `{ "type": "slack#/types/user", "user": { "user_id": "U..." } }` or a text-based user descriptor |
| `date_created`, `date_updated` | `{ "value": 1741164235 }` in Unix seconds |
| `description` | `{ "value": "...", "format": "markdown" }`; `format` is optional |
| `status`, `severity`, `service` | String `value`; string fields may add `tag_color` or `link` where appropriate |
| `due_date` | `value` as `YYYY-MM-DD` with `type: "slack#/types/date"`, or Unix seconds with `type: "slack#/types/timestamp"` |
| `priority` | String `value`, optionally `icon` and/or `link` (subject to the field-property compatibility rules below) |
| `file_size`, `mime_type` | String `value` |

For a File entity that also represents a Slack remote file, reuse `remote_file.external_id` as `external_ref.id` and optionally provide entity-level `slack_file` (`id`, plus optional extension `type`) for unified-file-browser compatibility.

### Custom fields and ordering

Every `custom_fields[]` entry requires `key`, `label`, `value` (except image cases where the image data replaces it), and `type`.

```json
{
  "custom_fields": [
    { "key": "sprint", "label": "Sprint", "value": "Sprint 14", "type": "string" }
  ],
  "display_order": ["sprint", "created_by"]
}
```

If `display_order` is omitted, standard fields use entity-schema order and custom fields follow them.

## Field schema and data types

### Common field properties

| Property | Applies to | Notes |
|---|---|---|
| `value` | Most types | Required except image-like fields |
| `type` | Custom fields and selected standard fields | See type table |
| `icon` | `string` | Incompatible with `tag_color` |
| `link` | `string`, date, timestamp | Hyperlinks the field value |
| `tag_color` | `string` | `red`, `yellow`, `green`, `gray`, or `blue` |
| `format` | `string` | Only `"markdown"`; incompatible with `icon` and `link` |
| `long` | `string` | `true` expands field width |
| `item_type` | `array` | Required; declares a supported array item type |
| `image_url` / `slack_file` / `alt_text` | image | Public image or Slack file |
| `user` | user | User descriptor below |
| `boolean` | boolean | Checkbox or custom text view rendering |
| `entity_ref` | entity reference | Same-app Work Object relationship; not editable |
| `edit` | Editable types | Flexpane edit descriptor |

### Type values

| `type` | Value shape |
|---|---|
| `string` | String |
| `integer` | Integer |
| `boolean` | Boolean plus optional `boolean` display descriptor |
| `array` | Array of one item type; supported item types: `string`, `integer`, `slack#/types/channel_id`, `slack#/types/user`, `slack#/types/entity_ref` |
| `slack#/types/user` | `user` object |
| `slack#/types/channel_id` | Slack conversation ID |
| `slack#/types/timestamp` | Unix seconds |
| `slack#/types/date` | `YYYY-MM-DD` |
| `slack#/types/image` | `image_url` or `slack_file`, normally with `alt_text` |
| `slack#/types/file` | Mentioned for custom automatic-file-share fields, but omitted from Slack's current canonical data-types table; validate before authoring |
| `slack#/types/entity_ref` | `entity_ref` relationship |
| `slack#/types/link` | Valid URL string |
| `slack#/types/email` | Valid email string |

Array values are arrays of objects, for example:

```json
{
  "type": "array",
  "item_type": "string",
  "value": [{ "value": "A" }, { "value": "B" }]
}
```

### User descriptors

Supply exactly one identity path:

- `user_id` when the Slack user ID is known; or
- `text` when only the person's name is known.

Optional `url`, `email`, and `icon` enrich the user. A matching email can resolve to the Slack user.

### Boolean display descriptors

Checkbox view:

```json
{
  "type": "boolean",
  "value": false,
  "boolean": {
    "type": "checkbox",
    "text": "Enable notifications",
    "description": "Receive update alerts"
  }
}
```

Text view:

```json
{
  "type": "boolean",
  "value": true,
  "boolean": {
    "type": "text",
    "true_text": "Public",
    "false_text": "Private",
    "true_description": "Visible to everyone",
    "false_description": "Visible to owners"
  }
}
```

### Entity references

`entity_ref` requires canonical `entity_url` (no tracking/query parameters) and `external_ref`; it may include `title`, `display_type`, and `icon`. Relationships only work among Work Objects from the same app, and entity-reference fields are not editable.

## Images, Slack files, and full-size previews

Image/file fields can use a public URL or a `slack_file`. When Work Object metadata contains a Slack file in `entity_payload.slack_file`, `attributes.product_icon`, a standard image/file field, or a custom image/file field, Slack automatically shares that file to the conversation. Create/upload the file first; no separate file block or `files.remote.share` call is needed. This automatic share does not apply to public `image_url` values.

```json
{
  "attributes": {
    "full_size_preview": {
      "is_supported": true,
      "preview_url": "https://example.com/document.pdf",
      "mime_type": "application/pdf"
    }
  },
  "fields": {
    "preview": {
      "type": "slack#/types/image",
      "alt_text": "Document preview",
      "slack_file": { "id": "F0123456" }
    }
  }
}
```

For an actual preview, `is_supported`, `preview_url`, and `mime_type` are required. Only images and PDFs are currently supported. The preview response must allow `https://app.slack.com` through `Access-Control-Allow-Origin`. A minimal `{ "is_supported": true }` in unfurl metadata can enable generation of short-lived preview URLs. `error.code` can be `file_not_supported`, `file_size_exceeded`, or `custom`, with an accompanying message.

## Flexpane details

Subscribe to `entity_details_requested`. The event contains:

- requesting `user`, `trigger_id`, `user_locale`, and `event_ts`;
- `entity_url`, `app_unfurl_url`, and `link { url, domain }`;
- optional `external_ref` (not guaranteed, notably for some Enterprise Search sources);
- `channel`, `message_ts`, and `thread_ts` only when opened from message context.

Call `entity.presentDetails` with the event `trigger_id`. It requires no additional scope and is Tier 3 (50+ per minute). The flexpane metadata is one entity rather than an `entities` array and omits `app_unfurl_url`; it may carry `url`, `external_ref`, `entity_type`, `entity_payload`, and `entity_comments`.

```json
{
  "trigger_id": "12345.67890.token",
  "metadata": {
    "url": "https://example.com/task/123",
    "external_ref": { "id": "task-123", "type": "task" },
    "entity_type": "slack#/entities/task",
    "entity_payload": {
      "attributes": { "title": { "text": "Fix login page error" } },
      "fields": { "status": { "value": "In progress" } }
    }
  }
}
```

### Refresh behavior

- First flexpane open and manual refresh always dispatch `entity_details_requested`.
- Within the 10-minute TTL, closing/reopening or switching Details/Conversations does not dispatch it; manual refresh does.
- After the TTL, reopening, tab switching, or manual refresh dispatches it.
- Flexpane `entity.presentDetails` responses and unfurl action clicks can refresh the unfurl automatically.
- Use increasing `metadata_last_modified`; Slack otherwise falls back to `date_updated`.

### Authentication and errors

Use `user_auth_required: true` with `user_auth_url` to gate sensitive per-user details. `entity.presentDetails.error.status` currently accepts `restricted`, `internal_error`, `not_found`, `custom`, `custom_partial_view`, `timeout`, and `edit_error`.

Custom partial views may add action buttons. Their action schema is the normal Work Object action schema plus optional `processing_state`:

```json
{
  "error": {
    "status": "custom_partial_view",
    "custom_title": "Access restricted",
    "custom_message": "Request access to view this item.",
    "message_format": "markdown",
    "actions": [
      {
        "text": "Request access",
        "action_id": "request_access",
        "processing_state": {
          "enabled": true,
          "interstitial_text": "Requesting access"
        }
      }
    ]
  }
}
```

## Editable fields

Add `edit.enabled: true` to an attribute/field. Optional `placeholder` and `hint` are `plain_text` objects (`emoji` is supported on hint but not placeholder); `optional` controls whether the user may clear it.

| `edit` child | Properties |
|---|---|
| `text` | `min_length`, `max_length` from 0 through 3000 |
| `number` | numeric `min_value`, `max_value` |
| `select` | `current_value`, `current_values`, `static_options`, `fetch_options_dynamically` (default `false`) |
| `boolean` | `input_type`: `checkbox`, `radio`, or `select`; defaults to `select`, except a checkbox view defaults to checkbox edit |

`static_options` use normal option shapes: required `value` (150 max) and `text` (75 max), optional `description` (75 max).

### Input mapping

| Field/input | Supported for Work Object edit | Notes |
|---|---:|---|
| Checkboxes | Yes | Boolean only, one checkbox |
| Date picker | Yes | Date fields |
| Datetime picker | Yes | Timestamp/datetime fields |
| Email input | Yes | Email fields |
| File input | No | |
| Multi-select | Yes | Array fields; channel arrays become multi-conversations select |
| Number input | Yes | Configure min/max and decimals via metadata |
| Plain-text input | Yes | Max 3000; edit disabled above that size |
| Radio button group | No as a general field mapping | Boolean `edit.boolean.input_type: "radio"` is the documented special case |
| Rich-text input | No | Edit raw Markdown through plain text instead |
| Select | Yes | Static/dynamic configuration; user/channel types map to native selectors |
| Time picker | Yes | |
| URL input | Yes | Link fields |

Dynamic selections dispatch `block_suggestions` with `block_id` equal to the field key and `action_id` `<field>.input`; return at most 100 options/option groups.

The field-mapping table says decimal acceptance for number inputs is configurable through edit metadata, but the current `edit.number` schema lists only `min_value` and `max_value`. Do not invent a decimal property; confirm the current SDK/method schema before relying on it.

### Saving and validating edits

Saving dispatches `view_submission` with `view.type: "entity_detail"`. Identify the entity through `view.external_ref` and `view.entity_url`; updated inputs are under `view.state.values`. Acknowledge within 3 seconds, then call `entity.presentDetails` with the submission `trigger_id` and updated metadata.

Validation layers:

1. Client-side constraints from `edit` metadata.
2. Field error acknowledgment: `{ "response_action": "errors", "errors": { "due_date": "..." } }` within 3 seconds.
3. Form error through `entity.presentDetails` with `error.status: "edit_error"`.

The Work Object edit view callback ID is `work-object-edit`.

## Work Object actions

Put `actions` inside `entity_payload`. Unfurl and flexpane metadata may intentionally define different actions.

- `primary_actions`: up to 2, always in the footer.
- `overflow_actions`: up to 5 in **More actions**.

| Action property | Required | Limit / values |
|---|---:|---|
| `text` | Yes | Human-readable string |
| `action_id` | Yes | 255 characters |
| `value` | No | 2000 characters |
| `style` | No | `primary` or `danger` |
| `url` | No | 3000 characters |
| `accessibility_label` | No | 75 characters |

Clicks dispatch `block_actions`. For an unfurl, `container.type` is `message_attachment`; for a flexpane, it is `entity_detail`. Both containers include Work Object context such as `entity_url`, `external_ref`, `app_unfurl_url`, message/thread timestamps, and channel ID. Acknowledge within 3 seconds, perform work asynchronously, then refresh with `chat.unfurl` or `entity.presentDetails` as appropriate.

## Bidirectional comments

Comments live in the external system, not Slack. Slack caches and presents them ephemerally in the flexpane. Add `entity_comments` as a sibling of `entity_payload` in either unfurl entity metadata or flexpane metadata:

```json
{
  "entity_comments": {
    "count": 5,
    "latest_timestamp": 1741165000
  }
}
```

Including `count: 0` still advertises that comments are supported and renders the entry point. Omit `entity_comments` entirely when the entity does not support comments.
Use the external system's total count and the latest comment's Unix-seconds timestamp for `latest_timestamp`.

### Reading and paging comments

Subscribe to `entity_comments_requested`. It fires on opening/refreshing the comments tab and when scrolling for another page. The event includes `user`, `entity_url`, `external_ref`, `link`, `trigger_id`, requested `limit`, optional app-provided `cursor`, and optional `thread_root_id` for thread replies.

Respond with `entity.presentComments`; it requires no additional scope and is Tier 3 (50+ per minute).

```json
{
  "trigger_id": "12345.67890.token",
  "comments": [
    {
      "id": "comment-001",
      "sender": { "user_id": "U123456789" },
      "timestamp": 1741164235,
      "comment": { "value": "Can someone review this?", "format": "markdown" },
      "url": "https://example.com/task/123#comment-001",
      "can_edit": true,
      "can_delete": true,
      "can_reply": true,
      "reply_count": 2,
      "reply_users": [{ "user_id": "U234567890" }],
      "latest_reply_ts": 1741165000
    }
  ],
  "can_post_comment": true,
  "delete_action_id": "delete_external_comment",
  "cursor": "next-page-token"
}
```

Slack's `entity.presentComments` page contradicts itself about `can_post_comment`: the Web API argument table marks it optional, while the detailed comment schema marks it required. Include it explicitly in every normal comments response so composer visibility is deterministic. The documented authentication branch is different: send `trigger_id`, `user_auth_required: true`, and `user_auth_url`, while omitting `comments` and `can_post_comment`. For normal responses, `trigger_id` and `comments` are required. Each comment requires `id`, `sender`, `timestamp`, and `comment`. `comment` provides either a single rich-text block through `blocks` or a string through `value` (with optional `format: "markdown"`). Optional comment fields: `url`, `cursor`, `last_edit_ts`, `can_edit`, `can_delete`, `can_reply`, `reply_count`, `reply_users` (max 2), `latest_reply_ts`, and `thread_root_id`.

When `can_delete` is true, set a non-empty `delete_action_id`; otherwise the delete control renders but does nothing. Use `user_auth_required` plus `user_auth_url` instead of `comments` if the user must authenticate.

### Posting, editing, and deleting

- Post/edit dispatches `view_submission` with `view.type: "entity_comment"` and callback ID `work-object-post-comment` or `work-object-edit-comment`. The rich input is at `view.state.values.comment_input_block.comment_input_action.rich_text_value`. For edit, `view.external_id` is the comment ID; for new comments it is empty.
- Delete dispatches `block_actions` with `container.type: "entity_comment"`; the action ID is your `delete_action_id`, and `actions[0].value` is the comment ID.
- Acknowledge the interactivity request within 3 seconds, persist externally, then call `entity.acknowledgeCommentAction` with the payload's `trigger_id`.

For a successful post/edit, include the persisted comment; for delete, only `trigger_id`; for failure, send `error` instead of `comment`. This method requires no additional scope and is Tier 3.

### Threaded replies

Set `can_reply: true` on a parent and advertise `reply_count`, up to two `reply_users`, and `latest_reply_ts`. Do not include replies in the top-level comments response. When Slack sends `entity_comments_requested.thread_root_id`, return only that thread's replies and set each reply's `thread_root_id` to the parent comment ID.

## Related conversations, search, and mentions

- The flexpane automatically aggregates conversations where the stable Work Object resource was referenced.
- Enterprise Search/traditional search/AI citation integrations must subscribe to `entity_details_requested` and respond with `entity.presentDetails`; search-origin events may omit `external_ref` and message context.
- The rich-text [`work_object_mention`](RICH-TEXT.md#complete-inline-element-index) element serializes a Work Object reference with required `entity_id`, `app_id`, `text`, and `url`. Treat it as a specialized rich-text reference and validate app-authored use in the target Slack flow.
- Marketplace apps adding the new event subscription require a new Marketplace submission. Existing link-unfurl scopes do not require workspace re-authentication when the app already has them.

## Validation checklist

- Work Object Previews enabled for every emitted entity type.
- Link-unfurl domains and `link_shared` subscription configured.
- `links:read` granted for link events and `links:write` granted for `chat.unfurl`.
- `metadata` URL-encoded only when the transport/SDK requires it.
- `app_unfurl_url` inside each unfurl entity and equal to the shared URL.
- Canonical `url` separated from the shared URL.
- Stable, opaque `external_ref.id`; optional type only when needed.
- `attributes.title` is `{ "text": "..." }`, never a bare string.
- Standard field keys and exact Work Object field shapes used; no invented `display_name` field.
- `actions` inside `entity_payload`; `entity_comments` outside it.
- Public-unfurl content safe for every conversation member.
- Image/PDF previews have the required MIME type and CORS response.
- All interaction requests acknowledged within 3 seconds.
- Comment delete action ID set whenever any comment has `can_delete: true`.
