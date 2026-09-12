"""Bounded Gemini requests through its documented Chat Completions endpoint."""

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler

DEFAULT_MODEL = "gemini-3.8-flash"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


class EvalUnavailable(Exception):
    """A provider/configuration limit prevented a scored trial."""


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Gemini:
    def __init__(self, *, max_requests=24, interval=15, timeout=90, max_tokens=4096):
        self.key = os.environ.get("GEMINI_API_KEY", "")
        if not self.key:
            raise EvalUnavailable("GEMINI_API_KEY is missing; no live evaluations ran")
        if os.environ.get("GEMINI_FREE_TIER") != "true":
            raise EvalUnavailable(
                "Set GEMINI_FREE_TIER=true only for a key from a project without billing"
            )
        self.max_requests = max_requests
        self.interval = interval
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.requests = 0
        self.last_request = None
        self.halted = None
        self.model = DEFAULT_MODEL
        self.opener = build_opener(NoRedirects)

    def chat(self, messages, tools):
        if self.halted:
            raise EvalUnavailable(self.halted)
        if self.requests >= self.max_requests:
            raise EvalUnavailable("Run request budget exhausted")
        if self.last_request is not None:
            time.sleep(max(0, self.interval - (time.monotonic() - self.last_request)))
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "reasoning_effort": "low",
            "stream": False,
        }
        if tools:
            payload.update(tools=tools, tool_choice="auto")
        req = Request(
            ENDPOINT,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "x-goog-api-client": "robust-skills-evals/1.0",
            },
        )
        self.requests += 1
        self.last_request = time.monotonic()
        try:
            with self.opener.open(req, timeout=self.timeout) as response:
                result = json.load(response)
        except HTTPError as exc:
            # Do not log response bodies or request headers, and never change providers.
            self.halted = (
                f"Gemini HTTP {exc.code}; run stopped without retry or paid fallback"
            )
            raise EvalUnavailable(self.halted) from None
        except (URLError, TimeoutError, OSError, ValueError):
            self.halted = "Gemini network or response error; run stopped without retry"
            raise EvalUnavailable(self.halted) from None
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("choices"), list)
            or not result["choices"]
        ):
            self.halted = "Gemini returned no completion choices"
            raise EvalUnavailable(self.halted)
        return result
