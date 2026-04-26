---
name: docker-dev-setup
description: Set up a Docker-based dev environment where language runtimes live in containers and Claude Code runs on the Mac. Generates docker-compose.yml, Justfile, CLAUDE.md, and README for the current project. Use when user wants to avoid installing languages locally, containerize a dev environment, set up docker for a project, run tests/builds in Docker, mentions "docker dev setup", "I don't want to install X on my machine", or wants a portable dev environment for Rust, Go, Node, Python, or React Native.
---

# Docker Dev Setup

Generates a Docker-based dev environment where:
- Code files stay local (edited in any IDE)
- Language runtimes (Rust, Node, Python, Go) live inside Docker — nothing to install on your Mac
- Claude Code runs on your Mac as normal — no installation inside containers
- A `CLAUDE.md` is generated so Claude knows to route commands through `docker compose exec dev`
- Auth comes from `~/.claude` mounted read-only — no re-login needed

## Process

1. **Detect language** — check the project directory for `Cargo.toml`, `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`. If found, confirm with user. If not found, ask. For `package.json`, also check if it's a React Native project (look for `react-native` in dependencies).

2. **Inspect existing commands** — before generating the Justfile, read what the project already defines, in priority order:
   - **Existing Justfile** (highest priority): read it, use its command names as-is. Do NOT overwrite — append only the missing docker infra commands (`up`, `down`, `shell`, `logs`, `ps`) at the bottom, skipping any that already exist. Do not re-map commands that are already there.
   - **Makefile** (if no Justfile): read its targets and mirror them in a new Justfile, wrapping each with `docker compose exec dev`
   - **`package.json` scripts** (if no Justfile and no Makefile): read `"scripts"` and use those exact names (e.g. `"dev"` → `npm run dev`, `"lint:fix"` → use for fmt, etc.)
   - **Nothing found**: fall back to language defaults from TEMPLATES.md, with `# update if your project uses a different command` comments

3. **Ask for version** — after language is confirmed, suggest the current recommended version and ask user to confirm or choose differently. Use your own knowledge of current stable/LTS versions — see TEMPLATES.md for guidance on what to say.

4. **Ask for port** — ask what port the app runs on (default 3000 for Node/React Native, 8080 for Go, 8000 for Python, none for Rust CLI). This gets added to `docker-compose.yml`.

5. **Ask for project name** — default to current directory name.

6. **Generate files** — create all four files using the templates in [TEMPLATES.md](TEMPLATES.md). Never skip any file.

7. **Print next steps** — tell user exactly what to run.

## Supported languages

- `rust` — `rust:{{version}}` image, cargo commands
- `node` — `node:{{version}}` image, scripts from `package.json`
- `react-native` — `node:{{version}}` image, scripts from `package.json` (note: native iOS/Android builds still require host tools)
- `python` — `python:{{version}}` image, pip + pytest/ruff commands
- `go` — `golang:{{version}}` image, go commands

## Justfile generation rules

- **Infra commands** (`up`, `down`, `shell`, `logs`, `ps`) — always include, they just wrap docker compose
- **Project commands** (`build`, `run`, `test`, `lint`, `fmt`) — derive from the project's existing scripts/tasks, not hardcoded defaults. If a script doesn't exist in the project, use the sensible default from TEMPLATES.md but add a comment: `# update this if your project uses a different command`
- **Never overwrite** an existing Justfile — only append

## Output

Always generate exactly these four files (or append, per rules above):
- `docker-compose.yml`
- `Justfile`
- `CLAUDE.md` — if one exists, update it by adding/merging the docker dev section without removing existing content; if it doesn't exist, create it
- `README.md` (only if one doesn't exist — if it does, append a "## Docker Dev" section)

## Next steps to print after generation

```
Setup complete. Run:
  just up     # start container
  just build  # install dependencies (first time)
  just run    # start the app
```

Then open Claude Code on your Mac as normal — it will read CLAUDE.md and automatically route commands into the container.
