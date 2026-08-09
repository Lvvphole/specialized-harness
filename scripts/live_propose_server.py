#!/usr/bin/env python3
"""Minimal HTTP propose endpoint for live / rehearsal experiments.

Protocol (HttpAgentProvider):
  Request body: node_id, task, task_brief, round, observations, agent_standard_*, ...
  Response: either {"tool_calls":[...]} or {"mutations":[...], "plan_summary": "..."}

If OPENAI_API_KEY is set, attempts a real model propose (mutations only).
Otherwise: multi-round tool rehearsal that repairs the known samples/repo_add or
samples/repo_mul bug after reading app.py via observations (not in-process ScriptedProvider).

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


def _rehearsal_propose(body: dict[str, Any]) -> dict[str, Any]:
    """Deterministic multi-round path for samples/repo_add and samples/repo_mul when no model key."""
    node = str(body.get("node_id") or "")
    round_i = int(body.get("round") or 0)
    obs = body.get("observations") or []
    task = f"{body.get('task') or ''} {body.get('task_brief') or ''}".lower()
    wants_mul = "multiply" in task or "repo_mul" in task

    if node == "plan" and round_i == 0 and not obs:
        query = "def multiply" if wants_mul else "def add"
        return {
            "tool_calls": [
                {"id": "p1", "name": "list_dir", "arguments": {"path": "."}},
                {"id": "p2", "name": "search_code", "arguments": {"query": query}},
            ],
            "token_usage": {"prompt": 0, "completion": 0},
            "_source": "rehearsal",
        }
    if node == "plan":
        summary = (
            "Inspect app.py; fix multiply to return a*b; leave tests as authority."
            if wants_mul
            else "Inspect app.py; fix add to return a+b; leave tests as authority."
        )
        return {
            "plan_summary": summary,
            "mutations": [],
            "token_usage": {"prompt": 0, "completion": 0},
            "_source": "rehearsal",
        }

    if node == "implement" and round_i == 0 and not obs:
        return {
            "tool_calls": [
                {"id": "i1", "name": "read_file", "arguments": {"path": "app.py"}},
                {"id": "i2", "name": "read_file", "arguments": {"path": "test_app.py"}},
            ],
            "token_usage": {"prompt": 0, "completion": 0},
            "_source": "rehearsal",
        }

    if wants_mul:
        fixed = (
            "def multiply(a, b):\n"
            '    """Return the product of a and b."""\n'
            "    return a * b\n"
        )
        return {
            "plan_summary": "Repair multiply to return a*b after reading workspace files.",
            "mutations": [{"path": "app.py", "content": fixed}],
            "token_usage": {"prompt": 12, "completion": 24},
            "_source": "rehearsal",
        }

    fixed = (
        "def add(a, b):\n"
        '    """Return the sum of a and b."""\n'
        "    return a + b\n"
    )
    return {
        "plan_summary": "Repair add to return a+b after reading workspace files.",
        "mutations": [{"path": "app.py", "content": fixed}],
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
