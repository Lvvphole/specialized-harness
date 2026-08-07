"""HTTP AgentProvider — proposals from an external endpoint (env-gated).

Harness still applies mutations via apply_proposal and decides ACCEPT independently.
Never treats model/HTTP text as success.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from specialized_harness.providers.base import AgentProposal, FileMutation


class HttpAgentProvider:
    """POST JSON {node_id, task, run_id} → {mutations, plan_summary}."""

    def __init__(
        self,
        endpoint: str,
        *,
        timeout_s: float = 30.0,
        opener: Any = None,
    ) -> None:
        if not endpoint:
            raise ValueError("HttpAgentProvider requires a non-empty endpoint URL")
        self.endpoint = endpoint
        self.timeout_s = timeout_s
        self._opener = opener  # injectable for tests

    def propose(self, node_id: str, context: dict[str, Any]) -> AgentProposal:
        body = {
            "node_id": node_id,
            "task": context.get("task"),
            "run_id": context.get("run_id"),
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            if self._opener is not None:
                raw = self._opener(req, timeout=self.timeout_s)
            else:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    raw = resp.read()
            if isinstance(raw, bytes):
                payload = json.loads(raw.decode("utf-8"))
            else:
                payload = json.loads(raw)
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            json.JSONDecodeError,
            OSError,
        ) as e:
            return AgentProposal(error=f"http provider failed: {e}")

        mutations: list[FileMutation] = []
        for m in payload.get("mutations") or []:
            if not isinstance(m, dict) or "path" not in m:
                continue
            mutations.append(
                FileMutation(path=str(m["path"]), content=m.get("content"))
            )
        return AgentProposal(
            mutations=mutations,
            plan_summary=str(payload.get("plan_summary") or ""),
            metadata={"provider": "HttpAgentProvider", "endpoint": self.endpoint},
        )


def provider_from_env(
    env: dict[str, str] | None = None,
) -> Any:
    """Return HttpAgentProvider if HARNESS_PROVIDER_URL is set; else ScriptedProvider."""
    from specialized_harness.providers.scripted import ScriptedProvider

    e = env if env is not None else os.environ
    url = (e.get("HARNESS_PROVIDER_URL") or "").strip()
    if not url:
        return ScriptedProvider()
    timeout = float(e.get("HARNESS_PROVIDER_TIMEOUT", "30"))
    return HttpAgentProvider(url, timeout_s=timeout)
