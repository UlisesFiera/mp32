# Notes
- Frontend development local route: http://localhost:5173/
    - Network route: http://172.20.10.2:5173/
- Backend development port: 8080
- The cmd folder in Go keeps files that store executable functions.
- Go has something similar to CPP objects: structs. You create the struct methods declaring a function with a receiver. Each one of these functions will be a method you can call on that struct, effectibly creating an object.
# Resources

- Go basic tutorial
    - https://www.youtube.com/watch?v=s3XItrqfccw

- Backend documentation
    - Router https://go-chi.io/#/pages/getting_started
    

- Frontend libraries and framework documentation:
    - https://svelte.dev/docs
    - https://tailwindcss.com/docs
    - https://www.skeleton.dev/docs/svelte/tailwind-components

- Assets and animations:
    - https://www.magnific.com
    - https://www.chartjs.org/
    - https://sveltebits.xyz/
    - https://fonts.google.com/
    - https://animation-svelte.vercel.app/
    
- Project set-up:
    - https://svelte.dev/docs/kit/creating-a-project
    - https://tailwindcss.com/docs/installation/using-vite


- Inspiration:
    - https://dribbble.com/shots/27229691-UI-UX-Design-for-Logistics-Dashboard-Haulix






# Complete Project Context & Technical Specification

> **Purpose of this document:** This is a self-contained knowledge base for an AI assistant (or a new team member) to understand the MP32 project end-to-end: the hardware, every architectural decision made and _why_, the rejected alternatives, the final chosen architecture (Option A), and all known caveats. Feed this document as context before asking for code, design help, or debugging assistance.

---

## 1. Project Overview

**Context:** This is the IoT module of an ft_transcendence project (42 school). The deliverable must be deployable with a single command using containerization (Docker), must include a frontend, a backend, and a database, and must integrate a physical IoT device.

**Product concept:** "MP32" — a device built around an ESP32 microcontroller with a micro-SD card slot. The SD card stores music. A web application lets the user upload music files, organize them into **two playlists (A and B)**, and control playback. Each track carries metadata: **name, album name, band name, playlist position, and a unique serial number**. The device must connect to the web app (Bluetooth and USB), files are uploaded through the web app, and the device's serial number is registered in a database.

**Physical controls on the device:**

- On/off switch
- Play, pause, next, previous buttons
- Pair / accept pairing button
- Playlist A/B selector switch (ideally read before power-on)

**Final scope decision (see §4):** Playback happens **on the PC** via the web app in the browser. The ESP32 never decodes or outputs audio. It is a **networked file server + control event source**.

---

## 2. Hardware Profile (Confirmed)

| Component              | Detail                                                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Board marking**      | "XXSR69", silkscreen "ESP32-S"                                                                                     |
| **Module class**       | ESP32-WROOM-32-class clone (ESP32-D0WD-V3, dual-core Xtensa LX6)                                                   |
| **USB-to-UART bridge** | **FTDI FT232RQ** (confirmed visually: "FTDI 0918-8 B63256 FT232RQ" near the micro-USB port, labeled U2)            |
| **Voltage regulator**  | AMS1117-3.3 (marking "1117C 33 D419") — 3.3 V LDO                                                                  |
| **Native USB**         | ❌ **None.** The ESP32-D0WD has no USB peripheral. The micro-USB port only feeds the FT232RQ UART bridge and power. |
| **PSRAM**              | ❌ **None** (classic WROOM-32 modules do not have PSRAM)                                                            |
| **Internal DAC**       | 2× 8-bit DAC on GPIO25/26 (not used in this project)                                                               |
| **Wireless**           | Wi-Fi 2.4 GHz (802.11 b/g/n) + Bluetooth Classic + BLE, sharing one radio                                          |
| **Flash**              | Likely 4 MB (unverified; check with `esptool.py flash_id`)                                                         |

### Hardware consequences that drive every architectural decision

1. **No native USB ⇒ USB Mass Storage (MSC) is physically impossible.** The FT232RQ is a pure UART bridge; it cannot present the SD card to a PC as a drive. Any design relying on "ESP32 appears as a USB flash drive" must be discarded for this board.
2. **No PSRAM ⇒ audio decoding on-device is heavily constrained.** This reinforces the decision to not decode on the ESP32.
3. **The FT232RQ is a standard UART bridge ⇒ RFC 2217 remote-serial flashing works perfectly.** The native-USB limitation documented by Espressif (`rfc2217://` does not support USB-OTG or USB-Serial-JTAG) **does not apply to this board**.

---

## 3. The Three Original Limitations and How Each Was Resolved

### Limitation 1 — Cross-OS flashing under Docker

**Problem:** Docker Desktop on macOS/Windows runs containers in a VM that cannot see host USB devices. Only native Linux Docker can pass `/dev/ttyUSB0` with `--device`. This would force OS-specific Makefile logic.

**Rejected alternatives:**

- Docker Desktop USB/IP (experimental, no reliable macOS server implementation)
    
- VirtualHere (paid, proprietary)
    
- Lima/Colima (heavyweight, replaces the whole Docker runtime)
    
- Flashing from the host with `esptool` (works, but breaks the single-command Docker workflow)
    
- Browser-based Web Serial flasher (works, OS-agnostic, but bypasses Docker for the flash step — kept as a documented fallback)
    

**Chosen solution:** A **cross-platform `bridge.py`** that auto-detects the serial port using `pyserial`'s `list_ports` (matching FTDI VID `0x0403`, CP210x `0x10C4`, CH340 `0x1A86`, Espressif `0x303A`), starts `esp_rfc2217_server`, invokes Docker Compose, and cleans up in a `finally` block. The container connects via `rfc2217://host.docker.internal:2217?ign_set_control`.

**Status:** ✅ **Solved and validated for this hardware.** The FT232RQ presents a plain UART; `esptool` can toggle DTR/RTS through the bridge for auto-reset, provided the board has the standard auto-reset transistor circuit. If auto-reset fails, manual BOOT+EN entry into download mode still works.

### Limitation 2 — "Headphones can't decode MP3"

**Problem:** Passive headphones are transducers (stage 5 only). Decoding (2), DAC (3), and amplification (4) must happen somewhere.

**Rejected alternatives:**

- **Option B1:** ESP32 internal 8-bit DAC + discrete amp (BC547 / LM386 / PAM8403). Cheapest, but noisy, low-quality, and `ESP32-audioI2S` ≥3.0 requires PSRAM which this board lacks.
- **Option B2:** Software decode → I2S → MAX98357A / PCM5102A. Good quality, but requires real-time firmware engineering (FreeRTOS audio task, DMA double-buffering, SD-card latency handling). High risk for a first embedded audio project.
- **Option B3:** Hardware decoder chip (VS1053) accepting MP3 over SPI and outputting analog audio. Pragmatic and simple firmware, but extra hardware and wiring.
- **Bluetooth A2DP source:** ESP32 streams SBC-encoded audio to Bluetooth headphones. **Rejected:** A2DP mandates SBC encoding (so uncompressed WAV does _not_ avoid compression), the A2DP stack consumes 81–82 KB IRAM, the library maintainer explicitly warns it is "tricky" and not for beginners, and Wi-Fi + A2DP cannot coexist reliably on the single shared radio.


### Limitation 3 — Bluetooth is the wrong channel for file transfer

**Confirmed:** BLE default MTU is 23 bytes (20 bytes payload); even with MTU negotiation, practical ESP32 BLE throughput is ~10–90 kB/s. A 4 MB MP3 would take 45 s to 6+ minutes. Bluetooth Classic SPP reaches ~175–200 kB/s but requires a custom client. Neither is acceptable for web-app-driven uploads.

**Resolution:** **Wi-Fi HTTP for file uploads and file serving. BLE for provisioning and control events only.**

---

## 4. Final Architecture — Option A (Corrected for This Hardware)

> ⚠️ **Important correction to the earlier definition of Option A:** The original phrasing was "ESP32 enumerates as a USB Mass Storage device; the PC reads files from the drive." **That is impossible on this board** because the ESP32-D0WD has no USB peripheral and the FT232RQ is UART-only. Option A is therefore redefined as **"the ESP32 is a Wi-Fi-attached file server; the PC downloads and plays the files."** All the benefits of Option A (zero audio work on the ESP32, excellent audio quality, low firmware complexity) are preserved. The transport changes from USB MSC to Wi-Fi HTTP.

### 4.1 High-level data flow

```text

[Browser / Svelte frontend on PC]
        │  (HTTP + WebSocket)
        ▼
[Go backend on PC] ──────────────► [PostgreSQL: metadata, devices, playlists]
        │  (HTTP, device discovery via mDNS or configured IP)
        ▼
[ESP32 (Wi-Fi HTTP server + BLE)]
        │  (SPI)
        ▼
[micro-SD card: MP3 files + index.json]
Audio playback: Browser HTML5 <audio> on the PC → PC sound card → PC speakers / headphones
```


### 4.2 Responsibility split

|Component|Responsibilities|
|---|---|
|**ESP32 firmware (C, ESP-IDF)**|Mount FAT32 SD card; run HTTP server (`/status`, `/files/*`, `/upload`, `/index`, `/control`); run BLE (NimBLE) for Wi-Fi provisioning + button-event notifications; read GPIO buttons and the playlist A/B switch; register itself with the backend on boot; serve MP3 bytes for streaming|
|**Go backend**|Serve the Svelte SPA; store metadata + device registry in PostgreSQL; proxy uploads to the ESP32 and keep `index.json` in sync; receive button events from the ESP32 (HTTP long-poll or WebSocket) and push them to the frontend via WebSocket; provide audio stream URLs|
|**Svelte frontend**|Upload UI (file + metadata form); playlist A/B view; HTML5 `<audio>` player; WebSocket listener for device button events; BLE provisioning via **Web Bluetooth** (Chromium)|
|**PostgreSQL**|`devices(serial, ip, last_seen, firmware_version)`, `tracks(serial, name, album, band, playlist, position, device_serial, file_path)`, `playlists`|
|**PC**|Owns the speakers/headphones, decodes and plays audio, runs Docker Compose|

### 4.3 Why this is the right choice

- ESP32 does zero decoding, zero DAC, zero audio timing → no PSRAM pressure, no real-time firmware risk.
- No mode switching between "USB drive" and "player" is needed (no USB MSC at all).
- Audio quality is whatever the PC's browser and sound card support (excellent).
- Wi-Fi and BLE can coexist (time-sliced radio); BLE traffic is tiny (provisioning + button events).
- The web app is the single control surface, matching the ft_transcendence requirement.

---

## 5. ESP32 Firmware Design

### 5.1 Task and concurrency model (FreeRTOS)

|Task|Core|Purpose|
|---|---|---|
|`wifi_http_task`|Core 0|Wi-Fi station management, `esp_http_server`, handles all HTTP endpoints|
|`ble_task`|Core 0|NimBLE host, provisioning GATT service, control-event GATT characteristic|
|`button_task`|Core 1|GPIO polling (20 ms) with debounce; sends events to a queue consumed by `ble_task`/`http` notifier|
|_(no audio task)_|—|—|

**Shared resources:**

- **SD card access must be serialized with a mutex** (`xSemaphoreCreateMutex`). Upload writes, download reads, and index reads can otherwise conflict and corrupt FATFS.
- Button events are pushed into a FreeRTOS queue; the BLE task pops them and sends GATT notifications; optionally the HTTP task exposes the latest event via `/events/longpoll` as a fallback.

### 5.2 State machine

```text

BOOT
 └─► NVS has Wi-Fi creds?
       ├─ no  ─► PROVISIONING (BLE advertising, provisioning service active)
       │            └─ creds received ─► CONNECTING
       └─ yes ─► CONNECTING
                    ├─ success ─► ONLINE (HTTP up, BLE control up, register with backend)
                    └─ fail (timeout) ─► PROVISIONING (or retry, configurable)
ONLINE ── (long-press Pair) ──► PROVISIONING
```

There is **no "playback" state on the device**. The device does not know whether music is playing; that state lives in the frontend/backend.

### 5.3 Pin map (classic ESP32, ESP32-WROOM-32)

> Avoid: GPIO 6–11 (flash), GPIO 0/2/5/12/15 (strapping), GPIO 34–39 (input-only, no internal pull-ups), GPIO 1/3 (UART0 console if used).

|Function|GPIO|Notes|
|---|---|---|
|SD CS|5||
|SD MOSI|23|VSPI|
|SD MISO|19|VSPI|
|SD SCLK|18|VSPI|
|SD power|3V3|From AMS1117-3.3|
|Button PLAY/PAUSE|32|`INPUT_PULLUP`, active-low|
|Button NEXT|33|`INPUT_PULLUP`, active-low|
|Button PREV|27|`INPUT_PULLUP`, active-low|
|Button PAIR|14|`INPUT_PULLUP`, active-low; long-press ⇒ PROVISIONING|
|Playlist A/B switch|13|`INPUT_PULLUP`; read at boot and on change|
|On/Off|—|Physical switch on the power rail (not a GPIO)|

Document this map in `HARDWARE.md` and keep firmware constants in sync.

### 5.4 SD card layout and metadata

- **Filesystem:** FAT32 (format with `guiformat`/`fat32format` on Windows, `diskutil` on macOS for >32 GB cards). Enable `CONFIG_FATFS_LFN_HEAP=y` for long filenames.
- **Layout:**
```text

/
├── playlistA/
│   └── 0001.mp3
├── playlistB/
│   └── 0001.mp3
└── index.json
```

- **Filenames are device-generated** (zero-padded position: `0001.mp3`), not user-supplied, to avoid encoding/ordering issues. The original name is preserved in `index.json`.
- **`index.json` schema:**

```json

{
  "device_serial": "MP32-A1B2C3",
  "version": 1,
  "playlists": {
    "A": [
      {"serial":"TRK-0001","file":"0001.mp3","name":"Song One","album":"Album X","band":"Band Y","position":1}
    ],
    "B": []
  }
}
```

- **Device serial:** derived from the ESP32's base MAC address (eFuse, guaranteed unique) or a provisioned value stored in NVS. Format: `MP32-<hex>`.


### 5.5 Firmware libraries and sdkconfig notes

|Concern|Choice|
|---|---|
|HTTP server|`esp_http_server` (ESP-IDF)|
|BLE stack|**NimBLE** (`CONFIG_BT_NIMBLE_ENABLED=y`) — much lighter than Bluedroid, critical without PSRAM|
|BLE provisioning|`wifi_prov_mgr` with `scheme_ble`, or a minimal custom GATT service (SSID + password write, status notify)|
|Wi-Fi + BLE coexistence|`CONFIG_ESP_COEX_SW_COEXIST_ENABLE=y`|
|SD|`esp_vfs_fat_sdspi_mount()` with `sdspi_host`|
|JSON|`cJSON` (bundled)|
|mDNS|optional (`mdns` component) so the backend can discover `mp32.local`|

**Upload handling without PSRAM:** do **not** buffer the whole MP3 in RAM. Use chunked reads from the HTTP request and write to the SD card incrementally (4–8 KB buffers). Set a maximum accepted upload size (e.g., 20 MB) and reject larger files with HTTP 413.

### 5.6 HTTP API contract (device side)

|Method|Path|Purpose|
|---|---|---|
|`GET`|`/status`|`{serial, ip, rssi, free_kb, total_kb, uptime_s, fw_version, playlist_switch:"A"\|"B"}`|
|`GET`|`/index`|Returns `index.json`|
|`GET`|`/files/{A\|B}/{filename}`|Streams an MP3 (with `Range` support if feasible; otherwise `200` + full body)|
|`POST`|`/upload`|Multipart: `file`, `name`, `album`, `band`, `playlist`, `position`. Writes file + updates `index.json`.|
|`DELETE`|`/files/{A\|B}/{filename}`|Removes file + index entry|
|`POST`|`/control`|Body `{action:"play"\|"pause"\|"next"\|"prev"\|"select_playlist", playlist:"A"\|"B"}` — **echoed to the backend**, not acted on locally|
|`GET`|`/events/longpoll?since=<n>`|Returns the latest button event (fallback if BLE notification path is not used)|

**CORS:** If the browser fetches audio directly from the ESP32, the ESP32 must send `Access-Control-Allow-Origin`. **Recommended:** the Go backend proxies `/files/*` to the ESP32 (`io.Copy`) so the browser only ever talks to the backend — simpler network topology, no CORS, no exposed device IP.

**Auth:** shared token header `X-Device-Token` on all mutating endpoints.

### 5.7 BLE protocol

- **Device name:** `MP32-<serial-suffix>`
- **Provisioning service:** SSID characteristic (write), password characteristic (write), status characteristic (notify: `unprovisioned | connecting | connected | failed`).
- **Control service:** button-event characteristic (notify): JSON `{event:"play"|"pause"|"next"|"prev"|"playlist_switch", playlist:"A"|"B", ts:<ms>}`.
- **Client:** the Svelte frontend uses **Web Bluetooth** (Chromium only — same browser constraint as the Web Serial fallback for flashing, so it is consistent).

---

## 6. Buttons Semantics (Option A)

|Button|Behavior|
|---|---|
|On/Off|Hardware power switch|
|Play/Pause|Emits `play`/`pause` event → backend → frontend `<audio>` controls|
|Next / Previous|Emits `next`/`prev` → frontend changes track|
|Pair|Short press: no-op (or re-advertise). **Long press (≥3 s):** re-enter BLE provisioning|
|Playlist A/B switch|Read at boot and on change; included in `/status` and in `playlist_switch` events; frontend selects the active playlist|

**Important UX caveat:** browser audio requires a user gesture before playback can start (autoplay policy). The frontend must prompt the user to click once ("Enable audio") before device button events can start playback.

---

## 7. End-to-End Flows

### 7.1 First boot / provisioning

1. ESP32 boots, NVS empty → `PROVISIONING`, BLE advertising.
2. User opens the web app → clicks "Provision device" → Web Bluetooth scan → selects `MP32-XXXX`.
3. Frontend writes SSID + password over GATT.
4. ESP32 stores creds in NVS, connects to Wi-Fi, brings up the HTTP server.
5. ESP32 `POST /devices/register` to the backend with `{serial, ip, fw_version}` → backend upserts the `devices` row.
6. Status characteristic notifies `connected`.

### 7.2 Upload

1. User selects a file + fills metadata (name, album, band, playlist A/B) in the frontend.
2. Frontend `POST /api/tracks` (multipart) → Go backend.
3. Backend computes the next `position` for the playlist, generates the serial `TRK-XXXX`, and forwards the file to the ESP32 `POST /upload` with metadata.
4. ESP32 streams the body to `/{playlist}/{position:04d}.mp3`, updates `index.json`, returns `201`.
5. Backend inserts the `tracks` row and returns success to the frontend.

### 7.3 Playback

1. Frontend loads `GET /api/playlists/A` (from PostgreSQL).
2. On play, frontend sets `<audio src="/api/stream/TRK-0001">`.
3. Backend `GET http://<esp32>/files/A/0001.mp3` and `io.Copy`s the body to the browser.
4. Browser decodes and plays through the PC's sound card → PC speakers / headphones.
5. Device button event → BLE notify → backend WebSocket → frontend → `audio.pause()` / `next()` etc.

---

## 8. Build, Flash, and Run Workflow (Validated)

### 8.1 `bridge.py` (cross-platform serial bridge)

```python
import subprocess, sys, time
import serial.tools.list_ports
ESP_VIDS = {0x0403, 0x10C4, 0x1A86, 0x303A}   # FTDI, CP210x, CH340, Espressif
RFC2217_PORT = "2217"
def find_esp_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if p.vid in ESP_VIDS:
            return p.device
    for p in ports:
        if any(k in p.device.lower() for k in ("usb", "acm", "com")):
            return p.device
    return None
def main():
    port = find_esp_port()
    if not port:
        sys.exit("Error: no ESP32 serial device detected.")
    print(f"[bridge] {port} -> tcp:{RFC2217_PORT}")
    server = subprocess.Popen(
        [sys.executable, "-m", "esp_rfc2217_server", "-p", RFC2217_PORT, port],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1.5)
        sys.exit(subprocess.run(sys.argv[1:]).returncode)
    finally:
        server.terminate(); server.wait()
if __name__ == "__main__":
    main()
```

### 8.2 `docker-compose.yml` (firmware service)

```yaml

services:
  esp-dev:
    image: espressif/idf:v5.3
    working_dir: /project
    volumes: [ ".:/project" ]
    environment:
      - ESPPORT=rfc2217://host.docker.internal:2217?ign_set_control
      - ESPBAUD=460800
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### 8.3 `Makefile` (thin Docker wrapper)

```makefile

PYTHON := $(shell command -v python3 2>/dev/null || echo python)
.PHONY: build flash monitor shell
build:   ; docker compose run --rm esp-dev idf.py build
flash:   ; $(PYTHON) bridge.py docker compose run --rm esp-dev idf.py flash
monitor: ; $(PYTHON) bridge.py docker compose run --rm -it esp-dev idf.py monitor
shell:   ; docker compose run --rm -it esp-dev bash
```

**Host prerequisites (one-time):** Python 3 + `pip install esptool pyserial`. On Windows, run inside Git Bash/WSL with Docker Desktop and the FTDI driver installed.

**Fallbacks if auto-reset fails:** hold BOOT, press EN, release BOOT, then run `make flash`.

---

## 9. Repository Layout

```text

mp32/
├── docker-compose.yml          # web app services
├── docker-compose.firmware.yml # esp-dev service (or profile in main file)
├── Makefile
├── bridge.py
├── .env.example
├── HARDWARE.md                 # pin map, BOM, board photos
├── API.md                      # device + backend contracts
├── firmware/
│   ├── CMakeLists.txt
│   ├── sdkconfig.defaults
│   └── main/
├── backend/                    # Go (Gin) + FastAPI if needed
├── frontend/                   # Svelte + Tailwind + Skeleton
└── database/                   # migrations
```

---

## 10. Development Milestones (incremental, each independently testable)

1. **SD + FAT32**: mount, list files, write a test file. Verify `CONFIG_FATFS_LFN_HEAP`.
2. **Wi-Fi + HTTP**: `/status` returns JSON; connect from a browser.
3. **Upload**: `POST /upload` streams a small MP3 to SD; verify file integrity (`md5sum` on PC vs. device read-back).
4. **File serving**: `GET /files/...` streams an MP3; `curl` to a file and compare hashes.
5. **Backend proxy + DB**: register device, upload via backend, stream via backend; metadata in Postgres.
6. **Frontend**: playlist view + `<audio>` playback of streamed tracks.
7. **BLE provisioning**: Web Bluetooth flow; NVS persistence; auto-reconnect on reboot.
8. **Buttons + WebSocket**: button event → backend → frontend playback control.
9. **Playlist A/B switch**: reflected in `/status` and frontend.
10. **Docker + Makefile + bridge.py**: full `make all` on macOS, Linux, and Windows (Git Bash/WSL).
11. **End-to-end demo**: fresh machine → `make all` → provision → upload → play → control with buttons.


---

## 11. Complete Caveats and Risks (do not ignore)

1. **USB MSC is impossible on this board.** Any request to "make the ESP32 show up as a drive" must be redirected to the Wi-Fi HTTP file server.
2. **No PSRAM.** Stream uploads to SD in small chunks; never buffer whole files. Monitor heap (`esp_get_free_heap_size`) — Wi-Fi + NimBLE + HTTP + FATFS should fit, but it is tight.
3. **Wi-Fi and BLE share one radio.** Coexistence works, but BLE notifications during heavy Wi-Fi transfers may be delayed. Keep BLE traffic minimal.
4. **SD card access must be mutex-protected** across HTTP upload, HTTP download, and index updates.
5. **FAT32 only.** Cards >32 GB may default to exFAT — reformat explicitly.
6. **Long filenames** require `CONFIG_FATFS_LFN_HEAP=y`; device-generated `0001.mp3` names sidestep the issue entirely.
7. **Power:** the AMS1117-3.3 is fine on the bench, but Wi-Fi TX peaks (~240 mA) + SD write spikes (~100 mA) can brown out cheap USB ports. Use a dedicated 5 V supply for the demo.
8. **Browser autoplay policy:** the frontend must require one user gesture before audio can start.
9. **Web Bluetooth and Web Serial are Chromium-only.** If the evaluator uses Safari/Firefox, provide the Espressif provisioning app as a fallback (and host-side `esptool` for flashing).
10. **CORS / network topology:** prefer proxying `/files/*` through the Go backend so the browser never needs the ESP32's IP and no CORS headers are required.
11. **Security:** a shared `X-Device-Token` is the minimum. Do not expose the ESP32's mutation endpoints on an untrusted network.
12. **Filename sanitization:** even though filenames are device-generated, the _metadata_ strings (name/album/band) come from users — validate and escape them before writing JSON or rendering in the Svelte UI (XSS).
13. **Firmware is a different discipline:** C, FreeRTOS, manual memory management, no exceptions. Budget learning time separately from the web stack.
14. **The device is a breadboard prototype.** Expect jumper wires in the demo; this is acceptable for ft_transcendence.
15. **The original requirement "connected to the web app (Bluetooth and USB)" must be restated** as: _"BLE for provisioning and control events; USB for power and flashing; Wi-Fi HTTP for data."_ USB data transfer to the web app is not possible on this hardware.

---

## 12. Explicit Non-Goals (do not re-litigate)

- ❌ Audio decoding on the ESP32
- ❌ I2S, DAC, amplifier, MAX98357A, PCM5102A, VS1053, 3.5 mm jack
- ❌ Bluetooth A2DP (source or sink)
- ❌ USB Mass Storage / USB Audio Class
- ❌ Writing a custom MP3 decoder
- ❌ Uncompressed WAV to "avoid compression" (irrelevant — no on-device compression happens in Option A)
- ❌ PSRAM-dependent libraries (`ESP32-audioI2S` ≥3.0)

---

## 13. Open Decisions Remaining

1. **Device discovery:** static IP configured in the backend `.env`, or mDNS (`mp32.local`)? mDNS is nicer but adds a component.
2. **Button event transport to the PC:** BLE notify → backend, or HTTP long-poll from the ESP32 to the backend? BLE is cleaner given Web Bluetooth is already in use.
3. **Range requests:** implement `Range` on `/files/*` for seeking in the browser `<audio>` element, or accept full-file downloads only (seeking still works client-side once buffered)?
4. **Upload ownership:** does the backend own `position` and `TRK-XXXX` serial generation, or does the ESP32? (Recommendation: backend owns them to keep the DB as the source of truth.)
5. **DB mirroring of `index.json`:** on device reboot, should the ESP32 push its `index.json` to the backend to reconcile, or is the DB always authoritative?

---

## 14. One-Paragraph Executive Summary (for quick AI priming)

_The MP32 project is an ft_transcendence IoT music device built on an XXSR69 ESP32-WROOM-32-class board with an FTDI FT232RQ UART bridge, no native USB, and no PSRAM, connected to a micro-SD card over SPI. Because the board cannot do USB MSC, cannot decode MP3 without PSRAM, and cannot reliably stream A2DP, the team chose **Option A**: the ESP32 acts purely as a Wi-Fi HTTP file server and BLE control-event source; the PC's browser decodes and plays the audio through the PC's own sound card and speakers/headphones. Files are uploaded over Wi-Fi HTTP via the Go backend; BLE (Web Bluetooth) handles Wi-Fi provisioning and button events; PostgreSQL stores all metadata and the device registry; everything except the physical flash step runs in Docker Compose, and the flash step is made cross-platform by `bridge.py`, which auto-detects the FTDI serial port and exposes it to the `espressif/idf` container over RFC 2217. The project is fully scoped, hardware-compatible, and ready for implementation following the milestones in §10.