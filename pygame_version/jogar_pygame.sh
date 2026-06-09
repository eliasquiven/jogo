#!/usr/bin/env bash
# Crônicas de Pedravale — versão Pygame (gráfica).
cd "$(dirname "$0")"
PY="../.venv/bin/python"
[ -x "$PY" ] || PY="python3"
exec "$PY" main.py
