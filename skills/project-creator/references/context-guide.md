# Project Context Guide

## Purpose

The `project-context.md` file is a cumulative document that captures important decisions, learnings, and context throughout the project lifecycle.

## Key Characteristics

- **Living document**: Updated continuously as project evolves
- **Historical record**: Captures the "why" behind decisions
- **Onboarding tool**: Helps new team members understand context
- **Optional at start**: Can have minimal content initially

## Creation Workflow

### Initial Setup

1. **Explain the purpose**
   - "This document will grow over time"
   - "It captures decisions and learnings"
   - "Think of it as the project's memory"

2. **Start with basics**
   - Any known constraints not in specs.md
   - Initial assumptions to track
   - Team knowledge to preserve

3. **Set expectations**
   - Will be sparse at start
   - Should be updated regularly
   - Remind user to add entries

### Questions for Initial Content

1. **Are there any decisions already made?**
   - Technology choices with reasoning
   - Design decisions
   - Business constraints

2. **What assumptions are being made?**
   - About users
   - About scale
   - About requirements

3. **What domain knowledge is needed?**
   - Industry terms
   - Business processes
   - Stakeholder preferences

4. **Are there known external dependencies?**
   - Third-party services
   - APIs with quirks
   - Integration requirements

## When to Update

Remind user to update when:
- A significant decision is made
- An assumption proves wrong
- A non-obvious solution is found
- External dependency behavior is discovered
- Performance baselines are established

## Entry Format

Each significant entry should include:
- **Date**: When the decision/discovery was made
- **Context**: What situation led to this
- **Decision/Learning**: What was decided or discovered
- **Rationale**: Why this conclusion
- **Consequences**: What follows from this

## Section Purposes

### Key Decisions
Major choices that shape the project. Include alternatives considered and why they were rejected.

### Learnings & Discoveries
Non-obvious findings during development. Saves time for future developers.

### Assumption Changes
Track when initial assumptions proved incorrect. Helps understand project evolution.

### External Dependencies Notes
Undocumented behaviors, workarounds, and gotchas for third-party services.

### Team Knowledge
Tribal knowledge that should be documented. Onboarding information.

### Performance Baselines
Recorded metrics to compare against. Helps identify regressions.

### Integration Notes
Setup instructions and pitfalls for integrations.

### Future Considerations
Deferred items, technical debt, enhancement ideas.

## Completion Criteria

At project start:
- [ ] Basic structure is in place
- [ ] Any pre-existing decisions are documented
- [ ] Initial assumptions are listed
- [ ] User understands the purpose
- [ ] User knows when to update

This document is never "complete" — it grows with the project.

## Sample Prompts

- "Have any decisions already been made about this project?"
- "What assumptions are we making about the users?"
- "Are there any external services we need to integrate with?"
- "Is there domain-specific terminology we should document?"
- "What should a new team member know on day one?"
