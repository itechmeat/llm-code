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

- `new`: start a change and scaffold structure.
- `continue`: create the next ready artifact.
- `apply`: implement tasks and update artifacts as needed.
- `sync`: reconcile delta specs with main specs.
- `archive`: finalize and move the change to archive.

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
