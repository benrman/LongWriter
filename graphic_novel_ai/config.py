"""Configuration models for the Graphic Novel AI studio."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


def default_agent_models() -> Dict[str, str]:
    """Reasonable defaults for an RTX 3070-class laptop."""
    return {
        "story_architect": "llama3.1:8b-instruct-q4_K_M",
        "character_designer": "llama3.1:8b-instruct-q4_K_M",
        "arc_planner": "llama3.1:8b-instruct-q4_K_M",
        "panel_writer": "qwen2.5:7b-instruct-q4_K_M",
        "dialogue_doctor": "qwen2.5:7b-instruct-q4_K_M",
        "continuity_editor": "qwen2.5:7b-instruct-q4_K_M",
        "art_prompt_packer": "llama3.1:8b-instruct-q4_K_M",
    }


HARDWARE_PROFILES: Dict[str, Dict[str, object]] = {
    "balanced": {
        "description": "General-purpose quality/performance blend.",
        "temperature": 0.7,
        "timeout_seconds": 240,
        "agent_models": default_agent_models(),
    },
    "rtx3070": {
        "description": "Tuned for laptop RTX 3070 with 64GB RAM.",
        "temperature": 0.7,
        "timeout_seconds": 300,
        "agent_models": default_agent_models(),
    },
    "high_quality": {
        "description": "Higher quality, slower output and heavier model choices.",
        "temperature": 0.65,
        "timeout_seconds": 360,
        "agent_models": {
            "story_architect": "qwen2.5:14b-instruct-q4_K_M",
            "character_designer": "qwen2.5:14b-instruct-q4_K_M",
            "arc_planner": "qwen2.5:14b-instruct-q4_K_M",
            "panel_writer": "llama3.1:8b-instruct-q4_K_M",
            "dialogue_doctor": "llama3.1:8b-instruct-q4_K_M",
            "continuity_editor": "qwen2.5:14b-instruct-q4_K_M",
            "art_prompt_packer": "llama3.1:8b-instruct-q4_K_M",
        },
    },
}


@dataclass
class ProjectBrief:
    """Input brief for a graphic novel project."""

    title: str
    premise: str
    genre: str = "Sci-Fi Fantasy"
    tone: str = "Cinematic, emotionally grounded"
    target_audience: str = "Young Adult"
    core_theme: str = "Identity, memory, and sacrifice"
    setting: str = "Near-future megacity with decaying magic"
    protagonist_overview: str = "A reluctant courier discovers reality-bending abilities."
    antagonist_overview: str = "A corporate mystic seeking to rewrite collective memory."
    supporting_cast_notes: str = ""
    inspirations: List[str] = field(default_factory=list)
    hard_constraints: List[str] = field(default_factory=list)
    issue_count: int = 6
    pages_per_issue: int = 24
    panels_per_page: int = 4
    art_style: str = "Cinematic comic style with dynamic framing"


@dataclass
class GenerationConfig:
    """Runtime generation configuration."""

    output_root: Path = field(default_factory=lambda: Path("outputs/graphic_novel_ai"))
    ollama_url: str = "http://localhost:11434"
    agent_models: Dict[str, str] = field(default_factory=default_agent_models)
    temperature: float = 0.7
    top_p: float = 0.9
    timeout_seconds: int = 240
    retry_attempts: int = 2
    max_agents_parallel: int = 3
    preserve_intermediate_json: bool = True
    include_dialogue_punchup: bool = True
    include_continuity_report: bool = True
    include_art_prompt_pack: bool = True

    @classmethod
    def from_profile(cls, profile: str) -> "GenerationConfig":
        """Build config from a named hardware profile."""
        cfg = cls()
        if profile not in HARDWARE_PROFILES:
            return cfg
        values = HARDWARE_PROFILES[profile]
        for key, value in values.items():
            if key == "description":
                continue
            if key == "agent_models":
                setattr(cfg, key, dict(value))  # defensive copy
                continue
            setattr(cfg, key, value)
        return cfg
