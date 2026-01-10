# Docs Ingestion Workflow

Autonomous workflow for creating skills from external documentation.

## When to Use

- Building a skill from vendor docs (multiple pages)
- Entry links are section pages with many sub-pages
- Want agent to ingest sequentially without asking after each page
- Goal is a practical playbook, not a docs mirror

## Output Structure

```
<skill-name>/
├── SKILL.md           # High-signal entry point
├── plan.md            # Progress tracking (temporary)
└── references/
    ├── concepts.md
    ├── api.md
    └── ...
```

## Phase 1: Scaffold

1. Create skill folder
2. Create `SKILL.md` with skeleton frontmatter
3. Create `plan.md` using checkbox format
4. Create `references/` directory

The skill should be valid even before ingestion starts.

## Phase 2: Build Ingestion Queue

For each provided doc link:

**If section/landing page:**

1. Fetch the page
2. Extract internal doc links (skip navigation duplicates)
3. Add content pages to queue

**If single doc page:**

- Add directly to queue

### Queue Prioritization

Prefer order: concepts → API → operations → troubleshooting

Prioritize pages answering:

- Data model decisions
- Integration patterns
- Failure modes and recovery
- Production deployment notes

### Queue Rules

- De-duplicate URLs
- Skip non-content pages (nav, footer links)
- Limit to relevant documentation scope

## Phase 3: Ingest Loop

**Repeat until queue is empty:**

### Step 1: Fetch One Page

Use `ai_fetch_url` or similar tool.

### Step 2: Create Reference Note

Create `references/<topic>.md`:

```markdown
# <Page Title>

Source: <URL>

## What this page is about

- 1-3 bullets

## Actionable takeaways

- 5-15 bullets of practical guidance

## Gotchas / prohibitions

- 0-7 bullets

## How to apply in a real repo

- 3-6 bullets
```

### Step 3: Update plan.md

- Mark checkbox as completed
- Add new unchecked items if page reveals sub-topics

### Step 4: Update SKILL.md (Conditionally)

Only update if it improves the practical playbook:

- Add a recipe
- Add a checklist
- Add an explicit rule of thumb

**Do NOT ask user after each page** — continue autonomously.

## Phase 4: Finalize

When queue is empty:

1. Review `SKILL.md` for:

   - Minimal mental model
   - Practical recipes
   - Ops runbook/checklists
   - Clear definition of done

2. Verify `plan.md` reflects what was ingested

3. Check file naming is consistent

**Note:** `plan.md` may be deleted manually after ingestion. Agent must NOT delete it automatically.

## Quality Gate

### Do

- Summarize in your own words
- Focus on what helps build/operate/debug
- Include practical examples
- Keep `SKILL.md` as router to references

### Do NOT

- Replicate documentation structure just because it exists
- Keep long code samples unless essential
- Introduce project-specific paths or secrets
- Create verbatim docs mirrors

## Plan Template

```markdown
# <Skill Name> Plan

Progress tracking for docs ingestion.

## Queue

- [ ] Initial seed links
- [ ] Expand section pages

## Foundation

- [ ] Concepts / mental model
- [ ] Installation / quickstart
- [ ] Data model

## Integration

- [ ] SDK/client usage
- [ ] Authentication
- [ ] Error handling

## Operations

- [ ] Deployment
- [ ] Monitoring
- [ ] Troubleshooting
```

## Reference Note Template

```markdown
# <Page Title>

Source: <URL>

## What this page is about

- <1-3 bullets>

## Actionable takeaways

- <5-15 bullets>

## Gotchas / prohibitions

- <0-7 bullets>

## How to apply in a real repo

- <3-6 bullets>
```
