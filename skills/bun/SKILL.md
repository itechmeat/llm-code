---
name: bun
description: "Bun JavaScript/TypeScript runtime and all-in-one toolkit. Covers runtime, package manager, bundler, test runner, HTTP server, WebSockets, SQLite, S3, Redis, file I/O, shell scripting, FFI, Markdown parser. Use when running JS/TS with Bun, managing packages, bundling, testing, or using Bun-specific APIs. Keywords: bun, bunx, bun install, bun run, bun test, bun build, Bun.serve, Bun.file, bun:sqlite, Bun.markdown."
metadata:
  version: "1.4.4"
  release_date: "2026-10-22"
---

# Bun

All-in-one JavaScript/TypeScript toolkit: runtime, package manager, test runner, bundler.

## Quick Navigation

| Topic              | Reference                            |
| ------------------ | ------------------------------------ |
| Package Manager    | `references/package-manager.md`      |
| Project Setup      | `references/project-scaffolding.md`  |
| Development        | `references/development.md`          |
| Module System      | `references/module-system.md`        |
| TypeScript & JSX   | `references/typescript-jsx.md`       |
| Type Check & Format | `references/type-checking-and-formatting.md` |
| Configuration      | `references/bunfig.md`               |
| HTTP Server        | `references/http-server.md`          |
| Browser Automation | `references/webview.md`              |
| WebSockets         | `references/websockets.md`           |
| File I/O           | `references/file-io.md`              |
| SQLite             | `references/sqlite.md`               |
| S3 Storage         | `references/s3.md`                   |
| Redis              | `references/redis.md`                |
| Low-Level Network  | `references/networking-low-level.md` |
| Fetch API          | `references/fetch.md`                |
| Shell Scripts      | `references/shell.md`                |
| Spawn Process      | `references/spawn.md`                |
| Workers            | `references/workers.md`              |
| Native FFI         | `references/native-interop.md`       |
| C/C++ Compile      | `references/cc.md`                   |
| Transpiler         | `references/transpiler.md`           |
| Plugins            | `references/plugins.md`              |
| FS Router          | `references/file-system-router.md`   |
| Environment Vars   | `references/env.md`                  |
| Utilities          | `references/utilities.md`            |
| Node.js Compat     | `references/nodejs-compat.md`        |

## When to Use Bun

- Running TypeScript/JSX without build step
- Fast HTTP server with native routing
- Headless browser automation with native input events
- SQLite database (embedded, no deps)
- WebSocket server/client
- S3-compatible storage (AWS, R2, MinIO)
- Redis caching/pub-sub
- Cross-platform shell scripts
- In-process cron scheduling
- **Markdown parsing** (v1.3.8+)
- Native library calls via FFI

## Core Advantages

- **4x faster startup** than Node.js
- **Native TypeScript/JSX** — no tsconfig needed
- **ESM + CommonJS** — both work seamlessly
- **Web APIs built-in** — fetch, WebSocket, etc.
- **30x faster installs** than npm

## Quick Start

```bash
# Run TypeScript directly
bun run index.ts

# Install packages
bun install

# Run package.json script
bun run dev

# Execute package binary
bunx cowsay "Hello"

# Run tests
bun test

# Build for production
bun build ./index.ts --outdir ./dist

# Bundle analysis for LLMs (v1.3.8+)
bun build ./index.ts --metafile-md --outdir ./dist
```

## Critical Rules

| Don't                  | Do                       |
| ---------------------- | ------------------------ |
| `http.createServer()`  | `Bun.serve()`            |
| `fs.readFileSync()`    | `Bun.file().text()`      |
| `better-sqlite3`       | `bun:sqlite`             |
| `child_process.exec()` | `Bun.$` or `Bun.spawn()` |
| `dotenv`               | Built-in `.env` support  |

## Release Highlights (1.4.3 -> 1.4.4)

- **Built-in TypeScript checker (`1.4.3`)**: `bun check` type-checks the project of the nearest `tsconfig.json` and passes 100% of the TypeScript 7.0.2 conformance suite. It reports the same errors as `tsc` (file, line, column, error code) at 3x-6.4x the speed and 2.2x-4.9x less memory; any compiler option works as a flag (`--strict`, `--target`) and overrides `tsconfig.json`.
- **`bun build --check` (`1.4.3`)**: type-checks and then bundles. A type error fails the build like any other build error and nothing is written. The JS API equivalent is `Bun.build({ check: true })`.
- **Built-in formatter (`1.4.4`)**: `bun fmt` is a Prettier-compatible formatter built into the runtime. On Prettier's own repository (2,616 files) `bun fmt --check` takes 60 ms against 17 seconds for Prettier - about 286x faster at 48 MB peak memory instead of 459 MB. It formats JavaScript, TypeScript, JSX, Flow, CSS, SCSS, Less, HTML, Vue, Svelte, Angular, LWC, MJML, JSON/JSONC/JSON5, YAML, TOML, Markdown, MDX, GraphQL and Handlebars, including embedded code.
- **`bun fmt` flags**: `--check` lists files that need formatting and exits with code 1, `--staged` formats and re-stages only what you are about to commit (replaces lint-staged), `--changed` formats what differs from the default branch (accepts a ref, e.g. `--changed=origin/dev`), `--doctor` shows how Bun reads your config and which packages you can uninstall, `--init` creates the `[fmt]` section.
- **`bun fmt` configuration**: reads `.prettierrc*`, `prettier.config.*`, `prettier` in `package.json`, `overrides`, `.editorconfig`, `.prettierignore`, plus `.oxfmtrc.json`, `.oxfmtrc.jsonc` and `oxfmt.config.ts`. Prettier options work under the same names in `bunfig.toml` (`[fmt] printWidth`, `semi`, plus `[[fmt.overrides]]` with `files` and `options`) and as flags (`--print-width 100`, `--no-semi`).
- **Built-in import sorting**: `sortImports` groups imports, sorts the names inside `{ }` and merges duplicate imports from the same module, so `@trivago/prettier-plugin-sort-imports`, `@ianvs/prettier-plugin-sort-imports` and `prettier-plugin-organize-imports` are no longer needed. `sortTailwindcss`, `sortPackageJson` and `jsdoc` are opt-in and need no Prettier config.
- **Built-in plugin equivalents**: `bun fmt` does the work of `prettier-plugin-tailwindcss`, `prettier-plugin-packagejson` and `prettier-plugin-svelte`, and their options are supported. Tailwind classes are sorted with the project's `tailwindcss` (v3 or v4). Languages that need a real Prettier plugin (e.g. Astro) fall back to the Prettier installed in the project.
- **Monorepo and skip rules**: in a monorepo `bun fmt` walks up to the nearest `bunfig.toml` with a `[fmt]` section; without a Prettier config it also formats TOML. It skips `*.min.js`, `*.min.css` and lockfiles unless you pass them explicitly.

Full details: `references/type-checking-and-formatting.md`

## Release Highlights (1.4.x)

- **Rust rewrite**: first release of the Rust port. Lower peak memory (mimalloc allocator, 13-48% less under load), ~2x faster startup, 5x lower idle CPU, and 1,500+ more passing Node.js test-suite tests.
- **HTTP/2 & HTTP/3**: `Bun.serve()` serves HTTP/1.1 and HTTP/2 on the same port via ALPN over TLS (v1.4.1); HTTP/3 is experimental via `http3: true`. `fetch()` can use HTTP/2/3 clients behind feature flags.
- **Serve static directories**: `routes: { "/static/*": { dir: "./public" } }` with sendfile, ETag, Range, conditional requests, and index.html.
- **CLI**: `bun run --parallel` for concurrent scripts; `bun audit fix`, `bun dedupe`, `bun prune`, `bun pm diff`, `bun pm licenses` for package maintenance.
- **`bun test`**: `--parallel`, `--isolate`, `--shard=M/N`, `--timings`, `--changed` (diff-based), `--retry`, and `jest.useFakeTimers()`.
- **`bun build`**: built-in React Compiler (`--react-compiler`), barrel-import optimization, tree-shaking through `export * as` and dynamic `import()`, `--min-chunk-size`, and module preloading.
- **`bun install`**: `--linker=isolated` global virtual store, `--offline` / `--prefer-offline`, `bun add --catalog`, nested overrides, and `selfContained` workspaces.
- **New runtime APIs**: `Bun.Terminal` (PTY), `Bun.Archive` (tar), `Bun.JSON5`/`JSONL`/`JSONC`/`XML`/`TOML` parsers, streaming `Bun.write(path, response)`, `WebSocket.pause()`/`resume()`, `crypto.argon2`, and post-quantum ML-DSA/ML-KEM in `crypto.subtle`.

## Release Highlights (1.3.14)

- **`Bun.Image`**: built-in image decoding, transforms, and encoding for common formats with no npm dependency or native addon build step.
- **Test workflow**: the `1.3.13` line improves dependency-aware filtering for changed-file test runs, which matters when you rely on partial local verification.
- **Patch-line runtime work**: `1.3.13`-`1.3.14` continues compatibility and performance work on top of the `1.3.12` WebView/cron/Markdown release line.

## Release Highlights (1.3.12)

- **`Bun.WebView`**: native headless browser automation with WebKit on macOS and Chrome/Chromium via CDP on all platforms.
- **`Bun.cron()` callback mode**: in-process scheduler with no-overlap execution, UTC semantics, hot-reload cleanup, and `Disposable` job handles.
- **Markdown in terminal**: `bun ./file.md` and `Bun.markdown.ansi()` make terminal-native rendering a first-class workflow.
- **Networking/runtime**: UDP error/truncation handling, Node-compatible unix-socket lifecycle, proxy tunnel reuse, and `Bun.serve()` accept/perf improvements.

## Essential Recipes

### HTTP Server

```ts
Bun.serve({
  port: 3000,
  fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/api/data") {
      return Response.json({ ok: true });
    }
    return new Response("Not Found", { status: 404 });
  },
});
```

### File Operations

```ts
// Read
const content = await Bun.file("data.txt").text();

// Write
await Bun.write("output.txt", "Hello World");

// JSON
const config = await Bun.file("config.json").json();
```

### SQLite

```ts
import { Database } from "bun:sqlite";

const db = new Database("app.db");
db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)");

const insert = db.prepare("INSERT INTO users (name) VALUES (?)");
insert.run("Alice");

const users = db.query("SELECT * FROM users").all();
```

### WebSocket Server

```ts
Bun.serve({
  fetch(req, server) {
    if (server.upgrade(req)) return;
    return new Response("Upgrade failed", { status: 400 });
  },
  websocket: {
    message(ws, message) {
      ws.send(`Echo: ${message}`);
    },
  },
});
```

### Shell Commands

```ts
import { $ } from "bun";

// Simple command
const files = await $`ls -la`.text();

// With variables (auto-escaped)
const name = "my file.txt";
await $`cat ${name}`;

// Piping
await $`cat data.csv | grep "pattern" | wc -l`;
```

### S3 Storage

```ts
import { s3 } from "bun";

// Upload
await s3.file("uploads/doc.pdf").write(data);

// Download
const content = await s3.file("uploads/doc.pdf").text();

// Presigned URL
const url = s3.presign("uploads/doc.pdf", { expiresIn: 3600 });
```

### Redis

```ts
import { redis } from "bun";

await redis.set("key", "value");
const value = await redis.get("key");
await redis.expire("key", 3600);
```

### Testing

```ts
import { expect, test, describe } from "bun:test";

describe("math", () => {
  test("2 + 2 = 4", () => {
    expect(2 + 2).toBe(4);
  });
});
```

## Configuration (bunfig.toml)

```toml
[run]
watch = true

[install]
registry = "https://registry.npmjs.org"

[test]
coverage = true
```

## Environment Variables

```bash
# .env files loaded automatically
DATABASE_URL=postgres://localhost/mydb
```

```ts
// Access
Bun.env.DATABASE_URL;
process.env.DATABASE_URL;
import.meta.env.DATABASE_URL;
```

## Links

- [Documentation](https://bun.sh/docs)
- [Releases](https://github.com/oven-sh/bun/releases)
- [Release blog](https://bun.com/blog/bun-v1.4.4)
- [GitHub](https://github.com/oven-sh/bun)
- [Discord](https://bun.sh/discord)
