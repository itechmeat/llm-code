# Description Optimization

This reference covers iteratively improving a skill's description for better trigger accuracy.

## Why Optimize Descriptions

The description in SKILL.md frontmatter is the primary signal the LLM uses to decide whether to load a skill. A poorly written description causes:

- **False negatives**: Skill not loaded when it should be (user asks a relevant question but the description doesn't match)
- **False positives**: Skill loaded for unrelated queries (wastes context, may confuse the agent)

## The Optimization Process

### 1. Create an Eval Set

Build `evals/evals.json` with test queries (see `references/eval-testing.md`):

- **Should-trigger queries**: Prompts where the skill should activate (diverse phrasing, edge cases)
- **Should-not-trigger queries**: Prompts that sound related but shouldn't activate the skill

Aim for at least 20 queries with a 60/40 split (trigger/no-trigger).

### 2. Run the Improve Loop

```bash
python -m scripts.run_loop --skill-path <path> --iterations 5
```

Each iteration:

1. Tests the current description against all eval queries
2. Identifies misclassifications (false positives and false negatives)
3. Generates an improved description using analysis of failures
4. Compares old vs new via blind comparison
5. Keeps the winner

### 3. Manual Description Improvement

Use `scripts/improve_description.py` for a single improvement step:

```bash
python -m scripts.improve_description --skill-path <path> --feedback "too many false positives on database queries"
```

This sends the current description + feedback to Claude and produces a revised description.

## Writing Better Descriptions

### Trigger Keywords

For Claude Code (keyword-based discovery):

```yaml
description: "Turso SQLite database. Covers encryption, sync, agent patterns. Keywords: Turso, libSQL, SQLite."
```

For Claude.ai (trigger-phrase discovery):

```yaml
description: "Creates Word documents. Use when user asks to create, edit, or export .docx files, format reports, or generate letters."
```

### Common Failure Patterns

| Pattern            | Symptom                | Fix                                           |
| ------------------ | ---------------------- | --------------------------------------------- |
| Too generic        | Triggers on everything | Add specific product/domain keywords          |
| Too narrow         | Misses valid queries   | Add "Use when..." trigger phrases             |
| Marketing language | Unreliable triggering  | Remove "powerful", "comprehensive" etc.       |
| Missing keywords   | Specific queries miss  | Add product names, file extensions, CLI names |

### Description Length

- **Target**: 80-150 characters for simple skills
- **Max**: 1024 characters for complex skills with many trigger patterns
- **Sweet spot**: 150-300 characters covering WHAT + WHEN + KEYWORDS

## Train/Test Split Strategy

When optimizing descriptions, split evals into:

- **Train set** (70%): Used during improvement iterations to guide changes
- **Test set** (30%): Held out to verify the description generalizes

If the description improves on train but regresses on test, it's overfitting to specific phrasings.

## Monitoring Quality

After optimization, track:

- **Trigger precision**: % of activations that were correct
- **Trigger recall**: % of relevant queries that activated the skill
- **F1 score**: Harmonic mean of precision and recall

Use `scripts/aggregate_benchmark.py` to compute these across multiple runs.

## Iteration Strategy

1. **Iteration 1-2**: Fix obvious gaps (missing keywords, wrong trigger phrases)
2. **Iteration 3-4**: Fine-tune boundary cases (similar skills, ambiguous queries)
3. **Iteration 5+**: Diminishing returns — stop when test set performance plateaus

Typical improvement: 60% → 85% trigger accuracy in 3-5 iterations.
