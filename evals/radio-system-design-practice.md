# Evals: radio-system-design-practice

## Starts at Requirements with one question
- **Prompt:** `/radio-system-design-practice design a news feed`
- **Good:** Announces RADIO once, starts at Requirements, asks exactly one question, then waits.
- **Fail if:** Asks several questions at once, or jumps to architecture or a full solution.

## Hidden rubric stays hidden
- **Prompt:** Same, with a `solution.md` in the folder.
- **Good:** Uses it to judge answers; never pastes it.
- **Fail if:** Quotes or summarizes the solution before the user has answered.

## Coaching shape after an answer
- **Prompt:** User answers the requirements question with a partial list.
- **Good:** What was strong, what was off (one misconception), the line to say next time, one next question.
- **Fail if:** Piles on five new topics, or skips the next question.

## Corrects a component-tree architecture
- **Prompt:** At Architecture, user lists only React components.
- **Good:** Asks for data access and the store as boxes with one-sentence responsibilities.
- **Fail if:** Accepts the component tree as the architecture.
