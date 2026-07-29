"""Result export and candidate summary reports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


EXPORT_COLUMNS = [
    "rank",
    "file",
    "name",
    "email",
    "phone",
    "score",
    "recommendation",
    "similarity_score",
    "skill_score",
    "skills",
    "matched_skills",
    "missing_skills",
    "education",
    "experience_years",
    "parse_error",
    "summary",
]


class ReportGenerator:
    """Generate CSV/XLSX ranked results and text summaries."""

    def __init__(self, output_path: str | Path):
        self.output_path = Path(output_path)

    def generate(self, ranked_candidates: list[dict]) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        frame = pd.DataFrame([flatten_candidate(candidate) for candidate in ranked_candidates])

        for column in EXPORT_COLUMNS:
            if column not in frame.columns:
                frame[column] = ""
        frame = frame[EXPORT_COLUMNS]

        suffix = self.output_path.suffix.lower()
        if suffix == ".csv":
            frame.to_csv(self.output_path, index=False)
        elif suffix in {".xlsx", ".xlsm"}:
            frame.to_excel(self.output_path, index=False)
        else:
            raise ValueError("Output file must use .csv, .xlsx, or .xlsm")

        self.generate_summary_reports(ranked_candidates)
        return self.output_path

    def generate_summary_reports(self, ranked_candidates: list[dict]) -> Path:
        summary_dir = self.output_path.with_suffix("").parent / (
            self.output_path.stem + "_summaries"
        )
        summary_dir.mkdir(parents=True, exist_ok=True)

        for candidate in ranked_candidates:
            safe_name = safe_filename(candidate.get("file") or f"candidate_{candidate['rank']}")
            summary_path = summary_dir / f"{candidate.get('rank', 0):02d}_{safe_name}.txt"
            summary_path.write_text(build_summary(candidate), encoding="utf-8")
        return summary_dir


def flatten_candidate(candidate: dict) -> dict:
    row = dict(candidate)
    for key in ("skills", "matched_skills", "missing_skills"):
        value = row.get(key, [])
        if isinstance(value, list):
            row[key] = ", ".join(value)
    row.pop("text", None)
    row.pop("anonymized_text", None)
    return row


def build_summary(candidate: dict) -> str:
    return "\n".join(
        [
            f"Rank: {candidate.get('rank', '')}",
            f"File: {candidate.get('file', '')}",
            f"Candidate: {candidate.get('name', 'Unknown')}",
            f"Score: {candidate.get('score', 0)}",
            f"Recommendation: {candidate.get('recommendation', '')}",
            f"Matched skills: {', '.join(candidate.get('matched_skills', [])) or 'None'}",
            f"Missing skills: {', '.join(candidate.get('missing_skills', [])) or 'None'}",
            "",
            "Summary:",
            candidate.get("summary", ""),
            "",
            "Parse status:",
            candidate.get("parse_error") or "Readable",
        ]
    )


def safe_filename(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in "._-" else "_" for char in value)
    return cleaned.strip("._") or "candidate"
