# Eval Testing & Benchmarking

This reference covers running evals, grading outputs, benchmarking skill quality, and the eval+improve loop.

## Concepts

- **Eval**: A test case with a prompt, optional input files, and expectations (verifiable assertions)
- **Grading**: Automated check of execution output against expectations
- **Benchmark**: Multiple runs per configuration (with/without skill) to measure variance
- **Improve loop**: Iterative cycle of eval → grade → analyze → improve description/instructions

## Directory Structure

```
<skill>/
├── evals/
│   ├── evals.json          # Eval definitions (see references/schemas.md)
│   └── files/              # Input files referenced by evals
├── benchmarks/
│   └── <timestamp>/
│       └── benchmark.json  # Benchmark results
└── workspace/              # Temporary execution workspace
```

## Writing Good Evals

1. **Diverse prompts**: Cover common use cases, edge cases, and should-not-trigger scenarios
2. **Specific expectations**: "Output contains table with column 'Name'" not "Output looks good"
3. **Verifiable assertions**: Each expectation should be checkable from the execution transcript
4. **Balance**: Include both should-trigger and should-not-trigger queries
5. **File-dependent evals**: Reference input files in `evals/files/` for tasks requiring data

## Running Evals

Use `scripts/run_eval.py` to execute evals:

```bash
python -m scripts.run_eval --skill-path <path> --eval-ids 1,2,3 --workers 2
```

This runs each eval via `claude -p` with stream-json output, captures the execution transcript, and saves outputs to the run directory.

**Parallel execution**: Use `--workers N` to run multiple evals concurrently (default: 1). Each worker spawns a separate `claude` process.

## Grading

The grader agent (`agents/grader.md`) evaluates execution output against expectations:

- Reads the execution transcript and output files
- Checks each expectation, providing pass/fail with evidence
- Produces `grading.json` (see `references/schemas.md`)

## Benchmarking

Use `scripts/aggregate_benchmark.py` to compute statistics across multiple runs:

```bash
python -m scripts.aggregate_benchmark --benchmark-dir benchmarks/<timestamp>
```

This reads all `grading.json` files from the benchmark directory and computes:

- Mean, stddev, min, max for pass rate per configuration
- Time and token usage statistics
- Delta between configurations

Output goes to `benchmark.json` in the benchmark directory.

## The Eval+Improve Loop

Use `scripts/run_loop.py` for automated improvement cycles:

```bash
python -m scripts.run_loop --skill-path <path> --iterations 5 --train-ids 1,2,3 --test-ids 4,5
```

Each iteration:

1. Runs evals on the current skill version
2. Grades outputs
3. Analyzes results to find improvement areas
4. Generates an improved version of the description/instructions
5. Re-runs evals to check if the improvement helped

**Train/test split**: Use `--train-ids` for evals used during improvement, `--test-ids` for held-out evals that verify generalization.

## Blind Comparison

The comparator agent (`agents/comparator.md`) performs blind A/B comparison:

- Receives two outputs labeled A and B (randomized assignment)
- Scores using a rubric (content: correctness/completeness/accuracy; structure: organization/formatting/usability)
- Declares a winner with reasoning
- Used by the improve loop to decide if a new version beats the current best

## Post-Hoc Analysis

The analyzer agent (`agents/analyzer.md`) performs deep analysis after comparison:

- Examines winner's strengths and loser's weaknesses at the instruction level
- Identifies specific skill content that caused better/worse execution
- Provides prioritized improvement suggestions
- Also aggregates benchmark data for statistical analysis

## Eval Review UI

Use `assets/eval_review.html` to visually review and edit eval sets:

1. Open the HTML file with placeholder data injected
2. Toggle should_trigger for each query
3. Add/delete queries
4. Export the updated eval set as JSON

## Eval Viewer

Use `eval-viewer/generate_review.py` to generate a review interface:

```bash
python -m eval_viewer.generate_review --workspace <path>
```

This discovers all runs in the workspace, embeds output data into `eval-viewer/viewer.html`, and serves an interactive review UI where you can:

- Browse outputs per eval
- See formal grades (pass/fail with evidence)
- Compare with previous iteration outputs
- Leave feedback per run
- View benchmark data in a separate tab

## Tips

- Start with 5-10 diverse evals before running benchmarks
- Use at least 3 runs per configuration for meaningful variance estimates
- Keep train/test split at roughly 70/30
- Review grader feedback (`eval_feedback` in grading.json) for eval quality issues
- The viewer's benchmark tab requires field names matching the schema exactly
