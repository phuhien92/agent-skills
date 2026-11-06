# 01: Rubric anchors

**Question:** What do a 1, a 3, and a 5 look like in each of the five areas, and what evidence justifies each?

**Seam:** `skills/codebase-rubric/rubric.md`, loaded on demand by the skill. Areas: architecture, modularity, abstraction, components, error description and tracing.

**Check:** artifact `rubric.md`. The user approves it or returns edits. Fails if any area lacks a 1, 3, or 5 anchor, or an anchor names no kind of evidence (such as "a file:line where X", "a module whose imports show Y").

**Must stay green:** `python3 tools/validate.py`, except the one expected "skills/codebase-rubric/ has no SKILL.md" error until 07 adds it. (Corrected during build: the validator treats every folder under `skills/` as a skill.)

**Decided:**
- Anchors only at 1, 3, 5; scores 2 and 4 mean "between." Fewer anchors, less to argue about.
- Error tracing anchors must cover four things a person needs: what broke, where, why, and an ID or context to trace it.

**Delegated to the worker:**
- Wording and examples inside each anchor.
- Whether to add a short "common misreads" note per area.

**Out of scope:**
- How the agent applies the anchors (07).
