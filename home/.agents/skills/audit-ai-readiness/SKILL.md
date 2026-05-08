---
name: audit-ai-readiness
description: Audit a repo against the AI-readiness rubric and produce a scored checklist with prioritized gaps. Use when user runs /audit-ai-readiness or asks to check if a repo is ready for AI to operate autonomously. Audit-only — does not modify the repo.
---

# audit-ai-readiness

Score the current repo against a 12-item AI-readiness checklist. Output a markdown scorecard with ✅/❌ per item, file paths checked, score (X/12), and top 3 gaps ordered by impact. Offer to save the report to `.ai-readiness-report.md` at the end.

**This skill is audit-only. It must NOT create, edit, or modify any files in the audited repo except optionally writing the final report when the user confirms.**

## Workflow

### Step 1 — Confirm scope

State what you're about to do: audit the current working directory against the AI-readiness rubric. One sentence. Then run the checks.

### Step 2 — Run all 12 checks

For each item, determine ✅ (present & adequate), ⚠️ (partial / weak), or ❌ (missing). Record the file path(s) inspected and a one-line note. Prefer Read/Grep/Glob over Bash.

**Do not guess.** If uncertain, mark ⚠️ and note the ambiguity.

#### The 12 checks

| # | Check | How to verify |
|---|-------|--------------|
| 1 | README with business section | `README.md` exists and top has product purpose / users / what it does (not just install steps). |
| 2 | Domain glossary | `GLOSSARY.md` exists, OR README has a `## Glossary` / `## Domain` section with ≥3 terms defined. |
| 3 | Root CLAUDE.md | `CLAUDE.md` at repo root. Should mention stack, key commands, conventions. |
| 4 | Command surface (justfile / Makefile / scripts) | `justfile`, `Justfile`, `Makefile`, OR `package.json` `scripts` covering dev/build/test/lint/format. |
| 5 | Single `ci` command | `just ci` target exists, OR `make ci`, OR `npm run ci` / `pnpm ci`. The command must chain format + lint + typecheck + test (at minimum). |
| 6 | CI config mirrors local `ci` | `.github/workflows/*.yml` (or equivalent) invokes the same `ci` command from check 5, not a bespoke pipeline. |
| 7 | Tests exist | Test files present (`**/*.test.*`, `**/*_test.*`, `**/test_*.py`, `tests/`, `__tests__/`). Note count and whether any look like integration tests. |
| 8 | Format + lint + typecheck configured | Formatter config (`.prettierrc`, `ruff.toml`, `rustfmt.toml`, etc.), linter config, type-checker config (`tsconfig.json` with `strict`, `mypy.ini`, etc.). |
| 9 | Secret scanning | `.pre-commit-config.yaml` with gitleaks/trufflehog, OR `.gitleaks.toml`, OR CI step running a secret scanner. |
| 10 | Branch protection on main | Run `gh api repos/:owner/:repo/branches/main/protection` (ok to fail silently if `gh` not authed — mark ⚠️ with reason). |
| 11 | PR template | `.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE.md` exists. |
| 12 | Dep-update automation | `.github/dependabot.yml`, `renovate.json`, OR a scheduled workflow / skill / cron that updates deps. |

#### Verification details

- For each check, use `Glob` to find candidate files, then `Read` or `Grep` to verify content.
- Check 1 (README): read the first ~60 lines. If it jumps straight to installation without explaining what the product is, mark ⚠️.
- Check 3 (CLAUDE.md): read it. If it's a stub (< 20 lines) or generic template, mark ⚠️.
- Check 5 (`ci` command): actually read the justfile/Makefile/package.json to confirm the chain, don't assume by target name.
- Check 8: TypeScript strict mode = `tsconfig.json` has `"strict": true`. Python strict = `mypy.ini` / `pyproject.toml` with `strict = true`. Non-strict configs → ⚠️.
- Check 10 (branch protection): use `gh` via `Bash`. If `gh` errors or repo has no remote, mark ⚠️ and note "cannot verify — `gh` not authed / no remote".

### Step 3 — Print scorecard

Output format (print exactly this shape):

```markdown
# AI-Readiness Audit — <repo-name>

**Score: X/12**  (✅ <green-count>  ⚠️ <yellow-count>  ❌ <red-count>)

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | README with business section | ✅ | `README.md:1-40` — explains product purpose |
| 2 | Domain glossary | ❌ | no `GLOSSARY.md`; README has no Domain section |
| ... | ... | ... | ... |

## Top 3 gaps (impact-first)

1. **<gap>** — <why it matters for AI reliability, one sentence>
2. **<gap>** — ...
3. **<gap>** — ...

## Notes
<any ambiguities, unverifiable checks, or caveats>
```

**Priority order for gaps** (use this when ranking the top 3):

1. Root CLAUDE.md
2. Single `ci` command + CI mirrors it
3. Tests exist (integration on user journeys)
4. Format + lint + typecheck configured
5. Branch protection on main
6. Secret scanning
7. README business section
8. Domain glossary
9. PR template
10. Dep-update automation
11. Command surface (justfile / Makefile)

Pick the three highest-priority items that are ❌ or ⚠️. If fewer than three gaps, list what's there.

### Step 4 — Offer to save report

After printing, ask: **"Save this report to `.ai-readiness-report.md` in this repo? (y/n)"**

If yes → write the exact scorecard markdown to `.ai-readiness-report.md` at repo root. Nothing else.
If no → stop.

## Hard rules

- Audit-only. Never create, edit, or modify files in the repo except the final report when the user confirms.
- Never run `just`, `make`, `npm`, or any build/test command. Only inspect config files.
- If `gh` calls fail, report the ambiguity — do not skip check 10 silently.
- Do not recommend fixes beyond the top-3 gaps list. This skill audits; the user decides what to fix and when.
