# 03: Scoring spike

**Question:** Can each of the four non-error areas be scored with evidence a person checks in under a minute?

**Seam:** a hand-written scorecard for the target repo, using `rubric.md`, written in a scratch folder outside both repos.

**Check:** artifact: the scorecard. The user picks three scores at random and times each check against its cited file:line. Passes if each takes under 60 seconds and the evidence supports the score. Fails otherwise; then 01's anchors or the evidence rules get resliced.

**Must stay green:** the target repo's working tree.

**Decided:**
- Every score cites at least one file:line. A score with no evidence is invalid.

**Delegated to the worker:**
- How many citations per score beyond the first.

**Out of scope:**
- File sizes (04). The scorecard file format (05).
