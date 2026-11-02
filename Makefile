NODE_BIN ?= $(or $(lastword $(wildcard $(HOME)/.nvm/versions/node/*/bin/node)),$(shell command -v node 2>/dev/null))
NODE_DIR := $(dir $(NODE_BIN))
NPM := PATH="$(NODE_DIR):$$PATH" "$(NODE_DIR)npm"

COMPOSE := docker compose -f docker-compose.yml

VISION_PORT ?= 8000
FRONTEND_PORT ?= 5173
VISION_URL ?= ws://localhost:$(VISION_PORT)/ws
LOCAL_DATABASE_URL := postgresql+psycopg://airplane:airplane@localhost:5432/airplane_cv

.PHONY: up dev dev-reload dev-api dev-web up-hardware camera-mac down logs check check-frontend check-python check-exclusions check-readme

up:
	@set -eu; \
	camera_pid=""; logs_pid=""; \
	cleanup() { \
		trap - EXIT INT TERM; \
		if [ -n "$$camera_pid" ]; then kill "$$camera_pid" 2>/dev/null || true; fi; \
		if [ -n "$$logs_pid" ]; then kill "$$logs_pid" 2>/dev/null || true; fi; \
		wait "$$camera_pid" 2>/dev/null || true; \
		wait "$$logs_pid" 2>/dev/null || true; \
		$(COMPOSE) down; \
	}; \
	trap cleanup EXIT INT TERM; \
	$(COMPOSE) up --build -d --wait --wait-timeout 120; \
	(cd vision && uv sync --frozen && exec env WS_SERVER_URL=ws://localhost:8000/ws REDIS_HOST=localhost REDIS_PORT=6379 uv run python -m src.application.servers.camera_streamer.streamer) & \
	camera_pid=$$!; \
	$(COMPOSE) logs -f & \
	logs_pid=$$!; \
	wait "$$camera_pid"

dev: up

# Everything you edit runs on the host: uvicorn reloads on a Python save,
# vite hot-reloads on a React save. Only Redis and Postgres stay in Docker.
dev-reload:
	@set -eu; \
	api_pid=""; web_pid=""; \
	cleanup() { \
		trap - EXIT INT TERM; \
		if [ -n "$$api_pid" ]; then kill "$$api_pid" 2>/dev/null || true; fi; \
		if [ -n "$$web_pid" ]; then kill "$$web_pid" 2>/dev/null || true; fi; \
		wait "$$api_pid" 2>/dev/null || true; \
		wait "$$web_pid" 2>/dev/null || true; \
		$(COMPOSE) stop redis-db postgres-db; \
	}; \
	trap cleanup EXIT INT TERM; \
	$(COMPOSE) up -d --wait --wait-timeout 60 redis-db postgres-db; \
	$(MAKE) dev-api & \
	api_pid=$$!; \
	$(MAKE) dev-web & \
	web_pid=$$!; \
	wait

dev-api:
	cd vision && uv sync --frozen
	cd vision && env DATABASE_URL=$(LOCAL_DATABASE_URL) REDIS_HOST=localhost REDIS_PORT=6379 \
		uv run uvicorn src.application.servers.mcp_server.rest_server:app \
		--host 0.0.0.0 --port $(VISION_PORT) --reload --reload-dir src

dev-web:
	$(NPM) --prefix frontend install
	env VITE_VISION_URL=$(VISION_URL) $(NPM) --prefix frontend run dev -- \
		--port $(FRONTEND_PORT) --strictPort

up-hardware:
	docker compose -f docker-compose.yml -f docker-compose.hardware.yml --profile linux-camera up --build

camera-mac:
	cd vision && uv sync --frozen
	cd vision && WS_SERVER_URL=ws://localhost:8000/ws REDIS_HOST=localhost REDIS_PORT=6379 uv run python -m src.application.servers.camera_streamer.streamer

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

check: check-frontend check-python check-exclusions check-readme
	docker compose config >/dev/null

check-frontend:
	$(NPM) --prefix frontend install
	$(NPM) --prefix frontend test
	$(NPM) --prefix frontend run lint
	$(NPM) --prefix frontend run build

check-python:
	cd vision && uv sync --frozen --extra dev
	cd vision && uv run pytest
	cd vision && uv run python -m compileall -q src

check-exclusions:
	@! rg -n -i "servo|motor|distance.sensor|i2c|gpio|robot.commander|movement.tool|set_all_leds|robot_patrol|raspbot|smbus" --glob '!README.md' --glob '!Makefile' --glob '!uv.lock' --glob '!package-lock.json' --glob '!node_modules/**' --glob '!dist/**' --glob '!.venv/**' frontend vision docker-compose.yml docker-compose.hardware.yml
	@test ! -e backend
	@test ! -e .gitignore
	@test ! -e .dockerignore
	@test ! -e .env.example
	@test -f frontend/.gitignore -a -f vision/.gitignore
	@test -f frontend/.dockerignore -a -f vision/.dockerignore
	@test -f frontend/.env.example -a -f vision/.env.example

check-readme:
	@rg -q "make up" README.md
	@rg -q "make dev" README.md
	@rg -q "http://localhost:5173" README.md
	@rg -q "http://localhost:8000/mcp" README.md
	@rg -q "ws://localhost:8000/ws" README.md
	@rg -q "speechSynthesis" README.md
	@rg -q "Docker Desktop" README.md
	@rg -q "make camera-mac" README.md
	@rg -q "uv sync --frozen" vision/README.md
	@rg -q "pytorch-cpu" vision/README.md
