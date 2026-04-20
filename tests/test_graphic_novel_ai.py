"""Unit tests for the local Graphic Novel AI package."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from graphic_novel_ai.cli import main as cli_main
from graphic_novel_ai.config import GenerationConfig, ProjectBrief
from graphic_novel_ai.pipeline import GraphicNovelStudio
from graphic_novel_ai.templates import write_example_brief, write_example_config


class FakeBackend:
    """Deterministic backend for testing orchestration."""

    def generate(self, *, model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
        lower = user_prompt.lower()
        if "story foundation" in lower:
            return json.dumps(
                {
                    "logline": "A courier uncovers a memory conspiracy.",
                    "themes": ["truth", "identity"],
                    "world_rules": ["memories can be edited"],
                    "series_hook": "Every fix creates a new paradox",
                    "act_structure": [
                        {"act": 1, "goal": "survive", "major_turn": "memory leak"},
                    ],
                }
            )
        if "character bible" in lower:
            return json.dumps(
                {
                    "protagonist": {"name": "Nyx", "goal": "restore truth"},
                    "antagonist": {"name": "Voss", "strategy": "control memory markets"},
                    "supporting_cast": [{"name": "Rin", "role": "Archivist"}],
                }
            )
        if "plan issue-by-issue arcs" in lower:
            return json.dumps(
                {
                    "issues": [
                        {
                            "issue_number": 1,
                            "title": "Static Wake",
                            "summary": "Nyx discovers erased districts.",
                            "emotional_beat": "fear to resolve",
                            "cliffhanger": "her own past is fabricated",
                            "key_scenes": ["rooftop chase", "archive break-in"],
                        }
                    ]
                }
            )
        if "write panel-by-panel scripts" in lower:
            return json.dumps(
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
                                            "description": "Nyx races through neon rain.",
                                            "camera": "wide angle",
                                            "dialogue": [{"speaker": "Nyx", "line": "Not tonight."}],
                                            "sfx": ["VRRRM"],
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                }
            )
        if "improve dialogue" in lower:
            return json.dumps(
                {
                    "issues": [
                        {
                            "issue_number": 1,
                            "changes": [
                                {
                                    "location": "Issue 1 Page 1 Panel 1",
                                    "old_line": "Not tonight.",
                                    "new_line": "Not this night.",
                                    "reason": "Sharper cadence",
                                }
                            ],
                            "revised_pages": [
                                {
                                    "page_number": 1,
                                    "panels": [
                                        {
                                            "panel_number": 1,
                                            "dialogue": [
                                                {"speaker": "Nyx", "line": "Not this night."}
                                            ],
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                }
            )
        if "audit continuity" in lower:
            return json.dumps(
                {
                    "continuity_score": 92,
                    "findings": [
                        {
                            "severity": "low",
                            "location": "Issue 1 Page 1",
                            "problem": "Costume accent color drifts",
                            "suggested_fix": "Lock style sheet to cobalt accents",
                        }
                    ],
                    "unresolved_threads": ["Who erased district seven?"],
                }
            )
        if "convert panel descriptions" in lower:
            return json.dumps(
                {
                    "style_guide": {
                        "global_prompt_prefix": "cinematic comic frame, dramatic rain",
                        "negative_prompt": "deformed hands, blurry face",
                    },
                    "issue_prompts": [
                        {
                            "issue_number": 1,
                            "panel_prompts": [
                                {
                                    "location": "Issue 1 Page 1 Panel 1",
                                    "prompt": "Courier on neon bike at night",
                                    "shot_type": "wide",
                                    "lighting": "neon rim light",
                                }
                            ],
                        }
                    ],
                }
            )
        return "{}"


class GraphicNovelStudioTests(unittest.TestCase):
    def test_pipeline_generates_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "out"
            cfg = GenerationConfig.from_profile("rtx3070")
            cfg.output_root = output_root
            studio = GraphicNovelStudio(config=cfg, backend=FakeBackend())

            steps: list[str] = []
            brief = ProjectBrief(title="Neon Trial", premise="A courier fights memory warfare.")
            payload, writes = studio.generate(brief, progress_callback=steps.append)

            self.assertIn("story_foundation", payload)
            self.assertIn("character_bible", payload)
            self.assertIn("issue_arcs", payload)
            self.assertIn("panel_scripts", payload)
            self.assertIn("dialogue_polish", payload)
            self.assertIn("continuity_report", payload)
            self.assertIn("art_prompt_pack", payload)

            self.assertIn("json", writes)
            self.assertIn("markdown", writes)
            self.assertIn("art_prompts_csv", writes)
            self.assertIn("production_checklist", writes)
            for path in writes.values():
                self.assertTrue(path.exists(), f"Expected artifact missing: {path}")

            self.assertIn("done", steps)

    def test_template_generation_and_cli_template_init(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template_root = Path(temp_dir) / "templates"
            brief_path = write_example_brief(template_root / "brief.example.json")
            cfg_path = write_example_config(template_root / "config.example.json")

            self.assertTrue(brief_path.exists())
            self.assertTrue(cfg_path.exists())
            brief_payload = json.loads(brief_path.read_text(encoding="utf-8"))
            self.assertEqual(brief_payload["title"], "Neon Ashes")

            cli_out = Path(temp_dir) / "cli_templates"
            exit_code = cli_main(["--init-templates", "--template-dir", str(cli_out)])
            self.assertEqual(exit_code, 0)
            self.assertTrue((cli_out / "brief.example.json").exists())
            self.assertTrue((cli_out / "config.example.json").exists())


if __name__ == "__main__":
    unittest.main()
