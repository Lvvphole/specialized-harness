# Sample: repo_stats

Minimal product tree for a **third repo-mode ACCEPT** proof (corpus growth).

Two axes are new relative to `repo_add` / `repo_mul`:

| Axis | `repo_add` / `repo_mul` | `repo_stats` |
|------|-------------------------|--------------|
| Tree shape | flat `app.py` + `test_app.py` | package (`statskit/`) + `tests/` directory |
| Bug class | arithmetic operator swap (one token) | even-length boundary case in `median` (multi-line repair) |

Starts broken: `median` returns the upper middle value, so even-length inputs are
wrong (`median([4, 1, 3, 2])` returns `3`, not `2.5`). `mean` and the odd-length
median path are already correct — the repair must not regress them.

```bash
specialized-harness run --repo samples/repo_stats --task "Fix the broken median function"
```

Harness decides ACCEPT only via ledger + pytest in the workspace.
