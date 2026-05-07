# Repo AI-Readiness Rubric

A stack-agnostic checklist for making any codebase ready for AI to operate with **supervised autonomy** — AI runs tasks end-to-end (writes code, runs checks, opens PRs, updates deps) and a human reviews at the PR boundary.

Scope covers both **technical conventions** (how the code is shaped) and **business/domain context** (what the product means), because AI mistakes are usually intent mistakes, not syntax mistakes.

---

## TL;DR — What Every Repo Needs

1. **Context**: `README.md` (with a business section), `GLOSSARY.md`, root `CLAUDE.md`.
2. **One-command surface**: `justfile` with `just ci` running format + lint + typecheck + test + build + smoke — and CI invokes the same `just ci` (no drift).
3. **Feedback loop**: formatter, linter, type checker, tests (integration on core user journeys), build, smoke test.
4. **Dep updates**: AI-driven, on-demand + scheduled, gated on `just ci` green.
5. **Guardrails**: pre-commit hooks (including secret scanning), branch protection on `main`, PR template, CODEOWNERS, Conventional Commits, no `--no-verify` / `--force` to main.
6. **Skills alignment**: pre-PR checklist in CLAUDE.md (simplify → code review → security review).

---

## Priority Ordering

Two orderings are provided because they optimize for different goals. Impact-first maximizes AI reliability per unit of work done. Effort-first builds momentum and adoption. Most teams will want a blend — use impact-first as the strategic roadmap, and effort-first to pick "what do we do this afternoon."

---

### Ordering A — Impact-First (maximum AI-reliability per item added)

This order is about which items, if missing, most often cause AI to produce wrong or broken output. Start at the top.

| # | Item | Why this rank |
|---|------|--------------|
| 1 | **Root `CLAUDE.md`** — stack, commands, conventions, workflow rules | Without this, AI improvises every session. Single highest-leverage artifact. |
| 2 | **`just ci` (or equivalent single command) that mirrors CI** | Forces AI to verify before claiming done. Eliminates local-vs-CI drift. Turns 6 forgettable steps into 1. |
| 3 | **Type checker in strict mode** | Catches a huge class of AI-generated bugs without needing a single test. Fastest feedback loop. |
| 4 | **Integration tests on critical user journeys (5–10 flows)** | The regression safety net that actually catches real breakage. Better than unit + mocks for AI confidence. |
| 5 | **Linter with project conventions encoded as rules** | Converts unwritten team rules into machine-checkable ones. AI cannot merge a violation. |
| 6 | **Formatter (Prettier / ruff / gofmt)** | Removes style debates entirely. AI output looks like your code. |
| 7 | **Branch protection on `main` + no direct commits rule** | Safety net against destructive AI actions. GitHub refuses the push even if AI tries. |
| 8 | **Secret scanning pre-commit hook (gitleaks / trufflehog)** | AI can hallucinate credentials in tests/examples. This blocks them at commit time. |
| 9 | **`README.md` with business/product section** | Tells AI what the product *does*, not just how to run it. Frames every task correctly. |
| 10 | **`GLOSSARY.md` (domain terms)** | Stops AI conflating Customer/User, Order/Shipment, etc. Cheap, high-signal. |
| 11 | **Build step in `just ci`** | Catches broken imports and runtime wiring unit tests miss. |
| 12 | **Smoke test in `just ci`** | Boots the app and hits one real path. Catches env/config breakage. |
| 13 | **`.github/pull_request_template.md`** | Forces AI to fill in what/why/test plan → faster human review. |
| 14 | **AI-driven dep update workflow** (on-demand + scheduled, gated on `just ci`) | Unblocks dep hygiene from human bandwidth. Keeps stack current without regressions. |
| 15 | **Pre-commit hooks for format + lint + typecheck** | Defense-in-depth with `just ci`. Prevents broken intermediate commits. |
| 16 | **`.env.example` + `.gitignore`** | AI knows what to configure and what never to commit. |
| 17 | **Per-directory `CLAUDE.md`** for large repos | Only when root `CLAUDE.md` exceeds ~300 lines or rules are area-specific. |
| 18 | **`/docs/adr/` (Architecture Decision Records)** | Start when you catch yourself explaining "why X not Y" twice. Prevents AI re-litigating settled tradeoffs. |
| 19 | **`CODEOWNERS`** | Auto-assigns reviewers. High value on multi-person teams; documents ownership on solo repos. |
| 20 | **`/docs/runbooks/`** | Only for services with real users / on-call. Lets AI help during incidents. |
| 21 | **Characterization-tests-on-demand policy (legacy repos only)** | For monoliths without coverage: AI writes a pinning test *before* modifying a function. Scales with AI activity instead of demanding a big-bang test project. |

---

### Ordering B — Effort-First (quickest wins, lowest setup cost)

This order is about what you can add this afternoon with the least friction. Useful for kicking off adoption on an existing repo.

| # | Item | Effort |
|---|------|--------|
| 1 | **`.gitignore` + `.env.example`** | Minutes. Copy-paste from a template. |
| 2 | **`README.md` with business/product section** | ~30 min of writing. No tooling. |
| 3 | **`GLOSSARY.md`** | Start with 10 terms. Grow as needed. |
| 4 | **Root `CLAUDE.md`** | ~1 hour. Template-able across repos. |
| 5 | **Formatter (Prettier / ruff / gofmt)** | One config file + one `npm install`. Zero thinking. |
| 6 | **`.github/pull_request_template.md`** | Single file. ~10 min. |
| 7 | **Conventional Commits rule in CLAUDE.md + `commitlint` config** | ~30 min. Pays off immediately in PR titles and changelogs. |
| 8 | **`justfile` skeleton with `dev`, `test`, `lint`, `format`, `ci`** | ~1 hour. The `/justify` skill can scaffold this. |
| 9 | **Branch protection on `main`** | GitHub UI, 2 minutes. |
| 10 | **`CODEOWNERS`** | Single file. ~15 min. |
| 11 | **Linter with basic config** | ~1 hour (install + default config). Adding custom rules comes later. |
| 12 | **Pre-commit hooks (pre-commit / husky + lint-staged)** | ~1 hour. Install, wire up format + lint. |
| 13 | **Secret scanning (gitleaks in pre-commit + CI)** | ~1 hour. One tool, clear install docs. |
| 14 | **Type checker (TypeScript / mypy) in non-strict mode** | ~1 hour in most repos. Strict mode is a separate migration. |
| 15 | **CI pipeline invoking `just ci`** | ~2 hours. GitHub Actions boilerplate. |
| 16 | **Smoke test (one endpoint / one workflow)** | ~2 hours. Start small. |
| 17 | **AI-driven dep update workflow (on-demand `/update-deps` command)** | ~2 hours to wire up a skill or script. |
| 18 | **Integration tests on 2–3 critical user journeys** | Days, not hours. Highest value but highest initial effort. |
| 19 | **Type checker in strict mode** | Highly variable. Can be days on an existing monolith. Plan as a migration. |
| 20 | **`/docs/adr/` + first few ADRs** | Ongoing. Adopt the practice; entries come as decisions are made. |
| 21 | **Scheduled dep-update loop (cron)** | ~Half day once on-demand version is stable. |
| 22 | **Per-directory `CLAUDE.md` for large repos** | Incremental. Add per area as size demands. |
| 23 | **`/docs/runbooks/`** | Incremental per incident / per service. |

---

## The Rubric — Details

### 1. Context & Intent (AI knows *what* and *why*)

| Item | Purpose |
|------|---------|
| `README.md` with business section | Product purpose, users, core workflows, how to run locally. |
| `GLOSSARY.md` | Domain terms → definitions. Prevents conflated concepts. |
| Root `CLAUDE.md` | Stack, commands, workflow rules, conventions. Keep under ~200 lines. |
| Per-directory `CLAUDE.md` | Local rules for specific subtrees. Add when root gets unwieldy. |
| `/docs/adr/` | Decision records — *why*, not *what*. |
| `/docs/runbooks/` | Operational "what to do when X breaks." |

### 2. Single Command Surface

| Item | Purpose |
|------|---------|
| `justfile` (or Makefile / npm scripts) | All commands discoverable via `just --list`. |
| `just ci` — full pipeline | `format-check && lint && typecheck && test && build && smoke`. |
| CI invokes the same `just ci` | No drift between "passes locally" and "passes CI." |
| CLAUDE.md rule | "Run `just ci` before claiming a task is done." |

### 3. Feedback Loops

| Item | Purpose |
|------|---------|
| Formatter | No style debate. Auto-format on pre-commit; format-check in CI. |
| Linter | Enforces patterns and conventions as rules. |
| Type checker (strict) | Catches whole bug classes without tests. |
| Test runner | Integration on user journeys; unit for pure logic; e2e for UI-heavy. |
| Build | Catches broken imports and runtime wiring. |
| Smoke test | Boots app, exercises one real path. |
| **Legacy fallback** | Characterization tests on-demand around code AI modifies. |

### 4. Dep Updates (AI-driven)

| Item | Purpose |
|------|---------|
| Scheduled AI task | Periodic: detect outdated → update → `just ci` → open PR. |
| On-demand command | Trigger updates any time, independent of schedule. |
| Renovate/Dependabot (signal-only, optional) | Tells you what's outdated; AI does the actual work. |
| Grouped PRs | Patch together, minor separate, major individual. |
| Hard rule | Never merge a dep update if `just ci` is red. |

### 5. Guardrails

| Item | Purpose |
|------|---------|
| Pre-commit hooks (format, lint, typecheck, secret scan) | Block bad commits at the gate. |
| Branch protection on `main` | Require PR + green CI + review. |
| No `--no-verify`, no `--force` to main | Hard rules in CLAUDE.md. |
| Conventional Commits | `<type>(<scope>): <description>`. Enables changelogs and semantic versioning. |
| `.github/pull_request_template.md` | Forces structured what/why/test-plan in every PR. |
| `CODEOWNERS` | Auto-assigns reviewers by path. |
| `.gitignore` + `.env.example` | AI knows what not to commit and how to configure. |

### 6. Skill & Tooling Alignment

| Item | Purpose |
|------|---------|
| Global skills apply repo-wide | `simplify`, `requesting-code-review`, `security-review`, `tdd`, etc. |
| Repo-specific skills in `.claude/skills/` | e.g., `deploy-staging`, `seed-db`. |
| Pre-PR checklist in CLAUDE.md | `simplify` → code review → security review before `gh pr create`. |

---

## Quick Audit Checklist

Walk any repo through this:

1. [ ] Can someone read the README and know what the product does in 2 minutes?
2. [ ] Is there a `GLOSSARY.md` (or domain section) defining core terms?
3. [ ] Is there a root `CLAUDE.md` with stack, commands, and conventions?
4. [ ] Does `just --list` (or equivalent) show every command needed?
5. [ ] Does `just ci` pass on a fresh clone?
6. [ ] Does CI run the same `just ci`?
7. [ ] Do tests cover the critical user journeys?
8. [ ] Are format, lint, typecheck enforced (pre-commit + CI)?
9. [ ] Is secret scanning installed?
10. [ ] Is `main` branch-protected?
11. [ ] Is there a PR template?
12. [ ] Can AI update a dep, run `just ci`, and open a green PR unattended?

An empty box = the next piece of AI-readiness to add.

---

## Explicitly Out of Scope (add when triggered)

| Skipped | Add when… |
|---------|-----------|
| Coverage gates / mutation tests | Recurring regressions slip past PR review. |
| Observability (Sentry, metrics dashboards) | Repo serves real users or has SLAs. |
| Feature flags / canary deploys | Traffic is high enough that 100% rollouts are risky. |
| Full DDD ubiquitous-language model | Flat GLOSSARY.md becomes ambiguous. |
| ADRs + runbooks | You've re-explained "why X not Y" more than twice. |

---

## Open Questions (to resolve as a team)

1. **Who owns domain-context upkeep?** GLOSSARY.md and README business sections rot fast. Manual discipline, scheduled skill, or PR-template question?
2. **Scheduled dep-update task — where does it run?** Laptop (cron + Claude Code skill) or CI (GitHub Actions schedule)? Trade: laptop pauses when off; CI needs scoped credentials.
3. **Rollout strategy across existing repos.** One-shot audit skill scoring repos against this rubric? Or incremental adoption as each repo is touched?
4. **Major dep updates.** Auto-merge patch/minor if green; majors as draft PRs requiring human review?
5. **Characterization-test policy for legacy code.** Hard rule ("always write a pinning test first") or soft guideline? Hard catches more regressions; soft keeps simple changes fast.
