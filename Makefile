
# Makefile for Tenantra Phase 0 & 1

TENANTRA_ENV ?= development
ENV_FILE := .env.$(TENANTRA_ENV)
TEST_DB_URL := sqlite:///./test_api.db
ifneq ($(wildcard $(ENV_FILE)),)
COMPOSE_ENV_ARG := --env-file $(ENV_FILE)
else
COMPOSE_ENV_ARG :=
endif

# Default compose chain; use DEV=1 to include dev override
ifdef DEV
COMPOSE := docker compose $(COMPOSE_ENV_ARG) -f docker/docker-compose.yml -f docker/docker-compose.override.dev.yml
else
COMPOSE := docker compose $(COMPOSE_ENV_ARG) -f docker/docker-compose.yml -f docker/docker-compose.override.yml
endif

# Build all services
build:
	$(COMPOSE) build

# Start all services
up:
	$(COMPOSE) up -d

# Stop all services
down:
	$(COMPOSE) down

# Run tests inside the backend container
test:
	$(COMPOSE) run --rm \
		-e TENANTRA_TEST_BOOTSTRAP=1 \
		-e TENANTRA_TEST_ADMIN_PASSWORD=Admin@1234 \
		-e TENANTRA_ADMIN_PASSWORD=Admin@1234 \
		-e DEFAULT_ADMIN_PASSWORD=Admin@1234 \
		-e DB_URL=$(TEST_DB_URL) \
		-e DATABASE_URL=$(TEST_DB_URL) \
		-e SQLALCHEMY_DATABASE_URI=$(TEST_DB_URL) \
		backend pytest

# Clean up
clean:
	$(COMPOSE) down -v

# Run Alembic migrations
migrate:
	$(COMPOSE) run --rm backend alembic upgrade head

# Seed the database with default tenant and admin user
seed:
	$(COMPOSE) run --rm backend python scripts/db_seed.py

# Validate repo configuration and runtime endpoints; outputs reports/*
validate:
	python tools/validate_tenantra.py --output-dir reports || exit $$?

# Run Lighthouse locally against gateway (requires Node + Chrome)
lighthouse:
	# BASE defaults to http://localhost; override with BASE=<url>
	pwsh -File tools/run_lighthouse.ps1 -BaseUrl $${BASE:-http://localhost}

# Generate OpenAPI snapshot at repo root
openapi:
	python backend/tools/generate_openapi.py --output openapi.json

# All-in-one dev stack (Phases 4–7)
dev-all:
	# Use EXPOSE=1 to bind backend:5000 and frontend:8080
	# Use BUILD=1 to rebuild images
	@if [ "$(EXPOSE)" = "1" ]; then EXPOSE_PORTS=1 ; else EXPOSE_PORTS=0 ; fi ; \
	 if [ "$(BUILD)" = "1" ]; then BUILD=1 ; else BUILD=0 ; fi ; \
	 EXPOSE_PORTS=$$EXPOSE_PORTS BUILD=$$BUILD ./scripts/dev_up_phase4to7_all.sh

dev-all-down:
	# Use VOLUMES=1 to remove volumes as well
	VOLUMES=$(VOLUMES) ./scripts/dev_down_phase4to7_all.sh

# Prune dangling images/volumes (optional)
dev-clean:
	-docker image prune -f
	-docker volume prune -f
