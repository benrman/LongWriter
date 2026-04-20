"""CLI entrypoint for the Graphic Novel AI studio."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import GenerationConfig, ProjectBrief
from .pipeline import GraphicNovelStudio
from .templates import write_example_brief, write_example_config


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _brief_from_json(path: Path) -> ProjectBrief:
    payload = _read_json(path)
    return ProjectBrief(**payload)


def _config_from_json(path: Path | None) -> GenerationConfig:
    if path is None:
        return GenerationConfig()
    payload = _read_json(path)
    profile = payload.pop("profile", None)
    config = GenerationConfig.from_profile(profile) if isinstance(profile, str) else GenerationConfig()
    for key, value in payload.items():
        setattr(config, key, value)
    return config


def _interactive_brief() -> ProjectBrief:
    print("Graphic Novel AI - Quick Start Wizard")
    title = input("Title: ").strip() or "Untitled Graphic Novel"
    premise = input("Premise (1-3 sentences): ").strip() or "A team faces a world-shaping crisis."
    genre = input("Genre [Sci-Fi Fantasy]: ").strip() or "Sci-Fi Fantasy"
    tone = input("Tone [Cinematic, emotionally grounded]: ").strip() or "Cinematic, emotionally grounded"
    audience = input("Target audience [Young Adult]: ").strip() or "Young Adult"
    issue_count = input("Issue count [6]: ").strip() or "6"
    pages_per_issue = input("Pages per issue [24]: ").strip() or "24"
    panels_per_page = input("Panels per page [4]: ").strip() or "4"
    art_style = input("Art style [Cinematic comic style with dynamic framing]: ").strip()
    art_style = art_style or "Cinematic comic style with dynamic framing"

    return ProjectBrief(
        title=title,
        premise=premise,
        genre=genre,
        tone=tone,
        target_audience=audience,
        issue_count=int(issue_count),
        pages_per_issue=int(pages_per_issue),
        panels_per_page=int(panels_per_page),
        art_style=art_style,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local Graphic Novel AI Studio")
    parser.add_argument(
        "--brief",
        type=Path,
        help="Path to a project brief JSON file.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional config JSON file to override runtime settings.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run with an interactive CLI wizard.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Override output root directory.",
    )
    parser.add_argument(
        "--profile",
        choices=["balanced", "rtx3070", "high_quality"],
        default="rtx3070",
        help="Hardware profile for model routing and timeouts.",
    )
    parser.add_argument(
        "--init-templates",
        action="store_true",
        help="Write starter brief/config templates and exit.",
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=Path("graphic_novel_ai_templates"),
        help="Directory for generated templates.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.init_templates:
        brief_path = write_example_brief(args.template_dir / "brief.example.json")
        config_path = write_example_config(args.template_dir / "config.example.json")
        print(f"Wrote: {brief_path}")
        print(f"Wrote: {config_path}")
        return 0

    config = _config_from_json(args.config)
    if args.config is None:
        config = GenerationConfig.from_profile(args.profile)
    if args.output_root is not None:
        config.output_root = args.output_root

    if args.interactive:
        brief = _interactive_brief()
    elif args.brief:
        brief = _brief_from_json(args.brief)
    else:
        print("Pass --interactive or --brief <file.json>.", file=sys.stderr)
        return 2

    studio = GraphicNovelStudio(config)
    _, writes = studio.generate(brief)

    print("Generation complete.")
    print(f"JSON output: {writes['json']}")
    print(f"Markdown output: {writes['markdown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
