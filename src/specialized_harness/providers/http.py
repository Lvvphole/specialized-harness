"""HTTP AgentProvider — multi-round tool protocol + final AgentProposal.

Remote may request list_dir / read_file / search_code; the harness validates and
executes against the sandbox only, then returns observations for the next round.
Mutations are never applied by the provider. ACCEPT remains ledger + CI only.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from specialized_harness.providers.base import AgentProposal, FileMutation
from specialized_harness.providers.context import ALLOWED_TOOLS, build_propose_body
from specialized_harness.providers.tokens import normalize_token_usage
from specialized_harness.sandboxes.workspace import WorkspaceError

DEFAULT_MAX_TOOL_ROUNDS = 8
ALLOWED_TOOL_SET = frozenset(ALLOWED_TOOLS)


class HttpAgentProvider:
    """POST JSON multi-round propose ↔ tool_calls / observations → AgentProposal."""

    def __init__(
        self,
        endpoint: str,
        *,
        timeout_s: float = 30.0,
        opener: Any = None,
        max_tool_rounds: int | None = None,
    ) -> None:
        if not endpoint:
            raise ValueError("HttpAgentProvider requires a non-empty endpoint URL")
        self.endpoint = endpoint
        self.timeout_s = timeout_s
        self._opener = opener
        self._max_tool_rounds_override = max_tool_rounds

    def propose(self, node_id: str, context: dict[str, Any]) -> AgentProposal:
        max_rounds = self._resolve_max_tool_rounds(context)
        inspect = context.get("repo_inspect")
        observations: list[dict[str, Any]] | None = None
        all_tool_meta: list[dict[str, Any]] = []
        agg_tokens: dict[str, int] = {}
        total_http_ms = 0
        rounds_used = 0

        for round_i in range(max_rounds):
            body = build_propose_body(
                node_id,
                context,
                round=round_i,
                observations=observations,
                max_tool_rounds=max_rounds,
            )
            t0 = time.perf_counter()
            payload, err = self._post_once(body)
            total_http_ms += int((time.perf_counter() - t0) * 1000)
            rounds_used = round_i + 1

            if err is not None:
                return AgentProposal(
                    error=err,
                    metadata=self._round_meta(
                        agg_tokens, all_tool_meta, rounds_used, total_http_ms
                    ),
                )

            tokens = normalize_token_usage(payload.get("token_usage"))
            for k, v in tokens.items():
                agg_tokens[k] = agg_tokens.get(k, 0) + v

            if payload.get("error"):
                return AgentProposal(
                    error=f"http provider error: {payload.get('error')}",
                    metadata=self._round_meta(
                        agg_tokens, all_tool_meta, rounds_used, total_http_ms
                    ),
                )

            tool_calls = payload.get("tool_calls") or []
            if tool_calls:
                if round_i >= max_rounds - 1:
                    return AgentProposal(
                        error=f"max_tool_rounds exceeded ({max_rounds})",
                        metadata=self._round_meta(
                            agg_tokens, all_tool_meta, rounds_used, total_http_ms
                        ),
                    )
                observations = self._execute_tools(tool_calls, inspect)
                all_tool_meta.append(
                    {
                        "round": round_i,
                        "tool_calls": tool_calls,
                        "observations": observations,
                    }
                )
                continue

            mutations = self._parse_mutations(payload)
            meta = self._round_meta(
                agg_tokens, all_tool_meta, rounds_used, total_http_ms
            )
            return AgentProposal(
                mutations=mutations,
                plan_summary=str(payload.get("plan_summary") or ""),
                metadata=meta,
            )

        return AgentProposal(
            error=f"max_tool_rounds exceeded ({max_rounds})",
            metadata=self._round_meta(
                agg_tokens, all_tool_meta, rounds_used, total_http_ms
            ),
        )

    def _resolve_max_tool_rounds(self, context: dict[str, Any]) -> int:
        if self._max_tool_rounds_override is not None:
            return max(1, int(self._max_tool_rounds_override))
        policy = context.get("policy")
        if policy is not None and hasattr(policy, "max_tool_rounds"):
            return max(1, int(policy.max_tool_rounds))
        return DEFAULT_MAX_TOOL_ROUNDS

    def _post_once(
        self, body: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, str | None]:
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
            if not isinstance(payload, dict):
                return None, "http provider failed: response is not a JSON object"
            return payload, None
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            json.JSONDecodeError,
            OSError,
            TypeError,
            ValueError,
        ) as e:
            return None, f"http provider failed: {e}"

    def _execute_tools(
        self,
        tool_calls: list[Any],
        inspect: Any,
    ) -> list[dict[str, Any]]:
        observations: list[dict[str, Any]] = []
        for tc in tool_calls:
            if not isinstance(tc, dict):
                observations.append(
                    {"ok": False, "error": "tool_call must be an object"}
                )
                continue
            name = str(tc.get("name") or tc.get("tool") or "")
            call_id = tc.get("id")
            args = tc.get("arguments") if "arguments" in tc else tc.get("args")
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            if not isinstance(args, dict):
                args = {}

            base = {"tool_call_id": call_id, "name": name}
            if name not in ALLOWED_TOOL_SET:
                observations.append(
                    {**base, "ok": False, "error": f"tool not allowed: {name}"}
                )
                continue
            if inspect is None:
                observations.append(
                    {
                        **base,
                        "ok": False,
                        "error": "no repo_inspect in context (sandbox not provisioned)",
                    }
                )
                continue
            try:
                if name == "list_dir":
                    result: Any = inspect.list_dir(str(args.get("path", ".")))
                elif name == "read_file":
                    result = inspect.read_file(str(args.get("path", "")))
                else:  # search_code
                    result = inspect.search_code(
                        str(args.get("query", "")),
                        str(args.get("path", ".")),
                    )
                observations.append({**base, "ok": True, "result": result})
            except (WorkspaceError, OSError, TypeError, ValueError) as e:
                observations.append({**base, "ok": False, "error": str(e)})
        return observations

    def _parse_mutations(self, payload: dict[str, Any]) -> list[FileMutation]:
        mutations: list[FileMutation] = []
        for m in payload.get("mutations") or []:
            if not isinstance(m, dict) or "path" not in m:
                continue
            mutations.append(
                FileMutation(path=str(m["path"]), content=m.get("content"))
            )
        return mutations

    def _round_meta(
        self,
        agg_tokens: dict[str, int],
        all_tool_meta: list[dict[str, Any]],
        rounds_used: int,
        total_http_ms: int,
    ) -> dict[str, Any]:
        meta: dict[str, Any] = {
            "provider": "HttpAgentProvider",
            "endpoint": self.endpoint,
            "http_rounds": rounds_used,
            "total_http_ms": total_http_ms,
            "tool_rounds": all_tool_meta,
        }
        if agg_tokens:
            meta["token_usage"] = dict(agg_tokens)
        tools: list[str] = []
        for rnd in all_tool_meta:
            for tc in rnd.get("tool_calls") or []:
                if isinstance(tc, dict):
                    name = str(tc.get("name") or tc.get("tool") or "")
                    if name:
                        tools.append(name)
        if tools:
            meta["tools_called"] = tools
        return meta


def resolve_provider(
    *,
    provider: str | None = None,
    provider_url: str | None = None,
    env: dict[str, str] | None = None,
) -> Any:
    """Select AgentProvider: explicit name/url, else env, else ScriptedProvider.

    Names: scripted | http
    HARNESS_PROVIDER / HARNESS_PROVIDER_URL still supported for operators.
    """
    from specialized_harness.providers.scripted import ScriptedProvider

    e = env if env is not None else os.environ
    name = (provider or e.get("HARNESS_PROVIDER") or "").strip().lower()
    url = (
        provider_url
        if provider_url is not None
        else e.get("HARNESS_PROVIDER_URL") or ""
    ).strip()
    timeout = float(e.get("HARNESS_PROVIDER_TIMEOUT", "30"))

    if name in ("", "scripted", "default"):
        if url and not provider:
            return HttpAgentProvider(url, timeout_s=timeout)
        return ScriptedProvider()
    if name == "http":
        if not url:
            raise ValueError(
                "provider=http requires provider_url or HARNESS_PROVIDER_URL"
            )
        return HttpAgentProvider(url, timeout_s=timeout)
    raise ValueError(f"unknown provider: {name!r} (supported: scripted, http)")


def provider_from_env(
    env: dict[str, str] | None = None,
) -> Any:
    """Backward-compatible: HARNESS_PROVIDER_URL → HTTP; else Scripted."""
    return resolve_provider(env=env)
