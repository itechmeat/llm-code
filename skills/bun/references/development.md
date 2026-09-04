````markdown
# Development Workflow

Runtime, watch mode, debugging, and environment variables.

## Running Code

```bash
bun run index.ts          # Run file
bun index.ts              # Same (shorthand)
bun run dev               # Run package.json script
bun dev                   # Same (if no file "dev" exists)
```
````

**Lifecycle scripts auto-run:**

```bash
bun install               # Runs postinstall
bun add react             # Runs postinstall for react
```

### Running Scripts in Parallel (v1.4)

```bash
bun run --parallel dev:api dev:web   # Concurrent scripts, prefixed output
bun run --parallel "build:*"         # Glob-match multiple scripts
bun run --parallel --filter=pkg-a    # Per-workspace
bun run --parallel --no-exit-on-error   # Keep going after a failure
```

Other `bun run`/process flags:

```bash
bun run --no-orphans        # Exit when the parent process dies (SIGKILLs descendants)
bun run --no-env-file       # Skip automatic .env loading
bun run --cpu-prof-md app.ts # CPU profile as a Markdown report
bun run --heap-prof-md app.ts # Heap profile as a Markdown report
BUN_CPU_PROFILE=1 bun app.ts # Flag-less profiling for any process
```

---

## Watch Mode

### --watch (Restart)

Restarts entire process on file changes:

```bash
bun --watch index.ts
bun --watch run dev
```

**bunfig.toml:**

```toml
[run]
watch = true
```

### --hot (Hot Reload)

Preserves state, reloads modules in-place:

```bash
bun --hot index.ts
```

```typescript
// module-level state preserved across reloads
let count = globalThis.count ?? 0;
globalThis.count = count;

// HTTP handlers auto-reload
export default {
  fetch() {
    return new Response(`Count: ${++count}`);
  },
};
```

**Differences:**

| Feature  | `--watch`   | `--hot`      |
| -------- | ----------- | ------------ |
| State    | Reset       | Preserved    |
| Process  | Restart     | In-place     |
| Speed    | Slower      | Faster       |
| Use case | General dev | HTTP servers |

### `Bun.cron()` in-process scheduler (v1.3.12)

Use in-process cron when the job should share memory, caches, DB pools, or module state with the current Bun process.

```typescript
process.on("unhandledRejection", console.error);

using job = Bun.cron("*/5 * * * *", async function () {
  await syncState();
});
```

Operational rules:

- In-process cron uses UTC, not the host local timezone.
- Jobs never overlap; the next run is scheduled only after the current handler settles.
- Under `bun --hot`, in-process cron jobs are cleared before module re-evaluation, so schedule edits do not leak duplicate timers.
- Use `Bun.cron(path, schedule, title)` only when you need OS-level persistence across restarts.

## Test Workflow Notes (v1.3.13)

The `1.3.13` line improves dependency-aware test filtering for changed-file workflows. If you rely on partial local verification, re-test your assumptions about which dependent test files Bun includes instead of assuming older file-only matching behavior.

Keep these rules in mind:

- `bun test` still discovers files by naming conventions such as `*.test.ts`, `*_test.ts`, `*.spec.ts`, and `*_spec.ts`.
- Positional filters remain simple path substring matches, not glob patterns.
- For exact files, prefer `bun test ./path/to/file.test.ts` so Bun treats the argument as a path rather than a fuzzy filter.

### Test runner additions (v1.4)

- `--parallel[=N]`: run test files across worker processes. Coverage and JUnit reports are merged, and `--bail` stops all workers. Implies `--isolate` (disable with `--no-isolate`).
- `--isolate`: fresh global object per test file; closes leaked servers, cancels timers, and kills leftover subprocesses between files.
- `--shard=M/N`: deterministic CI splitting with Jest/Vitest-compatible indexing.
- `--timings=<path>` / `--update-timings`: balance workers and shards by measured duration (longest-processing-time-first).
- `--changed[=ref]`: run only tests whose files appear in the git diff; works with `--watch`.
- `test({ retry: n })` and `--retry <N>`: retry flaky tests; `--repeats` mode repeats each test.
- `jest.useFakeTimers()`: fake `setTimeout`, `setInterval`, and `Date`; works with `@testing-library/react`'s `waitFor`.

---

## Debugging

### VS Code

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "bun",
      "request": "launch",
      "name": "Debug Bun",
      "program": "${workspaceFolder}/index.ts",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

Install **Bun for Visual Studio Code** extension.

### Inspector (Chrome DevTools)

```bash
bun --inspect index.ts            # Listen on ws://localhost:6499
bun --inspect=0.0.0.0:9229        # Custom host:port
bun --inspect-brk index.ts        # Break on first line
bun --inspect-wait index.ts       # Wait for debugger
```

Open `chrome://inspect` → Configure target.

### Web Debugger

```bash
bun --inspect index.ts
# Open: https://debug.bun.sh/
```

### Inspector API

```typescript
const inspector = Bun.inspector;
inspector.url; // WebSocket URL
inspector.open({ port: 9229 });
inspector.close();

// In-process breakpoint
Bun.inspect.break("reason");
```

---

## Performance

Bun is **4x faster startup** than Node.js due to:

- Native TS/JSX transpilation (no build step)
- Native ESM support
- Optimized module resolution
- Hardware-accelerated I/O

**Benchmarks:**

```bash
time bun index.ts    # ~6ms startup
time node index.js   # ~25ms startup
```

---

## Key Points

- `bun run` omits "run" if file doesn't exist
- `--hot` for HTTP servers, `--watch` for everything else
- `.env.local` has highest priority
- `Bun.env` is typed, `process.env` for compatibility
- VS Code debugger requires Bun extension
- `--inspect-brk` to break on first line

```

```
