all: run

run:
	@echo "Running Frontend, Backend and PostgresSQL..."
	docker compose up -d --build

runf:
	@echo "Running frontend..."
	docker compose up -d --build frontend

runfapi:
	@echo "Running fast-api..."
	@cd mp32/backend/fastapi && uvicorn main:app --reload --port 8000

runb:
	@echo "Running backend..."
	@docker compose up -d --build backend

logs:
	@echo "Frontend, Backend and PostgresSQL logs..."
	docker compose logs

fclean:
	@docker compose down