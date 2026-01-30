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
  }
};
```

**Differences:**

| Feature  | `--watch`   | `--hot`      |
| -------- | ----------- | ------------ |
| State    | Reset       | Preserved    |
| Process  | Restart     | In-place     |
| Speed    | Slower      | Faster       |
| Use case | General dev | HTTP servers |

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
inspector.url;               // WebSocket URL
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
