# Evals: behavioral-story-depth

## Missing metric becomes a question
- **Prompt:** `/behavioral-story-depth` then a story with no number in it.
- **Good:** Asks what result the user can prove. If they don't know, writes the answer around it and lists it under Open gaps.
- **Fail if:** Writes any metric, percentage, or count the user didn't give.

## One question at a time
- **Prompt:** `/behavioral-story-depth` with no story yet.
- **Good:** Asks for the story only, then waits.
- **Fail if:** Asks the story, the LP, and the result in one message.

## "We" gets called out in Drill
- **Prompt:** Drill mode; the user's answer says "we decided" three times.
- **Good:** Names the "we" drift as the slip and gives a first-person say-instead line.
- **Fail if:** Moves to the next probe without flagging it.

## Map refuses repeats
- **Prompt:** Map mode with two stories from the same project and a four-LP loop.
- **Good:** Treats them as one project, leads with it once, and flags the LPs left thin.
- **Fail if:** Assigns both stories as leads in the same loop.

## Opener stays short; depth goes to Actions
- **Prompt:** Build mode with a long, detailed story.
- **Good:** Opener is about 180–220 words; the extra detail lands in Actions-layer beats.
- **Fail if:** The opener runs past ~250 words.
