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
#
# This is the ESP32 VID (manufacturer's serial number)
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


def set_out_conn_path(device: str) -> str:
    """
    macOS (Darwin) exposes two device files for many serial ports:
        /dev/tty.*: Traditionally intended for incoming connections.
        /dev/cu.*: Traditionally intended for outgoing connections.
    macOS, /dev/tty.* blocks until te DCD signal arrives. So we need /dev/cu.*.
    """
    if platform.system() == "Darwin" and device.startswith("/dev/tty."):
        cu = device.replace("/dev/tty.", "/dev/cu.", 1)
        if os.path.exists(cu):
            return cu
    return device


def find_serial_port() -> str:
    """
    Returns the ESP32's port serial route
    Checks for the needed pyserial lib and the presence of a device, or multiple
    """
    try:
        from serial.tools import list_ports
    except ImportError:
        die("Missing pyserial. Install it with: pip install pyserial")
    all_ports  = list(list_ports.comports())
    candidates = []
    for port in all_ports:
        if port.vid == FTDI_VID:
            candidates.append(port)
    if not candidates:
        found_ports = "\n".join(f"  - {port.device} ({port.description})" for port in all_ports) or "  (none)"
        die(
            "No FTDI device found (VID 0x0403).\n"
            f"Available serial ports:\n{found_ports}\n"
            "Connect the ESP32 via USB"
        )
    if len(candidates) > 1:
        log("Multiple FTDI devices detected:")
        for port in candidates:
            log(f"  - {port.device} ({port.description})")
        die("Can only have 1 FTDI device connected at a time")
    port = candidates[0]
    final_port = set_out_conn_path(port.device)
    log(f"ESP32 DEVICE DETECTED: {final_port.device} ({final_port.description})")
    return port.device


def find_rfc_server_file() -> list[str]:
    """
    Localizes the esp_rfc2217_server file, that should be in the same folder as the script.
    """
    local = Path(__file__).resolve().parent / "esp_rfc2217_server.py"
    if local.exists():
        return [sys.executable, str(local)]
    die("esp_rfc2217_server.py was not found next to bridge.py.")


def ensure_port_free(host: str, port: int) -> None:
    """
    Fails is the port is free
    Would be nice to try another port in case of failure
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
        except OSError:
            die(
                f"TCP port {port} is already in use.\n"
                "Stop any previous esp_rfc2217_server and try again."
            )


def wait_for_server(server: subprocess.Popen[str], ready: threading.Event, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ready.is_set():
            return
        if server.poll() is not None:
            die("RFC 2217 server exited before opening the port")
        ready.wait(min(CONNECT_POLL_S, deadline - time.monotonic()))
    die(f"RFC 2217 server did not open the port within {timeout:.0f}s")


def main(argv: list[str]) -> int:
    '''
    1. Detects the ESP32
    2. Checks if the 2217 port is free
    3. Localizes the RFC 2217 server file
    4. Runs the server as a subprocess
    5. Registers exit signals and cleanup
    6. Runs the user's command for the server
    '''
    def _forward_server_output() -> None:
        assert server.stdout is not None
        for line in server.stdout:
            if f"TCP/IP port: {RFC2217_PORT}" in line:
                server_ready.set()

    def _cleanup() -> None:
        if server.poll() is None:
            log("Stopping RFC 2217 server...")
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()

    def _forward(signum, _frame):
        _cleanup()
        sys.exit(128 + signum)

    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    command = argv[1:]
    serial_port = find_serial_port()
    ensure_port_free("0.0.0.0", RFC2217_PORT)
    server_cmd  = find_rfc_server_file()
    server_argv = server_cmd + ["-p", str(RFC2217_PORT), serial_port]
    log(f"Starting RFC 2217 server: {' '.join(server_argv)}")
    server_ready = threading.Event()
    server = subprocess.Popen(
        server_argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    threading.Thread(target=_forward_server_output, daemon=True).start()
    atexit.register(_cleanup)
    for sig in (signal.SIGINT, signal.SIGTERM, getattr(signal, "SIGHUP", None)):
        if sig is not None:
            signal.signal(sig, _forward)
    log(f"Waiting for RFC 2217 port {RFC2217_PORT} to open...")
    wait_for_server(server, server_ready, CONNECT_TIMEOUT_S)
    log(f"Server ready. Running command: {command}")
    try:
        result = subprocess.run(command)
    except FileNotFoundError:
        die(f"Command not found: {command}")
    finally:
        _cleanup()
        atexit.unregister(_cleanup)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))