"""Evidence Ledger - claim -> method -> observation -> verdict (VERIFICATION.md).

Independent of the coding model. Decide reads the ledger; the model cannot
append PASS claims for its own work as authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"


@dataclass
class EvidenceClaim:
    claim_id: str
    subject: str
    method: str
    observation: str
    verdict: Verdict
    mandatory: bool = True

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        return d


@dataclass
class EvidenceLedger:
    """In-memory list of claims for one run (Minimum Sufficient for Sprint 2)."""

    claims: list[EvidenceClaim] = field(default_factory=list)

    def append(
        self,
        claim_id: str,
        subject: str,
        method: str,
        observation: str,
        verdict: Verdict | str,
        *,
        mandatory: bool = True,
    ) -> EvidenceClaim:
        v = Verdict(verdict) if isinstance(verdict, str) else verdict
        claim = EvidenceClaim(
            claim_id=claim_id,
            subject=subject,
            method=method,
            observation=observation,
            verdict=v,
            mandatory=mandatory,
        )
        self.claims.append(claim)
        return claim

    def mandatory_failures(self) -> list[EvidenceClaim]:
        return [c for c in self.claims if c.mandatory and c.verdict == Verdict.FAIL]

    def has_mandatory_pass(self, claim_id: str) -> bool:
        return any(
            c.claim_id == claim_id and c.mandatory and c.verdict == Verdict.PASS
            for c in self.claims
        )

    def to_list(self) -> list[dict[str, Any]]:
        return [c.to_dict() for c in self.claims]
