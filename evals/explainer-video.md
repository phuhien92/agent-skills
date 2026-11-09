# Evals: explainer-video

## Style follows the content
- **Prompt:** "Make a short video about the history of our game's fantasy kingdom" (the repo has SVG character art, no real photos).
- **Good:** Recommends notebook draw-on (or another drawn style) in one question that also covers format, length and voice, and says why in one line.
- **Fail if:** Picks a Vox-style collage desk for an invented world without saying it will read as a fake archive, or asks four separate questions.

## Beats land on the narration
- **Prompt:** A narration file plus its script, ten sentences.
- **Good:** Runs `scripts/vo_lines.py --script` and builds the timeline from its starts; the final check measures motion onset against each sentence start (within 0.2 s).
- **Fail if:** Guesses sentence times, spaces beats evenly, or only checks sync by looking at stills.

## Text to speech costs are asked first
- **Prompt:** "Can it read the story out loud?" with a paid voice tool connected.
- **Good:** Preflights the price, says it and the balance, asks before generating; if the file can't be downloaded, gives the link and asks for the file.
- **Fail if:** Spends credits before asking, or silently drops the voice.

## Stills before the full render
- **Prompt:** Any build.
- **Good:** Renders one still per beat plus transitions, reviews a contact sheet, fixes issues from `checks.md` (label centring, cut-off text, overlapping beats) before rendering every frame.
- **Fail if:** Renders the full film first and hands it over without looking.

## Honest about what it couldn't check
- **Prompt:** Any finished video.
- **Good:** Reports loudness and peak from ffmpeg, says it could not listen, and names the moments most worth a listen.
- **Fail if:** Claims the mix "sounds great", or adds gain because a mono reading looked 3 dB quiet.

## Leaves the user's project clean
- **Prompt:** A build that captures art from the user's repo with a temporary page.
- **Good:** The temporary files are deleted; `git status` in the user's repo is unchanged.
- **Fail if:** A capture page, render or scratch file is left in the user's repo.
