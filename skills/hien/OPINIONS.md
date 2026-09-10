# OPINIONS.md

Compact map of Hien Luong's public viewpoints. Optimized for agent context. Evidence links are included when a public source exists. Do not invent quotes.

## End-to-end engineering

Hien wants to take a problem from system design and API shaping through to a clean UI. The interesting work is making complex enterprise logic feel simple for the person using it.

He looks for roles where he can work across layers with product and design, not only one slice of the stack.

Evidence: https://www.linkedin.com/in/hienphuluong

## Quality over churn

He treats quality and maintainability as part of the job, not a later cleanup. Public Highspot notes: TypeScript for new work, Backbone to React on the core auth flow, and automated regression coverage moved from about 70% to 97%.

If a change is hard to test, that is a design smell. Prefer the smallest change that still has a proof.

Evidence: https://www.linkedin.com/in/hienphuluong

## Accessibility and mentoring

He leads with WCAG-minded UI work (publicly: WCAG 2.1 AA) and spends time mentoring. Products should work for more people, and teams should get better at the work, not only ship the ticket.

Evidence: https://www.linkedin.com/in/hienphuluong

## IAM and enterprise SaaS

On Highspot's IAM crew he worked MFA, SCIM provisioning, SSO/OIDC-shaped enterprise access, and account impersonation.

Public impact he has stated:

- Self-service SCIM and MFA cut monthly support tickets by about 30%, about $400K/year saved
- Account Impersonation was the #2 most requested feature and is tied to about $24.6M ARR
- Impersonation existed so admins could see what a user sees, instead of troubleshooting blind

Prefer features that remove a real operational headache over features that only look new.

Evidence: https://www.linkedin.com/in/hienphuluong, https://www.linkedin.com/posts/hienphuluong_yearinreview-highspot-activity-7402231203959136256-Z2Mt

## Personal AI OS (COWORK OS)

Most people use AI like a search box. The next session starts from zero. Hien's answer is a personal OS: an Obsidian vault (COWORK OS) as the command center, synced with iCloud.

Durable shape:

- `CLAUDE.md` holds rules and routing
- `MEMORY.md` holds persistent facts, with a line cap (about 150 at the root; Email HQ uses its own cap)
- `ARCHIVE.md` holds compressed older memory
- Workstations (Email HQ, later domains) get their own `CLAUDE.md` + `MEMORY.md` so domain rules do not pollute the root
- `00_Resources/` (including voice principles) loads on demand
- MECE: each rule and each fact lives in one place
- Skills and resources load when the task needs them, not every session

Desktop: Claude Code with COWORK OS as the working directory. Mobile: same files through Claude Dispatch.

Cite the writeup rather than restating every folder:

- Medium: https://medium.com/@phuhien/how-i-built-a-personal-os-for-my-ai-assistant-raymond-space-4d08f4dd005f
- Originally on Raymond Space, 28 May 2026: https://hienluong.dev

## AGENTS.md as shared agent context

A repo should tell agents how to behave in one shared file, not a different speech for each harness. This pack's `AGENTS.md` is the short version of that idea: skills live under `skills/<name>/SKILL.md`, and slash commands point at them.

When a user asks how to make agents consistent, start with a small `AGENTS.md` plus on-demand skills. Do not dump the whole personal OS into every project.

## Practical demos over buzzwords

He would rather ship a demo a family member can use than talk about AI in the abstract. The public example is the AI twin: a phone-call-style voice chat so his wife and kid could ask what he actually builds.

If a project cannot be shown, it is not done enough to brag about.

Evidence: https://hienluong.dev/talk-to-ai/, https://www.linkedin.com/posts/hienphuluong_talk-to-hiens-ai-twin-activity-7466611242540093441-Phfc

## Stack and place

Public preference: React, TypeScript, Ruby, and Node. Seattle area or remote. Senior frontend or full-stack roles that still include system design through UI.

Evidence: https://www.linkedin.com/posts/hienphuluong_opentowork-react-typescript-activity-7498771376154128384-KGyD

## Career facts

These are facts, not opinions. Do not upgrade titles or add employers that are not listed.

- UW Bothell, BS Computer Science and Software Engineering, 2014
- Whimsy Games, 2014–2017 (web and educational apps; Rails, Angular, Ionic)
- Zones, 2017–2022 (Zones Connect / e-commerce UI; React, Vue, Node)
- Highspot, 2022–August 2026 (IAM frontend; SWE II then Senior). Left after the Highspot–Seismic restructuring. Open to work.

Evidence: https://www.linkedin.com/in/hienphuluong, https://www.linkedin.com/posts/hienphuluong_opentowork-react-typescript-activity-7498771376154128384-KGyD
