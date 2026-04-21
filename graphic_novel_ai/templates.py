"""Template generation helpers for first-time users."""

from __future__ import annotations

import json
from pathlib import Path

from .config import GenerationConfig, ProjectBrief


def write_example_brief(path: Path) -> Path:
    """Write an example brief JSON."""
    brief = ProjectBrief(
        title="Neon Ashes",
        premise=(
            "A courier in a memory-modded city discovers she can restore erased truths. "
            "As corporate factions weaponize public memory, she must choose between "
            "exposing reality or protecting the people she loves."
        ),
        genre="Sci-Fi Fantasy Noir",
        tone="Cinematic, melancholic, hopeful",
        target_audience="Older Teen / Adult",
        core_theme="Truth versus comfort; identity under revision",
        setting="A neon megacity where myths are licensed as software.",
        protagonist_overview="A bike courier with involuntary empathic memory sync.",
        antagonist_overview="A charismatic CEO-priest controlling citywide memory feeds.",
        supporting_cast_notes="A rogue archivist, a former enforcer, a street-oracle child.",
        inspirations=["Blade Runner", "Saga", "Akira"],
        hard_constraints=["No explicit sexual content", "Limit gore to PG-13"],
        issue_count=6,
        pages_per_issue=24,
        panels_per_page=4,
        art_style="Painterly cyber-noir comic style with dramatic lighting",
    )
    payload = json.loads(json.dumps(brief.__dict__, ensure_ascii=True))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return path


def write_example_config(path: Path) -> Path:
    """Write an example runtime config JSON."""
    cfg = GenerationConfig.from_profile("rtx3070")
    payload = {
        "profile": "rtx3070",
        "output_root": str(cfg.output_root),
        "ollama_url": cfg.ollama_url,
        "temperature": cfg.temperature,
        "top_p": cfg.top_p,
        "timeout_seconds": cfg.timeout_seconds,
        "retry_attempts": cfg.retry_attempts,
        "max_agents_parallel": cfg.max_agents_parallel,
        "include_dialogue_punchup": cfg.include_dialogue_punchup,
        "include_continuity_report": cfg.include_continuity_report,
        "include_art_prompt_pack": cfg.include_art_prompt_pack,
        "export_fountain": cfg.export_fountain,
        "export_fdx": cfg.export_fdx,
        "export_storyboard_pdf": cfg.export_storyboard_pdf,
        "preview_images_enabled": cfg.preview_images_enabled,
        "preview_backend": cfg.preview_backend,
        "preview_endpoint": cfg.preview_endpoint,
        "preview_max_images": cfg.preview_max_images,
        "preview_width": cfg.preview_width,
        "preview_height": cfg.preview_height,
        "preview_steps": cfg.preview_steps,
        "preview_sampler": cfg.preview_sampler,
        "preview_cfg_scale": cfg.preview_cfg_scale,
        "preview_negative_prompt": cfg.preview_negative_prompt,
        "agent_models": cfg.agent_models,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    return path
