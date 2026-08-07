#!/usr/bin/env python3
"""Advisory Codex/OpenAI PR review for specialized-harness.

Writes /tmp/codex-review.md. Never declares merge authority.
Respects AGENTS.md: model is not authority; human merges only.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

OUT = Path("/tmp/codex-review.md")

SYSTEM = """You are an advisory code reviewer for specialized-harness, an authoritative
coding-agent harness (AGENTS.md). The coding model is NOT the authority.

Focus on:
1. Does the change weaken independent ACCEPT (ledger/CI/decide)?
2. Path escape / sandbox isolation regressions?
3. Provider writing success claims or applying mutations outside harness?
4. Missing tests for new behavior?
5. Scope creep vs Minimum Sufficient Harness?

Be concise. Bullet findings. Say "No blocking concerns" if none.
You do NOT approve merges. End with: "Human review required before merge (AGENTS.md \u00a78)."
"""


def main() -> int:
    diff_path = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/pr.bounded.diff")
    diff = (
        diff_path.read_text(encoding="utf-8", errors="replace")
        if diff_path.is_file()
        else ""
    )
    if not diff.strip():
        OUT.write_text(
            "## Codex advisory review\n\n_Empty diff \u2014 nothing to review._\n\n"
            "Human review required before merge (AGENTS.md \u00a78).\n",
            encoding="utf-8",
        )
        return 0

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        OUT.write_text(
            "## Codex advisory review\n\n_Skipped: no OPENAI_API_KEY._\n",
            encoding="utf-8",
        )
        return 0

    title = os.environ.get("PR_TITLE", "")
    body = (os.environ.get("PR_BODY") or "")[:2000]

    try:
        from openai import OpenAI

        client = OpenAI(api_key=key)
        model = os.environ.get("CODEX_REVIEW_MODEL", "gpt-4.1-mini")
        user = (
            f"PR title: {title}\n\nPR body (truncated):\n{body}\n\n"
            f"Diff (bounded):\n```\n{diff}\n```\n"
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=1200,
        )
        text = (resp.choices[0].message.content or "").strip()
    except Exception as e:
        text = f"_Reviewer error (non-blocking): {e}_"

    OUT.write_text(
        "## Codex advisory review\n\n"
        "> Advisory only. **Not** merge authority. "
        "CI unit/integration/evals remain the gates.\n\n"
        f"{text}\n\n"
        "---\nHuman review required before merge (AGENTS.md \u00a78).\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
