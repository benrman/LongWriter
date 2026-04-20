# Graphic Novel AI Studio (Local-First)

Graphic Novel AI Studio is a local multi-agent pipeline for planning and writing graphic novels on your own machine.

It is designed for creators who want:

- Local execution with your own GPU/CPU resources
- A multi-agent writing room (story, characters, arcs, panel scripts, dialogue polish, continuity, art prompts)
- Easy operation through either CLI wizard or desktop GUI

## 1) Hardware fit (your laptop profile)

For an RTX 3070-class laptop with 64GB RAM, use the default profile:

- `rtx3070` profile
- 7B/8B quantized models via Ollama
- Parallel post-processing agents for speed

## 2) Install

### Linux/macOS

```bash
bash scripts/install_graphic_novel_ai.sh
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_graphic_novel_ai.ps1
```

This will:

1. Create `.venv-graphic-novel-ai`
2. Install Python dependencies
3. Install and start Ollama (if needed)
4. Pull recommended models:
   - `llama3.1:8b-instruct-q4_K_M`
   - `qwen2.5:7b-instruct-q4_K_M`

## 3) Quick start

Generate starter files:

```bash
python -m graphic_novel_ai --init-templates
```

Then run in interactive wizard mode:

```bash
python -m graphic_novel_ai --interactive --profile rtx3070
```

Or run from a JSON brief:

```bash
python -m graphic_novel_ai --brief graphic_novel_ai_templates/brief.example.json --profile rtx3070
```

### GUI mode

```bash
bash scripts/run_graphic_novel_gui.sh
```

## 4) Outputs

By default, outputs are saved under:

`outputs/graphic_novel_ai/<project-slug>/`

Artifacts include:

- `project_bundle.json`
- `project_bundle.md`
- `art_prompts.csv` (if art prompt pack is enabled)
- `production_checklist.md`

## 5) Agent team

Pipeline agents:

1. `story_architect`
2. `character_designer`
3. `arc_planner`
4. `panel_writer`
5. `dialogue_doctor`
6. `continuity_editor`
7. `art_prompt_packer`

The first four run sequentially (dependency chain), and the final three can run in parallel.

## 6) Tips

- If generation is slow, reduce issue count/pages in the brief.
- If Ollama is remote, override `ollama_url` in a config JSON and pass `--config`.
- For quality-first workflows, switch to `--profile high_quality` and ensure sufficient VRAM/RAM headroom.
