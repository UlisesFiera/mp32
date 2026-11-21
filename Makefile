# ─── Variables ────────────────────────────────────────────────────────────────
PYTHON_HOST := $(shell command -v python3.12 2>/dev/null \
                 || command -v python3 2>/dev/null \
                 || command -v python  2>/dev/null \
                 || echo python)

VENV        := .venv
VENV_STAMP  := $(VENV)/.installed
REQ_FILE    := mp32/firmware/bridge/requirements.txt

ifeq ($(OS),Windows_NT)
  VENV_PY := $(VENV)/Scripts/python.exe
else
  VENV_PY := $(VENV)/bin/python
endif

FW_IMAGE      := mp32-esp-idf
FW_CONTAINER  := mp32-dev-fw
FW_DOCKERFILE := mp32/firmware/Dockerfile
FW_CONTEXT    := mp32/firmware
BRIDGE_PY     := mp32/firmware/bridge/bridge.py

# URL que el contenedor usará para hablar con el RFC 2217 del host
ESPPORT_URL   := rfc2217://host.docker.internal:2217?ign_set_control

FW_DOCKER_RUN := docker run --rm -it \
	--name $(FW_CONTAINER) \
	-v "$$PWD/$(FW_CONTEXT):/project" \
	-e "ESPPORT=$(ESPPORT_URL)" \
	--add-host=host.docker.internal:host-gateway \
	$(FW_IMAGE)

# ─── Phony ────────────────────────────────────────────────────────────────────
.PHONY: all run dev-fw build-fw-image \
         runf runfapi runb migrate logs \
         clean-venv fclean

# ─── Default ──────────────────────────────────────────────────────────────────
all: run

run: migrate
	@echo "Running Frontend and Backend..."
	docker compose up -d --build

# ─── Firmware: imagen y shell interactivo (existente, intacto) ────────────────
build-fw-image:
	@docker build -t $(FW_IMAGE) -f $(FW_DOCKERFILE) $(FW_CONTEXT)

dev-fw: $(VENV_STAMP) build-fw-image
	@set -eu; \
	container_ids=$$(docker ps -aq --filter "ancestor=$(FW_IMAGE)"); \
	if [ -n "$$container_ids" ]; then \
		echo "Removing previous firmware containers..."; \
		docker rm -f $$container_ids; \
	fi
	$(VENV_PY) $(BRIDGE_PY) $(FW_DOCKER_RUN) idf.py build
	$(VENV_PY) $(BRIDGE_PY) $(FW_DOCKER_RUN) \
		bash -lc 'cd /project/build && python -m esptool --chip esp32 -p "$(ESPPORT_URL)" -b 460800 \
		--before default_reset --after hard_reset write_flash @flash_args'
	$(VENV_PY) $(BRIDGE_PY) $(FW_DOCKER_RUN) \
		idf.py -p "$(ESPPORT_URL)" monitor

runf:
	@echo "Running frontend..."
	docker compose up -d --build frontend

runfapi:
	@echo "Running fast-api..."
	@cd mp32/backend/fastapi && uvicorn main:app --reload --port 8000

runb:
	@echo "Running backend..."
	@docker compose up -d --build backend

migrate:
	@echo "Starting PostgreSQL..."
	docker compose up -d --wait postgres
	@echo "Applying database migrations..."
	docker compose exec -T postgres sh /migrations/migration.sh

# ─── Logs (sin cambios) ───────────────────────────────────────────────────────
logs:
	@echo "Frontend, Backend and PostgreSQL logs..."
	docker compose logs

# ─── Ciclo de vida del venv ───────────────────────────────────────────────────
$(VENV)/pyvenv.cfg:
	$(PYTHON_HOST) -m venv $(VENV)

$(VENV_STAMP): $(VENV)/pyvenv.cfg $(REQ_FILE)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -r $(REQ_FILE)
	touch $(VENV_STAMP)

clean-venv:
	rm -rf $(VENV)

# ─── Clean ────────────────────────────────────────────────────────────────────
fclean:
	@docker compose down -v
	@rm -rf $(VENV)