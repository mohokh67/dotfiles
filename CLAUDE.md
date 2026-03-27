# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Personal dotfiles repo managed with GNU Stow. No build, lint, or test commands — configs only.

## Stow setup

```sh
stow home
```

Stow-managed files live in `home/`. To add a new file: place it under `home/` mirroring its `~` path, re-run stow.

## Structure

Stow-managed (`home/` → `~`):

| Path                        | Tool                                      |
| --------------------------- | ----------------------------------------- |
| `.zshrc`                    | Zsh shell (Oh My Zsh, aliases, env setup) |
| `.oh-my-posh.toml`          | Oh My Posh prompt theme                   |
| `.config/zed/settings.json` | Zed editor                                |
| `.claude/CLAUDE.md`         | Claude Code global instructions           |
| `.claude/settings.json`     | Claude Code global settings               |
| `.claude/skills/`           | Claude Code skills                        |

Note: `~/.claude/settings.local.json` is machine-specific — not stowed.

Reference only (not stowed):

| Path                  | Tool                                         |
| --------------------- | -------------------------------------------- |
| `vscode/settings.json` | VSCode                                      |
| `ghostly/config.ghostty` | Ghostty terminal                          |
| `betterfox/user.js`   | Firefox (Betterfox v146 performance/privacy) |

## Key zsh setup

- **Zoxide** replaces `cd`
- **Atuin** for history, **Carapace** for completions
- **NVM** lazy-loaded
- Aliases grouped by tool: git, `gh`, AWS, Docker, Node, Python, YouTube (`yt-dlp`)
- Custom functions: `lsofport`, `mkcd`, `brewall`
