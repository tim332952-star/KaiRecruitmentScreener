# Kai Recruitment Screener

## Purpose
An GUI AI-powered recruitment screening tool that processes candidate resumes, extracts key skills and experience, and ranks candidates against a job description.
The goal is to automate the first stage of recruitment, saving HR teams time while ensuring fair and consistent evaluation.

---

## Features
- Upload and parse resumes in PDF, DOCX, or TXT formats
- Extract candidate details: name, contact info, skills, education, work experience
- Match candidate profiles against a given job description
- Score and rank candidates based on relevance
- Export ranked results to CSV or Excel
- Provide a summary report for each candidate
- Handle multiple resumes in batch mode
- Basic bias mitigation: ignore gender, age, and other protected attributes
- Kai data analytics GUI theme aligned with KaiJobFinder

---

## Requirements
- **Python**: 3.10+
- **Libraries**:
  - `tkinter` (UI)
  - `pandas` (data handling)
  - `python-docx` (DOCX parsing)
  - `PyPDF2` (PDF parsing)
  - `spacy` (NLP support)
  - `scikit-learn` (text similarity scoring)
  - `openpyxl` (Excel export)
- Must run on Windows, macOS, and Linux
- Must include unit tests for all modules

---

## Architecture
- **main.py** - GUI entry point
- **parser.py** - Handles file reading and text extraction
- **extractor.py** - Extracts contact info, skills, education, experience, and anonymized scoring text
- **matcher.py** - Compares candidate profiles to job description
- **ranker.py** - Scores and ranks candidates
- **report.py** - Generates CSV/Excel reports and candidate summaries
- **config.py** - Stores constants and settings
- **ui/** - Tkinter screens and Kai theme
- **tests/** - Unit tests for the processing modules

---

## Input / Output
**Input**:
- Folder containing resumes selected in the GUI
- Job description loaded from a text file or entered directly in the GUI

**Output**:
- Ranked list of candidates in the GUI
- Ranked CSV/Excel export
- Summary report per candidate in a generated summaries folder

---

## Constraints
- No storing of candidate data beyond processing session and user-selected exports
- Must anonymize personal identifiers before scoring
- Follow PEP 8 style guide
- Handle corrupted or unreadable files gracefully
- Ensure reproducible scoring for the same input

---

## Running the App
```bash
python main.py
```
