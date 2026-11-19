all: run

run: migrate
	@echo "Running Frontend and Backend..."
	docker compose up -d --build

dev-fw:
	docker build -t mp32-esp-idf -f mp32/firmware/Dockerfile mp32/firmware
	docker run --rm -it \
		-v "$$PWD/mp32/firmware:/project" \
		mp32-esp-idf

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

fclean:
	@docker compose down