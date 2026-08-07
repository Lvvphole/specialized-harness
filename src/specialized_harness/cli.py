"""CLI entry point for specialized-harness."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from specialized_harness.runner import run_fixture_task


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="specialized-harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run a blueprint against a fixture task")
    run_p.add_argument("--blueprint", required=True)
    run_p.add_argument("--fixture-root", required=True)
    run_p.add_argument("--task", required=True)
    run_p.add_argument("--json", action="store_true")

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
                    },
                    indent=2,
                )
            )
        else:
            print(f"final_status={result.final_status.value} nodes={len(result.trajectory)}")
        return 0 if result.final_status.value in ("ACCEPT", "HUMAN_HANDOFF") else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
