# Forge Monorepo Makefile

.PHONY: help deps dev build test lint

help:
	@echo "Forge Monorepo Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  deps      - Install all dependencies"
	@echo "  dev       - Start development servers"
	@echo "  build     - Build all artifacts"
	@echo "  test      - Run all tests"
	@echo "  lint      - Run all linters"
	@echo "  clean     - Clean up artifacts"

deps:
	@echo "Installing Python dependencies..."
	cd src/api && uv sync
	@echo "Installing JavaScript dependencies..."
	cd src/web && pnpm install

dev:
	@echo "Starting development servers..."
	@echo "API: http://localhost:8000"
	@echo "Web: http://localhost:3000"
	@echo "Press Ctrl+C to stop"
	@make -C src/api dev &
	@make -C src/web dev
	@wait

build:
	@echo "Building multi-arch images..."
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		--push \
		-t forge-api:latest \
		-f src/api/Dockerfile \
		.
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		--push \
		-t forge-web:latest \
		-f src/web/Dockerfile \
		.

test:
	@echo "Running tests..."
	cd src/api && uv run pytest
	cd src/web && pnpm test

lint:
	@echo "Running linters..."
	cd src/api && uv run ruff check .
	cd src/api && uv run mypy .
	cd src/web && pnpm lint

clean:
	@echo "Cleaning up..."
	rm -rf src/api/__pycache__
	rm -rf src/api/.pytest_cache
	rm -rf src/web/.next
	rm -rf src/web/node_modules
