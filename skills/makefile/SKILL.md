---
name: makefile
description: "GNU Make automation and build system guidance. Use when creating or maintaining Makefiles, writing Make targets and recipes, or configuring GNU Make build automation. Keywords: Makefile, GNU Make, targets, recipes, build automation."
metadata:
  version: "2.2.0"
  release_date: "2026-05-22"
---

# Makefile Skill

Guidance for creating and maintaining GNU Make build automation.

## Quick Navigation

| Topic                         | Reference                               |
| ----------------------------- | --------------------------------------- |
| Rules, prerequisites, targets | [syntax.md](references/syntax.md)       |
| Variable types and assignment | [variables.md](references/variables.md) |
| Built-in functions            | [functions.md](references/functions.md) |
| Special and phony targets     | [targets.md](references/targets.md)     |
| Recipe execution, parallel    | [recipes.md](references/recipes.md)     |
| Implicit and pattern rules    | [implicit.md](references/implicit.md)   |
| Common practical patterns     | [patterns.md](references/patterns.md)   |
| Monorepo / umbrella repos     | Monorepo section below + [patterns.md](references/patterns.md) |

---

## Core Concepts

### Rule Structure

```makefile
target: prerequisites
        recipe
```

**Critical:** Recipe lines MUST start with TAB character.

### File vs Phony Targets

```makefile
# File target - creates/updates a file
build/app.o: src/app.c
        $(CC) -c $< -o $@

# Phony target - action, not a file
.PHONY: clean test install

clean:
        rm -rf build/
```

### Variable Assignment

| Operator | Name        | When Expanded           |
| -------- | ----------- | ----------------------- |
| `:=`     | Simple      | Once, at definition     |
| `?=`     | Conditional | If not already set      |
| `=`      | Recursive   | Each use (late binding) |
| `+=`     | Append      | Adds to existing value  |

```makefile
CC := gcc              # Immediate
CFLAGS ?= -O2          # Default, overridable
DEBUG = $(VERBOSE)     # Late binding
CFLAGS += -Wall        # Append
```

### Automatic Variables

| Variable | Meaning                         |
| -------- | ------------------------------- |
| `$@`     | Target                          |
| `$<`     | First prerequisite              |
| `$^`     | All prerequisites (unique)      |
| `$?`     | Prerequisites newer than target |
| `$*`     | Stem in pattern rules           |

---

## Essential Patterns

### Colored Help (Required)

**Always** use explicit, sectioned `@echo` help — never grep/awk auto-generation.

#### Color hierarchy

| Variable | Role | Usage |
| -------- | ---- | ----- |
| `BLUE`   | Section headers | `$(BLUE)Development servers$(RESET)` |
| `GREEN`  | Target names | `$(GREEN)dev-backend$(RESET)` |
| `YELLOW` | Commands, paths, hints | `$(YELLOW)bun run dev$(RESET)`, `$(YELLOW)apps/backend$(RESET)` |

Define colors once at the top:

```makefile
BLUE := $(shell printf '\033[34m')
GREEN := $(shell printf '\033[32m')
YELLOW := $(shell printf '\033[33m')
RESET := $(shell printf '\033[0m')
```

#### Help target rules

1. `.DEFAULT_GOAL := help`
2. Blank line before first section: `@echo ""`
3. Section header in **BLUE**, blank line between sections
4. Each target line: `@echo "  $(GREEN)target$(RESET)   description with $(YELLOW)hints$(RESET)"`
5. Reference delegation paths in help: `$(GREEN)make -C apps/backend dev$(RESET)`
6. Use inline color switches mid-line for nested emphasis (see Docker section example)
7. End help with a trailing blank line

```makefile
.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "$(BLUE)Development servers$(RESET)"
	@echo "  $(GREEN)dev$(RESET)                 $(YELLOW)turbo dev$(RESET) — all apps"
	@echo "  $(GREEN)dev-backend$(RESET), $(GREEN)backend$(RESET)   API only ($(GREEN)make -C apps/backend dev$(RESET))"
	@echo ""
	@echo "$(BLUE)Docker ($(RESET)delegates to $(GREEN)apps/backend/Makefile$(RESET)$(BLUE))$(RESET)"
	@echo "  $(GREEN)docker-up$(RESET)           $(GREEN)make -C apps/backend up$(RESET) — Postgres, Redis"
	@echo ""
```

#### Header boilerplate

```makefile
.PHONY: \
	help \
	install dev build \
	typecheck check

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BACKEND := $(ROOT)/apps/backend

BLUE := $(shell printf '\033[34m')
GREEN := $(shell printf '\033[32m')
YELLOW := $(shell printf '\033[33m')
RESET := $(shell printf '\033[0m')

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

.DEFAULT_GOAL := help
```

### Monorepo / Umbrella Repos (Required for multi-app projects)

For monorepos and umbrella repos, **generate a Makefile per app** (and per shared package that owns infra, e.g. `packages/db`) then delegate from the root.

#### Layout

```
Makefile                  # umbrella: help, setup, aggregates, docker
apps/backend/Makefile     # dev, build, start, typecheck, test
apps/extension/Makefile   # dev, build, zip, typecheck
packages/db/Makefile      # db-generate, db-migrate-*, db-seed, db-studio
```

#### Root delegation pattern

```makefile
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BACKEND := $(ROOT)/apps/backend
EXTENSION := $(ROOT)/apps/extension
DB := $(ROOT)/packages/db

ensure-apps:
	@if [ ! -f "$(BACKEND)/package.json" ] || [ ! -f "$(EXTENSION)/package.json" ]; then \
		echo "$(YELLOW)App checkouts missing. Check apps/ layout.$(RESET)"; \
		exit 1; \
	fi

dev-backend backend: ensure-apps docker-up
	@$(MAKE) -C "$(BACKEND)" dev

build-seq: ensure-apps
	@$(MAKE) -C "$(BACKEND)" build
	@$(MAKE) -C "$(EXTENSION)" build

db-migrate-deploy: ensure-apps
	@$(MAKE) -C "$(DB)" db-migrate-deploy
```

#### Per-app Makefile rules

1. Set `ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))` to the app directory
2. Include the same color variables and a scoped `help` target (app name in header)
3. Recipes run commands from `$(ROOT)` — use `@cd "$(ROOT)" && bun run dev`
4. Target aliases: `dev-backend backend:` on one line for shorthand
5. Root help documents every delegation with `make -C path target`

#### What stays at root vs app

| Root (umbrella) | Per-app Makefile |
| --------------- | ---------------- |
| `help`, `setup`, `install` | `dev`, `build`, `start` |
| Shared `docker-compose` up/down | App-specific runtime |
| Sequential `build-seq` | Single-app build |
| Turbo aggregates (`typecheck`, `test`) | Single-app typecheck/test |
| Guard targets (`ensure-apps`) | — |

#### Submodule variant

When apps are git submodules, add `ensure-submodules` + `submodules-init` and check for `package.json` before delegating (same guard pattern, different message).

### Platform Detection

```makefile
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Darwin)
    OPEN := open
else ifeq ($(UNAME_S),Linux)
    OPEN := xdg-open
endif
```

### Build Directory

```makefile
BUILDDIR := build
SOURCES := $(wildcard src/*.c)
OBJECTS := $(patsubst src/%.c,$(BUILDDIR)/%.o,$(SOURCES))

$(BUILDDIR)/%.o: src/%.c | $(BUILDDIR)
	$(CC) -c $< -o $@

$(BUILDDIR):
	mkdir -p $@
```

### Environment Export

```makefile
export PYTHONPATH := $(PWD)/src
export DATABASE_URL

test:
	pytest tests/  # sees exported variables
```

---

## Common Targets

### Quality Checks

```makefile
.PHONY: lint format check test

lint: ## Run linters
	ruff check .
	mypy src/

format: ## Format code
	ruff format .

check: format lint test ## All quality checks
```

### Cleanup

```makefile
.PHONY: clean clean-all

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

clean-all: clean ## Remove all generated files
	rm -rf .venv .pytest_cache .mypy_cache
```

### Docker Integration

```makefile
IMAGE := myapp
VERSION := $(shell git describe --tags --always)

docker-build: ## Build Docker image
	docker build -t $(IMAGE):$(VERSION) .

docker-run: ## Run container
	docker run -d -p 8000:8000 $(IMAGE):$(VERSION)
```

---

## Recipe Execution

### Each Line = Separate Shell

```makefile
# Won't work - cd lost between lines
bad:
	cd subdir
	pwd           # Still in original dir!

# Correct - combine commands
good:
	cd subdir && pwd

# Or use line continuation
also-good:
	cd subdir && \
	pwd && \
	make
```

### Silent and Error Handling

```makefile
target:
	@echo "@ suppresses command echo"
	-rm -f maybe.txt    # - ignores errors
```

### Parallel Execution

```bash
make -j4              # 4 parallel jobs
make -j4 lint test    # Run lint and test in parallel
```

---

## Output Discipline

**One line in, one line out.** Avoid echo spam.

```makefile
# ❌ Too chatty
start:
	@echo "Starting services..."
	docker compose up -d
	@echo "Waiting..."
	@sleep 3
	@echo "Done!"

# ✅ Concise
start: ## Start services
	@echo "Starting at http://localhost:8000 ..."
	@docker compose up -d
	@echo "Logs: docker compose logs -f"
```

---

## Conditionals

```makefile
DEBUG ?= 0

ifeq ($(DEBUG),1)
    CFLAGS += -g -O0
else
    CFLAGS += -O2
endif

ifdef CI
    TEST_FLAGS := --ci
endif
```

---

## Including Files

```makefile
# Required include (error if missing)
include config.mk

# Optional include (silent if missing)
-include local.mk
-include .env
```

---

## Common Pitfalls

| Pitfall               | Problem                                 | Solution                 |
| --------------------- | --------------------------------------- | ------------------------ |
| Spaces in recipes     | Recipes need TAB                        | Use actual TAB character |
| Missing .PHONY        | `make test` fails if `test` file exists | Declare `.PHONY: test`   |
| cd in recipes         | Each line is new shell                  | Use `cd dir && command`  |
| `=` vs `:=` confusion | Unexpected late expansion               | Use `:=` by default      |
| Unexported vars       | Subprocesses don't see vars             | `export VAR`             |
| Complex shell in make | Hard to maintain                        | Move to external script  |

---

## Quick Reference

```makefile
# Umbrella Makefile (monorepo root)
.PHONY: help ensure-apps install dev-backend build-seq typecheck

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BACKEND := $(ROOT)/apps/backend
ADMIN := $(ROOT)/apps/admin

BLUE := $(shell printf '\033[34m')
GREEN := $(shell printf '\033[32m')
YELLOW := $(shell printf '\033[33m')
RESET := $(shell printf '\033[0m')

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "$(BLUE)Development servers$(RESET)"
	@echo "  $(GREEN)dev-backend$(RESET), $(GREEN)backend$(RESET)   API ($(GREEN)make -C apps/backend dev$(RESET))"
	@echo ""
	@echo "$(BLUE)Quality (delegates per app)$(RESET)"
	@echo "  $(GREEN)typecheck$(RESET)             tsc in each app"
	@echo ""

ensure-apps:
	@test -f "$(BACKEND)/package.json" || (echo "$(YELLOW)Missing apps/backend$(RESET)" && exit 1)

install: ensure-apps
	bun install
	@$(MAKE) -C "$(BACKEND)" install

dev-backend backend: ensure-apps
	@$(MAKE) -C "$(BACKEND)" dev

build-seq: ensure-apps
	@$(MAKE) -C "$(BACKEND)" build
	@$(MAKE) -C "$(ADMIN)" build

typecheck: ensure-apps
	@$(MAKE) -C "$(BACKEND)" typecheck
	@$(MAKE) -C "$(ADMIN)" typecheck
```

---

## Links

- [Documentation](https://www.gnu.org/software/make/manual/make.html)

## See Also

- [patterns.md](references/patterns.md) - Extended patterns and recipes
