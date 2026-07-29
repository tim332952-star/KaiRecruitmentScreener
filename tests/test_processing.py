import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from extractor import CandidateExtractor, anonymize_text, extract_skills
from matcher import JobMatcher
from parser import ResumeParser
from ranker import CandidateRanker
from report import ReportGenerator, safe_filename


class ParserTests(unittest.TestCase):
    def test_parse_all_reads_supported_txt_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            (folder / "resume.txt").write_text("Jane Analyst\nPython SQL", encoding="utf-8")
            (folder / "ignore.md").write_text("ignore", encoding="utf-8")

            resumes = ResumeParser(folder).parse_all()

        self.assertEqual(len(resumes), 1)
        self.assertEqual(resumes[0]["file"], "resume.txt")
        self.assertIn("Python SQL", resumes[0]["text"])
        self.assertEqual(resumes[0]["error"], "")


class ExtractorTests(unittest.TestCase):
    def test_extracts_contacts_skills_and_anonymized_text(self):
        text = (
            "Jane Analyst\n"
            "jane@example.com 555-123-4567\n"
            "Python SQL Power BI. 7 years of experience. Bachelor degree."
        )

        candidate = CandidateExtractor()._extract_info(
            {"file": "resume.txt", "path": "resume.txt", "text": text, "error": ""}
        )

        self.assertEqual(candidate["name"], "Jane Analyst")
        self.assertEqual(candidate["email"], "jane@example.com")
        self.assertEqual(candidate["phone"], "555-123-4567")
        self.assertIn("Python", candidate["skills"])
        self.assertIn("SQL", candidate["skills"])
        self.assertEqual(candidate["experience_years"], 7)
        self.assertNotIn("jane@example.com", candidate["anonymized_text"])

    def test_anonymize_removes_protected_terms(self):
        anonymized = anonymize_text("John Doe\nMale candidate, age 42, python")

        self.assertNotIn("Male", anonymized)
        self.assertNotIn("age", anonymized.lower())
        self.assertIn("python", anonymized.lower())

    def test_extract_skills_is_deterministic(self):
        self.assertEqual(extract_skills("SQL and Python"), ["Python", "SQL"])


class MatcherRankerTests(unittest.TestCase):
    def test_matcher_scores_relevant_candidate_higher(self):
        candidates = [
            {
                "file": "a.txt",
                "skills": ["Python", "SQL", "Power Bi"],
                "anonymized_text": "Python SQL Power BI dashboard analytics",
            },
            {
                "file": "b.txt",
                "skills": ["Recruiting"],
                "anonymized_text": "Recruiting coordinator and scheduling",
            },
        ]

        matched = JobMatcher("Need Python SQL Power BI analytics").match_all(candidates)
        ranked = CandidateRanker().rank(matched)

        self.assertEqual(ranked[0]["file"], "a.txt")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertGreater(ranked[0]["score"], ranked[1]["score"])


class ReportTests(unittest.TestCase):
    def test_report_generates_csv_and_summaries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "ranked.csv"
            candidates = [
                {
                    "rank": 1,
                    "file": "resume.txt",
                    "name": "Jane Analyst",
                    "email": "jane@example.com",
                    "phone": "555-123-4567",
                    "score": 91,
                    "recommendation": "Strong Match",
                    "similarity_score": 88,
                    "skill_score": 100,
                    "skills": ["Python"],
                    "matched_skills": ["Python"],
                    "missing_skills": [],
                    "education": "BACHELOR",
                    "experience_years": 7,
                    "parse_error": "",
                    "summary": "Python analyst",
                }
            ]

            ReportGenerator(output_path).generate(candidates)

            frame = pd.read_csv(output_path)
            summary_files = list((Path(temp_dir) / "ranked_summaries").glob("*.txt"))

        self.assertEqual(frame.loc[0, "score"], 91)
        self.assertEqual(len(summary_files), 1)

    def test_safe_filename_removes_unsafe_characters(self):
        self.assertEqual(safe_filename("../bad name.txt"), "bad_name.txt")


if __name__ == "__main__":
    unittest.main()
