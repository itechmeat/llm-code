# Conservative Classification Rules

This reference exists to prevent low-quality list assignments.

The previous common failure mode was simple keyword matching that pushed repositories into broad buckets such as `Frontend & UX`, `Backend & Infra`, or `Learning & Reference` for weak reasons.

## Core Principle

Classify the repository by its **primary retrieval value**:

- why the user would want to find it later
- what job the repository mainly does
- what kind of thing it fundamentally is

Not:

- a random word in the description
- the implementation language
- the fact that it contains docs, demos, or examples
- the fact that developers might use it

## Confidence Model

Every proposed assignment should carry a confidence level.

## High Confidence

Use high confidence only when most signals align:

- repository name strongly indicates category
- description strongly indicates category
- repository type matches category
- no strong competing category exists

Example:

- `awesome-webauthn` -> `Learning & Reference`
- `agent-orchestrator` -> `AI Agents`
- `react-draft-wysiwyg` -> `Frontend & UX`

## Medium Confidence

Use medium confidence when:

- one or two signals suggest a category
- but another category is also plausible

Medium-confidence repos should usually be shown to the user before bulk apply unless the user explicitly wants aggressive automation.

## Low Confidence

Use low confidence when:

- the repo description is vague
- multiple categories are plausible
- the repo is a mixed product
- the category fit depends on assumptions

Low-confidence repos should not be auto-assigned.

## Anti-Randomness Rules

### Keep List Names Single-Purpose

Do not hide uncertainty inside compound list titles.

Bad:

- `Frontend & UX`
- `Backend & Infra`
- `Learning & Reference`

Better:

- `Frontend`
- `UX`
- `Backend`
- `Infrastructure`
- `Learning`
- `Reference`

If the category still feels ambiguous after splitting the name, the repository likely needs human review or a different taxonomy.

### Do Not Use Language as a Category Proxy

Bad:

- TypeScript -> `Frontend & UX`
- Python -> `Backend & Infra`
- Shell -> `Learning & Reference`

Language is almost never enough.

### Do Not Use Docs Presence as a Reference Signal

A runtime, framework, or product often has:

- docs
- examples
- demos

That does **not** make it `Learning & Reference`.

### Do Not Use Vague Infra Words

Words like these are weak on their own:

- `server`
- `node`
- `API`
- `platform`
- `tooling`
- `system`

Use `Backend & Infra` only when the repo is clearly an infrastructure or backend platform.

### Do Not Use Vague Frontend Words

Words like these are weak on their own:

- `dashboard`
- `app`
- `design`
- `visual`
- `browser`

Use `Frontend & UX` only when the repo is clearly about UI, web interaction, browser UX, front-end frameworks, or front-end components.

## Category Boundaries

## Learning & Reference

Use when the repo is mainly:

- an awesome-list
- a guide
- a tutorial
- a course
- a reference
- a starter meant primarily for learning
- an examples collection

Do not use when the repo is mainly:

- a production framework
- a runtime
- a real product
- a standalone app
- a utility library

## Frontend & UX

Use when the repo is mainly:

- a UI framework
- a component library
- a design system
- a browser-side interaction library
- an animation library
- a front-end editor
- CSS or layout tooling

Do not use when the repo is mainly:

- an agent platform with a UI
- a build system that is not specifically front-end oriented
- a general productivity app

## Backend & Infra

Use when the repo is mainly:

- a backend framework
- a database
- an auth server
- deployment infrastructure
- observability
- orchestration infrastructure
- queues, workers, storage, infra services

Do not use when the repo is mainly:

- front-end tooling
- a developer utility
- a reference list
- an app with a backend

## AI Coding Tools

Use when the repo is mainly:

- a coding assistant tool
- code review / code generation tooling
- an IDE or CLI companion for coding
- a code intelligence tool
- a build/run/test developer tool tightly tied to coding workflows

Do not use when the repo is mainly:

- a general library
- a front-end framework
- a backend platform
- an end-user app

## AI Agents

Use when the repo is mainly:

- an agent runtime
- an orchestrator
- an assistant platform
- a multi-agent system
- an autonomous task execution environment

Do not use when the repo is mainly:

- an awesome-list of agents
- prompts/skills only
- evaluation rules

## When to Propose a New List

If many repositories do not fit existing categories cleanly, propose a new list instead of forcing them into the wrong one.

Examples of legitimate new lists:

- `Web Tooling`
- `Build Tooling`
- `Auth`
- `Identity`
- `Browser Automation`

Only propose a new list when:

- at least 3 repositories would fit it now, or
- it is obviously a durable recurring category

## Ambiguity Escalation

Stop and ask the user if:

- a cluster of repos does not fit current lists cleanly
- many repos are medium/low confidence
- a new category is clearly needed but not yet approved

It is better to leave a repo unassigned than to poison the taxonomy.
