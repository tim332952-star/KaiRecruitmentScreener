"""Candidate detail extraction and anonymization."""

from __future__ import annotations

import re

from config import BIAS_PATTERNS, SKILL_KEYWORDS


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(
    r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}"
)
YEAR_EXPERIENCE_RE = re.compile(
    r"\b(\d{1,2})\+?\s+(?:years?|yrs?)\s+(?:of\s+)?experience\b",
    re.IGNORECASE,
)
DEGREE_RE = re.compile(
    r"\b(?:associate|bachelor|master|mba|phd|doctorate|b\.s\.|b\.a\.|m\.s\.|m\.a\.)\b",
    re.IGNORECASE,
)


class CandidateExtractor:
    """Extract candidate profile fields from parsed resume text."""

    def __init__(self):
        self.nlp = self._load_spacy()

    @staticmethod
    def _load_spacy():
        try:
            import spacy

            try:
                return spacy.load("en_core_web_sm")
            except OSError:
                return spacy.blank("en")
        except Exception:
            return None

    def extract_all(self, resumes: list[dict]) -> list[dict]:
        return [self._extract_info(resume) for resume in resumes]

    def _extract_info(self, resume: dict) -> dict:
        text = resume.get("text", "") or ""
        anonymized_text = anonymize_text(text)
        skills = extract_skills(text)
        name = self._extract_name(text)

        return {
            "file": resume.get("file", ""),
            "path": resume.get("path", ""),
            "name": name,
            "email": first_match(EMAIL_RE, text),
            "phone": first_match(PHONE_RE, text),
            "skills": skills,
            "education": self._extract_education(text),
            "experience_years": self._extract_experience_years(text),
            "summary": summarize_candidate(text, skills),
            "text": text,
            "anonymized_text": anonymized_text,
            "parse_error": resume.get("error", ""),
        }

    def _extract_name(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return "Unknown"

        first_line = lines[0]
        if EMAIL_RE.search(first_line) or PHONE_RE.search(first_line):
            return "Unknown"

        if self.nlp is not None:
            doc = self.nlp("\n".join(lines[:8]))
            for entity in getattr(doc, "ents", []):
                if entity.label_ == "PERSON":
                    return entity.text.strip()

        words = first_line.split()
        if 1 <= len(words) <= 4 and all(word[:1].isalpha() for word in words):
            return first_line
        return "Unknown"

    @staticmethod
    def _extract_education(text: str) -> str:
        matches = DEGREE_RE.findall(text)
        if not matches:
            return ""
        normalized = sorted({match.upper().replace(".", "") for match in matches})
        return ", ".join(normalized)

    @staticmethod
    def _extract_experience_years(text: str) -> int:
        years = [int(match) for match in YEAR_EXPERIENCE_RE.findall(text)]
        return max(years) if years else 0


def first_match(pattern: re.Pattern, text: str) -> str:
    match = pattern.search(text)
    return match.group(0).strip() if match else ""


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for skill in sorted(SKILL_KEYWORDS):
        pattern = r"\b" + re.escape(skill).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, lowered):
            found.append(skill.title() if len(skill) > 4 else skill.upper())
    return found


def anonymize_text(text: str) -> str:
    value = EMAIL_RE.sub(" ", text)
    value = PHONE_RE.sub(" ", value)

    lines = value.splitlines()
    if lines and 1 <= len(lines[0].split()) <= 4:
        lines[0] = " "
    value = "\n".join(lines)

    for pattern in BIAS_PATTERNS:
        value = re.sub(pattern, " ", value, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", value).strip()


def summarize_candidate(text: str, skills: list[str]) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return "No readable resume text was available."

    skill_text = ", ".join(skills[:8]) if skills else "No configured skills detected"
    preview = clean[:220].rstrip()
    if len(clean) > 220:
        preview += "..."
    return f"{skill_text}. {preview}"
