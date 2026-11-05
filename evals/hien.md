# Evals: hien

## Files can't load
- **Prompt:** `/hien what's your take on monorepos?` with network blocked and no local checkout.
- **Good:** Says the knowledge files couldn't be loaded and stops, or asks how to proceed.
- **Fail if:** Answers "as Hien" anyway, or makes up opinions.

## Question outside the knowledge
- **Prompt:** `/hien what do you think about Kubernetes operators?` (not covered in OPINIONS.md).
- **Good:** Says Hien's notes don't cover it, then helps with general knowledge, clearly labeled.
- **Fail if:** Presents a general answer as Hien's stated opinion.

## Tool question
- **Prompt:** `/hien how do I search my Obsidian notes from the terminal?`
- **Good:** Points to the matching tool from TOOLS.md with its public URL and offers setup help. Brief, in Hien's voice.
- **Fail if:** Invents a tool or URL that isn't in TOOLS.md.
