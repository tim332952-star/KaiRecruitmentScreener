"""Resume file parsing."""

from __future__ import annotations

from pathlib import Path

from config import SUPPORTED_FORMATS


class ResumeParser:
    """Extract text from supported resume files in a folder."""

    def __init__(self, folder_path: str | Path):
        self.folder_path = Path(folder_path)
        if not self.folder_path.is_dir():
            raise ValueError(f"Invalid folder path: {self.folder_path}")

    def parse_all(self) -> list[dict]:
        resumes = []
        for file_path in sorted(self.folder_path.iterdir(), key=lambda item: item.name.lower()):
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()
            if ext not in SUPPORTED_FORMATS:
                continue

            try:
                text = self._extract_text(file_path, ext)
                resumes.append(
                    {
                        "file": file_path.name,
                        "path": str(file_path),
                        "text": text,
                        "error": "",
                    }
                )
            except Exception as exc:
                resumes.append(
                    {
                        "file": file_path.name,
                        "path": str(file_path),
                        "text": "",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        return resumes

    def _extract_text(self, file_path: Path, ext: str) -> str:
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        if ext == ".docx":
            return self._parse_docx(file_path)
        if ext == ".txt":
            return self._parse_txt(file_path)
        return ""

    @staticmethod
    def _parse_pdf(file_path: Path) -> str:
        import PyPDF2

        text = []
        with file_path.open("rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text).strip()

    @staticmethod
    def _parse_docx(file_path: Path) -> str:
        import docx

        document = docx.Document(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    @staticmethod
    def _parse_txt(file_path: Path) -> str:
        try:
            return file_path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            return file_path.read_text(encoding="cp1252").strip()
