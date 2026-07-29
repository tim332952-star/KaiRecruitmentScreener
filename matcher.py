"""Candidate-to-job matching."""

from __future__ import annotations

import math
import re
from collections import Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ModuleNotFoundError:
    TfidfVectorizer = None
    cosine_similarity = None

from extractor import extract_skills


class JobMatcher:
    """Compare candidate profiles to a job description."""

    def __init__(self, job_description: str):
        self.job_description = job_description.strip()
        self.job_skills = extract_skills(self.job_description)

    def match_all(self, candidates: list[dict]) -> list[dict]:
        if not candidates:
            return []

        candidate_texts = [
            candidate.get("anonymized_text") or candidate.get("text", "")
            for candidate in candidates
        ]
        similarity_scores = self._similarity_scores(candidate_texts)

        matched = []
        required = {skill.lower() for skill in self.job_skills}
        for candidate, similarity in zip(candidates, similarity_scores):
            candidate_skills = {skill.lower() for skill in candidate.get("skills", [])}
            matched_skills = sorted(required & candidate_skills)
            missing_skills = sorted(required - candidate_skills)
            skill_score = 0.0 if not required else len(matched_skills) / len(required)
            score = int(round((similarity * 65 + skill_score * 35) * 100))

            row = dict(candidate)
            row.update(
                {
                    "similarity_score": round(similarity * 100, 2),
                    "skill_score": round(skill_score * 100, 2),
                    "score": max(0, min(100, score)),
                    "matched_skills": [skill.title() for skill in matched_skills],
                    "missing_skills": [skill.title() for skill in missing_skills],
                    "recommendation": recommendation_for_score(score),
                }
            )
            matched.append(row)
        return matched

    def _similarity_scores(self, candidate_texts: list[str]) -> list[float]:
        if not self.job_description:
            return [0.0 for _ in candidate_texts]

        if TfidfVectorizer is None or cosine_similarity is None:
            return [
                token_cosine_similarity(self.job_description, candidate_text)
                for candidate_text in candidate_texts
            ]

        documents = [self.job_description, *candidate_texts]
        try:
            matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(
                documents
            )
        except ValueError:
            return [0.0 for _ in candidate_texts]

        similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        return [float(value) for value in similarities]


def recommendation_for_score(score: int) -> str:
    if score >= 85:
        return "Strong Match"
    if score >= 70:
        return "Match"
    if score >= 50:
        return "Review"
    if score >= 30:
        return "Low Match"
    return "Skip"


def token_cosine_similarity(left: str, right: str) -> float:
    left_counts = Counter(tokenize(left))
    right_counts = Counter(tokenize(right))
    if not left_counts or not right_counts:
        return 0.0

    shared = set(left_counts) & set(right_counts)
    numerator = sum(left_counts[token] * right_counts[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left_counts.values()))
    right_norm = math.sqrt(sum(value * value for value in right_counts.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#.-]+", text.lower())
