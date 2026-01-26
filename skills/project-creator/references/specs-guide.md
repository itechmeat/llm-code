# Specs.md Guide

## Purpose

The `specs.md` file defines all technical requirements, technology choices, and quality standards for the project.

## Critical Rule

> ⚠️ **VERSION POLICY**: Downgrading package versions is **FORBIDDEN**. Upgrading is allowed.

Always specify latest stable versions. If a newer version is incompatible, document the reason and provide alternatives.

## Creation Workflow

### Phase 1: Technology Stack Questions

1. **Frontend (if applicable)**
   - What frameworks/libraries? (React, Vue, Angular, etc.)
   - Styling approach? (CSS-in-JS, Tailwind, etc.)
   - State management needs?
   - Suggest latest stable versions for each

2. **Backend (if applicable)**
   - Runtime environment? (Node.js, Python, Go, etc.)
   - Framework preferences?
   - API style? (REST, GraphQL, gRPC)

3. **Database**
   - SQL or NoSQL needs?
   - Data volume expectations?
   - Real-time requirements?

4. **Infrastructure**
   - Hosting preferences? (Cloud provider, self-hosted)
   - CI/CD requirements?
   - Containerization needs?

### Phase 2: Requirements Questions

5. **Performance**
   - Response time expectations?
   - Expected load/users?
   - Availability requirements?

6. **Security**
   - Authentication method?
   - Authorization model?
   - Compliance needs? (GDPR, HIPAA, etc.)

7. **Quality Standards**
   - Code style preferences?
   - Testing requirements?
   - Code review process?

### Phase 3: Environment & Tools

8. **Development Environment**
   - Team's current tools?
   - IDE preferences?
   - Required development tools?

9. **Deployment**
   - How many environments?
   - Deployment frequency?
   - Rollback strategy?

## Helping Non-Technical Users

When user lacks technical knowledge:

1. **Explain options simply**
   - "React is great for interactive UIs, Vue is simpler to learn"
   - "PostgreSQL is reliable for structured data, MongoDB for flexible schemas"

2. **Make recommendations**
   - Based on project requirements from about.md
   - Consider team expertise
   - Prioritize maintainability

3. **Explain trade-offs**
   - Performance vs. simplicity
   - Feature richness vs. learning curve
   - Cost vs. scalability

## Version Research

Before specifying versions:
1. Check official documentation for latest stable
2. Verify compatibility between technologies
3. Note any known issues or deprecations

## Completion Criteria

- [ ] All technologies have specified versions
- [ ] Performance requirements are quantified
- [ ] Security requirements are documented
- [ ] Quality standards are defined
- [ ] Development tools are listed
- [ ] Deployment strategy is outlined
- [ ] User understands and agrees with choices

## Sample Questions

- "What devices/browsers must be supported?"
- "How many concurrent users do you expect?"
- "Is there existing infrastructure to integrate with?"
- "What's the team's experience with [technology]?"
- "Are there any compliance requirements?"
- "How often do you need to deploy updates?"
- "What's your acceptable downtime?"
