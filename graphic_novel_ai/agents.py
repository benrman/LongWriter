"""Agent definitions for the local graphic novel pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from .config import GenerationConfig, ProjectBrief
from .llm import LLMBackend


def _to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def _parse_json_or_wrap(raw: str, field: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {field: raw}


@dataclass
class BaseAgent:
    name: str
    system_prompt: str
    output_schema_hint: str
    backend: LLMBackend
    model_name: str
    temperature: float

    def run(self, prompt: str) -> str:
        return self.backend.generate(
            model=self.model_name,
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            temperature=self.temperature,
        )


class StoryArchitectAgent(BaseAgent):
    def execute(self, brief: ProjectBrief) -> Dict[str, Any]:
        prompt = (
            "Create a story foundation for a serialized graphic novel.\n"
            "Return strict JSON only.\n\n"
            f"BRIEF:\n{_to_json(brief.__dict__)}\n\n"
            f"Required JSON schema shape:\n{self.output_schema_hint}\n"
        )
        return _parse_json_or_wrap(self.run(prompt), "story_foundation")


class CharacterDesignerAgent(BaseAgent):
    def execute(self, brief: ProjectBrief, foundation: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            "Design a production-ready character bible.\n"
            "Return strict JSON only.\n\n"
            f"BRIEF:\n{_to_json(brief.__dict__)}\n\n"
            f"FOUNDATION:\n{_to_json(foundation)}\n\n"
            f"Required JSON schema shape:\n{self.output_schema_hint}\n"
        )
        return _parse_json_or_wrap(self.run(prompt), "character_bible")


class ArcPlannerAgent(BaseAgent):
    def execute(
        self,
        brief: ProjectBrief,
        foundation: Dict[str, Any],
        characters: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = (
            "Plan issue-by-issue arcs with escalating stakes and thematic cohesion.\n"
            "Return strict JSON only.\n\n"
            f"BRIEF:\n{_to_json(brief.__dict__)}\n\n"
            f"FOUNDATION:\n{_to_json(foundation)}\n\n"
            f"CHARACTERS:\n{_to_json(characters)}\n\n"
            f"Required JSON schema shape:\n{self.output_schema_hint}\n"
        )
        return _parse_json_or_wrap(self.run(prompt), "issue_arcs")


class PanelWriterAgent(BaseAgent):
    def execute(
        self,
        brief: ProjectBrief,
        foundation: Dict[str, Any],
        characters: Dict[str, Any],
        arcs: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = (
            "Write panel-by-panel scripts for all issues.\n"
            "Each page must include panel description, camera/framing notes, and dialogue.\n"
            "Return strict JSON only.\n\n"
            f"BRIEF:\n{_to_json(brief.__dict__)}\n\n"
            f"FOUNDATION:\n{_to_json(foundation)}\n\n"
            f"CHARACTERS:\n{_to_json(characters)}\n\n"
            f"ARCS:\n{_to_json(arcs)}\n\n"
            f"Required JSON schema shape:\n{self.output_schema_hint}\n"
        )
        return _parse_json_or_wrap(self.run(prompt), "panel_scripts")


class DialogueDoctorAgent(BaseAgent):
    def execute(self, scripts: Dict[str, Any], brief: ProjectBrief) -> Dict[str, Any]:
        prompt = (
            "Improve dialogue for voice consistency, brevity, and emotional impact.\n"
            "Do not alter plot beats.\n"
            "Return strict JSON only.\n\n"
            f"BRIEF:\n{_to_json(brief.__dict__)}\n\n"
            f"SCRIPTS:\n{_to_json(scripts)}\n\n"
            f"Required JSON schema shape:\n{self.output_schema_hint}\n"
        )
        return _parse_json_or_wrap(self.run(prompt), "dialogue_polish")


class ContinuityEditorAgent(BaseAgent):
    def execute(
        self,
        foundation: Dict[str, Any],
        characters: Dict[str, Any],
        arcs: Dict[str, Any],
        scripts: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = (
            "Audit continuity and detect contradictions.\n"
            "Return strict JSON only.\n\n"
            f"FOUNDATION:\n{_to_json(foundation)}\n\n"
            f"CHARACTERS:\n{_to_json(characters)}\n\n"
            f"ARCS:\n{_to_json(arcs)}\n\n"
            f"SCRIPTS:\n{_to_json(scripts)}\n\n"
            f"Required JSON schema shape:\n{self.output_schema_hint}\n"
        )
        return _parse_json_or_wrap(self.run(prompt), "continuity_report")


class ArtPromptPackerAgent(BaseAgent):
    def execute(self, scripts: Dict[str, Any], brief: ProjectBrief) -> Dict[str, Any]:
        prompt = (
            "Convert panel descriptions into high-quality image prompts for comic illustration models.\n"
            "Include style, composition, lighting, lens, and mood tags.\n"
            "Return strict JSON only.\n\n"
            f"BRIEF:\n{_to_json(brief.__dict__)}\n\n"
            f"SCRIPTS:\n{_to_json(scripts)}\n\n"
            f"Required JSON schema shape:\n{self.output_schema_hint}\n"
        )
        return _parse_json_or_wrap(self.run(prompt), "art_prompt_pack")


def build_agents(config: GenerationConfig, backend: LLMBackend) -> Dict[str, BaseAgent]:
    """Create all agents with per-role model routing."""
    model_for = config.agent_models

    return {
        "story_architect": StoryArchitectAgent(
            name="story_architect",
            backend=backend,
            model_name=model_for["story_architect"],
            temperature=config.temperature,
            system_prompt=(
                "You are a veteran graphic novel architect. "
                "Output only valid JSON and keep narrative cohesion across long arcs."
            ),
            output_schema_hint=_to_json(
                {
                    "logline": "string",
                    "themes": ["string"],
                    "world_rules": ["string"],
                    "series_hook": "string",
                    "act_structure": [
                        {"act": 1, "goal": "string", "major_turn": "string"},
                    ],
                }
            ),
        ),
        "character_designer": CharacterDesignerAgent(
            name="character_designer",
            backend=backend,
            model_name=model_for["character_designer"],
            temperature=config.temperature,
            system_prompt=(
                "You are a character dramaturg and comics editor. "
                "Design cast with clear goals, flaws, visual motifs, and voice prints."
            ),
            output_schema_hint=_to_json(
                {
                    "protagonist": {
                        "name": "string",
                        "goal": "string",
                        "wound": "string",
                        "voice_notes": ["string"],
                        "visual_motifs": ["string"],
                    },
                    "antagonist": {
                        "name": "string",
                        "strategy": "string",
                        "contradiction": "string",
                    },
                    "supporting_cast": [
                        {
                            "name": "string",
                            "role": "string",
                            "arc_function": "string",
                            "relationship_to_protagonist": "string",
                        }
                    ],
                }
            ),
        ),
        "arc_planner": ArcPlannerAgent(
            name="arc_planner",
            backend=backend,
            model_name=model_for["arc_planner"],
            temperature=config.temperature,
            system_prompt=(
                "You are a long-form series planner for monthly comic issues. "
                "Balance spectacle, character growth, and cliffhangers."
            ),
            output_schema_hint=_to_json(
                {
                    "issues": [
                        {
                            "issue_number": 1,
                            "title": "string",
                            "summary": "string",
                            "emotional_beat": "string",
                            "cliffhanger": "string",
                            "key_scenes": ["string"],
                        }
                    ]
                }
            ),
        ),
        "panel_writer": PanelWriterAgent(
            name="panel_writer",
            backend=backend,
            model_name=model_for["panel_writer"],
            temperature=config.temperature,
            system_prompt=(
                "You are a panel-level script writer for comic production. "
                "Output cinematic but drawable panels with concise dialogue."
            ),
            output_schema_hint=_to_json(
                {
                    "issues": [
                        {
                            "issue_number": 1,
                            "pages": [
                                {
                                    "page_number": 1,
                                    "panels": [
                                        {
                                            "panel_number": 1,
                                            "description": "string",
                                            "camera": "string",
                                            "dialogue": [
                                                {"speaker": "string", "line": "string"}
                                            ],
                                            "sfx": ["string"],
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                }
            ),
        ),
        "dialogue_doctor": DialogueDoctorAgent(
            name="dialogue_doctor",
            backend=backend,
            model_name=model_for["dialogue_doctor"],
            temperature=config.temperature * 0.8,
            system_prompt=(
                "You are a dialogue polisher specialized in comics. "
                "Tighten lines and preserve voice consistency."
            ),
            output_schema_hint=_to_json(
                {
                    "issues": [
                        {
                            "issue_number": 1,
                            "changes": [
                                {
                                    "location": "Issue 1 Page 1 Panel 2",
                                    "old_line": "string",
                                    "new_line": "string",
                                    "reason": "string",
                                }
                            ],
                            "revised_pages": [
                                {
                                    "page_number": 1,
                                    "panels": [
                                        {
                                            "panel_number": 1,
                                            "dialogue": [
                                                {"speaker": "string", "line": "string"}
                                            ],
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                }
            ),
        ),
        "continuity_editor": ContinuityEditorAgent(
            name="continuity_editor",
            backend=backend,
            model_name=model_for["continuity_editor"],
            temperature=config.temperature * 0.4,
            system_prompt=(
                "You are a strict continuity editor. "
                "Flag contradictions, timeline errors, and missing setups/payoffs."
            ),
            output_schema_hint=_to_json(
                {
                    "continuity_score": 0,
                    "findings": [
                        {
                            "severity": "high|medium|low",
                            "location": "Issue X Page Y",
                            "problem": "string",
                            "suggested_fix": "string",
                        }
                    ],
                    "unresolved_threads": ["string"],
                }
            ),
        ),
        "art_prompt_packer": ArtPromptPackerAgent(
            name="art_prompt_packer",
            backend=backend,
            model_name=model_for["art_prompt_packer"],
            temperature=config.temperature,
            system_prompt=(
                "You are an art direction AI converting scripts to image prompts. "
                "Keep character and costume consistency across prompts."
            ),
            output_schema_hint=_to_json(
                {
                    "style_guide": {
                        "global_prompt_prefix": "string",
                        "negative_prompt": "string",
                    },
                    "issue_prompts": [
                        {
                            "issue_number": 1,
                            "panel_prompts": [
                                {
                                    "location": "Issue 1 Page 1 Panel 1",
                                    "prompt": "string",
                                    "shot_type": "string",
                                    "lighting": "string",
                                }
                            ],
                        }
                    ],
                }
            ),
        ),
    }
