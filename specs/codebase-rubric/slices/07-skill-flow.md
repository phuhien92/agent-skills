# 07: Skill flow

**Question:** Does one run, by hand or with no user present, produce a valid scorecard and change nothing else?

**Seam:** `skills/codebase-rubric/SKILL.md`: run the size script, spawn five scorers in one message (one per area, each given only `rubric.md`'s section for its area plus the repo path, never another area's score; the errors scorer runs the 02 trace), fill `scorecard.md`, run `delta.py` and `check_scorecard.py`, write `scorecards/<date>.md`.

**Check:** on the target repo, after `claude -p "/codebase-rubric"`: `git status --porcelain` lists only the new scorecard; `check_scorecard.py` exits 0 on it; the run asked no questions. Then the user spot-checks three scores in under a minute each (the success test).

**Must stay green:** all script tests; `python3 tools/validate.py`.

**Decided:**
- No-user rule: never wait, never overwrite (`<date>-2.md`), say if anchors were unapproved.
- `SKILL.md` stays under 8 KB; anchors and the template stay in on-demand files.
- With no way to spawn agents, score one area at a time, writing each score before reading the next area's anchors, and say in the scorecard that the scorers were not independent.

**Delegated to the worker:**
- Step wording and order inside the flow.

**Out of scope:**
- Registration and CI (08).
