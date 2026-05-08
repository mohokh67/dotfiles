# AGENTS.md

Personal dotfiles repo managed with GNU Stow. Configs only — no build, test, or lint commands.

## Stow mechanics

- `.stowrc` sets `--target=~`. Run `stow home` from repo root to symlink `home/*` → `~/*`.
- To add a new dotfile: place it under `home/` mirroring its `~` path, then run `stow home`.
- Stow refuses to overwrite existing regular files. Remove the target file first if conflicting.

## Directory boundaries

| Path | Purpose |
|------|---------|
| `home/` | Stow-managed — mirrors `~`. All live dotfiles go here. |
| `home/.claude/skills` | Symlink to `../.agents/skills`. Do not create real files here. |
| `home/.claude/settings.local.json` | Machine-specific — gitignored, never commit. |
| `betterfox/`, `vscode/`, `zsh/` | Reference only — not stowed. |

## Git conventions (enforced)

- **Conventional Commits only**: `<type>(<scope>): <description>`. Never plain messages like "update X".
- **Never commit/push to `main`**. Before any commit, run `git branch --show-current`. If on main, STOP and ask to create a branch first.
- No Co-Authored-By or Claude attribution in commits.

## Zsh quirks

- `~/.zshrc.local` is sourced at EOF for machine-specific overrides (not stowed, not in git).
- `~/.gitconfig.local` is included for machine-specific git config.
- `edit` and `view` aliases open `zed` (the editor).
- `python`/`python3`/`pip` are aliased to `uv run` variants.
- `brewall()` runs full Homebrew maintenance (update → upgrade → cleanup → autoremove → bundle dump → doctor).
