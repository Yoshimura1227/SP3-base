#!/usr/bin/env bash
set -eu

python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install pygame pandas pytest

echo "Setup complete."
echo "Run the game with:"
echo "  ./run_game1.sh"

