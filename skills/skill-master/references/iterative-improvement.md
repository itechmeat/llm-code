# Iterative Improvement Workflow

Use this reference when the task is not just "write a skill", but to iteratively shape, test, benchmark, and improve it until the results are good enough.

## Scope

This workflow covers the full loop that `skill-creator` handled:

- capture intent from the conversation
- draft or revise the skill
- define eval prompts
- run with-skill and baseline executions
- grade and benchmark the results
- collect user feedback in the viewer
- improve the skill and repeat

## 1. Capture Intent Before Writing

Before editing the skill, extract what is already known from the conversation:

- what the skill should enable
- when it should trigger
- what output or artifact matters most
- whether success is objectively testable

If the user already demonstrated a working workflow in chat, treat that transcript as source material for the first draft.

## 2. Interview for Missing Constraints

Fill gaps before inventing evals.

High-value questions:

- Which edge cases are costly or common?
- Which inputs or example files should be supported?
- What counts as a clear failure?
- What output format is required?
- Which parts should be automated with scripts instead of prose?

Prefer concrete examples over abstract preferences.

## 3. Draft the Skill First

Create or revise the skill so it has:

- strong frontmatter (`name`, `description`, version info as needed)
- a concise `SKILL.md` that routes to references/scripts/assets
- scripts only where determinism or reuse matters
- assets/templates only when the agent should copy something verbatim

Do not wait for a perfect draft before testing. A good first draft plus evals gives better signal than overthinking the prose.

## 4. Create Realistic Evals

Start with 2-3 prompts that sound like real user requests. Save them to `evals/evals.json`.

Good evals:

- represent common or high-risk tasks
- include file inputs when the workflow depends on them
- state expected outputs in plain language
- include only discriminating expectations

Avoid assertions that would pass for shallow or hallucinated outputs.

## 5. Run Skill and Baseline Together

When comparing behavior, launch both configurations in the same pass:

- `with_skill`: the current skill under test
- baseline: either `without_skill` for a new skill, or a snapshot of the pre-edit skill for an improvement pass

Keep each eval in its own directory under an iteration workspace, for example:

```text
<skill>-workspace/
  iteration-1/
    eval-0/
      with_skill/
      without_skill/
```

If you need a human-readable label, store it in `eval_metadata.json` next to the run.

## 6. Draft Assertions While Runs Are Active

Do not idle while runs are executing. Use that time to refine assertions.

Assertions should check outcomes that matter:

- correctness of the produced artifact
- required sections, fields, or schema
- evidence that critical steps actually happened

If a task is subjective, keep the benchmark light and rely more on qualitative review.

## 7. Capture Timing Immediately

When execution notifications expose token or duration data, save it at once to `timing.json`. That data is transient and should be preserved before moving on.

Recommended fields:

- `total_tokens`
- `duration_ms`
- `total_duration_seconds`
- executor/grader start and end timestamps when available

## 8. Grade, Aggregate, and Review

After runs complete:

1. Grade each run with `agents/grader.md` and save `grading.json`.
2. Aggregate benchmark results with `scripts/aggregate_benchmark.py`.
3. Review patterns with `agents/analyzer.md`.
4. Generate the qualitative review UI with `eval-viewer/generate_review.py`.

The viewer is the handoff point for human judgment:

- browse outputs per eval
- inspect formal grades
- compare against the previous iteration
- leave freeform feedback

## 9. Read Feedback and Generalize

When the user finishes review, ingest their feedback before editing the skill again.

Do not overfit to a single prompt. Translate specific complaints into general guidance:

- remove ambiguous instructions that caused drift
- add scripts when repeated manual work appears across evals
- tighten descriptions when triggering is weak
- add or improve assertions when the benchmark missed obvious defects

Aim for improvements that would help on unseen prompts, not just the current eval set.

## 10. Repeat Until Signal Flattens

Run another iteration when:

- the user found concrete issues
- the benchmark still shows unstable results
- baseline and with-skill outputs are too close to justify the skill

Stop when:

- user feedback is effectively empty
- the skill consistently beats baseline on the important evals
- new iterations no longer produce meaningful gains

## Practical Rules

- Run with-skill and baseline in parallel so comparisons are fair and faster.
- Keep eval names descriptive; avoid anonymous `eval-0` labels in user-facing reports when a real name is available.
- Preserve previous outputs so the viewer can show iteration-over-iteration differences.
- Prefer programmatic grading for things that can be checked mechanically.
- Use qualitative review for tone, design quality, and other subjective outcomes.

## Failure Modes to Watch

- Overfitting the skill to 2-3 prompts
- Weak assertions that reward superficial compliance
- Benchmark files with field names that do not match the viewer schema
- Improving only the description when the real issue is missing scripts or missing structure
- Letting the skill bloat instead of routing detail into `references/`
