NODE_BIN ?= $(or $(lastword $(wildcard $(HOME)/.nvm/versions/node/*/bin/node)),$(shell command -v node 2>/dev/null))
NODE_DIR := $(dir $(NODE_BIN))
NPM := PATH="$(NODE_DIR):$$PATH" "$(NODE_DIR)npm"

COMPOSE := docker compose -f docker-compose.yml

.PHONY: up dev up-hardware camera-mac down logs check check-backend check-frontend check-python check-exclusions check-readme

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
	(cd vision && uv sync --frozen && exec env WS_SERVER_URL=ws://localhost:8080 REDIS_HOST=localhost REDIS_PORT=6379 uv run python -m src.application.servers.camera_streamer.streamer) & \
	camera_pid=$$!; \
	$(COMPOSE) logs -f & \
	logs_pid=$$!; \
	wait "$$camera_pid"

dev: up

up-hardware:
	docker compose -f docker-compose.yml -f docker-compose.hardware.yml --profile linux-camera up --build

camera-mac:
	cd vision && uv sync --frozen
	cd vision && WS_SERVER_URL=ws://localhost:8080 REDIS_HOST=localhost REDIS_PORT=6379 uv run python -m src.application.servers.camera_streamer.streamer

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

check: check-backend check-frontend check-python check-exclusions check-readme
	docker compose config >/dev/null

check-backend:
	$(NPM) --prefix backend install
	$(NPM) --prefix backend test
	$(NPM) --prefix backend run typecheck
	$(NPM) --prefix backend run build

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
	@! rg -n -i "servo|motor|distance.sensor|i2c|gpio|robot.commander|movement.tool|set_all_leds|robot_patrol|raspbot|smbus" --glob '!README.md' --glob '!Makefile' --glob '!uv.lock' --glob '!package-lock.json' --glob '!node_modules/**' --glob '!dist/**' --glob '!.venv/**' backend frontend vision docker-compose.yml docker-compose.hardware.yml
	@test ! -e .gitignore
	@test ! -e .dockerignore
	@test ! -e .env.example
	@test -f backend/.gitignore -a -f frontend/.gitignore -a -f vision/.gitignore
	@test -f backend/.dockerignore -a -f frontend/.dockerignore -a -f vision/.dockerignore
	@test -f backend/.env.example -a -f frontend/.env.example -a -f vision/.env.example

check-readme:
	@rg -q "make up" README.md
	@rg -q "make dev" README.md
	@rg -q "http://localhost:5173" README.md
	@rg -q "http://localhost:8000/mcp" README.md
	@rg -q "speechSynthesis" README.md
	@rg -q "Docker Desktop" README.md
	@rg -q "make camera-mac" README.md
	@rg -q "uv sync --frozen" vision/README.md
	@rg -q "pytorch-cpu" vision/README.md

