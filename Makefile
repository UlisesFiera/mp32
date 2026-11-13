all: run

mac-install:
	@echo "## FRONT-END DEPENDENCIES ##"
	@echo "Installing nvm..."
	@curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
	@echo "Installing Node.js 24..."
	@. "$$HOME/.nvm/nvm.sh" && nvm install 24 && nvm alias default 24
	@echo "Installing Svelte dependencies..."
	@. "$$HOME/.nvm/nvm.sh" && cd mp32/frontend && npm install
	@echo "Installation completed. You may restart your terminal"
	@echo "Installing tailwind..."
	@. "$$HOME/.nvm/nvm.sh" && cd mp32/frontend && npx sv add tailwindcss && npm install -D @tailwindcss/forms && npm install lucide-svelte@0.577.0 && npx sv@1.1.1 add tailwindcss="plugins:none" --no-install
	@echo "Installing skeleton..."
	@. "$$HOME/.nvm/nvm.sh" && cd mp32/frontend && npm i -D @skeletonlabs/skeleton @skeletonlabs/skeleton-svelte
	@echo "Installing animation libs..."
	@. "$$HOME/.nvm/nvm.sh" && cd mp32/frontend && npx shadcn@latest add https://sveltebits.xyz/r/dot-field.json && npx shadcn@latest add https://sveltebits.xyz/r/magic-rings.json

	@echo "## BACK-END DEPENDENCIES ##"
	@echo "Installing go..."
	@brew install go
	@echo "Installing gin..."
	@cd mp32/backend && go get github.com/gin-gonic/gin
	@echo "Installing fast-api..."
	@cd mp32/backend/fastapi && pip install -r requirements.txt

run:
	@echo "Running frontend and backend..."
	docker compose up -d --build

runf:
	@echo "Running frontend..."
#	@cd mp32/frontend && npm run dev -- --host 0.0.0.0
	docker compose up -d --build frontend

runfapi:
	@echo "Running fast-api..."
	@cd mp32/backend/fastapi && uvicorn main:app --reload --port 8000

runb:
#	@cd mp32/backend && go get github.com/go-chi/chi/v5
	@echo "Running backend..."
	@docker compose up -d --build backend
#	@cd mp32/backend && go run cmd/*.go

fclean:
	@docker compose down