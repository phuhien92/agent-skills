# 05: Scorecard contract

**Question:** What shape must a scorecard have so a script can verify it and a later run can read it?

**Seam:** `skills/codebase-rubric/scorecard.md` (the template, loaded on demand) and `skills/codebase-rubric/scripts/check_scorecard.py <file>`. Machine-read tables sit between HTML comment markers (for example `<!-- scores:start -->`).

**Check:** `python3 skills/codebase-rubric/scripts/check_scorecard.py <fixture>` exits 0 on a good fixture, and exits 1 with a reason on fixtures that miss an area, have a score outside 1–5, have a score without a file:line, have no error trace, or lost a marker. Fixtures come from the spike outputs in 02 and 03.

**Must stay green:** 04's tests.

**Decided:**
- Sections: date, repo and commit, size table, skip counts, five scores with evidence, error trace hop by hop, delta (06), and whether `rubric.md` anchors were approved.

**Delegated to the worker:**
- Marker names and section headings.

**Out of scope:**
- Computing deltas (06).
