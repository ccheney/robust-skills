"""Targeted payload/markup constraints in addition to each case's content assertions."""

import json
import subprocess
import tempfile
from pathlib import Path
from html.parser import HTMLParser
from evals.checks import at


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def slack(output, config):
    payload = at(output, config.get("payload_path", []))
    if not isinstance(payload, dict):
        return [
            {
                "id": "slack-payload",
                "passed": False,
                "detail": "Expected an object payload",
            }
        ]
    surface = config.get("surface", "message")
    blocks = payload.get("blocks", [])
    if not isinstance(blocks, list):
        return [
            {"id": "slack-blocks", "passed": False, "detail": "blocks must be an array"}
        ]
    flags = {
        k: True
        for k in [
            "slack-block-count",
            "slack-surface",
            "slack-text-objects",
            "slack-ids",
            "slack-table-shape",
            "slack-markdown-budget",
            "slack-method-fields",
        ]
    }
    flags["slack-block-count"] = len(blocks) <= (50 if surface == "message" else 100)
    allowed = {
        "actions",
        "context",
        "divider",
        "header",
        "image",
        "input",
        "rich_text",
        "section",
        "video",
        "card",
    }
    allowed |= {"alert"} if surface == "modal" else {"carousel", "data_table", "table"}
    if surface == "message":
        allowed |= {
            "container",
            "context_actions",
            "data_visualization",
            "markdown",
            "plan",
            "task_card",
        }
    all_blocks = []

    def collect(items):
        for block in items:
            if not isinstance(block, dict):
                flags["slack-surface"] = False
                continue
            all_blocks.append(block)
            if block.get("type") not in allowed:
                flags["slack-surface"] = False
            if "child_blocks" in block:
                if not isinstance(block["child_blocks"], list):
                    flags["slack-surface"] = False
                else:
                    collect(block["child_blocks"])

    collect(blocks)
    ids = [
        b["block_id"]
        for b in all_blocks
        if "block_id" in b and b.get("type") != "markdown"
    ]
    flags["slack-ids"] = all(isinstance(i, str) and len(i) <= 255 for i in ids) and len(
        set(map(str, ids))
    ) == len(ids)
    markdown = 0
    for block in all_blocks:
        kind = block.get("type")
        if kind == "header":
            text = block.get("text", {})
            flags["slack-text-objects"] &= (
                isinstance(text, dict)
                and text.get("type") == "plain_text"
                and isinstance(text.get("text"), str)
                and 1 <= len(text["text"]) <= 150
            )
        if kind == "section":
            flags["slack-text-objects"] &= "text" in block or bool(block.get("fields"))
            fields = block.get("fields", [])
            flags["slack-text-objects"] &= (
                isinstance(fields, list)
                and len(fields) <= 10
                and all(
                    isinstance(f, dict)
                    and isinstance(f.get("text"), str)
                    and len(f["text"]) <= 2000
                    for f in fields
                )
            )
        if kind == "markdown":
            text = block.get("text")
            flags["slack-markdown-budget"] &= isinstance(text, str)
            if isinstance(text, str):
                markdown += len(text)
        if kind in ("table", "data_table"):
            rows = block.get("rows")
            valid = (
                isinstance(rows, list)
                and bool(rows)
                and len(rows) <= (201 if kind == "data_table" else 100)
            )
            if valid:
                valid = all(
                    isinstance(row, list)
                    and 1 <= len(row) <= 20
                    and all(
                        isinstance(c, dict)
                        and c.get("type") in ("raw_text", "raw_number", "rich_text")
                        for c in row
                    )
                    for row in rows
                )
            if kind == "data_table" and valid:
                valid = (
                    isinstance(block.get("caption"), str)
                    and bool(block["caption"])
                    and len({len(row) for row in rows}) == 1
                    and all(c.get("type") != "rich_text" for c in rows[0])
                )
            flags["slack-table-shape"] &= valid and "columns" not in block
    flags["slack-markdown-budget"] &= markdown <= 12000
    for obj in walk(payload):
        if obj.get("type") in ("plain_text", "mrkdwn"):
            text = obj.get("text")
            flags["slack-text-objects"] &= (
                isinstance(text, str) and 1 <= len(text) <= 3000
            )
            flags["slack-text-objects"] &= not (
                obj["type"] == "plain_text" and "verbatim" in obj
            ) and not (obj["type"] == "mrkdwn" and "emoji" in obj)
        if obj.get("type") == "button":
            text = obj.get("text", {})
            flags["slack-text-objects"] &= (
                isinstance(text, dict)
                and text.get("type") == "plain_text"
                and isinstance(text.get("text"), str)
                and len(text["text"]) <= 75
            )
    if (
        config.get("method")
        in (
            "chat.postMessage",
            "chat.update",
            "chat.scheduleMessage",
            "chat.postEphemeral",
        )
        and "markdown_text" in output
    ):
        flags["slack-method-fields"] = not any(k in output for k in ("text", "blocks"))
    return [{"id": id, "passed": bool(ok), "detail": id} for id, ok in flags.items()]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.tags = []
        self.mentions = []
        self.links = []
        self.active = None
        self.bold_depth = 0
        self.bold = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if tag in ("b", "strong"):
            self.bold_depth += 1
        if tag == "at":
            self.active = {"id": attrs.get("id"), "text": ""}
            self.mentions.append(self.active)
        if tag == "a":
            self.links.append(attrs.get("href"))

    def handle_endtag(self, tag):
        if tag == "at":
            self.active = None
        if tag in ("b", "strong"):
            self.bold_depth = max(0, self.bold_depth - 1)

    def handle_data(self, data):
        self.text.append(data)
        if self.bold_depth:
            self.bold.append(data)
        if self.active is not None:
            self.active["text"] += data


def markup_data(output, config):
    text = at(output, config["text_path"])
    if not isinstance(text, str):
        return {"valid": False}
    parsed = Markup()
    parsed.feed(text)
    result = {
        "text": "".join(parsed.text),
        "tags": parsed.tags,
        "links": parsed.links,
        "mentions": parsed.mentions,
        "valid": True,
        "bold_text": "".join(parsed.bold),
    }
    if config.get("graph_mentions"):
        mentions = output.get("mentions", [])
        result["mentions_consistent"] = (
            isinstance(mentions, list)
            and len(mentions) == len(parsed.mentions)
            and all(
                any(
                    str(m.get("id")) == p["id"] and m.get("mentionText") == p["text"]
                    for m in mentions
                    if isinstance(m, dict)
                )
                for p in parsed.mentions
            )
        )
    return result


def teams(root, output, config):
    with tempfile.TemporaryDirectory(prefix="teams-contract-") as directory:
        file = Path(directory) / "card.json"
        file.write_text(json.dumps(output))
        try:
            run = subprocess.run(
                [
                    "node",
                    str(
                        root
                        / "skills/teams-adaptive-cards/scripts/check-teams-card.mjs"
                    ),
                    "--target",
                    config.get("target", "card"),
                    str(file),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return {"status": "blocked", "detail": "Teams payload checker unavailable"}
        return [
            {
                "id": "teams-wire-contract",
                "passed": run.returncode == 0,
                "detail": run.stdout[-1000:],
            }
        ]
