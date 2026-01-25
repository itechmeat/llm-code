# Experimental Release Plan (OPSX)

## Scope and Intent

- Preserve existing OpenSpec commands.
- Introduce an experimental, granular artifact workflow.
- Enable cross-editor usage via Agent Skills.

## Key Work Items

1. Rename AWF commands to OPSX (new/continue).
2. Remove obsolete WF skill files.
3. Add Agent Skills for experimental workflow.
4. Update OPSX command content.
5. End-to-end testing of skills workflow.
6. User-facing docs and feedback loop.

## Experimental Skills Behavior

- Skills are generated to `.claude/skills/` and discovered by compatible editors.
- Expected skills include:
  - openspec-new-change
  - openspec-continue-change
  - openspec-apply-change

## Validation Checklist

- Skill files generated and detected.
- Dependency detection works in `status` and `next`.
- Templates are meaningful and actionable.
- Schemas other than spec-driven work.
- Documentation exists with setup and usage examples.

## Non-Goals

- No batch mode refactor of legacy commands.
- No new schemas beyond existing defaults.
- No editor-specific configurators.

## User Communication

- Emphasize experimental status.
- Provide clear setup instructions.
- Provide a feedback channel.
