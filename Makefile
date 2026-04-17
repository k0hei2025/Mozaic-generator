# ─────────────────────────────────────────────
#  Mozaik Generator — Makefile
# ─────────────────────────────────────────────
#  Usage:  make help
# ─────────────────────────────────────────────

# Default target image and tiles directory (override on command line)
TARGET   ?= target.jpg
TILES    ?= tiles/
OUTPUT   ?= mosaic_output.jpg
TILE_SIZE?= 40x40
WORKERS  ?= 4
ENLARGE  ?= 1
BLEND    ?= 0.0
K        ?= 40

.PHONY: help install run run-hq run-poster test test-cov lint clean

# ─────────── Help ───────────

help: ## Show this help message
	@echo ""
	@echo "  Mozaik Generator"
	@echo "  ════════════════"
	@echo ""
	@echo "  Setup:"
	@echo "    make install          Install dependencies"
	@echo ""
	@echo "  Generate mosaics:"
	@echo "    make run              Basic mosaic (fastest)"
	@echo "    make run-hq           High quality (blended, smaller tiles)"
	@echo "    make run-poster       Poster-ready (3x enlarged, blended)"
	@echo ""
	@echo "  Override defaults:"
	@echo "    make run TARGET=photo.jpg TILES=~/wedding_photos/"
	@echo "    make run-poster TARGET=best.jpg TILES=~/photos/ OUTPUT=poster.jpg"
	@echo ""
	@echo "  Development:"
	@echo "    make test             Run all tests"
	@echo "    make test-cov         Run tests with coverage report"
	@echo "    make clean            Remove generated files and caches"
	@echo ""
	@echo "  Defaults:"
	@echo "    TARGET=$(TARGET)  TILES=$(TILES)  OUTPUT=$(OUTPUT)"
	@echo "    TILE_SIZE=$(TILE_SIZE)  WORKERS=$(WORKERS)  K=$(K)"
	@echo ""

# ─────────── Setup ───────────

install: ## Install all dependencies
	pip3 install -r requirements.txt

install-dev: ## Install with dev/test dependencies
	pip3 install -r requirements.txt pytest pytest-cov

# ─────────── Generate Mosaics ───────────

run: ## Basic mosaic — fast, default settings
	python3 -m mozaik \
		--target $(TARGET) \
		--tiles-dir $(TILES) \
		--output $(OUTPUT) \
		--tile-size $(TILE_SIZE) \
		--k-neighbors $(K) \
		--workers $(WORKERS) \
		--cache

run-hq: ## High quality — smaller tiles + subtle blending
	python3 -m mozaik \
		--target $(TARGET) \
		--tiles-dir $(TILES) \
		--output $(OUTPUT) \
		--tile-size 25x25 \
		--k-neighbors $(K) \
		--blend 0.2 \
		--workers $(WORKERS) \
		--cache

run-poster: ## Poster-ready — 3x enlarged, blended, fine tiles
	python3 -m mozaik \
		--target $(TARGET) \
		--tiles-dir $(TILES) \
		--output $(OUTPUT) \
		--tile-size 30x30 \
		--k-neighbors $(K) \
		--blend 0.15 \
		--enlarge 3 \
		--workers $(WORKERS) \
		--cache

run-no-repeat: ## No tile reuse — every photo appears at most once
	python3 -m mozaik \
		--target $(TARGET) \
		--tiles-dir $(TILES) \
		--output $(OUTPUT) \
		--tile-size $(TILE_SIZE) \
		--k-neighbors $(K) \
		--no-reuse \
		--workers $(WORKERS) \
		--cache

# ─────────── Development ───────────

test: ## Run all tests
	python3 -m pytest tests/ -v

test-cov: ## Run tests with coverage report
	python3 -m pytest tests/ -v --cov=mozaik --cov-report=term-missing

clean: ## Remove caches, build artifacts, and generated outputs
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".mozaik_cache_*" -delete 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache build dist *.egg-info htmlcov .coverage
	@echo "Cleaned."
