# AGENTS.md

Personal dotfiles repo managed with GNU Stow. Configs only — no build, test, or lint commands.

## Stow mechanics

- `.stowrc` sets `--target=~`. Run `stow home` from repo root to symlink `home/*` → `~/*`.
- To add a new dotfile: place it under `home/` mirroring its `~` path, then run `stow home`.
- Stow refuses to overwrite existing regular files. Remove the target file first if conflicting.

## Directory layout

### Stowed (`home/` → `~`)

| Path | Tool |
|------|------|
| `.zshrc` | Zsh shell (Oh My Zsh, aliases, env setup) |
| `.oh-my-posh.toml` | Oh My Posh prompt theme |
| `.fzf.zsh`, `.fzf.bash` | fzf fuzzy finder |
| `.gitconfig` | Git config (delta diff pager, credential store, includes `~/.gitconfig.local`) |
| `.Brewfile` | Homebrew bundle (stowed to `~`) |
| `.wezterm.lua` | WezTerm terminal |
| `.hammerspoon/` | Hammerspoon automation |
| `.config/zed/settings.json` | Zed editor |
| `.config/tmux/tmux.conf` | tmux |
| `.config/yazi/` | yazi file manager (keymap, theme, flavors) |
| `.config/herdr/config.toml` | herdr config |
| `.config/opencode/opencode.json`, `tui.json` | OpenCode TUI config |
| `.claude/CLAUDE.md` | Claude Code behavioral instructions |
| `.claude/settings.json` | Claude Code global settings |
| `.claude/hooks/` | Claude Code PreToolUse hooks |
| `.claude/skills/` | Symlink → `../.agents/skills`. Do not create real files here. |
| `.claude/usage-report/` | Claude Code usage analytics dashboard |
| `.claude/statusline-command.sh` | Claude Code status line script |
| `.agents/skills/` | Agent skills (26 skills, shared across agents) |

Note: `~/.claude/settings.local.json` is machine-specific — gitignored, never commit.

### Reference only (not stowed)

| Path | Tool |
|------|------|
| `betterfox/user.js` | Firefox (Betterfox performance/privacy) |
| `vscode/settings.json` | VS Code |
| `zsh/` | Archive (`.zshrc_old`) |
| `brew/` | Brew management scripts (`dump.sh`, `install.sh`, `Brewfile`) |
| `Brewfile` (repo root) | Root-level Brewfile |
| `tools/` | Reference docs (`dev.md`, `mobile.md`, `tools_i_use.md`) |
| `opencode.json` (repo root) | OpenCode project config |

## Git conventions (enforced)

- **Conventional Commits only**: `<type>(<scope>): <description>`. Never plain messages like "update X".
- **Never commit/push to `main`**. Before any commit, run `git branch --show-current`. If on main, STOP and ask to create a branch first.
- No Co-Authored-By or Claude attribution in commits.

## Shell & CLI

- **zoxide** replaces `cd`
- **oh-my-posh** prompt theme
- **carapace** completions, **atuin** history, **thefuck** corrections
- **fzf** with bat preview (`Ctrl+T`)
- **bat** → `cat`, **eza** → `ls`, **delta** as git diff pager
- **yazi** file manager (shell function `y` changes directory on exit)
- `edit` and `view` aliases open `zed`
- `python`/`python3`/`pip` are aliased to `uv run` variants
- `~/.zshrc.local` sourced at EOF for machine-specific overrides (not stowed, not in git)
- `~/.gitconfig.local` included for machine-specific git config

## Agent skills

### Issue tracker

Issues and specs live as markdown files under `.scratch/<feature-slug>/` in this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

Uses the five canonical triage roles as-is (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at repo root. See `docs/agents/domain.md`.

## Other tooling

- **Hammerspoon** — macOS automation (`.hammerspoon/`)
- **Claude Code** — `cc`, `cch` (haiku), `ccx` (skip permissions), `claude-usage`
- **OpenCode** — `oc` (plan agent), `occ` (continue), `oc-free` (free model)
- **brewall()** — full Homebrew maintenance (update → upgrade → cleanup → autoremove → bundle dump → doctor)
- **yt-dlp** — `youtube`, `youtube-720`, `youtube-audio` aliases
- **Brewfile** — managed via `brew/` scripts and stowed `.Brewfile`
