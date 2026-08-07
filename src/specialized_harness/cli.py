"""CLI entry point for specialized-harness."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from specialized_harness.observability.metrics import summarize_runs_dir
from specialized_harness.runner import run_fixture_task


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="specialized-harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run a blueprint against a fixture task")
    run_p.add_argument("--blueprint", required=True)
    run_p.add_argument("--fixture-root", required=True)
    run_p.add_argument("--task", required=True)
    run_p.add_argument("--json", action="store_true")

    met_p = sub.add_parser(
        "metrics",
        help="Summarize offline metrics from persisted run.json files",
    )
    met_p.add_argument(
        "--runs-dir",
        default="artifacts/runs",
        help="Directory containing <run_id>/run.json (default: artifacts/runs)",
    )
    met_p.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.cmd == "run":
        result = run_fixture_task(args.blueprint, args.fixture_root, args.task)
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
                    },
                    indent=2,
                )
            )
        else:
            print(
                f"final_status={result.final_status.value} "
                f"nodes={len(result.trajectory)} total_ms={result.total_ms}"
            )
        return 0 if result.final_status.value in ("ACCEPT", "HUMAN_HANDOFF") else 1

    if args.cmd == "metrics":
        summary = summarize_runs_dir(Path(args.runs_dir))
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
