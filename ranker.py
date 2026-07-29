"""Candidate ranking."""

from __future__ import annotations


class CandidateRanker:
    """Sort candidates by score with deterministic tie breakers."""

    def rank(self, candidates: list[dict]) -> list[dict]:
        ranked = sorted(
            candidates,
            key=lambda item: (
                -int(item.get("score", 0)),
                item.get("file", "").lower(),
            ),
        )

        for index, candidate in enumerate(ranked, start=1):
            candidate["rank"] = index
        return ranked
