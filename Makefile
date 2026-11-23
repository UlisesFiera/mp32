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

ESPPORT_URL   := rfc2217://host.docker.internal:2217?ign_set_control

FW_DOCKER_RUN := docker run --rm -it \
	--name $(FW_CONTAINER) \
	-v "$$PWD/$(FW_CONTEXT):/project" \
	-e "ESPPORT=$(ESPPORT_URL)" \
	--add-host=host.docker.internal:host-gateway \
	$(FW_IMAGE)

.PHONY: all run dev-fw dev-fw-shell clean-fw-containers build-fw-image \
         runf runfapi runb migrate logs \
         clean-venv fclean

all: run

run: migrate
	@echo "Running Frontend and Backend..."
	docker compose up -d --build

build-fw-image:
	@docker build -t $(FW_IMAGE) -f $(FW_DOCKERFILE) $(FW_CONTEXT)

dev-fw: $(VENV_STAMP)
	@echo "[Make: 1/5] Cleaning firmware containers..."
	@$(MAKE) --no-print-directory clean-fw-containers
	@echo "[Make: 2/5] Building firmware Docker image..."
	@$(MAKE) --no-print-directory build-fw-image
	@echo "[Make: 3/5] Testing connection..."
	@$(VENV_PY) $(BRIDGE_PY) $(FW_DOCKER_RUN) idf.py build
	@echo "[Make: 4/5] Flashing firmware..."
	@$(VENV_PY) $(BRIDGE_PY) $(FW_DOCKER_RUN) \
		bash -lc 'cd /project/build && python -m esptool --chip esp32 -p "$(ESPPORT_URL)" -b 460800 \
		--before default_reset --after hard_reset write_flash @flash_args'
	@echo "[Make: 5/5] Starting firmware monitor..."
	@$(VENV_PY) $(BRIDGE_PY) $(FW_DOCKER_RUN) \
		idf.py -p "$(ESPPORT_URL)" monitor

clean-fw-containers:
	@set -eu; \
	named_container_ids=$$(docker ps -aq --filter "name=$(FW_CONTAINER)"); \
	for container_id in $$named_container_ids; do \
		container_name=$$(docker inspect --format '{{.Name}}' "$$container_id"); \
		if [ "$$container_name" = "/$(FW_CONTAINER)" ]; then \
			echo "Removing previous firmware container $(FW_CONTAINER)..."; \
			docker rm -f "$$container_id"; \
		fi; \
	done; \
	image_container_ids=$$(docker ps -aq --filter "ancestor=$(FW_IMAGE)"); \
	if [ -n "$$image_container_ids" ]; then \
		echo "Removing previous firmware containers..."; \
		docker rm -f $$image_container_ids; \
	fi

dev-fw-shell: $(VENV_STAMP)
	$(MAKE) clean-fw-containers
	$(MAKE) build-fw-image
	$(VENV_PY) $(BRIDGE_PY) $(FW_DOCKER_RUN) bash

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

logs:
	@echo "Frontend, Backend and PostgreSQL logs..."
	docker compose logs

$(VENV)/pyvenv.cfg:
	$(PYTHON_HOST) -m venv $(VENV)

$(VENV_STAMP): $(VENV)/pyvenv.cfg $(REQ_FILE)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -r $(REQ_FILE)
	touch $(VENV_STAMP)

clean-venv:
	rm -rf $(VENV)

fclean:
	@docker compose down -v
	@rm -rf $(VENV)