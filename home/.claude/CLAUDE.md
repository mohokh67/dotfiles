- In all interactions and commit messages, be extremely concise and sacrifice grammar for the sake of concision.

## Git
- Never add Co-Authored-By or any Claude/Anthropic attribution to commit messages. Use only the global git user name and email.
- **HARD RULE**: Every commit message must follow Conventional Commits format: `<type>(<optional scope>): <description>`. Valid types: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `test`, `ci`, `perf`, `build`. No exceptions — never use a plain message like "update X" or "add Y" without a type prefix.
- When creating or updating a PR, always include a concise description summarizing the changes.
- **HARD BLOCK**: Never commit or push directly to `main` or `master`. No exceptions.
  - Before ANY `git commit` or `git push`: run `git branch --show-current` first.
  - If on `main`/`master`: STOP. Do NOT run the command. Ask: "You're on main — create a branch first? Suggested: `<branch>`."
  - "Proceed" means: create/switch to a new branch, THEN commit. Never means: commit to main even with user approval.

## Documentation

After completing any significant work in a project:
- Update the project's `CLAUDE.md` with new patterns, conventions, or architectural decisions
- Update `README.md` to reflect new features, changed behavior, or removed functionality

## Plan Mode

- Make the plan extremely concise. Sacrifice grammar for the sake of concision.
- At the end of each plan, give me a list of unresolved questions to answer, if any.
