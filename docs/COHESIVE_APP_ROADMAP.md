# LongWriter + Nove AI Local Roadmap

This repository can become a cohesive local-first writing suite by treating
LongWriter as the long-form generation and research layer, while the local
studio app provides the creator workflow.

## Current integrated shape

- `agentwrite/`: planning and ultra-long data construction pipeline.
- `train/`: model training and long-context attention patches.
- `evaluation/`: length and quality evaluation utilities.
- `graphic_novel_ai/`: local Nove/graphic-novel studio with CLI, GUI,
  role-based agents, Ollama-backed model routing, script exports, storyboard
  PDF generation, and optional local image-preview hooks.
- `scripts/`: installer and app launch helpers.
- `tests/`: deterministic tests for the local studio pipeline.

The most important product boundary is:

1. LongWriter model assets create and improve long-form generation quality.
2. The studio turns those capabilities into a usable app for creators.
3. Exporters and evaluation close the loop from generation to production.

## Suggested next improvements

### 1. Rename and package the product surface

Choose one app-facing name, such as "Nove AI Local", and make that the public
brand while keeping `graphic_novel_ai` as an implementation package until a
planned rename is safe. Add:

- `pyproject.toml` with console scripts, for example `nove-local`.
- Version metadata and release notes.
- A single install command for app users and a separate developer install path.

### 2. Add a project library

The app currently writes generated artifacts to output folders. A lightweight
project library would make it feel like a full application:

- SQLite database for projects, scenes, characters, revisions, and exports.
- Import/export bundles for moving projects across machines.
- "Open recent project" and project search in the GUI.
- Autosave and snapshot history for generated drafts.

### 3. Build a structured editor loop

Generation should be editable between agent stages. Add screens or CLI steps
for:

- Editing the premise and constraints before planning.
- Reviewing the story foundation before character design.
- Locking character canon before arc planning.
- Regenerating only selected issues, pages, panels, or dialogue lines.
- Accepting/rejecting continuity and dialogue suggestions.

### 4. Connect LongWriter models directly

The current local studio uses Ollama-compatible model routing. Add a provider
interface that can also call:

- Local Hugging Face `transformers` models.
- vLLM endpoints for LongWriter models.
- Existing Ollama routes.
- Future OpenAI-compatible local servers.

This would let the app use LongWriter for long-draft generation and smaller
models for focused rewrite, continuity, or formatting tasks.

### 5. Add long-context memory and retrieval

Long projects need durable memory. Add a memory layer that indexes:

- Character bible entries.
- World rules and locations.
- Prior scenes, issues, and unresolved plot threads.
- User style preferences.

Use retrieval before each agent call so long series remain consistent without
forcing every prompt to include the entire project.

### 6. Improve visual workflows

The image hooks are a good start. Next features:

- Per-character visual reference sheets.
- Style-lock prompts and negative prompt presets.
- Panel-to-image retry controls.
- Contact sheet exports for thumbnails.
- Optional integration with local ComfyUI workflows.

### 7. Add quality gates

Turn the evaluation code into app-level checks:

- Length target checks for chapters/issues.
- Continuity contradiction reports.
- Character voice consistency scoring.
- Scene pacing and panel-density warnings.
- Export validation for Fountain, FDX, Markdown, and PDF outputs.

### 8. Make the GUI the primary experience

The CLI is useful for automation, but the app will feel more complete with:

- A project dashboard.
- Stage-by-stage generation progress.
- Editable tabs for outline, cast, arcs, pages, and exports.
- Settings for model providers, hardware profiles, and output formats.
- Preview thumbnails when local image rendering is enabled.

### 9. Add local privacy and safety defaults

Because the app is local-first, make privacy explicit:

- Show which provider each agent is using.
- Warn before sending prompts to non-local endpoints.
- Keep generated data under a user-selected project directory.
- Add a "delete project artifacts" workflow.

### 10. Expand tests around user workflows

Current tests cover deterministic pipeline generation. Add focused tests for:

- CLI error messages and invalid brief/config files.
- Provider selection and retry behavior.
- Export file contents, not only file existence.
- GUI-independent project library behavior once added.
- Partial regeneration and revision history.

## Near-term implementation sequence

1. Add `pyproject.toml` and console entrypoints.
2. Introduce a provider abstraction for Ollama, vLLM, and local transformers.
3. Add a project library with SQLite persistence.
4. Refactor the GUI around project stages and editable intermediate outputs.
5. Add retrieval-backed continuity memory.
6. Promote evaluation utilities into creator-facing quality reports.

