# Common Makefile Patterns

> Practical patterns for modern development workflows.

## Project Setup Pattern

```makefile
# Header
.DEFAULT_GOAL := help
SHELL := /bin/bash
.SHELLFLAGS := -ec

# Phony declarations (group at top)
.PHONY: all help install test lint format clean

# Help target (self-documenting)
help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
```

## Platform Detection

```makefile
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Linux)
    PLATFORM := linux
    OPEN_CMD := xdg-open
endif
ifeq ($(UNAME_S),Darwin)
    PLATFORM := macos
    OPEN_CMD := open
endif
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
    OPEN_CMD := start
endif
```

## Tool Detection

```makefile
HAS_DOCKER := $(shell command -v docker 2>/dev/null)
HAS_UV := $(shell command -v uv 2>/dev/null)

install:
ifdef HAS_UV
	uv sync
else
	pip install -r requirements.txt
endif

require-docker:
	@command -v docker >/dev/null 2>&1 || \
		(echo "Error: docker required" && exit 1)
```

## Version Management

```makefile
# From pyproject.toml
VERSION := $(shell grep -m1 version pyproject.toml | cut -d'"' -f2)

# From git
VERSION := $(shell git describe --tags --always)

# From file
VERSION := $(shell cat VERSION)

build: ## Build version $(VERSION)
	@echo "Building $(VERSION)"
```

## Python/UV Project

```makefile
UV := uv
PYTHON := python

.PHONY: install install-dev test lint format clean

install: ## Install production dependencies
	$(UV) sync

install-dev: ## Install with dev dependencies
	$(UV) sync --extra dev

test: ## Run tests
	$(UV) run pytest tests/ -v

lint: ## Run linters
	$(UV) run ruff check .
	$(UV) run mypy src/

format: ## Format code
	$(UV) run ruff format .

clean: ## Remove artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
```

## Node.js Project

```makefile
NPM := npm
NODE := node

.PHONY: install test lint build clean

install: node_modules ## Install dependencies

node_modules: package.json
	$(NPM) install
	touch $@

test: ## Run tests
	$(NPM) test

lint: ## Run linter
	$(NPM) run lint

build: ## Build project
	$(NPM) run build

clean: ## Clean build artifacts
	rm -rf node_modules dist
```

## Docker Patterns

```makefile
IMAGE := myapp
TAG := $(VERSION)

.PHONY: docker-build docker-run docker-stop docker-clean

docker-build: ## Build Docker image
	docker build -t $(IMAGE):$(TAG) .
	docker tag $(IMAGE):$(TAG) $(IMAGE):latest

docker-run: ## Run container
	docker run -d --name $(IMAGE) -p 8000:8000 $(IMAGE):$(TAG)

docker-stop: ## Stop container
	-docker stop $(IMAGE)
	-docker rm $(IMAGE)

docker-clean: docker-stop ## Remove images
	-docker rmi $(IMAGE):$(TAG)
	-docker rmi $(IMAGE):latest
```

## Build Directory Pattern

```makefile
BUILDDIR := build
SRCDIR := src
SOURCES := $(wildcard $(SRCDIR)/*.c)
OBJECTS := $(patsubst $(SRCDIR)/%.c,$(BUILDDIR)/%.o,$(SOURCES))

$(BUILDDIR)/%.o: $(SRCDIR)/%.c | $(BUILDDIR)
	$(CC) -c $< -o $@

$(BUILDDIR):
	mkdir -p $@

clean:
	rm -rf $(BUILDDIR)
```

## Multi-Environment Configs

```makefile
ENV ?= development

ifeq ($(ENV),production)
    CFLAGS := -O3 -DNDEBUG
    DEBUG := 0
else ifeq ($(ENV),test)
    CFLAGS := -O0 -g -DTEST
    DEBUG := 1
else
    CFLAGS := -O0 -g -DDEBUG
    DEBUG := 1
endif

# Usage: make build ENV=production
```

## Verbose/Quiet Mode

```makefile
V ?= 0

ifeq ($(V),0)
    Q := @
    VFLAG :=
else
    Q :=
    VFLAG := -v
endif

compile:
	$(Q)$(CC) $(CFLAGS) -c $< -o $@

# Usage: make compile V=1
```

## Parallel Quality Checks

```makefile
.PHONY: check lint test typecheck

check: ## Run all checks in parallel
	$(MAKE) -j3 lint typecheck test

lint:
	ruff check .

typecheck:
	mypy src/

test:
	pytest tests/
```

## Dependency Chains

```makefile
.PHONY: deploy build test

# Deploy requires build, which requires tests
deploy: build ## Deploy to production
	./scripts/deploy.sh

build: test ## Build application
	python -m build

test: ## Run tests
	pytest tests/
```

## Colored Output

```makefile
# Colors (may not work on all terminals)
RED := \033[31m
GREEN := \033[32m
CYAN := \033[36m
RESET := \033[0m

info:
	@echo "$(CYAN)Building...$(RESET)"

success:
	@echo "$(GREEN)Done!$(RESET)"

error:
	@echo "$(RED)Failed!$(RESET)"
```

## Guard Patterns

```makefile
# Require variable to be set
guard-%:
	@if [ -z '${${*}}' ]; then \
		echo "ERROR: $* is not set"; \
		exit 1; \
	fi

deploy: guard-AWS_REGION guard-AWS_ACCOUNT_ID
	./deploy.sh
```

## File Generation Pattern

```makefile
# Generate file if missing
.env:
	cp .env.example .env
	@echo "Created .env - please configure"

# Always regenerate
.PHONY: config
config:
	envsubst < config.template > config.yaml
```

## Include Pattern

```makefile
# Main Makefile
-include .env           # Load environment
-include local.mk       # Local overrides
-include .devcontainer/Makefile  # DevContainer targets

# Include if exists, ignore if missing
ifneq ($(wildcard config.mk),)
include config.mk
endif
```

## Archive/Release Pattern

```makefile
DIST := dist
NAME := myproject-$(VERSION)

.PHONY: dist dist-clean

dist: dist-clean ## Create release archive
	mkdir -p $(DIST)/$(NAME)
	cp -r src/ docs/ README.md $(DIST)/$(NAME)/
	cd $(DIST) && tar czf $(NAME).tar.gz $(NAME)
	cd $(DIST) && zip -r $(NAME).zip $(NAME)

dist-clean:
	rm -rf $(DIST)
```

## Watch Pattern (requires entr/fswatch)

```makefile
.PHONY: watch watch-test

watch: ## Watch and rebuild
	find src -name '*.c' | entr -c make build

watch-test: ## Watch and run tests
	find src tests -name '*.py' | entr -c make test
```

## Output Discipline

```makefile
# ❌ Too verbose
start:
	@echo "Starting services..."
	docker compose up -d
	@echo "Waiting for health..."
	sleep 5
	@echo "Services started!"
	@echo "Done!"

# ✅ One line in, one line out
start: ## Start services
	@echo "Starting at http://localhost:8000 ..."
	@docker compose up -d
	@echo "Logs: docker compose logs -f"
```
