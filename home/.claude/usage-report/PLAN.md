# Plan: Claude Code Usage Report

## Context

You wanted a personal dashboard for your Claude Code usage — which skills, plugins, MCP servers, tools, hooks, and subagents you actually use across all sessions on this machine, which ones are bloating your context window, and which ones are installed but never used. The framing started as "an HTML overview" and evolved through a grilling session into a re-runnable Python script that produces timestamped HTML reports with comparison-vs-previous-run support.

The motivation is **optimization** plus **curiosity**: prune dead skills and plugins, identify which tools return the most bytes, and watch usage trends over time.

## Decisions log

| # | Question | Decision | Reason |
|---|----------|----------|--------|
| 1 | What's the goal? | D — multi-tab HTML covering optimization audit, fun stats, and context forensics | You want everything; willing to trim later |
| 2 | Runnable form | B — standalone Python script, optional slash-command wrapper later | Free to re-run, doesn't squat in context budget |
| 3 | Scope | All 11 sections including hooks, permission modes, dead-weight detection | "Add everything, drop later" |
| 4 | Lookback window | C — show all-time AND 30-day usage side-by-side | "Used once two months ago" is functionally dead |
| 5 | Plugin dead/alive label | B — per-component breakdown, no binary verdict | Multi-skill plugins can be partly used |
| 6 | Output location | `~/.claude/usage-report/` with portable paths | Run on multiple machines |
| 6 | Charts | Yes — Chart.js, embedded inline | Better viz, offline-portable |
| 6 | Comparison | Auto-compare against latest previous JSON | Trend tracking |

## Architecture

```
usage_report.py
├── load_skills()         scans ~/.claude/skills + ~/.claude/plugins for SKILL.md
├── load_plugins()        reads ~/.claude/plugins/installed_plugins.json
├── load_settings()       merges settings.json + settings.local.json (mcpServers, hooks)
├── analyze(since)        walks every transcript JSONL, returns big stats dict
│   ├── tool_use blocks       → tool call counts + result bytes
│   ├── Skill tool calls      → skill invocation counts + last-used timestamp
│   ├── Agent tool calls      → subagent_type counts
│   ├── mcp__* tools          → per-server rollup with biggest-result tracking
│   ├── tool_result blocks    → joined back to tool name via tool_use_id
│   ├── usage field           → input/output/cache token totals
│   ├── system stop_hook_summary + attachment hook_success → hook firings
│   └── permission-mode       → mode switch counts per session
├── build_skill_table()       joins on-disk catalog with usage, computes recent-30d
├── build_plugin_table()      per-plugin rollup
├── build_unused_table()      zero-use skills/MCPs/hooks
├── diff_stats()              delta vs previous JSON sidecar
├── render_html()             single-file HTML with inline Chart.js
└── main()                    CLI entry: --since, --no-open, --no-compare, --output
```

## Data sources

**Transcripts (`~/.claude/projects/*/*.jsonl`):**
- 80 files at time of writing, ~21MB total, ~8000 lines
- Schema: line-delimited records with `type` field — `assistant`, `user`, `system`, `attachment`, `permission-mode`, `last-prompt`, `file-history-snapshot`
- Token counts live in `assistant` records under `message.usage`
- Tool calls live in `assistant` records under `message.content[].type=="tool_use"`
- Tool results live in `user` records under `message.content[].type=="tool_result"`, joined by `tool_use_id`
- Hook events: `system.subtype=="stop_hook_summary"` and `attachment.attachment.type=="hook_success"`

**On-disk catalog:**
- `~/.claude/skills/<name>/SKILL.md` — frontmatter has `name` and `description`
- `~/.claude/plugins/marketplaces/*/plugins/*/skills/<name>/SKILL.md`
- `~/.claude/plugins/installed_plugins.json` — list of installed plugins
- `~/.claude/settings.json` + `settings.local.json` — `mcpServers` and `hooks` config

## Out of scope (explicitly)

- **Permission prompts shown/denied** — not in transcript data
- **Time spent per skill** — no duration data per skill invocation
- **Whether a skill was useful** — no success/failure signal
- **Cost in dollars** — would need pricing table per model + model version drift
- **Cross-machine sync** — each machine analyzes its own `~/.claude/projects/`

## Future enhancements (not built)

- Slash command wrapper `/usage-report` that shells out to the script
- `--compare PATH` flag to pick a specific older snapshot
- Trend chart: tokens-per-day over time (would need to bucket sessions by day)
- Export tab: copy-pasteable list of skills to uninstall
- Cost estimation given model pricing
- Per-skill description fuzzy match → recommend pruning skills with overlapping triggers

## Verification

```sh
python3 ~/.claude/usage-report/usage_report.py --no-open
ls ~/.claude/usage-report/reports/
open ~/.claude/usage-report/reports/usage-*.html
```

Expected output: an HTML file with 13 tabs, populated tables and at least one bar chart (Tools tab), and a JSON sidecar of the same name. Re-running produces a new timestamped pair and the new HTML's Overview tab shows green/red deltas.
