#!/usr/bin/env python3
"""Claude Code usage report — scans transcripts and renders an HTML dashboard.

Run: python3 ~/.claude/usage-report/usage_report.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

CLAUDE_HOME = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_HOME / "projects"
SKILLS_DIR = CLAUDE_HOME / "skills"
PLUGINS_DIR = CLAUDE_HOME / "plugins"
SETTINGS_PATH = CLAUDE_HOME / "settings.json"
SETTINGS_LOCAL_PATH = CLAUDE_HOME / "settings.local.json"
SELF_DIR = Path(__file__).resolve().parent
REPORTS_DIR = Path.home() / "Desktop" / "claude-usage-reports"
ASSETS_DIR = SELF_DIR / "assets"
CHART_JS_PATH = ASSETS_DIR / "chart.min.js"


def iter_transcripts(since: dt.datetime | None = None):
    """Yield (project_dir_name, jsonl_path) for every transcript on disk."""
    if not PROJECTS_DIR.exists():
        return
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        for jsonl in project_dir.rglob("*.jsonl"):
            if since and dt.datetime.fromtimestamp(jsonl.stat().st_mtime) < since:
                continue
            yield project_dir.name, jsonl


def decode_project_name(dir_name: str) -> str:
    """Convert -Users-foo-bar-baz to /Users/foo/bar/baz."""
    return "/" + dir_name.lstrip("-").replace("-", "/")


def parse_transcript(path: Path):
    """Yield each parsed JSON record. Skip malformed lines silently."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def load_skills() -> dict:
    """Read every SKILL.md in ~/.claude/skills and ~/.claude/plugins/.../skills."""
    skills = {}
    search_roots = [SKILLS_DIR]
    if PLUGINS_DIR.exists():
        for marketplace in (PLUGINS_DIR / "marketplaces").glob("*"):
            search_roots.append(marketplace)
        for d in PLUGINS_DIR.glob("**/skills"):
            search_roots.append(d)

    seen_paths = set()
    for root in search_roots:
        if not root.exists():
            continue
        for skill_md in root.rglob("SKILL.md"):
            if skill_md in seen_paths:
                continue
            seen_paths.add(skill_md)
            try:
                content = skill_md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            name = parse_frontmatter_field(content, "name") or skill_md.parent.name
            description = parse_frontmatter_field(content, "description") or ""
            byte_size = len(content.encode("utf-8"))
            plugin = infer_plugin_for_path(skill_md)
            skills[name] = {
                "name": name,
                "description": description[:500],
                "bytes": byte_size,
                "path": str(skill_md),
                "plugin": plugin,
            }
    return skills


def parse_frontmatter_field(content: str, field: str) -> str | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    fm = content[3:end]
    pattern = rf"^{re.escape(field)}\s*:\s*(.+)$"
    m = re.search(pattern, fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def infer_plugin_for_path(p: Path) -> str | None:
    parts = p.parts
    for i, part in enumerate(parts):
        if part == "plugins" and i + 1 < len(parts):
            nxt = parts[i + 1]
            if nxt == "marketplaces" and i + 2 < len(parts):
                return parts[i + 2]
            if nxt not in {"cache", "data"}:
                return nxt
    return None


def load_plugins() -> dict:
    plugins = {}
    plugins_json = PLUGINS_DIR / "installed_plugins.json"
    if plugins_json.exists():
        try:
            data = json.loads(plugins_json.read_text())
            if isinstance(data, dict):
                for key, val in data.items():
                    plugins[key] = val if isinstance(val, dict) else {"raw": val}
            elif isinstance(data, list):
                for entry in data:
                    if isinstance(entry, dict):
                        nm = entry.get("name") or entry.get("id") or "unknown"
                        plugins[nm] = entry
        except (json.JSONDecodeError, OSError):
            pass
    return plugins


def load_settings() -> dict:
    out = {"mcp_servers": {}, "hooks": {}, "permissions": {}}
    for path in (SETTINGS_PATH, SETTINGS_LOCAL_PATH):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(data.get("mcpServers"), dict):
            out["mcp_servers"].update(data["mcpServers"])
        if isinstance(data.get("hooks"), dict):
            for event, items in data["hooks"].items():
                out["hooks"].setdefault(event, [])
                if isinstance(items, list):
                    out["hooks"][event].extend(items)
        if isinstance(data.get("permissions"), dict):
            out["permissions"].update(data["permissions"])
    return out


def safe_get(d, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
        if d is None:
            return default
    return d if d is not None else default


def content_bytes(content) -> int:
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content.encode("utf-8"))
    if isinstance(content, list):
        total = 0
        for item in content:
            if isinstance(item, dict):
                if "text" in item and isinstance(item["text"], str):
                    total += len(item["text"].encode("utf-8"))
                elif "content" in item:
                    total += content_bytes(item["content"])
                else:
                    total += len(json.dumps(item, default=str).encode("utf-8"))
            elif isinstance(item, str):
                total += len(item.encode("utf-8"))
        return total
    return len(json.dumps(content, default=str).encode("utf-8"))


def analyze(since: dt.datetime | None) -> dict:
    """Walk all transcripts, return aggregated stats dict."""
    stats = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "since": since.isoformat() if since else None,
        "totals": {
            "sessions": 0,
            "subagent_sessions": 0,
            "projects": 0,
            "user_msgs": 0,
            "assistant_turns": 0,
            "tool_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_create_tokens": 0,
            "cache_read_tokens": 0,
        },
        "models": Counter(),
        "tools": defaultdict(lambda: {"calls": 0, "result_bytes": 0}),
        "skills": defaultdict(lambda: {"calls": 0, "last_used": None}),
        "agents": defaultdict(int),
        "mcp": defaultdict(lambda: {"calls": 0, "result_bytes": 0, "biggest": 0}),
        "projects": defaultdict(lambda: {
            "sessions": 0, "tokens": 0, "tool_calls": 0, "path": "",
        }),
        "sessions": [],
        "context_bloat": [],
        "hooks": defaultdict(lambda: {
            "fires": 0, "errors": 0, "prevented": 0, "events": Counter(),
        }),
        "permission_modes": Counter(),
        "permission_switches_per_session": [],
        "slash_commands": Counter(),
        "first_seen": None,
        "last_seen": None,
    }

    project_paths_seen = set()
    tool_use_to_name = {}
    skill_last_used = {}
    project_session_files = defaultdict(list)

    for project_dir, jsonl in iter_transcripts(since):
        project_paths_seen.add(project_dir)
        project_session_files[project_dir].append(jsonl)

    for project_dir, files in project_session_files.items():
        project_path = decode_project_name(project_dir)
        stats["projects"][project_dir]["path"] = project_path
        for jsonl in files:
            is_subagent = "subagents" in jsonl.parts
            session_id = jsonl.stem
            mtime = dt.datetime.fromtimestamp(jsonl.stat().st_mtime)
            session_record = {
                "session_id": session_id,
                "project": project_path,
                "project_dir": project_dir,
                "is_subagent": is_subagent,
                "modified": mtime.isoformat(timespec="seconds"),
                "tokens": 0,
                "tool_calls": 0,
                "user_msgs": 0,
                "top_tools": Counter(),
                "models": set(),
            }
            permission_switches = 0
            for rec in parse_transcript(jsonl):
                rtype = rec.get("type")
                if rtype == "user":
                    session_record["user_msgs"] += 1
                    stats["totals"]["user_msgs"] += 1
                    msg_content = safe_get(rec, "message", "content")
                    text = ""
                    if isinstance(msg_content, str):
                        text = msg_content
                    elif isinstance(msg_content, list):
                        for blk in msg_content:
                            if isinstance(blk, dict) and isinstance(blk.get("text"), str):
                                text += blk["text"]
                    for m in re.findall(r"<command-name>([^<]+)</command-name>", text):
                        cmd = m.strip().lstrip("/")
                        stats["slash_commands"][cmd] += 1
                        if cmd not in BUILTIN_SLASH_COMMANDS:
                            sk = normalize_skill_name(cmd)
                            stats["skills"][sk]["calls"] += 1
                            stats["skills"][sk]["via_slash"] = stats["skills"][sk].get("via_slash", 0) + 1
                            cur = mtime.isoformat(timespec="seconds")
                            prev = stats["skills"][sk]["last_used"]
                            if prev is None or cur > prev:
                                stats["skills"][sk]["last_used"] = cur
                    if isinstance(msg_content, list):
                        for blk in msg_content:
                            if isinstance(blk, dict) and blk.get("type") == "tool_result":
                                tool_id = blk.get("tool_use_id")
                                tool_name = tool_use_to_name.get(tool_id)
                                if tool_name:
                                    nbytes = content_bytes(blk.get("content"))
                                    stats["tools"][tool_name]["result_bytes"] += nbytes
                                    if tool_name.startswith("mcp__"):
                                        server = mcp_server_from_tool(tool_name)
                                        stats["mcp"][server]["result_bytes"] += nbytes
                                        if nbytes > stats["mcp"][server]["biggest"]:
                                            stats["mcp"][server]["biggest"] = nbytes
                                    if nbytes > 5000:
                                        stats["context_bloat"].append({
                                            "tool": tool_name,
                                            "bytes": nbytes,
                                            "session": session_id,
                                            "project": project_path,
                                        })
                elif rtype == "assistant":
                    stats["totals"]["assistant_turns"] += 1
                    model = safe_get(rec, "message", "model")
                    if model:
                        stats["models"][model] += 1
                        session_record["models"].add(model)
                    usage = safe_get(rec, "message", "usage") or {}
                    for src, dst in [
                        ("input_tokens", "input_tokens"),
                        ("output_tokens", "output_tokens"),
                        ("cache_creation_input_tokens", "cache_create_tokens"),
                        ("cache_read_input_tokens", "cache_read_tokens"),
                    ]:
                        v = usage.get(src) or 0
                        if isinstance(v, (int, float)):
                            stats["totals"][dst] += v
                            if dst in ("input_tokens", "output_tokens"):
                                session_record["tokens"] += v
                    msg_content = safe_get(rec, "message", "content")
                    if isinstance(msg_content, list):
                        for blk in msg_content:
                            if not isinstance(blk, dict):
                                continue
                            if blk.get("type") == "tool_use":
                                tname = blk.get("name") or "unknown"
                                tid = blk.get("id")
                                if tid:
                                    tool_use_to_name[tid] = tname
                                stats["tools"][tname]["calls"] += 1
                                stats["totals"]["tool_calls"] += 1
                                session_record["tool_calls"] += 1
                                session_record["top_tools"][tname] += 1
                                if tname.startswith("mcp__"):
                                    stats["mcp"][mcp_server_from_tool(tname)]["calls"] += 1
                                if tname == "Skill":
                                    sk_raw = (blk.get("input") or {}).get("skill")
                                    if sk_raw:
                                        sk = normalize_skill_name(sk_raw)
                                        stats["skills"][sk]["calls"] += 1
                                        stats["skills"][sk]["via_tool"] = stats["skills"][sk].get("via_tool", 0) + 1
                                        prev = stats["skills"][sk]["last_used"]
                                        cur = mtime.isoformat(timespec="seconds")
                                        if prev is None or cur > prev:
                                            stats["skills"][sk]["last_used"] = cur
                                if tname == "Agent":
                                    sub = (blk.get("input") or {}).get("subagent_type") or "general-purpose"
                                    stats["agents"][sub] += 1
                elif rtype == "system":
                    sub = rec.get("subtype")
                    if sub == "stop_hook_summary":
                        for hi in rec.get("hookInfos") or []:
                            cmd = hi.get("command", "unknown")
                            hkey = shorten_hook(cmd)
                            stats["hooks"][hkey]["fires"] += 1
                            stats["hooks"][hkey]["events"]["Stop"] += 1
                            if rec.get("preventedContinuation"):
                                stats["hooks"][hkey]["prevented"] += 1
                        if rec.get("hookErrors"):
                            for hi in rec.get("hookInfos") or []:
                                hkey = shorten_hook(hi.get("command", "unknown"))
                                stats["hooks"][hkey]["errors"] += 1
                elif rtype == "attachment":
                    att = rec.get("attachment") or {}
                    if att.get("type") == "hook_success":
                        cmd = att.get("command", att.get("hookName", "unknown"))
                        hkey = shorten_hook(cmd)
                        stats["hooks"][hkey]["fires"] += 1
                        ev = att.get("hookEvent") or "unknown"
                        stats["hooks"][hkey]["events"][ev] += 1
                        if att.get("exitCode") and att["exitCode"] != 0:
                            stats["hooks"][hkey]["errors"] += 1
                elif rtype == "permission-mode":
                    mode = rec.get("permissionMode") or "default"
                    stats["permission_modes"][mode] += 1
                    permission_switches += 1
            session_record["models"] = sorted(session_record["models"])
            session_record["top_tools"] = dict(session_record["top_tools"].most_common(5))
            stats["sessions"].append(session_record)
            stats["permission_switches_per_session"].append({
                "session": session_id, "switches": permission_switches,
            })
            if not is_subagent:
                stats["totals"]["sessions"] += 1
                stats["projects"][project_dir]["sessions"] += 1
                stats["projects"][project_dir]["tokens"] += session_record["tokens"]
                stats["projects"][project_dir]["tool_calls"] += session_record["tool_calls"]
            else:
                stats["totals"]["subagent_sessions"] += 1
            if stats["first_seen"] is None or mtime < dt.datetime.fromisoformat(stats["first_seen"]):
                stats["first_seen"] = mtime.isoformat(timespec="seconds")
            if stats["last_seen"] is None or mtime > dt.datetime.fromisoformat(stats["last_seen"]):
                stats["last_seen"] = mtime.isoformat(timespec="seconds")

    stats["totals"]["projects"] = len(project_paths_seen)
    stats["context_bloat"].sort(key=lambda x: x["bytes"], reverse=True)
    stats["context_bloat"] = stats["context_bloat"][:30]
    stats["sessions"].sort(key=lambda s: s["modified"], reverse=True)
    return stats


BUILTIN_SLASH_COMMANDS = {
    "clear", "config", "login", "logout", "model", "memory", "usage",
    "doctor", "mcp", "hooks", "skills", "plugin", "reload-plugins",
    "effort", "fast", "help", "exit", "compact", "review", "init",
    "release-notes", "status", "cost", "bug", "feedback", "vim",
    "permissions", "agents", "ide", "pr_comments", "pr-comments",
    "add-dir", "remove-dir", "resume", "shortcuts", "terminal-setup",
    "theme",
}


def normalize_skill_name(name: str) -> str:
    """Strip plugin namespace prefix: 'foo:bar' -> 'bar'."""
    if ":" in name:
        return name.split(":", 1)[1]
    return name


def shorten_hook(cmd: str) -> str:
    cmd = cmd.replace("${CLAUDE_PLUGIN_ROOT}", "$ROOT")
    if len(cmd) > 80:
        return "..." + cmd[-77:]
    return cmd


def mcp_server_from_tool(tool_name: str) -> str:
    parts = tool_name.split("__")
    if len(parts) >= 2:
        return parts[1]
    return tool_name


def fmt_int(n) -> str:
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return "0"


def fmt_bytes(n) -> str:
    n = float(n or 0)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def latest_compare_file(current: Path) -> Path | None:
    candidates = sorted(REPORTS_DIR.glob("usage-*.json"), reverse=True)
    for c in candidates:
        if c.resolve() != current.resolve():
            return c
    return None


def diff_stats(curr: dict, prev: dict) -> dict:
    """Compute deltas vs previous run for headline numbers."""
    d = {}
    for k in ("sessions", "tool_calls", "input_tokens", "output_tokens",
              "cache_create_tokens", "cache_read_tokens", "user_msgs"):
        d[k] = (curr["totals"].get(k, 0) or 0) - (prev["totals"].get(k, 0) or 0)
    cur_tools = {t: v["calls"] for t, v in curr.get("tools", {}).items()}
    prev_tools = {t: v.get("calls", 0) for t, v in prev.get("tools", {}).items()}
    tool_deltas = []
    for t in set(cur_tools) | set(prev_tools):
        delta = cur_tools.get(t, 0) - prev_tools.get(t, 0)
        if delta != 0:
            tool_deltas.append({"tool": t, "delta": delta,
                                "now": cur_tools.get(t, 0), "before": prev_tools.get(t, 0)})
    tool_deltas.sort(key=lambda x: abs(x["delta"]), reverse=True)
    d["tools_top"] = tool_deltas[:15]
    return d


def build_skill_table(stats: dict, skills: dict) -> list[dict]:
    """Combine on-disk skill catalog with usage from transcripts."""
    rows = []
    used = stats.get("skills", {})
    thirty_days_ago = (dt.datetime.now() - dt.timedelta(days=30)).isoformat(timespec="seconds")
    for name, meta in skills.items():
        usage = used.get(name, {})
        last = usage.get("last_used")
        recent = bool(last and last >= thirty_days_ago)
        rows.append({
            "name": name,
            "plugin": meta.get("plugin") or "(personal)",
            "calls_all_time": usage.get("calls", 0),
            "via_slash": usage.get("via_slash", 0),
            "via_tool": usage.get("via_tool", 0),
            "last_used": last,
            "recent_30d": recent,
            "bytes": meta.get("bytes", 0),
            "description": meta.get("description", "")[:200],
        })
    for name, usage in used.items():
        if name not in skills:
            rows.append({
                "name": name,
                "plugin": "(unknown)",
                "calls_all_time": usage.get("calls", 0),
                "via_slash": usage.get("via_slash", 0),
                "via_tool": usage.get("via_tool", 0),
                "last_used": usage.get("last_used"),
                "recent_30d": bool(usage.get("last_used") and usage["last_used"] >= thirty_days_ago),
                "bytes": 0,
                "description": "(skill no longer on disk)",
            })
    rows.sort(key=lambda r: r["calls_all_time"], reverse=True)
    return rows


def build_plugin_table(stats: dict, skills: dict, plugins: dict) -> list[dict]:
    by_plugin = defaultdict(lambda: {"skills_total": 0, "skills_used": 0,
                                     "calls": 0, "bytes": 0, "skills": []})
    used = stats.get("skills", {})
    for name, meta in skills.items():
        plugin = meta.get("plugin") or "(personal)"
        info = by_plugin[plugin]
        info["skills_total"] += 1
        info["bytes"] += meta.get("bytes", 0)
        calls = used.get(name, {}).get("calls", 0)
        info["calls"] += calls
        if calls > 0:
            info["skills_used"] += 1
        info["skills"].append({"name": name, "calls": calls})
    rows = []
    for plugin, info in by_plugin.items():
        info["skills"].sort(key=lambda s: s["calls"], reverse=True)
        rows.append({"plugin": plugin, **info})
    rows.sort(key=lambda r: r["calls"], reverse=True)
    return rows


def build_unused_table(stats: dict, skills: dict, settings: dict) -> dict:
    used = stats.get("skills", {})
    unused_skills = []
    for name, meta in skills.items():
        if used.get(name, {}).get("calls", 0) == 0:
            unused_skills.append({
                "name": name, "plugin": meta.get("plugin") or "(personal)",
                "bytes": meta.get("bytes", 0),
            })
    unused_skills.sort(key=lambda s: s["bytes"], reverse=True)

    used_mcp = set(stats.get("mcp", {}).keys())
    unused_mcp = []
    for srv in (settings.get("mcp_servers") or {}):
        if srv not in used_mcp:
            unused_mcp.append(srv)

    fired_hook_keys = set(stats.get("hooks", {}).keys())
    unused_hooks = []
    for event, items in (settings.get("hooks") or {}).items():
        for item in items:
            if isinstance(item, dict):
                cmds = []
                for h in item.get("hooks") or []:
                    if isinstance(h, dict) and h.get("command"):
                        cmds.append(h["command"])
                for cmd in cmds:
                    sk = shorten_hook(cmd)
                    if sk not in fired_hook_keys:
                        unused_hooks.append({"event": event, "hook": sk})

    return {"skills": unused_skills, "mcp": unused_mcp, "hooks": unused_hooks}


def render_html(stats: dict, skills: dict, plugins: dict, settings: dict,
                compare: dict | None, prev_path: Path | None) -> str:
    skill_rows = build_skill_table(stats, skills)
    plugin_rows = build_plugin_table(stats, skills, plugins)
    unused = build_unused_table(stats, skills, settings)
    chart_js = ""
    if CHART_JS_PATH.exists():
        chart_js = CHART_JS_PATH.read_text(encoding="utf-8", errors="replace")

    payload = {
        "tools": sorted(
            [{"name": k, "calls": v["calls"], "result_bytes": v["result_bytes"]}
             for k, v in stats["tools"].items()],
            key=lambda x: x["calls"], reverse=True),
        "skills": skill_rows,
        "plugins": plugin_rows,
        "mcp": sorted(
            [{"server": k, **v} for k, v in stats["mcp"].items()],
            key=lambda x: x["calls"], reverse=True),
        "projects": sorted(
            [{"dir": k, **v} for k, v in stats["projects"].items()],
            key=lambda x: x["tokens"], reverse=True),
        "sessions": stats["sessions"],
        "context_bloat": stats["context_bloat"],
        "hooks": sorted(
            [{"key": k, "fires": v["fires"], "errors": v["errors"],
              "prevented": v["prevented"], "events": dict(v["events"])}
             for k, v in stats["hooks"].items()],
            key=lambda x: x["fires"], reverse=True),
        "permission_modes": dict(stats["permission_modes"]),
        "permission_switches": stats["permission_switches_per_session"],
        "agents": sorted(stats["agents"].items(), key=lambda x: -x[1]),
        "slash_commands": sorted(stats["slash_commands"].items(), key=lambda x: -x[1]),
        "models": dict(stats["models"]),
        "totals": stats["totals"],
        "first_seen": stats["first_seen"],
        "last_seen": stats["last_seen"],
        "generated_at": stats["generated_at"],
        "since": stats["since"],
        "unused": unused,
        "compare": compare,
        "compare_source": str(prev_path) if prev_path else None,
    }

    payload_json = json.dumps(payload, default=str)
    template = HTML_TEMPLATE
    return (template
            .replace("__CHART_JS__", chart_js)
            .replace("__PAYLOAD_JSON__", payload_json))


def open_in_browser(path: Path) -> None:
    try:
        if platform.system() == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        elif platform.system() == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except OSError:
        pass


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Claude Code usage report")
    parser.add_argument("--since", help="ISO date, e.g. 2026-04-01")
    parser.add_argument("--no-open", action="store_true", help="Skip auto-opening browser")
    parser.add_argument("--no-compare", action="store_true", help="Skip diff vs previous run")
    parser.add_argument("--output", help="Override output path")
    args = parser.parse_args(argv)

    since = None
    if args.since:
        try:
            since = dt.datetime.fromisoformat(args.since)
        except ValueError:
            print(f"Invalid --since date: {args.since}", file=sys.stderr)
            return 2

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/4] Loading skills, plugins, settings...", file=sys.stderr)
    skills = load_skills()
    plugins = load_plugins()
    settings = load_settings()

    print(f"[2/4] Scanning transcripts in {PROJECTS_DIR}...", file=sys.stderr)
    stats = analyze(since)

    compare = None
    prev_path = None
    if not args.no_compare:
        prev_path = latest_compare_file(REPORTS_DIR / "_never_matches.json")
        if prev_path:
            try:
                prev = json.loads(prev_path.read_text())
                compare = diff_stats(stats, prev)
                print(f"[3/4] Compared against {prev_path.name}", file=sys.stderr)
            except (json.JSONDecodeError, OSError):
                pass

    timestamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    if args.output:
        out_html = Path(args.output).expanduser()
    else:
        out_html = REPORTS_DIR / f"usage-{timestamp}.html"
    out_json = out_html.with_suffix(".json")

    print(f"[4/4] Rendering {out_html.name}...", file=sys.stderr)
    html = render_html(stats, skills, plugins, settings, compare, prev_path)
    out_html.write_text(html, encoding="utf-8")
    out_json.write_text(json.dumps({
        "totals": stats["totals"],
        "tools": {k: v for k, v in stats["tools"].items()},
        "skills": {k: v for k, v in stats["skills"].items()},
        "mcp": {k: v for k, v in stats["mcp"].items()},
        "first_seen": stats["first_seen"],
        "last_seen": stats["last_seen"],
        "generated_at": stats["generated_at"],
    }, default=str), encoding="utf-8")

    print(f"\nReport: {out_html}", file=sys.stderr)
    print(f"Data:   {out_json}", file=sys.stderr)

    if not args.no_open:
        open_in_browser(out_html)
    return 0


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Claude Code usage report</title>
<style>
  :root { --bg:#0e1117; --panel:#161b22; --fg:#e6edf3; --muted:#8b949e;
          --accent:#58a6ff; --good:#3fb950; --warn:#d29922; --bad:#f85149;
          --border:#30363d; }
  * { box-sizing: border-box; }
  body { margin:0; font:14px/1.5 -apple-system,BlinkMacSystemFont,system-ui,sans-serif;
         background:var(--bg); color:var(--fg); }
  header { padding:20px 30px; border-bottom:1px solid var(--border); }
  h1 { margin:0 0 4px; font-size:22px; }
  .meta { color:var(--muted); font-size:12px; }
  nav { display:flex; flex-wrap:wrap; gap:4px; padding:0 20px;
        border-bottom:1px solid var(--border); background:var(--panel); }
  nav button { background:none; color:var(--muted); border:0; padding:12px 14px;
               font:inherit; cursor:pointer; border-bottom:2px solid transparent; }
  nav button.active { color:var(--accent); border-bottom-color:var(--accent); }
  nav button:hover { color:var(--fg); }
  main { padding:24px 30px 60px; max-width:1400px; }
  section { display:none; }
  section.active { display:block; }
  h2 { margin:0 0 16px; font-size:18px; font-weight:600; }
  .grid { display:grid; gap:16px; grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
          margin-bottom:24px; }
  .card { background:var(--panel); border:1px solid var(--border); border-radius:6px;
          padding:14px 16px; }
  .card .label { color:var(--muted); font-size:11px; text-transform:uppercase;
                 letter-spacing:0.5px; }
  .card .value { font-size:24px; font-weight:600; margin-top:4px; }
  .card .delta { font-size:12px; margin-top:4px; }
  .delta.up { color:var(--good); } .delta.down { color:var(--bad); }
  table { width:100%; border-collapse:collapse; background:var(--panel);
          border:1px solid var(--border); border-radius:6px; overflow:hidden; }
  th, td { padding:8px 12px; text-align:left; border-bottom:1px solid var(--border);
           font-size:13px; vertical-align:top; }
  th { background:#0d1117; color:var(--muted); text-transform:uppercase;
       font-size:10px; letter-spacing:0.5px; cursor:pointer; user-select:none; }
  th:hover { color:var(--fg); }
  tr:last-child td { border-bottom:0; }
  tr:hover td { background:#1c2128; }
  td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; }
  .bar { height:6px; background:var(--accent); border-radius:3px; }
  .pill { display:inline-block; padding:2px 8px; border-radius:10px;
          font-size:11px; background:#21262d; color:var(--muted); }
  .pill.good { color:var(--good); background:#0d2818; }
  .pill.bad { color:var(--bad); background:#2d1416; }
  .pill.warn { color:var(--warn); background:#2c2412; }
  .chart-wrap { background:var(--panel); border:1px solid var(--border);
                border-radius:6px; padding:16px; margin-bottom:24px;
                position:relative; height:340px; }
  details { background:var(--panel); border:1px solid var(--border);
            border-radius:6px; padding:8px 14px; margin-bottom:8px; }
  summary { cursor:pointer; font-weight:500; }
  code { background:#21262d; padding:1px 5px; border-radius:3px; font-size:12px; }
  .small { color:var(--muted); font-size:12px; }
  .compare-banner { background:#1c2128; padding:10px 16px; border-radius:6px;
                    border-left:3px solid var(--accent); margin-bottom:16px;
                    color:var(--muted); font-size:13px; }
</style></head>
<body>
<header>
  <h1>Claude Code usage report</h1>
  <div class="meta" id="header-meta"></div>
</header>
<nav id="tabs"></nav>
<main id="main"></main>

<script>__CHART_JS__</script>
<script id="payload" type="application/json">__PAYLOAD_JSON__</script>
<script>
(function(){
  const D = JSON.parse(document.getElementById('payload').textContent);
  const fmt = n => (n==null?'-':Number(n).toLocaleString());
  const fmtBytes = n => {
    if (!n) return '0 B';
    const u=['B','KB','MB','GB']; let i=0; let v=n;
    while (v>=1024 && i<u.length-1) { v/=1024; i++; }
    return v.toFixed(1)+' '+u[i];
  };
  const tabs = [
    ['overview','Overview'], ['tools','Tools'], ['skills','Skills'],
    ['plugins','Plugins'], ['mcp','MCP servers'], ['agents','Subagents'],
    ['projects','Projects'], ['sessions','Sessions'],
    ['bloat','Context bloat'], ['hooks','Hooks'],
    ['perms','Permissions'], ['commands','Slash commands'],
    ['unused','Unused & underused']
  ];
  const nav = document.getElementById('tabs');
  const main = document.getElementById('main');
  tabs.forEach(([id,label],i) => {
    const b = document.createElement('button');
    b.textContent = label; b.dataset.tab = id;
    b.onclick = () => activate(id);
    if (i===0) b.classList.add('active');
    nav.appendChild(b);
    const s = document.createElement('section');
    s.id = 'sec-'+id; if (i===0) s.classList.add('active');
    main.appendChild(s);
  });
  function activate(id) {
    document.querySelectorAll('nav button').forEach(b =>
      b.classList.toggle('active', b.dataset.tab===id));
    document.querySelectorAll('main section').forEach(s =>
      s.classList.toggle('active', s.id==='sec-'+id));
  }

  const meta = document.getElementById('header-meta');
  meta.textContent = 'Generated ' + D.generated_at + ' | ' +
    'data range: ' + (D.first_seen||'?') + ' to ' + (D.last_seen||'?') +
    (D.since ? ' | --since '+D.since : '');

  // OVERVIEW
  const ov = document.getElementById('sec-overview');
  const t = D.totals;
  let cards = [
    ['Sessions', fmt(t.sessions)],
    ['Subagent runs', fmt(t.subagent_sessions)],
    ['Projects', fmt(t.projects)],
    ['Assistant turns', fmt(t.assistant_turns)],
    ['Tool calls', fmt(t.tool_calls)],
    ['User messages', fmt(t.user_msgs)],
    ['Input tokens', fmt(t.input_tokens)],
    ['Output tokens', fmt(t.output_tokens)],
    ['Cache create', fmt(t.cache_create_tokens)],
    ['Cache read', fmt(t.cache_read_tokens)],
  ];
  let html = '';
  if (D.compare) {
    html += '<div class="compare-banner">Compared against previous run: <code>' +
            (D.compare_source||'').split('/').pop() + '</code></div>';
  }
  html += '<div class="grid">' + cards.map(([l,v],i) => {
    let delta = '';
    if (D.compare) {
      const keys = ['sessions','subagent_sessions','projects','assistant_turns',
                    'tool_calls','user_msgs','input_tokens','output_tokens',
                    'cache_create_tokens','cache_read_tokens'];
      const dval = D.compare[keys[i]];
      if (dval !== undefined && dval !== 0) {
        const cls = dval>0 ? 'up' : 'down';
        delta = '<div class="delta '+cls+'">' + (dval>0?'+':'') + fmt(dval) + ' since last run</div>';
      }
    }
    return '<div class="card"><div class="label">'+l+'</div><div class="value">'+v+'</div>'+delta+'</div>';
  }).join('') + '</div>';
  html += '<h2>Models used</h2><table><tr><th>Model</th><th class="num">Turns</th></tr>' +
    Object.entries(D.models).sort((a,b)=>b[1]-a[1]).map(([m,c]) =>
      '<tr><td><code>'+m+'</code></td><td class="num">'+fmt(c)+'</td></tr>').join('') +
    '</table>';
  ov.innerHTML = html;

  // TOOLS
  renderTable('tools', D.tools, [
    {h:'Tool', f: r => '<code>'+r.name+'</code>'},
    {h:'Calls', f: r => fmt(r.calls), num:true},
    {h:'Total result bytes', f: r => fmtBytes(r.result_bytes), num:true},
    {h:'', f: r => bar(r.calls, Math.max(...D.tools.map(x=>x.calls)))},
  ], 'Tool usage');
  addChart('tools', 'Tool calls (top 15)',
    D.tools.slice(0,15).map(r=>r.name),
    D.tools.slice(0,15).map(r=>r.calls));

  // SKILLS
  renderTable('skills', D.skills, [
    {h:'Skill', f: r => r.name},
    {h:'Plugin', f: r => '<span class="pill">'+r.plugin+'</span>'},
    {h:'Calls (all-time)', f: r => fmt(r.calls_all_time), num:true},
    {h:'Triggered via', f: r => {
      const parts = [];
      if (r.via_slash) parts.push('<code>/cmd</code>:'+r.via_slash);
      if (r.via_tool) parts.push('<code>Skill</code>:'+r.via_tool);
      return parts.length ? parts.join(' ') : '-';
    }},
    {h:'Recent (30d)?', f: r => r.recent_30d ?
      '<span class="pill good">yes</span>' :
      (r.calls_all_time>0 ? '<span class="pill warn">stale</span>'
                          : '<span class="pill bad">never</span>')},
    {h:'Last used', f: r => r.last_used || '-'},
    {h:'SKILL.md', f: r => fmtBytes(r.bytes), num:true},
    {h:'Description', f: r => '<span class="small">'+escapeHtml(r.description||'')+'</span>'},
  ], 'Skills (sorted by call count)');

  // PLUGINS
  renderTable('plugins', D.plugins, [
    {h:'Plugin', f: r => r.plugin},
    {h:'Skills (used / total)', f: r => r.skills_used+' / '+r.skills_total},
    {h:'Total calls', f: r => fmt(r.calls), num:true},
    {h:'Total SKILL.md bytes', f: r => fmtBytes(r.bytes), num:true},
    {h:'Components', f: r => r.skills.map(s =>
      '<code>'+s.name+'</code> ('+s.calls+')').join(', ')},
  ], 'Plugins (per-component breakdown)');

  // MCP
  renderTable('mcp', D.mcp, [
    {h:'Server', f: r => '<code>'+r.server+'</code>'},
    {h:'Tool calls', f: r => fmt(r.calls), num:true},
    {h:'Result bytes', f: r => fmtBytes(r.result_bytes), num:true},
    {h:'Biggest single result', f: r => fmtBytes(r.biggest), num:true},
  ], 'MCP servers');

  // AGENTS
  document.getElementById('sec-agents').innerHTML =
    '<h2>Subagent invocations</h2>' +
    (D.agents.length ?
      '<table><tr><th>subagent_type</th><th class="num">Calls</th></tr>' +
      D.agents.map(([n,c]) => '<tr><td><code>'+n+'</code></td><td class="num">'+fmt(c)+'</td></tr>').join('') +
      '</table>' :
      '<p class="small">No subagent invocations recorded.</p>');

  // PROJECTS
  renderTable('projects', D.projects, [
    {h:'Project', f: r => '<code>'+r.path+'</code>'},
    {h:'Sessions', f: r => fmt(r.sessions), num:true},
    {h:'Tool calls', f: r => fmt(r.tool_calls), num:true},
    {h:'Tokens (in+out)', f: r => fmt(r.tokens), num:true},
  ], 'Projects');

  // SESSIONS
  renderTable('sessions', D.sessions.slice(0,200), [
    {h:'Modified', f: r => r.modified},
    {h:'Project', f: r => '<code>'+(r.project||'').split('/').pop()+'</code>'},
    {h:'Session', f: r => '<span class="small">'+r.session_id.slice(0,8)+'</span>'},
    {h:'Type', f: r => r.is_subagent ? '<span class="pill">subagent</span>' : ''},
    {h:'User msgs', f: r => fmt(r.user_msgs), num:true},
    {h:'Tool calls', f: r => fmt(r.tool_calls), num:true},
    {h:'Tokens', f: r => fmt(r.tokens), num:true},
    {h:'Top tools', f: r => Object.entries(r.top_tools||{}).map(
      ([k,v]) => '<code>'+k+'</code>:'+v).join(' ')},
  ], 'Sessions (most recent 200)');

  // BLOAT
  renderTable('bloat', D.context_bloat, [
    {h:'Tool', f: r => '<code>'+r.tool+'</code>'},
    {h:'Bytes returned', f: r => fmtBytes(r.bytes), num:true},
    {h:'Project', f: r => '<span class="small">'+r.project+'</span>'},
    {h:'Session', f: r => '<span class="small">'+r.session.slice(0,8)+'</span>'},
  ], 'Top 30 fattest tool results (potential context window bloat)');

  // HOOKS
  renderTable('hooks', D.hooks, [
    {h:'Hook command', f: r => '<code>'+escapeHtml(r.key)+'</code>'},
    {h:'Fires', f: r => fmt(r.fires), num:true},
    {h:'Errors', f: r => r.errors ? '<span class="pill bad">'+r.errors+'</span>' : '0', num:true},
    {h:'Prevented continuation', f: r => r.prevented ?
      '<span class="pill warn">'+r.prevented+'</span>' : '0', num:true},
    {h:'Events', f: r => Object.entries(r.events).map(
      ([k,v]) => '<code>'+k+'</code>:'+v).join(' ')},
  ], 'Hook executions');

  // PERMISSIONS
  let permsHtml = '<h2>Permission mode events</h2><table><tr><th>Mode</th><th class="num">Count</th></tr>' +
    Object.entries(D.permission_modes||{}).sort((a,b)=>b[1]-a[1]).map(([m,c]) =>
      '<tr><td><code>'+m+'</code></td><td class="num">'+fmt(c)+'</td></tr>').join('') +
    '</table>' +
    '<h2 style="margin-top:24px">Permission switches per session (top 30 most active)</h2>' +
    '<table><tr><th>Session</th><th class="num">Switches</th></tr>' +
    (D.permission_switches||[]).sort((a,b)=>b.switches-a.switches).slice(0,30).map(p =>
      '<tr><td><span class="small">'+p.session.slice(0,12)+'</span></td><td class="num">'+
      fmt(p.switches)+'</td></tr>').join('') + '</table>';
  document.getElementById('sec-perms').innerHTML = permsHtml;

  // COMMANDS
  document.getElementById('sec-commands').innerHTML =
    '<h2>Slash command usage</h2>' +
    (D.slash_commands.length ?
      '<table><tr><th>Command</th><th class="num">Invocations</th></tr>' +
      D.slash_commands.map(([n,c]) => '<tr><td><code>/'+escapeHtml(n)+'</code></td><td class="num">'+fmt(c)+'</td></tr>').join('') +
      '</table>' :
      '<p class="small">No slash commands detected in transcripts.</p>');

  // UNUSED
  let uh = '<h2>Skills with zero invocations (sorted by SKILL.md size — biggest waste first)</h2>';
  uh += D.unused.skills.length ?
    '<table><tr><th>Skill</th><th>Plugin</th><th class="num">SKILL.md</th></tr>' +
    D.unused.skills.map(s =>
      '<tr><td>'+s.name+'</td><td><span class="pill">'+s.plugin+'</span></td><td class="num">'+
      fmtBytes(s.bytes)+'</td></tr>').join('') + '</table>' :
    '<p class="small">All installed skills have at least one recorded invocation.</p>';
  uh += '<h2 style="margin-top:24px">MCP servers configured but never invoked</h2>';
  uh += D.unused.mcp.length ?
    '<ul>' + D.unused.mcp.map(s => '<li><code>'+s+'</code></li>').join('') + '</ul>' :
    '<p class="small">All configured MCP servers have been used.</p>';
  uh += '<h2 style="margin-top:24px">Hooks configured but never observed firing</h2>';
  uh += D.unused.hooks.length ?
    '<table><tr><th>Event</th><th>Command</th></tr>' +
    D.unused.hooks.map(h =>
      '<tr><td><code>'+h.event+'</code></td><td><code>'+escapeHtml(h.hook)+'</code></td></tr>').join('') +
    '</table>' :
    '<p class="small">All configured hooks fired at least once in scanned transcripts.</p>';
  document.getElementById('sec-unused').innerHTML = uh;

  // helpers
  function escapeHtml(s) {
    return String(s||'').replace(/[&<>"']/g, c => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function bar(v, max) {
    if (!max) return '';
    const w = Math.round(100 * v / max);
    return '<div class="bar" style="width:'+w+'%"></div>';
  }
  function renderTable(id, rows, cols, title) {
    const sec = document.getElementById('sec-'+id);
    if (!rows || !rows.length) {
      sec.innerHTML = '<h2>'+title+'</h2><p class="small">No data.</p>';
      return;
    }
    let h = '<h2>'+title+'</h2><table><thead><tr>' +
      cols.map(c => '<th'+(c.num?' class="num"':'')+'>'+c.h+'</th>').join('') +
      '</tr></thead><tbody>';
    rows.forEach(r => {
      h += '<tr>' + cols.map(c =>
        '<td'+(c.num?' class="num"':'')+'>'+c.f(r)+'</td>').join('') + '</tr>';
    });
    h += '</tbody></table>';
    sec.innerHTML = h;
  }
  function addChart(secId, title, labels, values) {
    if (typeof Chart === 'undefined') return;
    const sec = document.getElementById('sec-'+secId);
    const wrap = document.createElement('div');
    wrap.className = 'chart-wrap';
    wrap.innerHTML = '<canvas></canvas>';
    sec.insertBefore(wrap, sec.firstChild.nextSibling);
    const ctx = wrap.querySelector('canvas').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets: [{ label: title, data: values, backgroundColor:'#58a6ff'}] },
      options: { responsive:true, maintainAspectRatio:false,
                 plugins:{ legend:{ labels:{ color:'#e6edf3'}}, title:{ display:true, text:title, color:'#e6edf3'}},
                 scales: { x:{ ticks:{ color:'#8b949e'}, grid:{ color:'#21262d'}},
                           y:{ ticks:{ color:'#8b949e'}, grid:{ color:'#21262d'}}}}
    });
  }
})();
</script>
</body></html>"""


if __name__ == "__main__":
    sys.exit(main())



