#!/usr/bin/env python3
"""
bridge.py — Puente serie host ↔ contenedor para `make flash`.

Uso:
    python bridge.py <comando...>

Ejemplo:
    python bridge.py docker compose -f docker-compose.yml \
        -f docker-compose.flash.yml --profile flash run --rm esp-dev idf.py flash
"""

from __future__ import annotations

import atexit
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

# --- Constantes -------------------------------------------------------------

FTDI_VID           = 0x0403
RFC2217_PORT       = 2217
CONNECT_TIMEOUT_S  = 10.0
CONNECT_POLL_S     = 0.1

# --- Utilidades -------------------------------------------------------------

def log(msg: str) -> None:
    print(f"[bridge] {msg}", flush=True)

def die(msg: str, code: int = 1) -> NoReturn:
    print(f"[bridge] ERROR: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)

def prefer_callout(device: str) -> str:
    """En macOS, /dev/tty.* bloquea hasta DCD. Preferimos /dev/cu.*."""
    if platform.system() == "Darwin" and device.startswith("/dev/tty."):
        cu = device.replace("/dev/tty.", "/dev/cu.", 1)
        if os.path.exists(cu):
            return cu
    return device

def find_serial_port() -> str:
    """Devuelve la ruta del puerto serie del ESP32 (FTDI VID 0x0403)."""
    override = os.environ.get("MP32_PORT")
    if override:
        log(f"Usando MP32_PORT={override}")
        return prefer_callout(override)

    try:
        from serial.tools import list_ports
    except ImportError:
        die("Falta pyserial. Instala con: pip install pyserial")

    all_ports  = list(list_ports.comports())
    candidates = [p for p in all_ports if p.vid == FTDI_VID]

    if not candidates:
        avail = "\n".join(f"  - {p.device} ({p.description})" for p in all_ports) or "  (ninguno)"
        die(
            "No se encontró ningún dispositivo FTDI (VID 0x0403).\n"
            f"Puertos serie disponibles:\n{avail}\n"
            "Conecta el ESP32 por USB o define MP32_PORT=/dev/ttyXXX"
        )

    if len(candidates) > 1:
        log("Varios dispositivos FTDI detectados:")
        for p in candidates:
            log(f"  - {p.device} ({p.description})")
        die("Selecciona uno con MP32_PORT=/dev/ttyXXX")

    port = candidates[0]
    log(f"Detectado: {port.device} ({port.description})")
    return prefer_callout(port.device)

def find_rfc_server_cmd() -> list[str]:
    """
    Localiza esp_rfc2217_server. Intentos en orden:
      1) Console script en PATH (pip puede o no instalarlo).
      2) Módulo esptool.rfc2217_server (según versión de esptool).
      3) Archivo esp_rfc2217_server.py junto a este bridge.py.
    """
    on_path = shutil.which("esp_rfc2217_server")
    if on_path:
        return [on_path]

    try:
        import esptool.rfc2217_server  # noqa: F401
        return [sys.executable, "-m", "esptool.rfc2217_server"]
    except ImportError:
        pass

    local = Path(__file__).resolve().parent / "esp_rfc2217_server.py"
    if local.exists():
        return [sys.executable, str(local)]

    die(
        "No se encontró esp_rfc2217_server.\n"
        "Opciones:\n"
        "  1) pip install --upgrade esptool\n"
        "  2) Descarga esp_rfc2217_server.py desde\n"
        "     https://github.com/espressif/esptool y colócalo junto a bridge.py"
    )

def ensure_port_free(host: str, port: int) -> None:
    """Falla rápido si algo ya está escuchando en `port`."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
        except OSError:
            die(
                f"El puerto TCP {port} ya está en uso.\n"
                "Detén cualquier esp_rfc2217_server previo y reintenta."
            )

def wait_for_port(host: str, port: int, timeout: float) -> None:
    """Espera a que `host:port` acepte conexiones TCP."""
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError as e:
            last_err = e
            time.sleep(CONNECT_POLL_S)
    die(f"El servidor RFC 2217 no respondió en {timeout:.0f}s ({last_err})")

# --- Orquestador ------------------------------------------------------------

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    command = argv[1:]

    # ① Detectar el ESP32
    serial_port = find_serial_port()

    # ② Verificar que el puerto 2217 esté libre
    ensure_port_free("0.0.0.0", RFC2217_PORT)

    # ③ Localizar el servidor RFC 2217
    server_cmd  = find_rfc_server_cmd()
    server_argv = server_cmd + ["-p", str(RFC2217_PORT), serial_port]
    log(f"Lanzando servidor RFC 2217: {' '.join(server_argv)}")

    # ④ Arrancar el servidor en background
    server = subprocess.Popen(
        server_argv,
        stdout=subprocess.DEVNULL,          # no ensuciar la salida de idf.py
        stderr=subprocess.STDOUT,
    )

    # ⑤ Cleanup garantizado
    def _cleanup() -> None:
        if server.poll() is None:
            log("Deteniendo servidor RFC 2217…")
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()

    atexit.register(_cleanup)

    def _forward(signum, _frame):
        _cleanup()
        sys.exit(128 + signum)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _forward)

    # ⑥ Esperar a que el servidor esté listo
    log(f"Esperando a que escuche en 127.0.0.1:{RFC2217_PORT}…")
    wait_for_port("127.0.0.1", RFC2217_PORT, CONNECT_TIMEOUT_S)
    log("Servidor listo. Ejecutando comando…")

    # ⑦ Ejecutar el comando del usuario
    try:
        result = subprocess.run(command)
    except FileNotFoundError:
        die(f"Comando no encontrado: {command[0]}")
    finally:
        _cleanup()
        atexit.unregister(_cleanup)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))