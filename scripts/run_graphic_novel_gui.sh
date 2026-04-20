#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-graphic-novel-ai"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "Virtualenv not found at ${VENV_DIR}."
  echo "Run scripts/install_graphic_novel_ai.sh first."
  exit 1
fi

source "${VENV_DIR}/bin/activate"
python -m graphic_novel_ai.gui
