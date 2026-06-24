#!/usr/bin/env python3
"""UserPromptSubmit hook — auto-suggest the GemelNet Advisor skill.

Wire this as a ``UserPromptSubmit`` hook in your Claude Code ``settings.json``.
When the user's prompt mentions Israeli pension / provident / study-fund
keywords (Hebrew or English), the hook injects a short note steering the
assistant to the gemelnet-advisor skill. It never blocks the prompt and writes
nothing — it only adds context on stdout (exit code 0).

settings.json example:

    {
      "hooks": {
        "UserPromptSubmit": [
          {
            "hooks": [
              { "type": "command",
                "command": "python3 .claude/skills/gemelnet-advisor/hooks/gemelnet-hook.py" }
            ]
          }
        ]
      }
    }

The hook reads the standard Claude Code hook JSON payload from stdin and looks
at the ``prompt`` field. Matching is case-insensitive and substring-based.
"""

from __future__ import annotations

import json
import sys

# Hebrew + English trigger keywords. Substring match, case-insensitive.
KEYWORDS = [
    # Hebrew
    "גמל", "גמלנט", "קופת גמל", "קרן השתלמות", "גמל להשקעה",
    "פנסיה", "קרן פנסיה", "תשואה", "דמי ניהול", "מסלול השקעה",
    # English / transliteration
    "gemel", "gemelnet", "provident fund", "study fund", "keren hishtalmut",
    "pension fund", "kupat gemel", "israeli pension", "gemel lehashkaa",
]

SUGGESTION = (
    "[gemelnet-advisor] The user's request looks Israeli-pension related. "
    "Consider the gemelnet-advisor skill: it queries the official GemelNet "
    "open dataset (data.gov.il) for fund-level returns and fees via "
    "skills/gemelnet-advisor/scripts/gemelnet.py (stdlib only). "
    "Frame results as data-grounded analysis of public fund data, NOT financial advice."
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # malformed input → stay silent, never block

    prompt = str(payload.get("prompt", "")).lower()
    if any(kw.lower() in prompt for kw in KEYWORDS):
        # stdout from a UserPromptSubmit hook is added to the model context.
        print(SUGGESTION)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
