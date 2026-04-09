# Templates

Use these verbatim, substituting `{{project}}` with the project name and `{{image}}` / commands with the language-specific values below.

---

## Version guidance

Use your own knowledge of current stable/LTS versions. When asking the user to confirm, say something like:

- **rust**: "Rust stable (`latest`) — or pin a version like `1.78`?"
- **node / react-native**: "Node 22 (Active LTS) — or choose 20 (Maintenance LTS) or 24 (Current)?"
- **python**: "Python 3.12 (stable) — or choose 3.13 (latest)?"
- **go**: "Go 1.23 (stable) — or a different version?"

If your knowledge suggests a newer version is current, use that instead.

---

## Language config

| language      | image                | build                               | run                        | test             | lint                     | fmt                        | clean                              |
|---------------|----------------------|-------------------------------------|----------------------------|------------------|--------------------------|----------------------------|------------------------------------|
| rust          | `rust:{{version}}`   | `cargo build`                       | `cargo run`                | `cargo test`     | `cargo clippy`           | `cargo fmt`                | `cargo clean`                      |
| node          | `node:{{version}}`   | `npm install`                       | `npm start`                | `npm test`       | `npm run lint`           | `npx prettier --write .`   | `rm -rf node_modules dist`         |
| react-native  | `node:{{version}}`   | `npm install`                       | `npx expo start`           | `npm test`       | `npm run lint`           | `npx prettier --write .`   | `rm -rf node_modules .expo`        |
| python        | `python:{{version}}` | `pip install -r requirements.txt`   | `python main.py`           | `pytest`         | `ruff check .`           | `ruff format .`            | `find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true` |
| go            | `golang:{{version}}` | `go build ./...`                    | `go run .`                 | `go test ./...`  | `go vet ./...`           | `gofmt -w .`               | `go clean`                         |

---

## docker-compose.yml

```yaml
services:
  dev:
    image: {{image}}
    working_dir: /app
    volumes:
      - .:/app
      - ~/.claude:/root/.claude:ro
    ports:
      - "3000:3000"
    stdin_open: true
    tty: true
    command: sleep infinity
```

Ask the user if port 3000 is correct, or if they need a different port (e.g. 8080 for Go/Python). Update both sides of the mapping accordingly (e.g. `"8080:8080"`).

---

## Justfile

```just
# {{project}} — docker dev environment
# Usage: just <command>

up:
    docker compose up -d

down:
    docker compose down

shell:
    docker compose exec dev bash

# update if your project uses a different command
build:
    docker compose exec dev {{build}}

# update if your project uses a different command
run:
    docker compose exec dev {{run}}

# update if your project uses a different command
test:
    docker compose exec dev {{test}}

# update if your project uses a different command
lint:
    docker compose exec dev {{lint}}

# update if your project uses a different command
fmt:
    docker compose exec dev {{fmt}}

clean:
    docker compose run --rm dev {{clean}}
    docker compose down --volumes --remove-orphans

logs:
    docker compose logs -f dev

ps:
    docker compose ps
```

---

## CLAUDE.md

This file tells Claude Code (running on your Mac) to route all shell commands through the container automatically.

```markdown
# {{project}}

## Dev environment

This project runs inside Docker. The container must be running (`just up`) before Claude executes any commands.

When running any shell command (build, test, lint, format, etc.), always use `just <command>` rather than running language tools directly — the Justfile proxies everything into the container via `docker compose exec dev`.

Available commands: `just build`, `just run`, `just test`, `just lint`, `just fmt`, `just clean`, `just shell`, `just logs`, `just ps`.
```

---

## README.md (Docker Dev section)

If a README exists, append this section. If not, create a README with a `# {{project}}` heading followed by this content.

### Docker Dev

All development runs inside Docker — no need to install {{language}} locally. Claude Code runs on your Mac as normal.

**Prerequisites**

- [Docker](https://docs.docker.com/get-docker/)
- [just](https://github.com/casey/just#installation) (`brew install just`)
- Claude Code CLI on your Mac (not inside Docker)

**Quick start**

    just up     # start container
    just shell  # open a shell inside the container (optional)

Then open Claude Code on your Mac as normal. It reads `CLAUDE.md` and routes commands into the container automatically.

**Commands**

| Command       | What it does                              |
|---------------|-------------------------------------------|
| `just up`     | Start the dev container                   |
| `just down`   | Stop the dev container                    |
| `just shell`  | Open a shell inside the container         |
| `just build`  | Build / install dependencies              |
| `just run`    | Run the project                           |
| `just test`   | Run tests                                 |
| `just lint`   | Lint the code                             |
| `just fmt`    | Format the code                           |
| `just clean`  | Clean build artifacts + remove containers |
| `just logs`   | Tail container logs                       |
| `just ps`     | Show container status                     |

**How Claude Code auth works**

`~/.claude` from your Mac is mounted read-only into the container. Your browser login, skills, and settings are available automatically — no re-authentication needed.

**Security note**

Only the project folder and `~/.claude` (read-only) are mounted. Claude cannot access anything else on your Mac.
