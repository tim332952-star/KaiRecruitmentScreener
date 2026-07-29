"""Application constants for Kai Recruitment Screener."""

from pathlib import Path


APP_NAME = "Kai Recruitment Screener"
SUPPORTED_FORMATS = {".pdf", ".docx", ".txt"}
DEFAULT_OUTPUT_FILE = "ranked_candidates.xlsx"

THEME = {
    "window_background": "#001F3F",
    "surface": "#0F172A",
    "panel_background": "#1E293B",
    "text": "#EDF2F7",
    "muted_text": "#CBD5E1",
    "title": "#FFD700",
    "accent": "#3399FF",
    "accent_active": "#F2C811",
    "success": "#00CC66",
    "warning": "#FF9900",
    "danger": "#FF6666",
    "preview_text_background": "#060E1F",
    "preview_text_insert": "#EDF2F7",
    "ai_strong_apply_background": "#004D00",
    "ai_apply_background": "#003300",
    "ai_review_background": "#333300",
    "ai_low_match_background": "#4D2600",
    "ai_skip_background": "#2B2B2B",
    "ai_text": "#FFFF99",
}

SKILL_KEYWORDS = {
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "pandas",
    "numpy",
    "scikit-learn",
    "machine learning",
    "statistics",
    "data analysis",
    "data analytics",
    "etl",
    "azure",
    "aws",
    "gcp",
    "snowflake",
    "power query",
    "dax",
    "dashboard",
    "reporting",
    "project management",
    "communication",
    "leadership",
    "recruiting",
    "hr",
    "talent acquisition",
    "workday",
    "greenhouse",
    "lever",
    "ats",
    "javascript",
    "typescript",
    "react",
    "node",
    "django",
    "flask",
    "api",
    "git",
    "docker",
    "kubernetes",
}

BIAS_PATTERNS = (
    r"\b(?:male|female|man|woman|gender|married|single|divorced|widowed)\b",
    r"\b(?:he|she|his|her|hers|him)\b",
    r"\b(?:age|date of birth|dob|birthday|birthdate)\b",
    r"\b(?:race|ethnicity|religion|church|mosque|synagogue)\b",
    r"\b(?:pregnant|disability|disabled|veteran)\b",
)

PROJECT_ROOT = Path(__file__).resolve().parent
