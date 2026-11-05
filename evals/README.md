# Evals

Behavior cases for each skill: `evals/<skill>.md`. Structure checks live in `tools/validate.py`; these files check what the skill *does*.

## Case format

```
## <short name>
- **Prompt:** what the user says (plus any setup)
- **Good:** what a passing response does
- **Fail if:** the specific behavior that means the skill broke
```

Keep 3–6 cases per skill. Prefer cases that pin a rule the skill states (one question at a time, never invent facts, stop when files can't load) over cases that grade style.

## Running

By hand for now. Open a fresh session with the skill loaded, send the prompt, and mark each case pass/fail against **Fail if**. Record failures in the PR that changes the skill.

Automate (scripted runs, an LLM judge) only after these cases have caught a real regression, and only after checking the judge against hand grades.
