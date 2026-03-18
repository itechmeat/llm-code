---
name: github-stars-organizer
description: "GitHub stars and lists organizer. Reuses existing lists, finds unlisted starred repositories, creates only necessary broad lists, and adds repos without disturbing existing assignments. Use when user asks to organize GitHub stars, sort starred repos, clean up lists, or file unlisted stars. Keywords: GitHub stars, GitHub lists, starred repositories, chrome-cdp."
metadata:
  author: techmeat
  version: "1.1.0"
  release_date: "2026-03-18"
---

# GitHub Stars Organizer

Organize a user's GitHub starred repositories by reusing existing lists, creating only a small number of broad missing lists, and adding unlisted repositories to the right places.

This skill is for **organizing starred repositories**, not for general GitHub account maintenance.

Default stance: be **conservative, review-first, and additive**. A bad list assignment is worse than leaving a repository unfiled for later review.

## Required Tooling

- Preferred browser automation skill: [chrome-cdp](https://github.com/pasky/chrome-cdp-skill/tree/main/skills/chrome-cdp)
- A compatible equivalent is acceptable only if it can:
  - control an authenticated local browser session
  - read the GitHub Stars page
  - inspect repository list membership
  - create lists
  - add repositories to lists

If `chrome-cdp` or an equivalent browser automation skill is unavailable, stop and say that authenticated browser automation is required.

## Remote Debugging Prerequisite

If Chrome remote debugging is not enabled yet, tell the user to do this first:

1. Open `chrome://inspect/#remote-debugging`
2. Enable remote debugging / remote target discovery
3. Make sure GitHub is logged in in that Chrome profile
4. Confirm the local debugging endpoint is available, commonly `127.0.0.1:9222`
5. Approve any Chrome "Allow debugging" prompt for the GitHub tab if it appears

Do not proceed until browser automation can reach the GitHub tab.

## Inputs

The user should provide at least one of:

- GitHub username
- GitHub profile URL
- GitHub Stars URL

Do not hardcode any specific account, repository, or list names.

## Default Safety Rules

- Default to **additive organization only**
- Do not unstar repositories
- Do not remove repositories from lists
- Do not rename or delete lists
- If a repository is already in one or more lists, skip it by default
- Reuse existing lists before creating new ones
- Keep the final list system compact and reusable
- Prefer **one primary list** per repository
- Add a second list only when it clearly improves retrieval
- Add a third list only for genuine cross-domain repositories
- If confidence is not high, do not guess
- Report ambiguous repositories instead of forcing them into a weak category

If the user explicitly asks for reorganization that would modify existing assignments, ask for confirmation before changing any existing list membership.

## Operating Modes

- **Default mode: review-first**
  - analyze lists
  - analyze unlisted repositories
  - propose taxonomy and assignments
  - stop for confirmation before writing if ambiguity is material
- **Auto-apply mode**
  - only use when the user explicitly asks for direct execution
  - still stop if ambiguity is high or list count would exceed the cap

If the user did not clearly ask for immediate writes, prefer the default review-first mode.

## Primary Workflow

1. Open the target user's Stars page in the authenticated GitHub browser session.
2. Read **all existing lists first** and build a normalized map of:
   - list name
   - semantic meaning
   - probable duplicates or near-duplicates
3. Read **all starred repositories**.
   Important:
   - GitHub Stars pagination is cursor-based.
   - Follow the `Next` link/cursor.
   - Do not assume `page=N` is reliable.
4. For each starred repository, inspect its list membership.
5. Split repositories into:
   - already listed
   - unlisted
6. Only organize the **unlisted** repositories unless the user explicitly asks for broader reorganization.
7. Build a taxonomy plan:
   - strongly prefer existing suitable lists
   - create missing lists only when they are broad and reusable
   - avoid near-duplicate lists
8. Classify each unlisted repository by **primary intent**, not by incidental words in the description.
9. Assign a confidence level to each proposed placement:
   - high
   - medium
   - low
10. Keep the total number of lists ideally between **5 and 15**.
11. If the plan would require more than **15 total lists**, stop and ask the user whether the extra lists may be created.
   Include:
   - the exact proposed new list names
   - a short reason for each
12. If ambiguity is material, stop and ask the user before writing.
   Treat ambiguity as material when:
   - more than 10 repositories are medium/low confidence, or
   - more than 10% of unlisted repositories are medium/low confidence, or
   - many repositories appear to require a new category not yet approved by the user
13. Create any approved missing lists.
14. Add each unlisted repository to the smallest reasonable number of lists.
    Target:
   - usually 1 list
   - sometimes 2
   - rarely 3
15. Verify every repository after update by re-reading its current list membership.
16. Report:
   - lists reused
   - lists created
   - repositories added
   - repositories skipped because they were already organized
   - repositories intentionally left unassigned because confidence was too low
   - ambiguities or repos that may need user judgment

## Taxonomy Rules

- Prefer broad, stable themes over tiny one-off buckets
- New lists should usually represent a category that can hold multiple repositories
- Do not create a new list for fewer than 3 repositories unless the user explicitly wants that category
- Prefer **single-responsibility list names**
- Do not use compound list titles with `&`, `/`, or other bundled meanings unless the user explicitly asked for that style
- One list title should represent one retrieval concept
- Avoid trivial distinctions like:
  - `AI Agents` vs `Agent Frameworks` vs `Autonomous Agents`
  - `UI`, `Frontend`, `Web UI`, `Frontend Tools`
- Prefer merging into one broad list unless the distinction is genuinely useful for retrieval
- Good list systems usually include a mix of:
  - domain buckets
  - tooling buckets
  - reference/awesome/tutorial buckets
- Avoid creating language-only lists unless the user explicitly wants language-based organization

If the current taxonomy is missing an obvious stable category, create it only when it has a clear long-term use.

Examples of acceptable missing categories:

- `Web Tooling`
- `Build Tooling`
- `Auth`
- `Identity`
- `Browser Automation`

Examples of bad categories:

- `Random JS`
- `Stuff To Try`
- `Interesting Repos`
- `Tools 2`

## Better Algorithm

Use a two-pass planner:

1. **Reuse-first pass**
   Match every unlisted repository against existing lists before proposing anything new.

2. **Gap-creation pass**
   Create new lists only for clusters that:
   - do not fit an existing list cleanly
   - are broad enough to be useful again
   - help retrieve repositories later

This keeps the system stable and prevents uncontrolled list growth.

Also cap per-repository assignment density:

- prefer 1 list
- allow 2 when both are clearly helpful
- allow 3 only when the repository spans multiple major themes

This prevents over-tagging.

Add a **confidence gate**:

- high confidence:
  - repository name, description, and ecosystem all point to the same category
- medium confidence:
  - one strong clue exists, but there are plausible alternatives
- low confidence:
  - the repository could fit multiple categories equally well, or the description is too vague

Default write policy:

- auto-apply only high-confidence assignments
- ask the user before applying medium-confidence assignments in bulk
- never auto-apply low-confidence assignments

Add a **naming gate**:

- if a proposed new list name feels like two categories glued together, split it
- prefer `Frontend` and `Design Systems` over `Frontend & UX`
- prefer `Backend` and `Infrastructure` over `Backend & Infra`
- prefer `Learning` and `Reference` only if the user wants both as separate retrieval concepts; otherwise pick the one that best matches intent

## Classification Rules

Classify by the repository's **primary job**, not by stray words in its description.

Signal priority:

1. repository name
2. short description / tagline
3. project type and user
4. ecosystem and technology
5. only then secondary keywords

Negative rule:

- a repo is **not** backend just because it mentions `server`, `node`, `API`, or `auth`
- a repo is **not** frontend just because it has a UI or demo
- a repo is **not** learning/reference just because it has docs or examples
- a repo is **not** AI coding tooling just because it is used by developers
- a repo is **not** productivity just because it is an app

Use the category only when the category is the main value proposition.

## Category Intent

- `Learning`
  - use only for awesome-lists, tutorials, guides, courses, examples, templates, references, and educational starter material
  - do not use for mature runtimes, frameworks, products, or libraries unless their main role is educational

- `Frontend`
  - use for UI frameworks, component libraries, CSS systems, animation libraries, editors, design systems, browser interaction tooling, and clear front-end app frameworks
  - do not use for agent systems just because they have a UI

- `Backend`
  - use for APIs, databases, deployment stacks, observability systems, infrastructure platforms, queues, auth servers, server-side platforms, and operations tooling
  - do not dump generic developer tooling or web build tooling here by default

- `AI Coding Tools`
  - use for tools whose primary purpose is helping people write, inspect, run, review, or manage code with AI or developer automation
  - do not use for ordinary libraries, frameworks, or product apps

- `AI Agents`
  - use for agent runtimes, orchestration systems, agent operating environments, autonomous assistants, and multi-agent control planes
  - do not use for prompt collections, awesome-lists, or evaluation content unless the repo itself is an agent system

- `AI Skills & Prompts`
  - use for reusable prompts, skills, instruction packs, subagents, templates, and other composable prompting artifacts

- `RAG & Search`
  - use for retrieval, vector search, memory systems, embedding pipelines, indexing, semantic search, and knowledge retrieval

- `Productivity & Personal Tools`
  - use for end-user note apps, personal systems, automation tools, messaging bridges, utilities, and personal workflow software

Descriptions may be broader than titles, but the title itself should stay single-purpose.

If a repository does not fit an existing category cleanly, prefer:

- proposing a new stable list, or
- leaving it unassigned for review

instead of forcing it into the nearest broad bucket.

## GitHub-Specific Notes

- Read detailed implementation guidance in `references/algorithm.md`
- Read conservative classification guidance in `references/classification.md`
- The core repository membership endpoint is `/<owner>/<repo>/lists`
- Use that endpoint to detect whether a repository is already organized
- If a repository already has checked lists, skip it by default
- After adding list assignments, re-fetch the same menu and confirm the expected checked state

## When to Ask the User

Ask before proceeding only when one of these is true:

- the target account is unclear
- browser automation is unavailable
- Chrome remote debugging is not enabled
- the GitHub session is not authenticated
- more than 15 total lists would be needed
- ambiguity is high enough that bulk writes would likely create bad assignments
- a large number of borderline or duplicate list names already exist and safe reuse is unclear

## Critical Prohibitions

- Do not use a specific user's account as a hidden default
- Do not blindly create dozens of lists
- Do not destroy or rewrite existing organization without explicit permission
- Do not rely on `page=N` for GitHub Stars traversal
- Do not treat a repository as unlisted until its current list membership has been checked
- Do not classify by programming language alone
- Do not use `Learning & Reference` as a lazy fallback for uncertain repositories
- Do not classify a repository into `Backend & Infra` or `Frontend & UX` based on weak incidental keywords
