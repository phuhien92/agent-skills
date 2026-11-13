---
description: Score a codebase's health and write a scorecard with path:line evidence. Use for a periodic health check, before a big refactor, or when the user asks whether a repo is drifting. Not a per-change gate.
---

Follow the `codebase-rubric` skill.

Write only scorecards/<date>.md in the target repo. One independent scorer per area. Every score cites path:line. Run check_scorecard.py --repo until it prints ok.
