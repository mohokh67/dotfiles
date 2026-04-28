---
name: justify
description: Generate a standardized justfile for any project. Use when user runs /justify or asks to create/regenerate a justfile. Detects language/framework from project files and maps standard recipes (dev, build, test, lint, format, typecheck, clean, ci).
---

# justify

Generate a standardized `justfile` with consistent recipe names across all projects. Actual commands adapt to the detected stack.

## Standard recipes

Always present (TODO placeholder if command can't be detected):
`dev` · `start` · `build` · `test` · `lint` · `format` · `typecheck` · `clean` · `ci`

`ci` is always: `just lint && just typecheck && just test`

## Workflow

### Step 1 — Detect stack

Read project root files to determine language, framework, and package manager:

| Signal file | Stack |
|-------------|-------|
| `package.json` + `pnpm-lock.yaml` | Node / pnpm |
| `package.json` + `yarn.lock` | Node / yarn |
| `package.json` | Node / npm |
| `Cargo.toml` | Rust |
| `pyproject.toml` or `setup.py` | Python |
| `go.mod` | Go |
| `docker-compose.yml` (no other signal) | Docker |

For Node projects, read `package.json` `scripts` field to find exact script names before mapping.

### Step 2 — Show detected mappings and confirm

Present the detected stack and planned recipe → command table. Wait for user confirmation before writing.

Example output:
```
Detected: Node / pnpm

  dev        → pnpm dev
  start      → pnpm start
  build      → pnpm build
  test       → pnpm test
  lint       → pnpm lint
  format     → pnpm format
  typecheck  → pnpm exec tsc --noEmit
  clean      → rm -rf node_modules dist .next .turbo
  ci         → just lint && just typecheck && just test

Generate justfile?
```

### Step 3 — Check for existing justfile

If `justfile` or `Justfile` exists at project root, ask: **overwrite or cancel?**

### Step 4 — Write justfile

Use this template (tabs for recipe indentation, required by just):

```
set shell := ["bash", "-c"]

default:
    @just --list

dev:
    <cmd>

start:
    <cmd>

build:
    <cmd>

test:
    <cmd>

lint:
    <cmd>

format:
    <cmd>

typecheck:
    <cmd>

clean:
    <cmd>

ci:
    just lint && just typecheck && just test
```

If a command can't be detected, use: `echo 'TODO: add <recipe> command'`

## Command mappings by stack

### Node / pnpm
| Recipe | Command |
|--------|---------|
| dev | `pnpm dev` (or `pnpm run dev` if not in scripts) |
| start | `pnpm start` |
| build | `pnpm build` |
| test | `pnpm test` |
| lint | `pnpm lint` |
| format | `pnpm format` |
| typecheck | `pnpm typecheck` or `pnpm exec tsc --noEmit` |
| clean | `rm -rf node_modules dist .next .turbo` |

### Node / yarn
Same as pnpm but replace `pnpm` with `yarn`.

### Node / npm
Same as pnpm but replace `pnpm` with `npm run` (except `npm test` and `npm start` have no `run`).

### Rust
| Recipe | Command |
|--------|---------|
| dev | `cargo run` |
| start | `cargo run` |
| build | `cargo build` |
| test | `cargo test` |
| lint | `cargo clippy` |
| format | `cargo fmt` |
| typecheck | `cargo check` |
| clean | `cargo clean` |

### Python
| Recipe | Command |
|--------|---------|
| dev | `python -m uvicorn main:app --reload` (FastAPI) or `flask run` or `python main.py` |
| start | same as dev |
| build | `python -m build` |
| test | `pytest` |
| lint | `ruff check .` or `flake8 .` |
| format | `ruff format .` or `black .` |
| typecheck | `mypy .` |
| clean | `find . -type d -name __pycache__ -exec rm -rf {} +` |

Detect FastAPI vs Flask vs plain script from imports in main entry file.

### Go
| Recipe | Command |
|--------|---------|
| dev | `go run .` |
| start | `go run .` |
| build | `go build ./...` |
| test | `go test ./...` |
| lint | `golangci-lint run` |
| format | `gofmt -w .` |
| typecheck | `go vet ./...` |
| clean | `go clean` |
