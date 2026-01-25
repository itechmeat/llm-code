# Vitest CLI Reference

Command line interface for running tests.

## Basic Commands

```bash
# Run tests in watch mode (default in dev)
vitest

# Run tests once (no watch)
vitest run

# Watch mode (explicit)
vitest watch

# Run benchmarks
vitest bench

# Run type checking
vitest typecheck

# List matching tests without running
vitest list
vitest list --filesOnly

# Initialize browser testing
vitest init browser
```

## Test Filtering

```bash
# Filter by file path (contains "foobar")
vitest foobar

# Filter by filename and line number
vitest src/utils.test.ts:10
vitest ./src/utils.test.ts:10
vitest /absolute/path/utils.test.ts:10

# Filter by test name pattern
vitest -t "should work"
vitest --testNamePattern="user.*login"

# Exclude patterns
vitest --exclude "**/*.e2e.test.ts"

# Run related tests (for lint-staged)
vitest related src/index.ts src/utils.ts --run

# Run only changed files
vitest --changed
vitest --changed HEAD~1
vitest --changed origin/main
```

## Coverage

```bash
# Enable coverage
vitest --coverage
vitest run --coverage

# With options
vitest --coverage.enabled --coverage.provider=istanbul
vitest --coverage.reporter=html --coverage.reporter=json

# Thresholds
vitest --coverage.thresholds.100
vitest --coverage.thresholds.lines=80
vitest --coverage.thresholds.functions=80
vitest --coverage.thresholds.branches=80
vitest --coverage.thresholds.statements=80

# Output directory
vitest --coverage.reportsDirectory=./reports
```

## Environment

```bash
# Set environment
vitest --environment=jsdom
vitest --environment=happy-dom
vitest --environment=node

# Set pool
vitest --pool=threads
vitest --pool=forks
vitest --pool=vmThreads

# Enable globals
vitest --globals
```

## Watch Mode Options

```bash
# Disable watch (same as "run")
vitest --run

# Start without running tests (run on change)
vitest --standalone

# Clear screen on rerun
vitest --clearScreen
```

## Reporters

```bash
# Use specific reporter
vitest --reporter=verbose
vitest --reporter=dot
vitest --reporter=json
vitest --reporter=junit
vitest --reporter=html
vitest --reporter=github-actions

# Multiple reporters
vitest --reporter=default --reporter=json

# Output to file
vitest --outputFile=./results.json
vitest --outputFile.json=./json.json --outputFile.junit=./junit.xml
```

## UI

```bash
# Open Vitest UI
vitest --ui

# Auto-open in browser
vitest --ui --open

# Specify port
vitest --api.port=51204
```

## Debugging

```bash
# Enable Node.js inspector
vitest --inspect
vitest --inspect=127.0.0.1:9229

# Break before test starts
vitest --inspectBrk
```

## Timeouts

```bash
# Test timeout (default: 5000ms)
vitest --testTimeout=10000

# Hook timeout (default: 10000ms)
vitest --hookTimeout=30000

# Teardown timeout
vitest --teardownTimeout=10000
```

## Parallelism

```bash
# Max worker threads
vitest --maxWorkers=4

# Disable file parallelism
vitest --no-file-parallelism

# Disable isolation
vitest --no-isolate

# Max concurrent tests
vitest --maxConcurrency=10
```

## Retry & Bail

```bash
# Retry failed tests
vitest --retry=3

# Stop after N failures
vitest --bail=1
```

## Sharding (CI)

```bash
# Split tests into 3 parts
vitest run --shard=1/3
vitest run --shard=2/3
vitest run --shard=3/3

# Merge reports from shards
vitest --merge-reports --reporter=junit
```

## Browser Mode

```bash
# Enable browser testing
vitest --browser.enabled
vitest --browser.name=chromium
vitest --browser.name=firefox
vitest --browser.name=webkit

# Headless mode
vitest --browser.headless

# Browser UI
vitest --browser.ui
```

## Type Checking

```bash
# Enable type checking
vitest --typecheck.enabled

# Run only type tests
vitest typecheck
vitest --typecheck.only

# Specify checker
vitest --typecheck.checker=tsc
vitest --typecheck.checker=vue-tsc
```

## Project Selection

```bash
# Run specific project
vitest --project=unit
vitest --project=e2e

# Multiple projects
vitest --project=unit --project=integration

# Wildcard
vitest --project="packages*"

# Exclude
vitest --project="!e2e"
```

## Output Control

```bash
# Silent mode
vitest --silent

# Only show failed test logs
vitest --silent=passed-only

# Hide skipped tests
vitest --hideSkippedTests

# Disable colors
vitest --no-color

# Log heap usage
vitest --logHeapUsage
```

## Snapshots

```bash
# Update snapshots
vitest -u
vitest --update

# Expand snapshot diff
vitest --expandSnapshotDiff
```

## Sequences

```bash
# Shuffle tests
vitest --sequence.shuffle.tests
vitest --sequence.shuffle.files

# Set shuffle seed
vitest --sequence.seed=12345

# Run concurrently
vitest --sequence.concurrent
```

## Configuration

```bash
# Use specific config
vitest --config=./vitest.e2e.config.ts
vitest -c ./custom-config.ts

# Set root directory
vitest --root=./packages/core
vitest -r ./packages/core

# Set test directory
vitest --dir=./tests

# Clear cache
vitest --clearCache
```

## Common Patterns

### CI Pipeline

```bash
# Basic CI run
vitest run --coverage --reporter=junit --outputFile=./junit.xml

# With coverage thresholds
vitest run --coverage --coverage.thresholds.100
```

### lint-staged Integration

```js
// .lintstagedrc.js
export default {
  "*.{js,ts}": "vitest related --run",
};
```

### Watch Specific Files

```bash
vitest --watch src/utils
```

### Debug Single Test

```bash
vitest --inspect-brk src/specific.test.ts
```

## Exit Codes

- `0` - All tests passed
- `1` - Tests failed or errors occurred
- Non-zero with `--bail` if threshold exceeded
