# Streaming Agent Output

Use `chat.startStream`, `chat.appendStream`, and `chat.stopStream` for live AI responses (all require `chat:write`). Start requires `channel` and `thread_ts`—streamed messages should reply to a user request. Append always requires `channel` and the streaming message `ts`; send at least one of `markdown_text` or `chunks` under the official SDK contract described below. Stop requires `channel` and `ts`. When streaming to channels, start also requires `recipient_user_id` and `recipient_team_id`.

`chunks` (accepted by all three methods) can include:
- `markdown_text` chunks — `{ "type": "markdown_text", "text": "standard Markdown" }` (the chunk field is `text`, unlike the top-level `markdown_text` argument)
- `task_update` chunks — flat `id`, `title`, `status` (`pending`/`in_progress`/`complete`/`error`), optional string `details`/`output`, and URL `sources`
- `plan_update` chunks — flat `title`
- `blocks` chunks — `blocks` array (max 50; extras are dropped with a warning)

`task_update` and `plan_update` chunk fields are limited to 256 characters.

Set `task_display_mode` on `chat.startStream`:
- `timeline` (default): tasks appear individually in sequence
- `plan`: tasks grouped in one plan; first task placement determines plan placement
- `dense`: consecutive tool calls collapse into a single summarized task card

All three method references accept `blocks` chunks inside `chunks`. Only `chat.stopStream` accepts a top-level `blocks` argument, rendered below the finalized stream. Its separate 50-block limit is distinct from a streamed blocks chunk; do not infer that start/append accept top-level blocks. Rate limits: start/stop Tier 2 (20+/min), append Tier 4 (100+/min).

Streaming messages do not unfurl links.

Slack's current sources contradict one another on `chat.appendStream`: the Web API argument table marks `markdown_text` required and `chunks` optional; the official Node SDK interface marks both optional but states that either `markdown_text` or `chunks` is required; the Python SDK signature accepts both as optional; and the Developing an agent guide shows a chunks-only append. For SDK calls, provide at least one of `markdown_text` or `chunks` as the Node contract directs. Raw-HTTP callers should check the current method schema before omitting `markdown_text` and include it whenever that schema still marks it required. The guide also contains alternate nested chunk shapes, so validate chunk payloads against the current method reference and SDK model.


## Sources

- [Streaming guide](https://docs.slack.dev/ai/developing-agents/#streaming)
- [chat.startStream](https://docs.slack.dev/reference/methods/chat.startStream/)
- [chat.appendStream](https://docs.slack.dev/reference/methods/chat.appendStream/)
- [chat.stopStream](https://docs.slack.dev/reference/methods/chat.stopStream/)
- [Node SDK contract](https://docs.slack.dev/tools/node-slack-sdk/reference/web-api/interfaces/ChatAppendStreamArguments/)
