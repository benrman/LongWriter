"""IO and formatting helpers for output artifacts."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .config import ProjectBrief


def _json_dump(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")


def save_project_json(project_payload: Dict[str, Any], output_root: Path, slug: str) -> Path:
    out = output_root / slug / "project_bundle.json"
    _json_dump(project_payload, out)
    return out


def save_markdown(project_payload: Dict[str, Any], brief: ProjectBrief, output_root: Path, slug: str) -> Path:
    out = output_root / slug / "project_bundle.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {brief.title} - Graphic Novel Studio Output",
        "",
        f"- Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"- Genre: {brief.genre}",
        f"- Tone: {brief.tone}",
        f"- Target Audience: {brief.target_audience}",
        "",
        "## Premise",
        brief.premise,
        "",
    ]

    for section_name in (
        "story_foundation",
        "character_bible",
        "issue_arcs",
        "panel_scripts",
        "dialogue_polish",
        "continuity_report",
        "art_prompt_pack",
    ):
        if section_name not in project_payload:
            continue
        lines.append(f"## {section_name.replace('_', ' ').title()}")
        lines.append("```json")
        lines.append(json.dumps(project_payload[section_name], ensure_ascii=True, indent=2))
        lines.append("```")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def _extract_art_prompt_rows(project_payload: Dict[str, Any]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    art_pack = project_payload.get("art_prompt_pack", {})
    issue_prompts = art_pack.get("issue_prompts", []) if isinstance(art_pack, dict) else []
    for issue in issue_prompts:
        issue_number = str(issue.get("issue_number", ""))
        for panel in issue.get("panel_prompts", []):
            rows.append(
                {
                    "issue_number": issue_number,
                    "location": str(panel.get("location", "")),
                    "shot_type": str(panel.get("shot_type", "")),
                    "lighting": str(panel.get("lighting", "")),
                    "prompt": str(panel.get("prompt", "")),
                }
            )
    return rows


def save_art_prompts_csv(project_payload: Dict[str, Any], output_root: Path, slug: str) -> Path | None:
    rows = _extract_art_prompt_rows(project_payload)
    if not rows:
        return None
    out = output_root / slug / "art_prompts.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["issue_number", "location", "shot_type", "lighting", "prompt"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return out


def save_production_checklist(brief: ProjectBrief, output_root: Path, slug: str) -> Path:
    out = output_root / slug / "production_checklist.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    checklist = [
        f"# Production Checklist - {brief.title}",
        "",
        "## Writing Room",
        "- [ ] Review story foundation and world rules.",
        "- [ ] Confirm character voices and visual motifs.",
        "- [ ] Lock issue-by-issue arcs and cliffhangers.",
        "",
        "## Script Drafting",
        "- [ ] Review panel scripts for page-turn beats.",
        "- [ ] Run dialogue polish notes against final balloons.",
        "- [ ] Confirm SFX and caption density per page.",
        "",
        "## Art Direction",
        "- [ ] Validate art prompts for character consistency.",
        "- [ ] Ensure camera framing variety across action scenes.",
        "- [ ] Verify lighting and mood continuity by issue.",
        "",
        "## Continuity and QA",
        "- [ ] Resolve high-severity continuity findings first.",
        "- [ ] Resolve medium findings or log intentional exceptions.",
        "- [ ] Re-run continuity report after revisions.",
        "",
        "## Delivery",
        "- [ ] Export final script package.",
        "- [ ] Archive JSON, markdown, and prompt CSV artifacts.",
    ]
    out.write_text("\n".join(checklist), encoding="utf-8")
    return out
