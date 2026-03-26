---
name: ignis-slack-cross-team-communication
description: "Generate Slack messages for cross-team announcements. Use when: announcing migrations, deprecations, breaking changes, security updates, decommissioning, or any action-required communication to other teams. Triggers on 'announce to teams', 'migration message', 'deprecation notice', 'breaking change alert', 'cross-team update', 'notify other teams'."
---

# Cross-Team Communication Generator

Generate standardized Slack messages for project changes that require action from other teams.

## Quick Mode

If user says "quick", "simple", or "brief" announcement:
1. Ask only: title, system, deadline, one-line action required, contact
2. Use `assets/template-quick.md`
3. Skip phases, environments, detailed resources

## Process

1. **Intro**: Explain you'll ask questions one at a time to build a communication. User can say "skip" or "N/A" to omit any field.

2. **Gather Info** (one question per message):

   **Core Details:**
   - Project/change title
   - Change type: moving / securing / decommissioning / deprecating / other
   - System/tool name affected
   - Urgency: critical / standard / fyi (affects tone)
   - Action-required deadline
   - Consequence of not migrating/acting
   - Risk level / blast radius
   - Stability/security benefits of this change

   **Timeline:**
   - Hard cut-off date + what happens after
   - Number of phases → for each: date range + description

   **Impact:**
   - Who is impacted? (checklist: uses X API, accesses Y database, etc.)

   **Links & Resources:**
   - Contact person (@slack-handle)
   - Jira ticket
   - Confluence/wiki page
   - Logs/dashboard link
   - Runbook link
   - Architecture diagram
   - Documentation link
   - Observability/monitoring link
   - Alerting/PagerDuty link

   **Environments:**
   - Which environments? (ask which apply, don't assume DEV/TEST/PROD)
   - For each: URL + how to access/test

   **Action Items:**
   - Number of required actions → for each: description
   - Completion criteria (checklist items)

   **Support:**
   - Slack channel for questions

3. **Final Checklist**: Before generating, ask:
   > "Before I generate the message, confirm you haven't missed any of these: Jira ticket, Confluence page, dashboards, logs, runbooks, architecture docs, monitoring/alerting links?"

4. **Review**: Present all collected info in a structured summary. Ask if anything needs editing.

5. **Generate**: Fill the template from `assets/template.md`, output as Slack mrkdwn in a code block for easy copy.

6. **Save Option**: Ask if user wants to save as markdown file. If yes, prompt for file path.

## Key Behaviors

- **One question per message** — don't overwhelm
- **"skip" / "N/A" / "don't have"** → omit that section from output
- **Multiple choice** where sensible (change type, yes/no questions)
- **Flexible environments** — ask which apply, don't hardcode DEV/TEST/PROD
- **Slack mrkdwn format** — use `*bold*`, `_italic_`, `• ` bullets, `>` quotes (not markdown)
- **Code block output** — wrap final message in triple backticks for copy

## Tone by Urgency

- **Critical**: Lead with action, direct language, deadline prominent. Use :rotating_light: emoji.
- **Standard**: Balanced info + action, professional tone. Use :warning: for action items.
- **FYI**: Casual, no pressure, informational. Lighter tone, optional emoji.

## Emoji Conventions

Use sparingly for visual scanning:
- :rotating_light: Breaking/critical changes
- :calendar: Timeline/dates
- :warning: Action required
- :white_check_mark: Completion criteria
- :question: Questions/support
- :link: Resources/links

## Template Reference

See `assets/template.md` for full structure, `assets/template-quick.md` for lightweight variant.

## Example Output

```
:rotating_light: *MatterContext API Migration Required*

We are deprecating the old MatterContext API v1.

*Why?*
Security improvements and better caching performance.

*Action Required By:* 2026-04-15
:warning: After this date, v1 endpoints will return 404.

*Are You Impacted?*
You need to act if you:
• Call `/api/v1/matter-context/*` endpoints
• Use the `matter-context-client` npm package < v2.0

*Required Actions*
1. Update to `matter-context-client@^2.0.0`
2. Replace v1 endpoint calls with v2

*Questions?*
Contact @bogusz or ask in #ep-ignis-raven-sysdb-retirement
```
