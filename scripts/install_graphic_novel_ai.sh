#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-graphic-novel-ai"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "${ROOT_DIR}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Python executable not found: ${PYTHON_BIN}"
  exit 1
fi

echo "[1/6] Checking Python version (>=3.10)..."
"${PYTHON_BIN}" - <<'PY'
import sys
if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10 or newer is required.")
PY

if [[ -d "${VENV_DIR}" ]]; then
  echo "[2/6] Virtual environment already exists at ${VENV_DIR}."
else
  echo "[2/6] Creating virtual environment at ${VENV_DIR}..."
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

echo "[3/6] Activating environment..."
source "${VENV_DIR}/bin/activate"

echo "[4/6] Upgrading pip..."
python -m pip install --upgrade pip

echo "[5/6] Installing requirements..."
pip install -r requirements.txt

echo "[6/6] Checking local Ollama setup..."
if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama CLI not found."
  echo "Install Ollama from https://ollama.com/download then run:"
  echo "  ollama serve"
  echo "  ollama pull llama3.1:8b-instruct-q4_K_M"
  echo "  ollama pull qwen2.5:7b-instruct-q4_K_M"
else
  if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
    echo "Ollama installed but server is not running."
    echo "Start it with: ollama serve"
  fi
  echo "Pulling recommended models for RTX 3070 profile..."
  ollama pull llama3.1:8b-instruct-q4_K_M
  ollama pull qwen2.5:7b-instruct-q4_K_M
fi

echo ""
echo "Install complete."
echo "Next:"
echo "  source ${VENV_DIR}/bin/activate"
echo "  python -m graphic_novel_ai --init-templates"
echo "  python -m graphic_novel_ai --interactive --profile rtx3070"
