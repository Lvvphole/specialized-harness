#!/usr/bin/env python3
"""Minimal HTTP propose endpoint for live / rehearsal experiments.

Protocol (HttpAgentProvider):
  Request body: node_id, task, task_brief, round, observations, agent_standard_*, ...
  Response: either {"tool_calls":[...]} or {"mutations":[...], "plan_summary": "..."}

If OPENAI_API_KEY is set, attempts a real model propose (mutations only).
Otherwise: multi-round tool rehearsal that repairs a known harness sample
(samples/repo_add, samples/repo_mul, samples/repo_stats) after reading the target
files via observations (not the in-process ScriptedProvider).

Never declares ACCEPT — harness ledger + CI only (AGENTS.md).
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib import error, request

HOST = os.environ.get("LIVE_PROPOSE_HOST", "127.0.0.1")
PORT = int(os.environ.get("LIVE_PROPOSE_PORT", "8765"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.environ.get("LIVE_PROPOSE_MODEL", "gpt-4.1-mini")


def _openai_propose(body: dict[str, Any]) -> dict[str, Any] | None:
    if not OPENAI_API_KEY:
        return None
    node = body.get("node_id") or "implement"
    task = body.get("task") or body.get("task_brief") or ""
    obs = body.get("observations") or []
    std = (body.get("agent_standard_context") or "")[:4000]
    system = (
        "You are a coding agent behind an authoritative harness. "
        "You may only propose file mutations. You never declare success, "
        "ACCEPT, or PASS. Respond with a single JSON object only.\n"
        'If you need to inspect the repo, respond with:\n'
        '{"tool_calls":[{"id":"t1","name":"list_dir"|"read_file"|"search_code",'
        '"arguments":{...}}]}\n'
        "Allowed tools: list_dir{path}, read_file{path}, search_code{query,path?}.\n"
        'When ready to change code, respond with:\n'
        '{"plan_summary":"...","mutations":[{"path":"rel/path","content":"..."}],'
        '"token_usage":{"prompt":0,"completion":0}}\n'
        "Mutations replace whole files. Prefer minimal correct fixes."
    )
    user = {
        "node_id": node,
        "task": task,
        "task_brief": body.get("task_brief"),
        "round": body.get("round"),
        "observations": obs,
        "last_ci_stdout": body.get("last_ci_stdout"),
        "agent_standard_excerpt": std,
    }
    payload = {
        "model": OPENAI_MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user)},
        ],
    }
    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        content = data["choices"][0]["message"]["content"]
        out = json.loads(content)
        usage = data.get("usage") or {}
        out.setdefault(
            "token_usage",
            {
                "prompt": int(usage.get("prompt_tokens") or 0),
                "completion": int(usage.get("completion_tokens") or 0),
            },
        )
        out["_source"] = "openai"
        return out
    except (
        error.URLError,
        error.HTTPError,
        TimeoutError,
        KeyError,
        json.JSONDecodeError,
        OSError,
    ) as e:
        return {"error": f"openai propose failed: {e}"}


# Rehearsal targets. Each entry is one harness sample the offline (no-key) path
# can repair after reading the workspace. `match` is checked against the lowered
# task + brief; the first entry that matches wins, else the default (repo_add).
_REHEARSAL_ADD = {
    "match": ("add", "repo_add"),
    "query": "def add",
    "reads": ("app.py", "test_app.py"),
    "path": "app.py",
    "plan": "Inspect app.py; fix add to return a+b; leave tests as authority.",
    "implement": "Repair add to return a+b after reading workspace files.",
    "content": (
        "def add(a, b):\n"
        '    """Return the sum of a and b."""\n'
        "    return a + b\n"
    ),
}

_REHEARSAL_TARGETS = (
    {
        "match": ("multiply", "repo_mul"),
        "query": "def multiply",
        "reads": ("app.py", "test_app.py"),
        "path": "app.py",
        "plan": "Inspect app.py; fix multiply to return a*b; leave tests as authority.",
        "implement": "Repair multiply to return a*b after reading workspace files.",
        "content": (
            "def multiply(a, b):\n"
            '    """Return the product of a and b."""\n'
            "    return a * b\n"
        ),
    },
    {
        "match": ("median", "repo_stats"),
        "query": "def median",
        "reads": ("statskit/core.py", "tests/test_core.py"),
        "path": "statskit/core.py",
        "plan": (
            "Inspect statskit/core.py; make median average the two middle values "
            "for even-length input; leave tests as authority."
        ),
        "implement": "Repair median for even-length input after reading workspace files.",
        "content": (
            '"""Descriptive statistics over numeric sequences."""\n'
            "\n"
            "\n"
            "def mean(values):\n"
            '    """Return the arithmetic mean of values."""\n'
            "    if not values:\n"
            '        raise ValueError("mean() requires at least one value")\n'
            "    return sum(values) / len(values)\n"
            "\n"
            "\n"
            "def median(values):\n"
            '    """Return the median of values.\n'
            "\n"
            "    Even-length inputs average the two middle values.\n"
            '    """\n'
            "    if not values:\n"
            '        raise ValueError("median() requires at least one value")\n'
            "    ordered = sorted(values)\n"
            "    mid = len(ordered) // 2\n"
            "    if len(ordered) % 2 == 1:\n"
            "        return ordered[mid]\n"
            "    return (ordered[mid - 1] + ordered[mid]) / 2\n"
        ),
    },
    _REHEARSAL_ADD,
)


def _rehearsal_target(task: str) -> dict[str, Any]:
    for target in _REHEARSAL_TARGETS:
        if any(token in task for token in target["match"]):
            return target
    return _REHEARSAL_ADD


def _rehearsal_propose(body: dict[str, Any]) -> dict[str, Any]:
    """Deterministic multi-round path for the harness samples when no model key is set."""
    node = str(body.get("node_id") or "")
    round_i = int(body.get("round") or 0)
    obs = body.get("observations") or []
    task = f"{body.get('task') or ''} {body.get('task_brief') or ''}".lower()
    target = _rehearsal_target(task)

    if node == "plan" and round_i == 0 and not obs:
        return {
            "tool_calls": [
                {"id": "p1", "name": "list_dir", "arguments": {"path": "."}},
                {"id": "p2", "name": "search_code", "arguments": {"query": target["query"]}},
            ],
            "token_usage": {"prompt": 0, "completion": 0},
            "_source": "rehearsal",
        }
    if node == "plan":
        return {
            "plan_summary": target["plan"],
            "mutations": [],
            "token_usage": {"prompt": 0, "completion": 0},
            "_source": "rehearsal",
        }

    if node == "implement" and round_i == 0 and not obs:
        return {
            "tool_calls": [
                {"id": f"i{i}", "name": "read_file", "arguments": {"path": path}}
                for i, path in enumerate(target["reads"], start=1)
            ],
            "token_usage": {"prompt": 0, "completion": 0},
            "_source": "rehearsal",
        }

    return {
        "plan_summary": target["implement"],
        "mutations": [{"path": target["path"], "content": target["content"]}],
        "token_usage": {"prompt": 12, "completion": 24},
        "_source": "rehearsal",
    }


def handle_propose(body: dict[str, Any]) -> dict[str, Any]:
    if OPENAI_API_KEY:
        out = _openai_propose(body)
        if out is not None:
            return out
    return _rehearsal_propose(body)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[live-propose] {self.address_string()} {fmt % args}")

    def do_POST(self) -> None:  # noqa: N802
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            body = {}
        if not isinstance(body, dict):
            body = {}
        result = handle_propose(body)
        data = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    mode = "openai" if OPENAI_API_KEY else "rehearsal"
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"[live-propose] listening on http://{HOST}:{PORT}/ mode={mode}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
