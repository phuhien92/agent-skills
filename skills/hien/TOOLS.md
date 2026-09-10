# TOOLS.md

Public surfaces and projects Hien Luong owns or maintains in public. Use this file to know what exists and what it is for before reaching for something else.

Only real public projects are listed. Do not invent private, unpublished, or employer-internal tools.

## Raymond Space

https://hienluong.dev

Raymond Space is Hien's personal site and writing home. It holds the public bio, posts, and the AI twin entry point.

It solves the "where do I send people" problem: one URL for work, writing, and demos instead of a pile of profiles.

Open the site for the latest posts and contact path. Email listed on the site: luongphuhien@gmail.com.

## GitHub

https://github.com/phuhien92

Public code, experiments, and this skill pack. Use it when the user wants a repo URL, a clone path, or a sense of what Hien has actually shipped in public.

Browse the profile, then open the specific repo below. Do not treat star count as a quality bar. Several useful repos here are small personal builds.

## Medium

https://medium.com/@phuhien

Longer writeups, including the Personal OS / Raymond Space post and older frontend and Node notes.

Use it when the user wants the public essay behind an opinion, especially COWORK OS. Prefer linking the post over restating the whole piece.

## LinkedIn

https://www.linkedin.com/in/hienphuluong

Public career record and short posts: IAM work, open-to-work note, and the AI twin announcement.

Use it for role history and for evidence behind impact numbers. Do not treat the headline as current employment if a later post says the Highspot chapter ended.

## AI twin

https://hienluong.dev/talk-to-ai/

A voice-conversation demo of Hien. Click, it picks up, and you talk. It answers questions about his work, projects, and what he cares about.

It started as a way to explain software work to family without a dinner-table jargon dump. Public note: still beta, still rough; a later step is cloning his actual voice.

Open the page and talk, or send the URL when someone wants a demo instead of a resume paragraph.

Evidence: https://www.linkedin.com/posts/hienphuluong_talk-to-hiens-ai-twin-activity-7466611242540093441-Phfc

## agent-skills

https://github.com/phuhien92/agent-skills

This pack. One directory per skill, slash commands as entry points, plugin manifests for Claude Code and Cursor.

It solves "I want agents to follow a specific workflow" without dumping a pile of notes into every chat. Current public skills include `/hien` and `/radio-system-design-practice`.

Install one skill:

```bash
npx skills add phuhien92/agent-skills --skill hien
```

Or open the repo and run `/hien` / `/radio-system-design-practice` from the mapped commands.

## kid-coins

https://github.com/phuhien92/kid-coins

A web app that teaches kids responsibility and money basics through daily tasks and gamified rewards. Kids complete chores, homework, hygiene, or self-care to earn coins that can convert to real money or rewards.

It solves "how do I make chores and basics stick without turning it into a lecture."

Clone the repo and follow its README. Design reference is linked from the project README.

## pampa

https://github.com/phuhien92/pampa

Hien's public fork of PAMPA (Protocol for Augmented Memory of Project Artifacts). MCP-compatible codebase memory with semantic search.

It solves agents losing project context: give them a queryable, updated memory of a repo instead of hoping the chat window remembers.

Clone https://github.com/phuhien92/pampa and follow the project's install docs (`npx` workflow). Treat it as Hien's public checkout of the protocol, not as a claim that he authored the upstream PAMPA project.

## firestore-shopping-app

https://github.com/phuhien92/firestore-shopping-app

A shopping-list app built with Ionic 4 and Cloud Firestore.

It is a practical mobile/web list app: shared list state without standing up a custom backend.

Clone the repo and follow its README for the Ionic + Firestore setup.

## nodejs-sqlite3

https://github.com/phuhien92/nodejs-sqlite3

A small experiment: a Node server plus SQLite3.

It solves "I know Rails + SQLite; what does the same idea look like on Node?" Writeup: https://medium.com/@phuhien (post titled "Experiment with Node JS and Sqlite3", April 2018).

Clone the repo and run it as a local learning project, not as a production service.

## react-node-ssr

https://github.com/phuhien92/react-node-ssr

React + Node + Redux server-side rendering experiment. The stated goal was to work through real SSR problems rather than stop at a client-only demo.

It solves "how do I render React on the server and hydrate on the client" for a small app.

Clone the repo and follow its README. An older demo URL is listed there (`https://ssr-demo.herokuapp.com`); treat hosted demos as possibly gone.

## Interview coach and agent tooling experiments

https://github.com/phuhien92/interview-coach-skill-1

https://github.com/phuhien92/skills

Public experiments with interview-coach style agent commands and a personal skills directory. `interview-coach-skill-1` is a Claude Code interview coach covering JD analysis, resume work, mocks, and negotiation. `skills` is a public copy of a personal skills directory (planning, TDD, triage, architecture, tooling).

They solve "can I run interview prep and coding workflows as skills, not as a one-off prompt."

Clone the repo you care about and follow its README. These are experiments and, in some cases, forks. Do not present them as polished products Hien sells.

## Contact

Email: luongphuhien@gmail.com
