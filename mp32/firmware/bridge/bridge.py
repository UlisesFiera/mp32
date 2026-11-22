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
import threading
import time
from pathlib import Path
from typing import NoReturn, TextIO

# Constants

FTDI_VID           = 0x0403
RFC2217_PORT       = 2217
CONNECT_TIMEOUT_S  = 10.0
CONNECT_POLL_S     = 0.1

# Utils

def _bridge_prefix(stream: TextIO) -> str:
    if stream.isatty() and "NO_COLOR" not in os.environ:
        return "\033[33m[bridge]\033[0m"
    return "[bridge]"


def log(msg: str) -> None:
    print(f"{_bridge_prefix(sys.stdout)} {msg}", flush=True)

def die(msg: str, code: int = 1) -> NoReturn:
    print(f"{_bridge_prefix(sys.stderr)} ERROR: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)

def prefer_callout(device: str) -> str:
    """En macOS, /dev/tty.* bloquea hasta DCD. Preferimos /dev/cu.*."""
    if platform.system() == "Darwin" and device.startswith("/dev/tty."):
        cu = device.replace("/dev/tty.", "/dev/cu.", 1)
        if os.path.exists(cu):
            return cu
    return device

def find_serial_port() -> str:
    """
    Returns the ESP32's port serial route
    """
    override = os.environ.get("MP32_PORT")
    if override:
        log(f"Using MP32_PORT={override}")
        return prefer_callout(override)
    try:
        from serial.tools import list_ports
    except ImportError:
        die("Missing pyserial. Install it with: pip install pyserial")

    all_ports  = list(list_ports.comports())
    candidates = [p for p in all_ports if p.vid == FTDI_VID]

    if not candidates:
        avail = "\n".join(f"  - {p.device} ({p.description})" for p in all_ports) or "  (none)"
        die(
            "No FTDI device found (VID 0x0403).\n"
            f"Available serial ports:\n{avail}\n"
            "Connect the ESP32 via USB or set MP32_PORT=/dev/ttyXXX"
        )

    if len(candidates) > 1:
        log("Multiple FTDI devices detected:")
        for p in candidates:
            log(f"  - {p.device} ({p.description})")
        die("Select one with MP32_PORT=/dev/ttyXXX")

    port = candidates[0]
    log(f"Detected: {port.device} ({port.description})")
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
        "esp_rfc2217_server was not found.\n"
        "Options:\n"
        "  1) pip install --upgrade esptool\n"
        "  2) Download esp_rfc2217_server.py from\n"
        "     https://github.com/espressif/esptool and place it next to bridge.py"
    )

def ensure_port_free(host: str, port: int) -> None:
    """Falla rápido si algo ya está escuchando en `port`."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
        except OSError:
            die(
                f"TCP port {port} is already in use.\n"
                "Stop any previous esp_rfc2217_server and try again."
            )

def wait_for_server(
    server: subprocess.Popen[str], ready: threading.Event, timeout: float
) -> None:
    """Espera a que el servidor confirme que ya abrió el puerto."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ready.is_set():
            return
        if server.poll() is not None:
            die("RFC 2217 server exited before opening the port")
        ready.wait(min(CONNECT_POLL_S, deadline - time.monotonic()))
    die(f"RFC 2217 server did not open the port within {timeout:.0f}s")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    command = argv[1:]

    # ① Detect ESP32
    serial_port = find_serial_port()

    # ② Check if the 2217 port is free
    ensure_port_free("0.0.0.0", RFC2217_PORT)

    # ③ Localizar el servidor RFC 2217
    server_cmd  = find_rfc_server_cmd()
    server_argv = server_cmd + ["-p", str(RFC2217_PORT), serial_port]
    log(f"Starting RFC 2217 server: {' '.join(server_argv)}")

    # ④ Arrancar el servidor en background
    server_ready = threading.Event()
    server = subprocess.Popen(
        server_argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    def _forward_server_output() -> None:
        assert server.stdout is not None
        for line in server.stdout:
            sys.stderr.write(line)
            sys.stderr.flush()
            if f"TCP/IP port: {RFC2217_PORT}" in line:
                server_ready.set()

    threading.Thread(target=_forward_server_output, daemon=True).start()

    # ⑤ Cleanup garantizado
    def _cleanup() -> None:
        if server.poll() is None:
            log("Stopping RFC 2217 server...")
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()

    atexit.register(_cleanup)

    def _forward(signum, _frame):
        _cleanup()
        sys.exit(128 + signum)

    for sig in (signal.SIGINT, signal.SIGTERM, getattr(signal, "SIGHUP", None)):
        if sig is not None:
            signal.signal(sig, _forward)

    # ⑥ Esperar a que el servidor esté listo
    log(f"Waiting for RFC 2217 port {RFC2217_PORT} to open...")
    wait_for_server(server, server_ready, CONNECT_TIMEOUT_S)
    log("Server ready. Running command...")

    # ⑦ Ejecutar el comando del usuario
    try:
        result = subprocess.run(command)
    except FileNotFoundError:
        die(f"Command not found: {command[0]}")
    finally:
        _cleanup()
        atexit.unregister(_cleanup)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))