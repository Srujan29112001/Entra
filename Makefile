.PHONY: help install dev build test clean docker-up docker-down db-migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	pnpm install
	cd apps/agents && pip install -r requirements.txt

dev: ## Start development servers
	docker-compose up -d postgres redis
	pnpm dev

dev-full: ## Start all services (frontend, backend, monitoring)
	docker-compose up

build: ## Build all applications
	pnpm build
	docker build -t entra-agents:latest -f docker/Dockerfile.agents .

test: ## Run all tests
	pnpm test
	cd apps/agents && pytest tests/

test-frontend: ## Run frontend tests
	pnpm test

test-backend: ## Run backend tests
	cd apps/agents && pytest tests/ -v

lint: ## Run linting
	pnpm lint
	cd apps/agents && black . && ruff check .

format: ## Format code
	pnpm format
	cd apps/agents && black . && ruff check --fix .

type-check: ## Run type checking
	pnpm type-check
	cd apps/agents && mypy app/

clean: ## Clean build artifacts
	pnpm clean
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

db-migrate: ## Run database migrations
	docker-compose exec postgres psql -U postgres -d entra -f /docker-entrypoint-initdb.d/001_initial_schema.sql

db-reset: ## Reset database (WARNING: destroys data)
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	make db-migrate

shell-agents: ## Open shell in agents container
	docker-compose exec agents bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d entra

logs-agents: ## View agents logs
	docker-compose logs -f agents

monitoring: ## Open monitoring dashboards
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001 (admin/admin)"

# Production commands
deploy-backend: ## Deploy backend to production
	docker build -t entra-agents:latest -f docker/Dockerfile.agents .
	docker tag entra-agents:latest your-registry/entra-agents:latest
	docker push your-registry/entra-agents:latest

deploy-frontend: ## Deploy frontend to Vercel
	cd apps/web && vercel --prod
