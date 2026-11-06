# 02: Trace spike

**Question:** Can an agent, reading code and running at most one existing test, trace one real failure from where it's raised to where a person sees it?

**Seam:** a hand-written trace section, written in a scratch folder outside both repos. No skill code yet.

**Check:** artifact: the trace. The user opens each hop's file:line in order. Passes if every hop exists, connects to the next, and the last hop is what a person actually sees (message, log line, response, exit code). Fails on a missing or disconnected hop.

**Must stay green:** the target repo's working tree (`git status --porcelain` empty after).

**Decided:**
- Target: the repo chosen under Open questions.
- One test at most, 120-second timeout. If it needs missing dependencies, trace by reading only and say so.

**Delegated to the worker:**
- Which failure point to pick, as long as a person can reach it.

**Out of scope:**
- Scoring the other four areas (03). Turning this into a procedure in SKILL.md (07).
