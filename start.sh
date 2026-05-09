#!/bin/bash
set -e

FORWARDER_SCRIPT="/home/msi/proyectos/superagente/scripts/ollama_forward.py"
PID=$(pgrep -f ollama_forward.py 2>/dev/null || true)

if [ -n "$PID" ]; then
    echo "[OK] Forwarder ya corriendo (PID $PID)"
else
    echo "[..] Iniciando forwarder Ollama..."
    setsid python3 "$FORWARDER_SCRIPT" &
    echo "[OK] Forwarder iniciado"
fi

echo "[..] Iniciando servicios Docker..."
docker compose up
