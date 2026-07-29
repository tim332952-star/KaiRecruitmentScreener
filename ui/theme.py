"""Kai data analytics Tkinter theme."""

from __future__ import annotations

from tkinter import ttk

from config import THEME


def apply_kai_theme(root) -> dict:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=THEME["window_background"])

    style.configure(
        ".",
        background=THEME["window_background"],
        foreground=THEME["text"],
        fieldbackground=THEME["panel_background"],
        font=("Segoe UI", 10),
    )
    style.configure("TFrame", background=THEME["window_background"])
    style.configure("Panel.TFrame", background=THEME["panel_background"])
    style.configure(
        "TLabel",
        background=THEME["window_background"],
        foreground=THEME["text"],
    )
    style.configure(
        "Muted.TLabel",
        background=THEME["window_background"],
        foreground=THEME["muted_text"],
    )
    style.configure(
        "Title.TLabel",
        background=THEME["window_background"],
        foreground=THEME["title"],
        font=("Segoe UI", 18, "bold"),
    )
    style.configure(
        "Metric.TLabel",
        background=THEME["panel_background"],
        foreground=THEME["title"],
        font=("Segoe UI", 16, "bold"),
    )
    style.configure(
        "MetricCaption.TLabel",
        background=THEME["panel_background"],
        foreground=THEME["muted_text"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "TLabelframe",
        background=THEME["window_background"],
        foreground=THEME["title"],
        bordercolor=THEME["accent"],
    )
    style.configure(
        "TLabelframe.Label",
        background=THEME["window_background"],
        foreground=THEME["title"],
        font=("Segoe UI", 10, "bold"),
    )
    style.configure(
        "TEntry",
        fieldbackground=THEME["panel_background"],
        foreground=THEME["text"],
        insertcolor=THEME["text"],
    )
    style.configure(
        "TButton",
        background=THEME["accent"],
        foreground="#FFFFFF",
        padding=(10, 6),
        borderwidth=1,
    )
    style.map(
        "TButton",
        background=[("active", THEME["accent_active"]), ("disabled", "#334155")],
        foreground=[("active", "#000000"), ("disabled", "#94A3B8")],
    )
    style.configure(
        "Treeview",
        background=THEME["surface"],
        fieldbackground=THEME["surface"],
        foreground=THEME["text"],
        rowheight=28,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=THEME["accent"],
        foreground="#FFFFFF",
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Treeview",
        background=[("selected", THEME["accent_active"])],
        foreground=[("selected", "#000000")],
    )
    style.configure(
        "Vertical.TScrollbar",
        background=THEME["panel_background"],
        troughcolor=THEME["surface"],
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=THEME["panel_background"],
        troughcolor=THEME["surface"],
    )

    return THEME
