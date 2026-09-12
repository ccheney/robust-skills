# Slack Message Parsing and Fallbacks

## Contents

- Links and Unfurls
- Top-Level Message Text and Parsing
- Accessibility and Notification Fallbacks
- Legacy Secondary Attachments

## Links and Unfurls

```text
https://example.com
<https://example.com>
<https://example.com|Display text>
<mailto:user@example.com|Email user>
```

Raw URLs in mrkdwn are normally auto-transformed into links. URLs containing spaces break parsing; remove or URL-encode the spaces. When messages are retrieved, Slack returns auto-transformed URLs in angle-bracket form, sometimes with an explicit label.

Slack normally unfurls links posted by users and apps, including media links in Block Kit blocks. For publishing methods that expose these parameters:

| Parameter | Controls |
|---|---|
| `unfurl_links` | Primarily text-based content |
| `unfurl_media` | Media such as images, video, and audio |

Set both to `false` to suppress all link previews. For messages containing LLM-generated URLs, disable unfurls by default with both `unfurl_links: false` and `unfurl_media: false`: Slack warns that its outbound preview request can complete prompt-injection data exfiltration. If previews are required, allow-list trusted external domains and reject or report URLs outside that list. Slack does not unfurl a manually labeled link when the label is a complete substring of the URL after removing the protocol (for example, `<http://example.com|example.com>`). Streaming messages do not unfurl links.

Custom app unfurls use the renderer of each receiving field. Composer preview `elements` can contain an object with `type: "mrkdwn"`; blocks within the unfurl use their normal text-object rules. Exception: `chat.unfurl` does not currently support rich-text blocks and may return `invalid_blocks` for an otherwise valid Block Kit payload containing a rich-text section element. A `chat.unfurl` `user_auth_message` supports simple Slack formatting, while `user_auth_blocks` supplies a Block Kit alternative. Work Object entity metadata remains a separate standard-Markdown case as described above.

## Top-Level Message Text and Parsing

When a message has no `blocks`, top-level `text` is the rendered body and uses mrkdwn by default. When `blocks` are present, top-level `text` is a fallback rather than visible block content.

For `chat.postMessage`:

| Setting | Current documented effect |
|---|---|
| default `parse` | mrkdwn is applied; raw URLs are hyperlinked |
| `parse: "none"` | mrkdwn is still applied; raw URL hyperlinking is disabled |
| `parse: "full"` | mrkdwn formatting is ignored |
| `mrkdwn: false` | Disables mrkdwn processing for top-level `text` |
| `link_names: true` | Finds and links user groups; no individual-user linking |

Use explicit ID-based syntax and disable unwanted preprocessing. Slack's formatting guide recommends manual parsing because names can change and automatic parsing can turn third-party input into unintended notifications.

For best results, keep top-level `text` under 4,000 characters. Slack truncates messages over 40,000 characters. Blocks have their own limits.

## Accessibility and Notification Fallbacks

Screen readers default to the message's top-level `text` and do not read interior blocks directly. With `blocks`, Slack documents two accessible approaches:

1. Include every necessary piece of content in top-level `text`.
2. Omit top-level `text` and let Slack attempt to synthesize it from supported blocks.

Prefer an explicit, complete textual summary when notification and assistive-technology parity matters.

Notification behavior changed in July 2026:

- Desktop notifications extract text from supported blocks first, then fall back to `message.text` if nothing can be extracted.
- Mobile notifications exclusively use `message.text`.

Do not assume a richly formatted block layout will produce a complete mobile notification or screen-reader experience.

## Legacy Secondary Attachments

Secondary attachments are legacy. Prefer Block Kit for new development. Legacy fields can be subject to reduced visibility or functionality.

- `mrkdwn_in` is an array naming attachment fields to format as mrkdwn. The documented mrkdwn-capable legacy content is `text`, `pretext`, and field-object `value`s via `fields`.
- A field-object `title` cannot contain markup and is escaped.
- `fallback` is a plain-text summary for clients that do not show formatted attachment content.
- Without attachment `blocks`, one of `fallback` or `text` is required.
- Attachment `text` collapses at 700+ characters or 5+ line breaks.
- Slack allows no more than 20 attachments in a message.

```json
{
  "fallback": "Deployment completed",
  "text": "Deployment *completed*",
  "mrkdwn_in": ["text"]
}
```

## Sources

- https://docs.slack.dev/reference/methods/chat.postMessage/
- https://docs.slack.dev/messaging/unfurling-links-in-messages/
- https://docs.slack.dev/changelog/2026/07/13/notification-changes/
- https://docs.slack.dev/legacy/legacy-messaging/legacy-secondary-message-attachments/
