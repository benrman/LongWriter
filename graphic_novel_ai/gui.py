"""Tkinter GUI for the local Graphic Novel AI studio."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .cli import _brief_from_json, _config_from_json
from .config import GenerationConfig, ProjectBrief
from .pipeline import GraphicNovelStudio


def _path_or_home(path_value: str) -> Path:
    cleaned = path_value.strip()
    return Path(cleaned) if cleaned else Path.home()


class GraphicNovelApp(tk.Tk):
    """Simple desktop UI focused on easy local operation."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Graphic Novel AI Studio")
        self.geometry("980x760")
        self.resizable(True, True)

        self.profile_var = tk.StringVar(value="rtx3070")
        self.output_var = tk.StringVar(value="outputs/graphic_novel_ai")
        self.status_var = tk.StringVar(value="Ready.")
        self.config_path_var = tk.StringVar(value="")
        self.preview_enabled_var = tk.BooleanVar(value=False)
        self.preview_backend_var = tk.StringVar(value="automatic1111")
        self.preview_endpoint_var = tk.StringVar(value="http://127.0.0.1:7860")
        self.preview_max_var = tk.StringVar(value="6")

        self.title_var = tk.StringVar(value="Neon Ashes")
        self.genre_var = tk.StringVar(value="Sci-Fi Fantasy")
        self.tone_var = tk.StringVar(value="Cinematic, emotionally grounded")
        self.audience_var = tk.StringVar(value="Young Adult")
        self.issue_var = tk.StringVar(value="6")
        self.pages_var = tk.StringVar(value="24")
        self.panels_var = tk.StringVar(value="4")
        self.art_style_var = tk.StringVar(value="Cinematic comic style with dynamic framing")

        self._build_layout()

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        top = ttk.LabelFrame(root, text="Runtime")
        top.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(top, text="Hardware profile").grid(row=0, column=0, sticky=tk.W, padx=8, pady=6)
        ttk.Combobox(
            top,
            textvariable=self.profile_var,
            values=["balanced", "rtx3070", "high_quality"],
            state="readonly",
            width=18,
        ).grid(row=0, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(top, text="Output folder").grid(row=0, column=2, sticky=tk.W, padx=8, pady=6)
        ttk.Entry(top, textvariable=self.output_var, width=42).grid(row=0, column=3, sticky=tk.EW, padx=8, pady=6)
        ttk.Button(top, text="Browse", command=self._pick_output).grid(row=0, column=4, padx=8, pady=6)
        top.columnconfigure(3, weight=1)

        cfg = ttk.LabelFrame(root, text="Optional Config Override (.json)")
        cfg.pack(fill=tk.X, pady=(0, 8))
        ttk.Entry(cfg, textvariable=self.config_path_var).grid(row=0, column=0, sticky=tk.EW, padx=8, pady=6)
        ttk.Button(cfg, text="Load Config", command=self._pick_config).grid(row=0, column=1, padx=8, pady=6)
        cfg.columnconfigure(0, weight=1)

        preview = ttk.LabelFrame(root, text="Optional Storyboard Preview Images")
        preview.pack(fill=tk.X, pady=(0, 8))
        ttk.Checkbutton(
            preview,
            text="Enable local preview image generation",
            variable=self.preview_enabled_var,
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=8, pady=4)
        ttk.Label(preview, text="Backend").grid(row=1, column=0, sticky=tk.W, padx=8, pady=4)
        ttk.Combobox(
            preview,
            textvariable=self.preview_backend_var,
            values=["automatic1111", "comfyui"],
            state="readonly",
            width=18,
        ).grid(row=1, column=1, sticky=tk.W, padx=8, pady=4)
        ttk.Label(preview, text="Endpoint").grid(row=1, column=2, sticky=tk.W, padx=8, pady=4)
        ttk.Entry(preview, textvariable=self.preview_endpoint_var, width=34).grid(
            row=1,
            column=3,
            sticky=tk.EW,
            padx=8,
            pady=4,
        )
        ttk.Label(preview, text="Max images").grid(row=1, column=4, sticky=tk.W, padx=8, pady=4)
        ttk.Entry(preview, textvariable=self.preview_max_var, width=8).grid(row=1, column=5, sticky=tk.W, padx=8, pady=4)
        preview.columnconfigure(3, weight=1)

        brief_frame = ttk.LabelFrame(root, text="Project Brief")
        brief_frame.pack(fill=tk.BOTH, expand=True)

        row = 0
        for label, var in (
            ("Title", self.title_var),
            ("Genre", self.genre_var),
            ("Tone", self.tone_var),
            ("Target audience", self.audience_var),
            ("Issue count", self.issue_var),
            ("Pages/issue", self.pages_var),
            ("Panels/page", self.panels_var),
            ("Art style", self.art_style_var),
        ):
            ttk.Label(brief_frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=8, pady=4)
            ttk.Entry(brief_frame, textvariable=var).grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
            row += 1

        ttk.Label(brief_frame, text="Premise").grid(row=row, column=0, sticky=tk.NW, padx=8, pady=4)
        self.premise_text = tk.Text(brief_frame, height=4)
        self.premise_text.insert(
            tk.END,
            "A courier discovers she can rewrite memories in the city and must choose between truth and survival.",
        )
        self.premise_text.grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
        row += 1

        ttk.Label(brief_frame, text="Core theme").grid(row=row, column=0, sticky=tk.NW, padx=8, pady=4)
        self.theme_text = tk.Text(brief_frame, height=2)
        self.theme_text.insert(tk.END, "Identity, memory, and who owns the story of a city.")
        self.theme_text.grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
        row += 1

        ttk.Label(brief_frame, text="Setting").grid(row=row, column=0, sticky=tk.NW, padx=8, pady=4)
        self.setting_text = tk.Text(brief_frame, height=2)
        self.setting_text.insert(tk.END, "A floodlit cyberpunk metropolis where myths are licensed by corporations.")
        self.setting_text.grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
        row += 1

        ttk.Label(brief_frame, text="Protagonist").grid(row=row, column=0, sticky=tk.NW, padx=8, pady=4)
        self.protagonist_text = tk.Text(brief_frame, height=2)
        self.protagonist_text.insert(tk.END, "A bike courier with a fragmented past and dangerous empathy.")
        self.protagonist_text.grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
        row += 1

        ttk.Label(brief_frame, text="Antagonist").grid(row=row, column=0, sticky=tk.NW, padx=8, pady=4)
        self.antagonist_text = tk.Text(brief_frame, height=2)
        self.antagonist_text.insert(tk.END, "A memory-architect CEO who edits public reality for profit.")
        self.antagonist_text.grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
        row += 1

        ttk.Label(brief_frame, text="Supporting cast notes").grid(row=row, column=0, sticky=tk.NW, padx=8, pady=4)
        self.supporting_text = tk.Text(brief_frame, height=3)
        self.supporting_text.grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
        row += 1

        ttk.Label(brief_frame, text="Inspirations (comma-separated)").grid(row=row, column=0, sticky=tk.W, padx=8, pady=4)
        self.inspiration_var = tk.StringVar(value="Blade Runner, Saga, Akira")
        ttk.Entry(brief_frame, textvariable=self.inspiration_var).grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
        row += 1

        ttk.Label(brief_frame, text="Hard constraints (comma-separated)").grid(row=row, column=0, sticky=tk.W, padx=8, pady=4)
        self.constraints_var = tk.StringVar(value="No explicit sexual content, Keep PG-13 violence")
        ttk.Entry(brief_frame, textvariable=self.constraints_var).grid(row=row, column=1, sticky=tk.EW, padx=8, pady=4)
        row += 1

        brief_frame.columnconfigure(1, weight=1)

        actions = ttk.Frame(root)
        actions.pack(fill=tk.X, pady=8)
        ttk.Button(actions, text="Load Brief JSON", command=self._load_brief_json).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="Generate Project", command=self._kickoff_generate).pack(side=tk.LEFT, padx=4)
        ttk.Label(actions, textvariable=self.status_var).pack(side=tk.RIGHT)

    def _pick_output(self) -> None:
        chosen = filedialog.askdirectory(
            title="Choose output directory",
            initialdir=str(_path_or_home(self.output_var.get())),
        )
        if chosen:
            self.output_var.set(chosen)

    def _pick_config(self) -> None:
        chosen = filedialog.askopenfilename(
            title="Select config JSON",
            initialdir=str(_path_or_home(self.config_path_var.get()).parent),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if chosen:
            self.config_path_var.set(chosen)

    def _load_brief_json(self) -> None:
        chosen = filedialog.askopenfilename(
            title="Load project brief JSON",
            initialdir=str(Path.cwd()),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not chosen:
            return
        try:
            brief = _brief_from_json(Path(chosen))
        except Exception as exc:
            messagebox.showerror("Brief load failed", str(exc))
            return
        self._fill_from_brief(brief)

    def _fill_from_brief(self, brief: ProjectBrief) -> None:
        self.title_var.set(brief.title)
        self.genre_var.set(brief.genre)
        self.tone_var.set(brief.tone)
        self.audience_var.set(brief.target_audience)
        self.issue_var.set(str(brief.issue_count))
        self.pages_var.set(str(brief.pages_per_issue))
        self.panels_var.set(str(brief.panels_per_page))
        self.art_style_var.set(brief.art_style)
        self.premise_text.delete("1.0", tk.END)
        self.premise_text.insert(tk.END, brief.premise)
        self.theme_text.delete("1.0", tk.END)
        self.theme_text.insert(tk.END, brief.core_theme)
        self.setting_text.delete("1.0", tk.END)
        self.setting_text.insert(tk.END, brief.setting)
        self.protagonist_text.delete("1.0", tk.END)
        self.protagonist_text.insert(tk.END, brief.protagonist_overview)
        self.antagonist_text.delete("1.0", tk.END)
        self.antagonist_text.insert(tk.END, brief.antagonist_overview)
        self.supporting_text.delete("1.0", tk.END)
        self.supporting_text.insert(tk.END, brief.supporting_cast_notes)
        self.inspiration_var.set(",".join(brief.inspirations))
        self.constraints_var.set(",".join(brief.hard_constraints))

    def _parse_csv(self, value: str) -> list[str]:
        return [piece.strip() for piece in value.split(",") if piece.strip()]

    def _collect_brief(self) -> ProjectBrief:
        return ProjectBrief(
            title=self.title_var.get().strip(),
            premise=self.premise_text.get("1.0", tk.END).strip(),
            genre=self.genre_var.get().strip(),
            tone=self.tone_var.get().strip(),
            target_audience=self.audience_var.get().strip(),
            core_theme=self.theme_text.get("1.0", tk.END).strip(),
            setting=self.setting_text.get("1.0", tk.END).strip(),
            protagonist_overview=self.protagonist_text.get("1.0", tk.END).strip(),
            antagonist_overview=self.antagonist_text.get("1.0", tk.END).strip(),
            supporting_cast_notes=self.supporting_text.get("1.0", tk.END).strip(),
            inspirations=self._parse_csv(self.inspiration_var.get()),
            hard_constraints=self._parse_csv(self.constraints_var.get()),
            issue_count=int(self.issue_var.get().strip()),
            pages_per_issue=int(self.pages_var.get().strip()),
            panels_per_page=int(self.panels_var.get().strip()),
            art_style=self.art_style_var.get().strip(),
        )

    def _kickoff_generate(self) -> None:
        try:
            brief = self._collect_brief()
        except Exception as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        self.status_var.set("Generating...")
        thread = threading.Thread(target=self._run_generation, args=(brief,), daemon=True)
        thread.start()

    def _run_generation(self, brief: ProjectBrief) -> None:
        try:
            if self.config_path_var.get().strip():
                cfg = _config_from_json(Path(self.config_path_var.get().strip()))
            else:
                cfg = GenerationConfig.from_profile(self.profile_var.get().strip())
            cfg.output_root = Path(self.output_var.get().strip())
            cfg.preview_images_enabled = self.preview_enabled_var.get()
            cfg.preview_backend = self.preview_backend_var.get().strip() or cfg.preview_backend
            cfg.preview_endpoint = self.preview_endpoint_var.get().strip() or cfg.preview_endpoint
            cfg.preview_max_images = max(0, int(self.preview_max_var.get().strip() or "0"))

            studio = GraphicNovelStudio(cfg)
            _, writes = studio.generate(brief, progress_callback=self._on_progress)
            self.after(
                0,
                lambda: messagebox.showinfo(
                    "Generation complete",
                    "\n".join(
                        ["Artifacts:"] + [f"- {key}: {value}" for key, value in sorted(writes.items())]
                    ),
                ),
            )
            self.after(0, lambda: self.status_var.set("Done."))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("Generation failed", str(exc)))
            self.after(0, lambda: self.status_var.set("Failed."))

    def _on_progress(self, step: str) -> None:
        self.after(0, lambda: self.status_var.set(f"Running: {step}"))


def main() -> int:
    app = GraphicNovelApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
