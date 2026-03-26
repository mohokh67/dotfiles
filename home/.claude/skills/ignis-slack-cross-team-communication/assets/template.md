# Slack Message Template

Use Slack mrkdwn format. Omit any section where user said skip/N/A.
Add emoji based on urgency (see SKILL.md for conventions).

---

{URGENCY_EMOJI} *{TITLE}*

We are {CHANGE_TYPE} {SYSTEM_NAME}.

*Why?*
{STABILITY_BENEFITS}

:warning: *Action Required By:* {DEADLINE}
{CONSEQUENCE_IF_NOT_ACTED}

*Risk/Blast Radius:*
{RISK_DESCRIPTION}

---

:calendar: *Timeline*

{FOR_EACH_PHASE}
• *Phase {N} ({DATE_RANGE}):* {PHASE_DESCRIPTION}
{END_FOR_EACH}

*Hard Cut-off:* {CUTOFF_DATE}
> {CUTOFF_ACTION}

---

*Are You Impacted?*
You need to act if you:
{FOR_EACH_IMPACT_CRITERIA}
• {CRITERIA}
{END_FOR_EACH}

---

*Environments*

{FOR_EACH_ENVIRONMENT}
*{ENV_NAME}:*
• URL: {ENV_URL}
• Access: {ENV_ACCESS_METHOD}
{END_FOR_EACH}

---

*Required Actions*

{FOR_EACH_ACTION}
{N}. {ACTION_DESCRIPTION}
{END_FOR_EACH}

:white_check_mark: *How do I know I'm done?*
{FOR_EACH_COMPLETION_CRITERIA}
• {CRITERIA}
{END_FOR_EACH}

---

:link: *Resources*

• Jira: {JIRA_LINK}
• Confluence: {CONFLUENCE_LINK}
• Documentation: {DOCS_LINK}
• Runbook: {RUNBOOK_LINK}
• Architecture: {ARCHITECTURE_LINK}
• Dashboards: {DASHBOARD_LINK}
• Monitoring: {MONITORING_LINK}
• Alerting: {ALERTING_LINK}

---

:question: *Questions?*
Contact {CONTACT_PERSON} or ask in {SLACK_CHANNEL}

*After-hours issues:*
Use Slack's `/genie` command: https://csdisco.atlassian.net/wiki/spaces/dd/pages/3850109135/Engineering+-+SHIELD+Support#How-to-alert-the-person-on-call-through-opsgenie-vs-phone-call

*Working hours support:*
Reach out on Slack #engineering-ignis
