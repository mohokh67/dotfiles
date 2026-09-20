#!/bin/bash

SKILL="$HOME/.agents/skills/caveman/SKILL.md"

[ -f "$SKILL" ] || exit 0

jq -n --rawfile skill "$SKILL" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: ("Caveman mode is ACTIVE for this session, starting with the first response. Applies to chat replies only, not human-facing drafts, commit messages, code, code comments, or file content.\n\n" + $skill)
  },
  suppressOutput: true
}'
