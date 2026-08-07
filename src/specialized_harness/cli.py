"""CLI entry point for specialized-harness (operator + vibe-coder UX)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from specialized_harness.cli_summary import format_run_summary
from specialized_harness.config import load_config
from specialized_harness.observability.metrics import summarize_runs_dir
from specialized_harness.observability.persistence import load_run
from specialized_harness.providers.http import resolve_provider
from specialized_harness.runner import run_fixture_task

# Errors that mean "the operator asked for something impossible", not "the
# harness broke". These are reported as a one-line message; anything else keeps
# its traceback, because an unexpected exception is an infrastructure failure.
USAGE_ERRORS = (ValueError, FileNotFoundError)


def _resolve_run_args(args: argparse.Namespace, cfg) -> dict:
    task = args.task or getattr(args, "task_pos", None)
    blueprint = args.blueprint or cfg.blueprint
    fixture_root = args.fixture_root or args.repo or cfg.resolved_fixture_root()
    provider = (args.provider or cfg.provider or "scripted").strip().lower()
    provider_url = args.provider_url or cfg.provider_url
    runs_dir = args.runs_dir or cfg.runs_dir

    missing = []
    if not task:
        missing.append("task (positional or --task)")
    if not blueprint:
        missing.append("--blueprint or config.blueprint")
    if not fixture_root:
        missing.append("--fixture-root / --repo or config.fixture_root")
    if missing:
        raise SystemExit(
            "missing required options: "
            + "; ".join(missing)
            + "\n(hint: add a .specialized-harness.yaml or pass flags)"
        )
    return {
        "task": task,
        "blueprint": blueprint,
        "fixture_root": fixture_root,
        "provider": provider,
        "provider_url": provider_url,
        "runs_dir": runs_dir,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="specialized-harness",
        description=(
            "Governed coding runs: model proposes; harness verifies and decides."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser(
        "run",
        help="Run a blueprint (defaults from .specialized-harness.yaml)",
    )
    run_p.add_argument(
        "task_pos",
        nargs="?",
        default=None,
        help="Task name (shortcut for --task)",
    )
    run_p.add_argument("--task", default=None, help="Task / fixture name")
    run_p.add_argument("--blueprint", default=None)
    run_p.add_argument("--fixture-root", default=None)
    run_p.add_argument(
        "--repo",
        default=None,
        help="Repo or fixture root (alias of --fixture-root)",
    )
    run_p.add_argument(
        "--provider",
        default=None,
        help="Proposal source: scripted | http (default: config or scripted)",
    )
    run_p.add_argument("--provider-url", default=None)
    run_p.add_argument("--config", default=None, help="Path to YAML config")
    run_p.add_argument(
        "--runs-dir",
        default=None,
        help="Where to write run.json (default: artifacts/runs)",
    )
    run_p.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable output instead of human summary",
    )

    met_p = sub.add_parser(
        "metrics",
        help="Summarize offline metrics from persisted run.json files",
    )
    met_p.add_argument(
        "--runs-dir",
        default=None,
        help="Directory containing <run_id>/run.json (default: config.runs_dir)",
    )
    met_p.add_argument("--config", default=None, help="Path to YAML config")
    met_p.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        try:
            cfg = load_config(args.config)
            resolved = _resolve_run_args(args, cfg)
            # Resolved here rather than inside the runner so an unknown provider
            # or a missing provider URL is reported before any run starts.
            provider = resolve_provider(
                provider=resolved["provider"],
                provider_url=resolved["provider_url"],
            )
        except USAGE_ERRORS as e:
            raise SystemExit(f"error: {e}") from e
        result = run_fixture_task(
            resolved["blueprint"],
            resolved["fixture_root"],
            resolved["task"],
            runs_dir=resolved["runs_dir"],
            provider=provider,
        )
        claims: list = []
        run_json = Path(resolved["runs_dir"]) / result.run_id / "run.json"
        if run_json.is_file():
            claims = load_run(run_json).get("claims") or []

        if args.json:
            print(
                json.dumps(
                    {
                        "run_id": result.run_id,
                        "final_status": result.final_status.value,
                        "trajectory_len": len(result.trajectory),
                        "nodes": [e.node_id for e in result.trajectory],
                        "error": result.error,
                        "total_ms": result.total_ms,
                        "task": resolved["task"],
                        "provider": resolved["provider"],
                        "claims": claims,
                    },
                    indent=2,
                )
            )
        else:
            print(
                format_run_summary(
                    result,
                    task=resolved["task"],
                    provider=resolved["provider"],
                    claims=claims,
                    runs_dir=resolved["runs_dir"],
                )
            )
        return 0 if result.final_status.value in ("ACCEPT", "HUMAN_HANDOFF") else 1

    if args.cmd == "metrics":
        try:
            # `run` writes to config.runs_dir, so `metrics` must read from the
            # same place or it silently reports on a directory nobody wrote to.
            runs_dir = args.runs_dir or load_config(args.config).runs_dir
        except USAGE_ERRORS as e:
            raise SystemExit(f"error: {e}") from e
        summary = summarize_runs_dir(Path(runs_dir))
        data = summary.to_dict()
        if args.json:
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(
                f"runs={data['runs']} accept={data['accept']} "
                f"handoff={data['human_handoff']} failed={data['failed']} "
                f"mean_total_ms={data['mean_total_ms']}"
            )
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
