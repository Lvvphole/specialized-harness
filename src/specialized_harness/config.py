"""Project config for CLI defaults (Minimum Sufficient operator UX)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_NAMES = (".specialized-harness.yaml", ".specialized-harness.yml")


@dataclass
class HarnessConfig:
    blueprint: str | None = None
    fixture_root: str | None = None
    repo: str | None = None  # alias for fixture_root when set
    provider: str = "scripted"
    provider_url: str | None = None
    runs_dir: str = "artifacts/runs"
    extra: dict[str, Any] = field(default_factory=dict)

    def resolved_fixture_root(self) -> str | None:
        return self.fixture_root or self.repo


def load_config(path: str | Path | None = None, cwd: Path | None = None) -> HarnessConfig:
    """Load YAML config from explicit path or first default name in cwd."""
    if path is not None:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"config not found: {p}")
        return _parse(p.read_text(encoding="utf-8"), source=str(p))

    base = cwd or Path.cwd()
    for name in DEFAULT_CONFIG_NAMES:
        candidate = base / name
        if candidate.is_file():
            return _parse(candidate.read_text(encoding="utf-8"), source=str(candidate))
    return HarnessConfig()


def _parse(text: str, source: str = "") -> HarnessConfig:
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"config must be a mapping ({source})")
    return HarnessConfig(
        blueprint=_str_or_none(data.get("blueprint")),
        fixture_root=_str_or_none(data.get("fixture_root") or data.get("fixture-root")),
        repo=_str_or_none(data.get("repo")),
        provider=str(data.get("provider") or "scripted").strip().lower() or "scripted",
        provider_url=_str_or_none(data.get("provider_url") or data.get("provider-url")),
        runs_dir=str(data.get("runs_dir") or data.get("runs-dir") or "artifacts/runs"),
        extra={
            k: v
            for k, v in data.items()
            if k
            not in {
                "blueprint",
                "fixture_root",
                "fixture-root",
                "repo",
                "provider",
                "provider_url",
                "provider-url",
                "runs_dir",
                "runs-dir",
            }
        },
    )


def _str_or_none(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None
