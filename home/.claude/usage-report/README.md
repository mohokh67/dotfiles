# Claude Code Usage Report

Self-contained Python script that scans your local Claude Code transcripts and renders an HTML dashboard showing what skills, plugins, MCP servers, hooks, tools, and subagents you actually use — and which ones are sitting around unused.

## Quick start

```sh
python3 ~/.claude/usage-report/usage_report.py
```

That's it. It will:

1. Scan every `.jsonl` transcript under `~/.claude/projects/`
2. Read installed skills (`~/.claude/skills/`) and plugins (`~/.claude/plugins/`)
3. Read `~/.claude/settings.json` for configured MCP servers and hooks
4. Render `~/Desktop/claude-usage-reports/usage-YYYY-MM-DD-HHMMSS.html` and a `.json` sidecar
5. Compare against the previous run and show deltas in the Overview tab
6. Open the HTML in your default browser

## Layout

```
~/.claude/usage-report/
├── usage_report.py        # the script (Python 3 stdlib only)
├── README.md              # this file
├── PLAN.md                # design doc + decisions log
└── assets/
    └── chart.min.js       # Chart.js, embedded inline into each report

~/Desktop/claude-usage-reports/
├── usage-2026-05-21-112845.html   # browse-able dashboard
└── usage-2026-05-21-112845.json   # raw stats for comparison
```

Reports land in `~/Desktop/claude-usage-reports/` (auto-created on first run) so they stay out of the dotfiles repo and aren't synced across machines. All other paths are computed from `Path.home()` and `Path(__file__).parent` — copy the script directory to any machine and it just works.

## Flags

| Flag | Purpose |
|------|---------|
| `--since 2026-05-01` | Only include transcripts modified on or after this ISO date |
| `--no-open` | Skip auto-opening the report in a browser |
| `--no-compare` | Skip the diff-vs-previous-run banner |
| `--output PATH` | Write the HTML to a custom path (the JSON sidecar follows) |

## What's in the report

Tabs:

- **Overview** — total sessions, tool calls, tokens (input/output/cache), models used. Deltas vs previous run when available.
- **Tools** — every tool name ever invoked, ranked by call count and total bytes returned. Bar chart of the top 15.
- **Skills** — every skill installed on disk, joined with usage data. Columns: call count, last used, recent-30d flag, `SKILL.md` size (always-loaded context cost), description.
- **Plugins** — per-plugin rollup. Skills used vs total, total calls, total `SKILL.md` bytes shipped, per-component drilldown.
- **MCP servers** — calls per server, total bytes returned, biggest single result.
- **Subagents** — `Agent` tool invocations grouped by `subagent_type`.
- **Projects** — sessions, tool calls, tokens per working directory.
- **Sessions** — most recent 200 transcripts with date, project, user message count, tool calls, tokens, top tools.
- **Context bloat** — top 30 individual tool results that returned the most bytes (the "what eats my context window" view).
- **Hooks** — every hook execution observed in transcripts: command, fires, errors, prevented-continuation count, event types.
- **Permissions** — permission-mode events per mode and most-toggled sessions.
- **Slash commands** — every `/command` invoked.
- **Unused & underused** — skills with zero invocations (sorted by `SKILL.md` size, biggest waste first), MCP servers configured but never called, hooks configured but never observed firing.

## Comparison mode

By default, every run is automatically compared against the most recent `.json` sidecar in `~/Desktop/claude-usage-reports/`. The Overview tab shows green/red deltas for headline numbers. Disable with `--no-compare`.

To compare against a specific older snapshot, just delete or move the newer ones aside — the script picks up the most recent file that isn't the one being written.

## Caveats

- **Skill counts only reflect the `Skill` tool path.** Skills triggered via slash command land in the **Slash commands** tab instead, since the harness loads them by command name without going through the `Skill` tool.
- **Permission prompts shown/denied are not logged in transcripts.** Only mode switches (default → plan → bypass etc.) are visible.
- **Token totals include cache reads**, which can be very large but cost less than fresh input. Look at `cache_read_tokens` separately when reasoning about cost.
- **Hook detection is best-effort.** Hook commands are matched by their command string (with `${CLAUDE_PLUGIN_ROOT}` substituted) — if you change a hook command, it'll register as a new entry.

## Re-running

Run it as often as you like. Each run produces a new file in `reports/`. The reports directory is yours to prune.

## Portability

Stdlib-only, no `pip install`. Tested on macOS (Darwin). Should run on Linux unchanged — `xdg-open` is used for browser launch. On Windows it falls back to `os.startfile`.
