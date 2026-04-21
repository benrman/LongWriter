"""Optional local image generation hooks for storyboard previews."""

from __future__ import annotations

import base64
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _safe_slug(text: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in text.strip().lower())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "project"


def _panel_prompt_entries(project_payload: Dict[str, Any]) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    art_pack = project_payload.get("art_prompt_pack", {})
    issue_prompts = art_pack.get("issue_prompts", []) if isinstance(art_pack, dict) else []
    for issue in _as_list(issue_prompts):
        if not isinstance(issue, dict):
            continue
        issue_number = str(issue.get("issue_number", ""))
        for panel in _as_list(issue.get("panel_prompts")):
            if not isinstance(panel, dict):
                continue
            location = str(panel.get("location", "")).strip()
            prompt = str(panel.get("prompt", "")).strip()
            if not location or not prompt:
                continue
            entries.append(
                {
                    "issue_number": issue_number,
                    "location": location,
                    "prompt": prompt,
                    "shot_type": str(panel.get("shot_type", "")).strip(),
                    "lighting": str(panel.get("lighting", "")).strip(),
                }
            )
    return entries


def _build_filename(location: str) -> str:
    digest = hashlib.md5(location.encode("utf-8")).hexdigest()[:8]
    base = _safe_slug(location.replace(" ", "_"))
    return f"{base}-{digest}.png"


def _http_post_json(url: str, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status_code = getattr(response, "status", 200)
        if status_code >= 400:
            raise RuntimeError(f"Request failed with status {status_code}: {url}")
        return json.loads(response.read().decode("utf-8"))


def _http_get_json(url: str, timeout: int) -> Dict[str, Any]:
    request = urllib.request.Request(url=url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status_code = getattr(response, "status", 200)
        if status_code >= 400:
            raise RuntimeError(f"Request failed with status {status_code}: {url}")
        return json.loads(response.read().decode("utf-8"))


def _render_automatic1111(
    *,
    endpoint: str,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    sampler: str,
    cfg_scale: float,
    timeout_seconds: int,
) -> bytes:
    body = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "sampler_name": sampler,
        "cfg_scale": cfg_scale,
        "batch_size": 1,
        "n_iter": 1,
    }
    data = _http_post_json(f"{endpoint.rstrip('/')}/sdapi/v1/txt2img", body, timeout_seconds)
    images = data.get("images", [])
    if not images:
        raise RuntimeError("Automatic1111 returned no images.")
    return base64.b64decode(images[0])


def _render_comfyui(
    *,
    endpoint: str,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    cfg_scale: float,
    timeout_seconds: int,
) -> bytes:
    # Minimal prompt graph targeting common ComfyUI default node IDs.
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 12345,
                "steps": steps,
                "cfg": cfg_scale,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "model.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt, "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "graphic_novel_preview", "images": ["8", 0]}},
    }
    result = _http_post_json(f"{endpoint.rstrip('/')}/prompt", {"prompt": workflow}, timeout_seconds)
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise RuntimeError("ComfyUI did not return a prompt_id.")

    history = _http_get_json(f"{endpoint.rstrip('/')}/history/{prompt_id}", timeout_seconds)
    record = history.get(prompt_id, {})
    outputs = record.get("outputs", {})
    for node in outputs.values():
        images = node.get("images", [])
        if not images:
            continue
        image_meta = images[0]
        filename = image_meta.get("filename")
        subfolder = image_meta.get("subfolder", "")
        if not filename:
            continue
        query = f"filename={filename}&subfolder={subfolder}&type=output"
        with urllib.request.urlopen(f"{endpoint.rstrip('/')}/view?{query}", timeout=timeout_seconds) as response:
            return response.read()
    raise RuntimeError("ComfyUI finished but no image outputs were found.")


def generate_preview_images(
    *,
    project_payload: Dict[str, Any],
    output_root: Path,
    slug: str,
    backend: str,
    endpoint: str,
    max_images: int,
    width: int,
    height: int,
    steps: int,
    sampler: str,
    cfg_scale: float,
    negative_prompt: str,
    timeout_seconds: int,
    enabled: bool,
) -> Tuple[Dict[str, str], Dict[str, Any]]:
    """
    Generate optional preview images from panel prompts.

    Returns:
      - location -> image path map
      - manifest data including errors
    """
    if not enabled:
        return {}, {"enabled": False, "backend": backend, "results": [], "errors": []}

    entries = _panel_prompt_entries(project_payload)
    if not entries:
        return {}, {"enabled": True, "backend": backend, "results": [], "errors": ["No panel prompts found."]}

    selected = entries[: max(0, max_images)]
    preview_dir = output_root / slug / "preview_images"
    preview_dir.mkdir(parents=True, exist_ok=True)

    map_by_location: Dict[str, str] = {}
    results: List[Dict[str, str]] = []
    errors: List[str] = []

    for entry in selected:
        location = entry["location"]
        prompt = entry["prompt"]
        filename = _build_filename(location)
        target = preview_dir / filename
        try:
            if backend == "automatic1111":
                blob = _render_automatic1111(
                    endpoint=endpoint,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    steps=steps,
                    sampler=sampler,
                    cfg_scale=cfg_scale,
                    timeout_seconds=timeout_seconds,
                )
            elif backend == "comfyui":
                blob = _render_comfyui(
                    endpoint=endpoint,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    timeout_seconds=timeout_seconds,
                )
            else:
                raise ValueError(f"Unsupported preview backend: {backend}")
            target.write_bytes(blob)
            path_text = str(target)
            map_by_location[location] = path_text
            results.append(
                {
                    "location": location,
                    "prompt": prompt,
                    "file": path_text,
                }
            )
        except (RuntimeError, ValueError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            errors.append(f"{location}: {exc}")

    manifest = {
        "enabled": True,
        "backend": backend,
        "endpoint": endpoint,
        "width": width,
        "height": height,
        "steps": steps,
        "sampler": sampler,
        "cfg_scale": cfg_scale,
        "negative_prompt": negative_prompt,
        "requested": len(selected),
        "completed": len(results),
        "results": results,
        "errors": errors,
    }
    return map_by_location, manifest
