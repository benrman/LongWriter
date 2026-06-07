"""End-to-end orchestration for the graphic novel generation workflow."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

from .agents import build_agents
from .config import GenerationConfig, ProjectBrief
from .exporters import (
    save_fdx_script,
    save_fountain_script,
    save_storyboard_pdf,
)
from .image_hooks import generate_preview_images
from .io_utils import (
    save_art_prompts_csv,
    save_markdown,
    save_preview_manifest_json,
    save_production_checklist,
    save_project_json,
)
from .llm import LLMBackend, OllamaBackend


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return cleaned or "graphic-novel-project"


class GraphicNovelStudio:
    """Main orchestration class for multi-agent generation."""

    def __init__(self, config: GenerationConfig, backend: LLMBackend | None = None) -> None:
        self.config = config
        self.backend: LLMBackend = backend or OllamaBackend(config)
        self.agents = build_agents(config, self.backend)

    def generate(
        self,
        brief: ProjectBrief,
        progress_callback: Callable[[str], None] | None = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Path]]:
        """Run the full pipeline and persist outputs."""
        def report(step: str) -> None:
            if progress_callback is not None:
                progress_callback(step)

        payload: Dict[str, Any] = {"brief": asdict(brief)}

        report("story_architect")
        story_foundation = self.agents["story_architect"].execute(brief)
        payload["story_foundation"] = story_foundation

        report("character_designer")
        character_bible = self.agents["character_designer"].execute(brief, story_foundation)
        payload["character_bible"] = character_bible

        report("arc_planner")
        issue_arcs = self.agents["arc_planner"].execute(brief, story_foundation, character_bible)
        payload["issue_arcs"] = issue_arcs

        report("panel_writer")
        panel_scripts = self.agents["panel_writer"].execute(
            brief,
            story_foundation,
            character_bible,
            issue_arcs,
        )
        payload["panel_scripts"] = panel_scripts

        post_tasks: Dict[str, Callable[[], Dict[str, Any]]] = {}
        if self.config.include_dialogue_punchup:
            post_tasks["dialogue_polish"] = lambda: self.agents["dialogue_doctor"].execute(panel_scripts, brief)
        if self.config.include_continuity_report:
            post_tasks["continuity_report"] = lambda: self.agents["continuity_editor"].execute(
                story_foundation,
                character_bible,
                issue_arcs,
                panel_scripts,
            )
        if self.config.include_art_prompt_pack:
            post_tasks["art_prompt_pack"] = lambda: self.agents["art_prompt_packer"].execute(panel_scripts, brief)

        if post_tasks:
            max_workers = max(1, min(self.config.max_agents_parallel, len(post_tasks)))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_map = {
                    executor.submit(task): output_key for output_key, task in post_tasks.items()
                }
                for future in as_completed(future_map):
                    output_key = future_map[future]
                    report(output_key)
                    payload[output_key] = future.result()

        slug = slugify(brief.title)
        output_root = Path(self.config.output_root)
        writes: Dict[str, Path] = {}
        report("saving_outputs")
        writes["json"] = save_project_json(payload, output_root, slug)
        writes["markdown"] = save_markdown(payload, brief, output_root, slug)
        art_csv = save_art_prompts_csv(payload, output_root, slug)
        if art_csv is not None:
            writes["art_prompts_csv"] = art_csv
        writes["production_checklist"] = save_production_checklist(brief, output_root, slug)

        preview_map: Dict[str, str] = {}
        if self.config.preview_images_enabled:
            report("preview_images")
            preview_map, preview_manifest = generate_preview_images(
                project_payload=payload,
                output_root=output_root,
                slug=slug,
                backend=self.config.preview_backend,
                endpoint=self.config.preview_endpoint,
                max_images=self.config.preview_max_images,
                width=self.config.preview_width,
                height=self.config.preview_height,
                steps=self.config.preview_steps,
                sampler=self.config.preview_sampler,
                cfg_scale=self.config.preview_cfg_scale,
                negative_prompt=self.config.preview_negative_prompt,
                timeout_seconds=self.config.timeout_seconds,
                enabled=True,
            )
            writes["preview_manifest"] = save_preview_manifest_json(preview_manifest, output_root, slug)

        if self.config.export_fountain:
            writes["fountain"] = save_fountain_script(payload, brief, output_root, slug)
        if self.config.export_fdx:
            writes["fdx"] = save_fdx_script(payload, brief, output_root, slug)
        if self.config.export_storyboard_pdf:
            writes["storyboard_pdf"] = save_storyboard_pdf(
                payload,
                brief,
                output_root,
                slug,
                preview_manifest=preview_map,
            )
        report("done")
        return payload, writes
