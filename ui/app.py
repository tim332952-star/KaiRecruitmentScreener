"""Tkinter GUI for Kai Recruitment Screener."""

from __future__ import annotations

import queue
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import openpyxl
from config import APP_NAME, DEFAULT_OUTPUT_FILE, THEME
from extractor import CandidateExtractor
from matcher import JobMatcher
from parser import ResumeParser
from ranker import CandidateRanker
from report import ReportGenerator
from ui.theme import apply_kai_theme


class RecruitmentScreenerApp(tk.Tk):
    """Main GUI application."""

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1180x760")
        self.minsize(980, 620)
        self.theme = apply_kai_theme(self)
        self.result_queue: queue.Queue = queue.Queue()
        self.ranked_candidates: list[dict] = []
        self.resume_folder_var = tk.StringVar()
        self.job_file_var = tk.StringVar()
        self.output_path_var = tk.StringVar(value=str(Path.cwd() / DEFAULT_OUTPUT_FILE))
        self.status_var = tk.StringVar(value="Ready")
        self.total_var = tk.StringVar(value="0")
        self.top_score_var = tk.StringVar(value="0")
        self.review_var = tk.StringVar(value="0")

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self, padding=(18, 14, 18, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text=APP_NAME, style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Batch resume screening, anonymized scoring, ranked export",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        metrics = ttk.Frame(header)
        metrics.grid(row=0, column=1, rowspan=2, sticky="e")
        self._metric(metrics, "Candidates", self.total_var, 0)
        self._metric(metrics, "Top Score", self.top_score_var, 1)
        self._metric(metrics, "Review+", self.review_var, 2)

        inputs = ttk.LabelFrame(self, text="Screening Inputs", padding=12)
        inputs.grid(row=1, column=0, sticky="ew", padx=18, pady=(4, 10))
        inputs.columnconfigure(1, weight=1)

        self._path_row(inputs, 0, "Resume folder", self.resume_folder_var, self._browse_resumes)
        self._path_row(inputs, 1, "Job file", self.job_file_var, self._browse_job_file)
        self._path_row(inputs, 2, "Export file", self.output_path_var, self._browse_output)

        ttk.Button(inputs, text="Run Screening", command=self._run_screening).grid(
            row=0, column=3, rowspan=2, sticky="nsew", padx=(10, 0)
        )
        ttk.Button(inputs, text="Export Current Results", command=self._export_current).grid(
            row=2, column=3, sticky="ew", padx=(10, 0)
        )

        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 10))

        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=3)
        body.add(right, weight=2)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(left, text="Ranked Candidates", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        self.results_tree = self._build_results_tree(left)
        self.results_tree.grid(row=1, column=0, sticky="nsew")
        self.results_tree.bind("<<TreeviewSelect>>", self._show_selected_summary)

        ttk.Label(right, text="Job Description", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        self.job_text = self._text_box(right, height=9)
        self.job_text.grid(row=1, column=0, sticky="nsew")

        ttk.Label(right, text="Candidate Summary", style="Muted.TLabel").grid(
            row=2, column=0, sticky="w", pady=(10, 6)
        )
        self.summary_text = self._text_box(right, height=12)
        self.summary_text.grid(row=3, column=0, sticky="nsew")
        right.rowconfigure(3, weight=1)

        footer = ttk.Frame(self, padding=(18, 0, 18, 12))
        footer.grid(row=3, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status_var, style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )

    def _metric(self, parent, caption_var: str, value_var: tk.StringVar, column: int) -> None:
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=(16, 8))
        frame.grid(row=0, column=column, padx=(8, 0), sticky="e")
        ttk.Label(frame, textvariable=value_var, style="Metric.TLabel").pack(anchor="e")
        ttk.Label(frame, text=caption_var, style="MetricCaption.TLabel").pack(anchor="e")

    def _path_row(self, parent, row, label, variable, command) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=variable).grid(
            row=row, column=1, sticky="ew", padx=(10, 0), pady=4
        )
        ttk.Button(parent, text="Browse", command=command).grid(
            row=row, column=2, sticky="e", padx=(10, 0), pady=4
        )

    def _build_results_tree(self, parent) -> ttk.Treeview:
        columns = ("rank", "file", "score", "recommendation", "matched", "missing", "status")
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        headings = {
            "rank": "Rank",
            "file": "Resume",
            "score": "Score",
            "recommendation": "Recommendation",
            "matched": "Matched Skills",
            "missing": "Missing Skills",
            "status": "Status",
        }
        widths = {
            "rank": 56,
            "file": 180,
            "score": 70,
            "recommendation": 120,
            "matched": 220,
            "missing": 220,
            "status": 95,
        }
        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(column, width=widths[column], anchor="w", stretch=column in {"matched", "missing"})

        tree.tag_configure("Strong Match", background=THEME["ai_strong_apply_background"], foreground=THEME["ai_text"])
        tree.tag_configure("Match", background=THEME["ai_apply_background"], foreground=THEME["ai_text"])
        tree.tag_configure("Review", background=THEME["ai_review_background"], foreground=THEME["ai_text"])
        tree.tag_configure("Low Match", background=THEME["ai_low_match_background"], foreground=THEME["ai_text"])
        tree.tag_configure("Skip", background=THEME["ai_skip_background"], foreground="#999999")

        y_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        x_scroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.grid(row=1, column=1, sticky="ns")
        x_scroll.grid(row=2, column=0, sticky="ew")
        return tree

    def _text_box(self, parent, height: int) -> tk.Text:
        return tk.Text(
            parent,
            height=height,
            wrap="word",
            bg=THEME["preview_text_background"],
            fg=THEME["text"],
            insertbackground=THEME["preview_text_insert"],
            relief="flat",
            padx=10,
            pady=8,
            font=("Segoe UI", 10),
        )

    def _browse_resumes(self) -> None:
        folder = filedialog.askdirectory(title="Select resume folder")
        if folder:
            self.resume_folder_var.set(folder)
            output = Path(folder) / DEFAULT_OUTPUT_FILE
            self.output_path_var.set(str(output))

    def _browse_job_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select job description",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        self.job_file_var.set(path)
        try:
            self.job_text.delete("1.0", tk.END)
            self.job_text.insert("1.0", Path(path).read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            self.job_text.insert("1.0", Path(path).read_text(encoding="cp1252"))
        except Exception as exc:
            messagebox.showerror("Job File Error", str(exc))

    def _browse_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save ranked results",
            defaultextension=".xlsx",
            filetypes=[("Excel workbook", "*.xlsx"), ("CSV file", "*.csv")],
        )
        if path:
            self.output_path_var.set(path)

    def _run_screening(self) -> None:
        resume_folder = self.resume_folder_var.get().strip()
        job_description = self.job_text.get("1.0", tk.END).strip()
        output_path = self.output_path_var.get().strip()

        if not resume_folder:
            messagebox.showwarning("Missing Input", "Select a resume folder.")
            return
        if not job_description:
            messagebox.showwarning("Missing Input", "Load or enter a job description.")
            return
        if not output_path:
            messagebox.showwarning("Missing Output", "Select an export file.")
            return

        self.status_var.set("Screening resumes...")
        self._set_controls_state("disabled")
        worker = threading.Thread(
            target=self._screen_worker,
            args=(resume_folder, job_description, output_path),
            daemon=True,
        )
        worker.start()
        self.after(100, self._check_worker)

    def _screen_worker(self, resume_folder: str, job_description: str, output_path: str) -> None:
        try:
            resumes = ResumeParser(resume_folder).parse_all()
            candidates = CandidateExtractor().extract_all(resumes)
            matched = JobMatcher(job_description).match_all(candidates)
            ranked = CandidateRanker().rank(matched)
            ReportGenerator(output_path).generate(ranked)
            self.result_queue.put(("success", ranked, output_path))
        except Exception as exc:
            self.result_queue.put(("error", exc, ""))

    def _check_worker(self) -> None:
        try:
            status, payload, output_path = self.result_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._check_worker)
            return

        self._set_controls_state("normal")
        if status == "error":
            self.status_var.set("Screening failed")
            messagebox.showerror("Screening Error", str(payload))
            return

        self.ranked_candidates = payload
        self._populate_results(payload)
        self._update_metrics(payload)
        self.status_var.set(f"Screening complete. Results saved to {output_path}")

    def _set_controls_state(self, state: str) -> None:
        for child in self.winfo_children():
            self._set_child_state(child, state)

    def _set_child_state(self, widget, state: str) -> None:
        if isinstance(widget, (ttk.Button, ttk.Entry)):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            self._set_child_state(child, state)

    def _populate_results(self, candidates: list[dict]) -> None:
        self.results_tree.delete(*self.results_tree.get_children())
        self.summary_text.delete("1.0", tk.END)
        for candidate in candidates:
            status = "Error" if candidate.get("parse_error") else "Readable"
            values = (
                candidate.get("rank", ""),
                candidate.get("file", ""),
                candidate.get("score", 0),
                candidate.get("recommendation", ""),
                ", ".join(candidate.get("matched_skills", [])),
                ", ".join(candidate.get("missing_skills", [])),
                status,
            )
            self.results_tree.insert(
                "",
                tk.END,
                iid=str(candidate.get("rank", "")),
                values=values,
                tags=(candidate.get("recommendation", "Skip"),),
            )

        children = self.results_tree.get_children()
        if children:
            self.results_tree.selection_set(children[0])
            self.results_tree.focus(children[0])
            self._show_selected_summary()

    def _update_metrics(self, candidates: list[dict]) -> None:
        self.total_var.set(str(len(candidates)))
        self.top_score_var.set(str(max((item.get("score", 0) for item in candidates), default=0)))
        review_count = sum(1 for item in candidates if item.get("score", 0) >= 50)
        self.review_var.set(str(review_count))

    def _show_selected_summary(self, _event=None) -> None:
        selection = self.results_tree.selection()
        if not selection:
            return

        rank = int(selection[0])
        candidate = next(
            (item for item in self.ranked_candidates if item.get("rank") == rank),
            None,
        )
        if candidate is None:
            return

        lines = [
            f"{candidate.get('name') or 'Unknown'}",
            f"File: {candidate.get('file', '')}",
            f"Score: {candidate.get('score', 0)} ({candidate.get('recommendation', '')})",
            "",
            f"Email: {candidate.get('email') or 'Not detected'}",
            f"Phone: {candidate.get('phone') or 'Not detected'}",
            f"Education: {candidate.get('education') or 'Not detected'}",
            f"Experience: {candidate.get('experience_years', 0)} years detected",
            "",
            "Matched skills:",
            ", ".join(candidate.get("matched_skills", [])) or "None",
            "",
            "Missing skills:",
            ", ".join(candidate.get("missing_skills", [])) or "None",
            "",
            "Summary:",
            candidate.get("summary", ""),
        ]
        if candidate.get("parse_error"):
            lines.extend(["", "Parse error:", candidate["parse_error"]])

        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", "\n".join(lines))

    def _export_current(self) -> None:
        if not self.ranked_candidates:
            messagebox.showinfo("No Results", "Run screening before exporting results.")
            return
        output_path = self.output_path_var.get().strip()
        if not output_path:
            self._browse_output()
            output_path = self.output_path_var.get().strip()
        if not output_path:
            return
        try:
            ReportGenerator(output_path).generate(self.ranked_candidates)
            self.status_var.set(f"Results exported to {output_path}")
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc))


def run_app() -> None:
    app = RecruitmentScreenerApp()
    app.mainloop()
