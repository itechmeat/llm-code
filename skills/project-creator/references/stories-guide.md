# Stories Guide

## Purpose

Stories document features and requirements in a structured, prioritized format ready for implementation planning.

## Two-Level Structure

1. **stories.md** — Master list of all stories with status and priorities
2. **NNN-story-name.md** — Individual story files with full details

## Creation Workflow

### Phase 1: Story Discovery

1. **Review existing documents**
   - Features from about.md
   - Capabilities implied by specs.md
   - Components from architecture.md

2. **Ask about priorities**
   - "What's absolutely essential for launch?"
   - "What can wait until later?"
   - "What's the logical order?"

3. **Identify dependencies**
   - "Does story X need story Y first?"
   - Group related stories
   - Find parallel tracks

### Phase 2: Story List Creation

4. **Create stories.md**
   - List all identified stories
   - Assign numbers (001, 002, etc.)
   - Set initial statuses (mostly Draft)
   - Note dependencies

5. **Prioritize together**
   - MVP vs. later phases
   - High/Medium/Low within phases
   - User validates priority

### Phase 3: Individual Story Files

6. **Focus on first story**
   - Must be well-defined before development starts
   - Complete acceptance criteria
   - Clear scope boundaries

7. **Sketch remaining stories**
   - Basic user story format
   - Initial acceptance criteria
   - Note that details will evolve

## Story Naming Convention

```
NNN-descriptive-name.md
```

- **NNN**: Three-digit number (001, 002, 010, 100)
- **descriptive-name**: Kebab-case, meaningful name
- Numbers don't have to be sequential

Examples:
- `001-user-authentication.md`
- `002-dashboard-layout.md`
- `010-notification-system.md`

## Story Quality Criteria

### Good Story
- Clear user benefit ("so that...")
- Testable acceptance criteria
- Bounded scope
- Known dependencies

### Bad Story
- Technical task without user context
- Vague acceptance criteria
- Unbounded scope ("and also...")
- Missing dependencies

## Acceptance Criteria Format

Each criterion should be:
- **Specific**: Clear what to verify
- **Measurable**: Can be objectively checked
- **Testable**: Can be demonstrated

Examples:
```markdown
✅ Good:
- [ ] User can upload images up to 10MB in PNG, JPG, or GIF format
- [ ] Upload progress is shown with percentage
- [ ] Error message appears if file exceeds size limit

❌ Bad:
- [ ] Image upload works
- [ ] Good user experience
- [ ] Fast performance
```

## Story Evolution

### First story (before development)
- Complete and detailed
- All acceptance criteria defined
- Technical notes included
- No open questions

### Later stories (can evolve)
- Basic structure present
- User story defined
- Initial acceptance criteria
- May have open questions
- Will be refined before implementation

## Questions to Ask

### For story list:
- "What features were mentioned in the about.md?"
- "What would make the MVP complete?"
- "What's nice-to-have vs. must-have?"

### For individual stories:
- "Who is the user for this feature?"
- "What triggers this action?"
- "What's the happy path?"
- "What could go wrong?"
- "How will we know it's done?"

## Completion Criteria

### stories.md is ready when:
- [ ] All known stories are listed
- [ ] Priorities are assigned
- [ ] MVP stories are identified
- [ ] Dependencies are mapped
- [ ] User confirms completeness

### First story is ready when:
- [ ] User story is clear
- [ ] All acceptance criteria are testable
- [ ] Scope boundaries are set
- [ ] No blocking open questions
- [ ] User confirms readiness

### Other stories are ready when:
- [ ] Basic user story exists
- [ ] Initial acceptance criteria listed
- [ ] User understands they'll evolve
