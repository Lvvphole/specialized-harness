# Sample: repo_add

Minimal product tree for **repo-mode ACCEPT** proof.

```bash
specialized-harness run --repo samples/repo_add --task "Fix the broken add function"
```

Starts broken (`a - b`). ScriptedProvider repairs `app.py` when brief/path matches.
Harness decides ACCEPT only via ledger + pytest in the workspace.
