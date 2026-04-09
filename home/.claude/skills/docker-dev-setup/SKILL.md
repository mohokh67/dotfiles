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

2. **Ask for version** — after language is confirmed, suggest the current recommended version and ask user to confirm or choose differently. Use your own knowledge of current stable/LTS versions — see TEMPLATES.md for guidance on what to say.

3. **Ask for project name** — default to current directory name.

4. **Generate files** — create all four files in the current working directory using the templates in [TEMPLATES.md](TEMPLATES.md). Never skip any file.

5. **Print next steps** — tell user exactly what to run.

## Supported languages

- `rust` — `rust:{{version}}` image, cargo commands
- `node` — `node:{{version}}` image, npm commands
- `react-native` — `node:{{version}}` image, npm + expo/rn commands (note: native iOS/Android builds still require host tools)
- `python` — `python:{{version}}` image, pip + pytest/ruff commands
- `go` — `golang:{{version}}` image, go commands

## Output

Always generate exactly these four files:
- `docker-compose.yml`
- `Justfile`
- `CLAUDE.md` — tells Claude Code (running on Mac) to use `docker compose exec dev` for all shell commands
- `README.md` (only if one doesn't exist — if it does, append a "## Docker Dev" section)

## Next steps to print after generation

```
Setup complete. Run:
  just up     # start container
  just shell  # open a shell inside the container (optional)
```

Then open Claude Code on your Mac as normal — it will read CLAUDE.md and automatically route commands into the container.
