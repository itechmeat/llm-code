# OPSX Workflow (Experimental)

## Purpose

OPSX provides a fluid, iterative workflow for OpenSpec changes. It replaces rigid phases with flexible actions guided by artifact dependencies.

## Why OPSX Exists

- Hardcoded instructions are difficult to customize.
- One-shot batch commands are hard to test or iterate on.
- Fixed workflows do not fit all teams or codebases.
- OPSX enables schema-driven, editable prompts and dependency-aware progress.

## User Experience Principles

- Actions, not phases: you can update any artifact as you learn.
- Dependencies enable, they do not gate.
- Iteration is expected: adjust proposals, specs, and design during implementation.

## Commands (Typical)

- `status`: inspect what exists and what is ready; safe even before the first change exists.
- `new`: start a change and scaffold structure.
- `continue`: create the next ready artifact.
- `apply`: implement tasks and update artifacts as needed.
- `sync`: reconcile delta specs with main specs.
- `archive`: finalize and move the change to archive.

### Status behavior (v1.3.0)

- `openspec status` now exits gracefully when no changes exist instead of failing hard.
- Use it as a safe preflight check before telling the operator to create a new change or continue an existing one.

## Profiles and the “Propose” Workflow (v1.2.0)

### Workflow profiles

OpenSpec v1.2.0 adds **workflow profiles** to control which workflows/commands are installed for your AI tool(s):

- Use `openspec config profile` to review/change delivery + workflows.
- Fast preset: `openspec config profile core` (minimal essential workflows).
- To apply your selected workflows to a project’s installed command/skill files, run `openspec update`.

### All-at-once propose (legacy)

If you want to generate the full planning set in one request (proposal + specs + design + tasks), OpenSpec provides the legacy slash command:

- `/openspec:proposal`

This is conceptually similar to doing `/opsx:new` and then `/opsx:ff`, but in a single step. Prefer OPSX for incremental control; use the legacy command when you intentionally want “all planning artifacts now”.

## Choosing Update vs New Change

Update the existing change when:

- Intent remains the same and you are refining execution.
- Scope narrows or is clarified.
- Learning reveals corrections to design or specs.

Start a new change when:

- Intent or core problem shifts materially.
- Scope expands beyond recognition.
- The original change can be completed independently.

## Dependency Model

- Artifacts form a DAG: `proposal → specs → design → tasks` (default schema).
- Blocked artifacts show unmet dependencies.
- Ready artifacts are those with all dependencies complete.

## Communication Guidelines

- Explicitly name the change when invoking commands.
- Show progress and what is unlocked after each step.
- If schema selection is ambiguous, clarify before continuing.

## Task Tracking Format

- Use checklist items in tasks artifacts.
- Required format for apply tracking: `- [ ]` for pending and `- [x]` for done.
