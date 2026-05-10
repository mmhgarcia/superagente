#!/bin/bash
set -e

SERVICE="forwarder-ollama.service"
if systemctl --user is-active "$SERVICE" &>/dev/null; then
    echo "[OK] Forwarder ya corriendo como servicio systemd"
else
    echo "[..] Iniciando forwarder Ollama como servicio systemd..."
    systemctl --user reset-failed "$SERVICE" 2>/dev/null || true
    systemd-run --user --unit=forwarder-ollama --same-dir \
        -p Restart=on-failure \
        python3 /home/msi/proyectos/superagente/scripts/forwarder_simple.py
    sleep 2
    if systemctl --user is-active "$SERVICE" &>/dev/null; then
        echo "[OK] Forwarder iniciado como servicio"
    else
        echo "[ERROR] No se pudo iniciar el forwarder"
        exit 1
    fi
fi

echo "[..] Iniciando servicios Docker..."
docker compose up
