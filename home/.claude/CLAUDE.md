## Behavior

- Be extremely concise. Sacrifice grammar for concision.

## Git

- Never add Co-Authored-By or any Claude/Anthropic attribution to commit messages. Use only the global git user name and email.
- **HARD RULE**: Every commit message must follow Conventional Commits format: `<type>(<optional scope>): <description>`. Valid types: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `test`, `ci`, `perf`, `build`. No exceptions — never use a plain message like "update X" or "add Y" without a type prefix.
- When creating or updating a PR, always include a concise description summarizing the changes.
- **HARD BLOCK**: Never commit or push directly to `main` or `master`. No exceptions.
  - Before ANY `git commit` or `git push`: run `git branch --show-current` first.
  - If on `main`/`master`: STOP. Do NOT run the command. Ask: "You're on main — create a branch first? Suggested: `<branch>`."
  - "Proceed" means: create/switch to a new branch, THEN commit. Never means: commit to main even with user approval.

## Post-Code Workflow

After completing a chunk of **code work** (not docs/config-only changes):

1. Announce work is complete with a one-line summary
2. Recommend creating a branch — suggest name in format `<type>/<short-description>` (e.g., `feat/add-login`, `fix/null-check`) — wait for confirmation before creating
3. If confirmed: update the **project's** `CLAUDE.md` with new patterns if any; update `README.md` if behavior/features changed; then stage all relevant files and commit using Conventional Commits format
4. Recommend creating a PR — if confirmed, offer the Pre-PR Checklist before running `gh pr create`

## Pre-PR Checklist

Before ANY `gh pr create`, ask the user:

> "Before creating the PR, which checks would you like to run?
> 1. `simplify` — clean up code
> 2. `requesting-code-review` — subagent code review
> 3. `security-review` — security audit
> Reply with numbers (e.g. `1 3`), `all`, or `none`."

Run only the selected checks. Fix any critical issues found before proceeding.

## Plan Mode

- Use the `writing-plans` skill before writing any multi-step implementation plan.
- At the end of each plan, list any unresolved questions for me to answer.
- End planning turns with `ExitPlanMode`, not with text asking for approval.