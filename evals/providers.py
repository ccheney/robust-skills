"""Bounded Gemini requests through its documented Chat Completions endpoint."""

import json
import os
import random
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler

DEFAULT_MODEL = "gemini-3.8-flash"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
TRANSIENT_HTTP = {408, 500, 502, 503, 504}
MAX_RETRIES = 2


class EvalUnavailable(Exception):
    """A provider/configuration limit prevented a scored trial."""


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Gemini:
    def __init__(
        self,
        *,
        max_requests=24,
        interval=15,
        timeout=90,
        max_tokens=4096,
        key=None,
        verified_free_tier=False,
    ):
        self.key = key or os.environ.get("GEMINI_API_KEY", "")
        if not self.key:
            raise EvalUnavailable(
                "No Gemini credentials; configure evals/local.json or GEMINI_API_KEY"
            )
        if not verified_free_tier and os.environ.get("GEMINI_FREE_TIER") != "true":
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
        self.events = []
        self.opener = build_opener(NoRedirects)

    def chat(self, messages, tools):
        if self.halted:
            raise EvalUnavailable(self.halted)
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
        backoff = 0
        for attempt in range(MAX_RETRIES + 1):
            if self.requests >= self.max_requests:
                raise EvalUnavailable(
                    "Run request budget exhausted (including retries)"
                )
            spacing = (
                0
                if self.last_request is None
                else max(0, self.interval - (time.monotonic() - self.last_request))
            )
            if max(spacing, backoff):
                time.sleep(max(spacing, backoff))
            self.requests += 1
            self.last_request = time.monotonic()
            event = {"request": self.requests, "attempt": attempt + 1}
            self.events.append(event)
            try:
                with self.opener.open(req, timeout=self.timeout) as response:
                    result = json.load(response)
            except HTTPError as exc:
                event["status"] = exc.code
                if exc.code not in TRANSIENT_HTTP:
                    self.halted = f"Gemini HTTP {exc.code}; stopped without retry or paid fallback"
                    raise EvalUnavailable(self.halted) from None
                failure = f"Gemini HTTP {exc.code}"
            except (URLError, TimeoutError, OSError):
                event["status"] = "network_error"
                failure = "Gemini network error"
            except ValueError:
                event["status"] = "invalid_response"
                raise EvalUnavailable("Gemini returned invalid JSON") from None
            else:
                event["status"] = 200
                if (
                    not isinstance(result, dict)
                    or not isinstance(result.get("choices"), list)
                    or not result["choices"]
                ):
                    raise EvalUnavailable("Gemini returned no completion choices")
                return result
            finally:
                event["elapsed_seconds"] = round(
                    time.monotonic() - self.last_request, 3
                )
            if attempt == MAX_RETRIES:
                # A transient outage blocks this trial, not all independent later trials.
                raise EvalUnavailable(
                    f"{failure}; exhausted {MAX_RETRIES} retries for this completion"
                )
            backoff = min(30, 2 ** (attempt + 1) + random.random())
            print(
                f"{failure}; retry {attempt + 1}/{MAX_RETRIES} within the request budget",
                file=sys.stderr,
                flush=True,
            )
        raise AssertionError("Unreachable")
