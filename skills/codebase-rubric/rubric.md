# Rubric

Loaded by `codebase-rubric` when scoring. Five areas, each scored 1 to 5. Only 1, 3, and 5 are defined; a 2 or a 4 means the evidence sits between two anchors. Every score needs at least one `path:line` that a person can open and see the reason in under a minute.

The five areas and the size tiers (target 500, soft 800, hard 1,000 lines) come from a screenshot the user shared; its source is not yet known.

## How to score

1. Read the anchors for the area.
2. Find evidence first, then pick the score it supports. Never pick a score and go looking for evidence.
3. Cite the strongest evidence for the score, and one counter-example if the repo is mixed.
4. When two anchors both fit, pick the lower anchor and say what would earn the higher. A 4 needs the 5 anchor to fit most of the repo; a 2 needs the 1 anchor to fit most of it.

## Architecture

How the system is split into layers or parts, and whether data and control flow in one readable direction.

- **1:** No visible structure. Entry points, business rules, and I/O sit in the same files. You can't tell where a request goes without reading everything. *Evidence:* one file that parses input, applies rules, and writes output.
- **3:** Layers exist and are named, but some paths skip them: a command handler that writes the database directly, or a util that calls back up into the app. *Evidence:* an import that crosses a layer the wrong way.
- **5:** Each layer has one job, dependencies point one way, and the README or folder names describe the shape. A newcomer can draw the system from the folder tree. *Evidence:* the entry point and the one or two modules it delegates to.

## Modularity

Whether each file or module has one reason to change, and whether you can change one without touching others.

- **1:** God files. One file owns many unrelated concerns, and most changes touch it. *Evidence:* a file in the hard size tier with several unrelated sections.
- **3:** Most modules are focused, but one or two hubs collect everything new. *Evidence:* a file in the soft or hard tier that many others import.
- **5:** Modules are small and focused, and a feature change touches a predictable, short list of files. *Evidence:* a recent feature whose files share one folder or prefix.

## Abstraction

Whether the code names the ideas in its domain once, at the right level, with no needless layers.

- **1:** No shared ideas. The same logic is copied in several places, or wrapped in layers that only pass arguments through. *Evidence:* two near-identical blocks, or a wrapper that adds nothing.
- **3:** The main concepts have names, but some leak: callers reach into internals, or one concept has two names. *Evidence:* a caller using a field that should be private.
- **5:** Each domain concept has one name and one home. Interfaces hide how, show what, and have no extra layers. *Evidence:* a type or function that callers use without knowing its internals.

## Components

Whether the reusable building blocks (functions, classes, UI components, commands) have clear inputs and outputs and can be used and tested alone.

- **1:** Units depend on hidden global state, so none can be used or tested alone. *Evidence:* a function that reads a global or environment value deep inside.
- **3:** Most units take explicit inputs, but some need a large setup or mocks of half the system to test. *Evidence:* a test with heavy setup for a small behavior.
- **5:** Units take what they need as inputs, return results, and have tests that set up only what they use. *Evidence:* a unit and its small, direct test.

## Errors: description and tracing

When something fails, whether the person who sees it learns four things: **what** broke, **where**, **why**, and **a handle to trace it** (an ID, a path, a request or command name, or the original cause kept attached).

- **1:** Failures are swallowed or reduced to "something went wrong." The cause is lost at the first catch. *Evidence:* an empty catch, or a catch that throws a new error without the original.
- **3:** Messages say what failed, but context drops between layers, so you know what broke but not where or why. *Evidence:* a rethrow that keeps the message but drops the cause, or a log line with no identifiers.
- **5:** Every failure a person sees carries all four. The cause chain is kept, exit codes or statuses are specific, and a log line or message leads back to the origin. *Evidence:* the traced failure path, hop by hop, with all four present at the last hop.

The error score always rests on the one traced path (see the trace in the scorecard), plus any pattern the trace shows repeats across the repo.
