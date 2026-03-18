# GitHub Stars Organizer Algorithm

This reference documents a safe, repeatable workflow for organizing GitHub starred repositories with browser automation.

## Goal

Create or reuse a compact list system so starred repositories become easy to find later.

Default operating mode:

- only organize repositories that are not yet in any list
- preserve all existing organization
- add, do not subtract
- prefer review-first over blind bulk writes

## Required Environment

- Authenticated GitHub session in a local browser
- Browser automation via `chrome-cdp` or equivalent
- Chrome remote debugging enabled

If the browser tool cannot read and interact with the live GitHub session, stop.

## Remote Debugging Instructions

For Chrome or Chromium-based browsers:

1. Open `chrome://inspect/#remote-debugging`
2. Enable remote debugging
3. Confirm the local endpoint is available, typically `127.0.0.1:9222`
4. Open GitHub in that same browser profile
5. Approve any one-time Chrome "Allow debugging" prompt for the GitHub tab

## Data Collection Order

Always collect data in this order:

1. Existing lists
2. All starred repositories
3. Current list membership for each repository
4. Candidate taxonomy updates
5. New list creation
6. Repository additions
7. Verification

This order matters because existing lists should shape the plan before any new lists are proposed.

## Default Execution Policy

Use this policy unless the user explicitly asks for aggressive direct execution:

1. analyze existing lists
2. analyze all unlisted repositories
3. build a proposed mapping
4. identify ambiguous repositories
5. stop for confirmation if ambiguity is material
6. only then write changes

Ambiguity is material when:

- more than 10 repositories are medium/low confidence, or
- more than 10% of unlisted repositories are medium/low confidence, or
- the taxonomy would need several new lists to stay coherent

## Existing Lists

Start by reading all current lists and normalize names conceptually.

Look for:

- exact duplicates
- near-duplicates
- singular/plural variants
- wording variants with the same retrieval purpose

Examples of near-duplicates:

- `AI Tools` and `AI Tooling`
- `Frontend` and `Frontend & UX`
- `Learning`, `Tutorials`, `Reference`

Do not create new lists that overlap heavily with these.

Also infer what each existing list is really meant to contain. Use repository samples from that list, not just the list title.

## Traversing Stars

GitHub Stars uses cursor-based pagination.

Do this:

- open the Stars page
- read repository cards on the current page
- follow the `Next` link href/cursor
- continue until there is no `Next`

Do not do this:

- do not rely on `page=1`, `page=2`, etc.
- do not assume every page URL can be synthesized safely

## Repository Membership Check

Each repository has a list-menu endpoint:

`/<owner>/<repo>/lists`

Use it to determine:

- repository id
- list form action
- CSRF/authenticity token
- current checked list ids

If one or more list checkboxes are already checked:

- treat the repository as already organized
- skip it by default

Only include it in the plan if the user explicitly asked for deeper reorganization.

This is non-negotiable in additive mode.

## Planning Rules

For unlisted repositories:

1. Try to map them into existing lists first.
2. Group the leftovers into broad reusable clusters.
3. Create new lists only for those clusters.

Before assigning a repository, determine its:

- primary job
- likely future retrieval need
- confidence level

If the category fit is weak, leave it unassigned for review.

Good new lists:

- broad enough to be reused
- distinct from current lists
- useful as search buckets later
- likely to hold at least 3 repositories now or soon
- named around one clear concept

Bad new lists:

- one-off lists for a single repository
- overly narrow technology splits
- lists that repeat the meaning of an existing list
- vague catch-all lists
- compound names that bundle multiple retrieval concepts together

## List Count Guardrail

Target total list count:

- ideal: 5 to 15

Rules:

- if the current system is already within that range, prefer reuse over creation
- if new list creation would push the total over 15, stop and ask the user

When asking the user, present:

- proposed new list names
- why each is needed
- how many repositories each would likely contain

## Naming Guardrail

Prefer single-purpose list titles.

Good:

- `Frontend`
- `Backend`
- `Infrastructure`
- `Learning`
- `Reference`
- `Browser Automation`
- `Build Tooling`

Bad:

- `Frontend & UX`
- `Backend & Infra`
- `Learning & Reference`
- `Tools / Utilities`

If a name needs `&` to make sense, it is usually hiding two categories.

## Assignment Density

Per repository:

- prefer 1 list
- allow 2 if both are clearly useful
- allow 3 only for genuine cross-category repositories

Avoid tagging a repository into many lists. The goal is retrieval, not exhaustive ontology.

Default tagging policy:

- one list when possible
- two only when both materially improve retrieval
- three only for truly cross-domain repositories
- zero is acceptable when confidence is too low

## Safe Update Pattern

When adding a repository to lists:

1. Read the repository's current list form from `/<owner>/<repo>/lists`
2. Compute desired list ids
3. Submit the update
4. Re-fetch `/<owner>/<repo>/lists`
5. Verify checked ids match expectation

If operating in default additive mode, desired list ids are just the new target lists because the repo started unlisted.

If later extending this skill for editing already-listed repos, preserve the existing checked ids unless the user explicitly approved reassignment.

## Conservative Classification

Read `references/classification.md` before applying assignments.

Mandatory rules:

- classify by primary intent, not incidental keywords
- do not classify by implementation language
- do not dump vague repos into `Learning & Reference`
- do not treat general web tooling as `Backend & Infra` by default
- do not treat every repo with a UI as `Frontend & UX`

Use high confidence only when the name, description, and repo type all point to the same category.

## Suggested Default Taxonomy

Do not hardcode this taxonomy, but it is a useful baseline when the account has no lists yet:

- `AI Agents`
- `AI Coding Tools`
- `AI Skills & Prompts`
- `AI Safety & Evals`
- `RAG & Search`
- `Frontend & UX`
- `Backend & Infra`
- `Productivity & Personal Tools`
- `Learning & Reference`

This is a strong default because it is:

- broad
- stable
- discoverable
- well under the 15-list cap

But it is still only a baseline.

If a repository cluster clearly does not fit these buckets, propose a better reusable list instead of forcing the fit.

Example:

- `webpack`, `vite`, bundler plugins, and web build analyzers may justify `Build Tooling` or `Web Tooling`

## Reporting

Final report should include:

- total starred repositories processed
- existing lists reused
- new lists created
- repositories added
- repositories skipped because they already had lists
- repositories withheld because confidence was too low
- any ambiguous cases

If there were no changes, say why:

- no unlisted repositories
- all unlisted repos already fit existing lists after inspection plan
- user did not approve exceeding the list cap

## Failure Cases

Stop and explain the blocker if:

- browser automation cannot attach to the GitHub tab
- the user is not logged into GitHub
- GitHub returns list menu pages that cannot be parsed
- Chrome remote debugging is disabled
- the required tool is missing

Do not guess around these failures.
