# Bun Node.js Compatibility

Bun aims for 100% Node.js API compatibility. Most frameworks (Next.js, Express) and npm packages work out of the box.

**Policy**: If a package works in Node.js but not in Bun, it's a bug — please report it.

## Fully Implemented Modules

| Module                     | Status               |
| -------------------------- | -------------------- |
| `node:assert`              | ✅ Full              |
| `node:buffer`              | ✅ Full              |
| `node:console`             | ✅ Full              |
| `node:dgram`               | ✅ Full (>90% tests) |
| `node:diagnostics_channel` | ✅ Full              |
| `node:dns`                 | ✅ Full (>90% tests) |
| `node:events`              | ✅ Full (100% tests) |
| `node:fs`                  | ✅ Full (92% tests)  |
| `node:http`                | ✅ Full              |
| `node:net`                 | ✅ Full              |
| `node:os`                  | ✅ Full (100% tests) |
| `node:path`                | ✅ Full (100% tests) |
| `node:punycode`            | ✅ Full (deprecated) |
| `node:querystring`         | ✅ Full (100% tests) |
| `node:readline`            | ✅ Full              |
| `node:stream`              | ✅ Full              |
| `node:string_decoder`      | ✅ Full (100% tests) |
| `node:timers`              | ✅ Full              |
| `node:tty`                 | ✅ Full              |
| `node:url`                 | ✅ Full              |
| `node:zlib`                | ✅ Full (98% tests)  |

## Mostly Implemented Modules

| Module                | Missing/Notes                                                             |
| --------------------- | ------------------------------------------------------------------------- |
| `node:async_hooks`    | `AsyncLocalStorage`, `AsyncResource` work. V8 promise hooks not called.   |
| `node:child_process`  | Missing `proc.gid`, `proc.uid`. IPC can't send socket handles.            |
| `node:cluster`        | Works, but socket passing only on Linux (via `SO_REUSEPORT`).             |
| `node:crypto`         | Missing `secureHeapUsed`, `setEngine`, `setFips`.                         |
| `node:http2`          | 95%+ gRPC tests pass. Missing `allowHTTP1`, `pushStream`.                 |
| `node:https`          | Implemented, but `Agent` not always used.                                 |
| `node:module`         | Missing `syncBuiltinESMExports`, `module.register`.                       |
| `node:perf_hooks`     | APIs implemented, tests not passing yet.                                  |
| `node:tls`            | Missing `tls.createSecurePair`.                                           |
| `node:util`           | Missing `getCallSite`, `transferableAbortSignal`.                         |
| `node:v8`             | `writeHeapSnapshot`, `getHeapSnapshot` work. Use `bun:jsc` for profiling. |
| `node:vm`             | Core functionality works. Missing `measureMemory`, some `cachedData`.     |
| `node:worker_threads` | Missing some Worker options, `markAsUntransferable`.                      |

## Partially/Not Implemented

| Module              | Status                     |
| ------------------- | -------------------------- |
| `node:domain`       | Missing `Domain`, `active` |
| `node:inspector`    | Profiler API works         |
| `node:wasi`         | Partial                    |
| `node:test`         | Partial — use `bun:test`   |
| `node:repl`         | ❌ Not implemented         |
| `node:sqlite`       | ❌ Use `bun:sqlite`        |
| `node:trace_events` | ❌ Not implemented         |

## Globals

All standard Node.js globals are fully implemented:

- `AbortController`, `AbortSignal`
- `Buffer`, `Blob`
- `console`, `process`
- `fetch`, `Request`, `Response`, `Headers`, `FormData`
- `setTimeout`, `setInterval`, `setImmediate`, `clearTimeout`, `clearInterval`, `clearImmediate`
- `URL`, `URLSearchParams`
- `TextEncoder`, `TextDecoder`
- `crypto`, `SubtleCrypto`, `CryptoKey`
- `ReadableStream`, `WritableStream`, `TransformStream`
- `MessageChannel`, `MessagePort`, `BroadcastChannel`
- `structuredClone`, `queueMicrotask`
- `require`, `module`, `exports`, `__dirname`, `__filename`
- `WebAssembly`
- `Event`, `EventTarget`, `CustomEvent`
- `performance`, `PerformanceObserver`

### process Differences

- `process.binding` — partially implemented
- `process.title` — no-op on macOS/Linux
- `process.loadEnvFile`, `process.getBuiltinModule` — not implemented
- `getActiveResourcesInfo` — stub

## Bun-Native Alternatives

| Node.js             | Bun Alternative                    |
| ------------------- | ---------------------------------- |
| `node:test`         | `bun:test`                         |
| `node:sqlite`       | `bun:sqlite`                       |
| `node:v8` profiling | `bun:jsc`                          |
| `child_process`     | `Bun.spawn`, `Bun.$`               |
| `node:crypto`       | `Bun.CryptoHasher`, `Bun.password` |
| `fs.readFile`       | `Bun.file().text()`                |
| `fs.writeFile`      | `Bun.write()`                      |

## Common Compatibility Patterns

### ESM/CJS Interop

```ts
// Both work
import fs from "node:fs";
const fs = require("node:fs");

// Bun handles the conversion automatically
import pkg from "./cjs-package"; // Works even if CJS
```

### require.cache

```ts
// Supported for both ESM & CJS
delete require.cache[require.resolve("./module")];
```

### \_\_dirname in ESM

```ts
// Node.js ESM doesn't have __dirname
// Bun provides it, or use:
import.meta.dir;  // Directory
import.meta.file; // Filename
import.meta.path; // Full path
```

### Checking Runtime

```ts
if (typeof Bun !== "undefined") {
  // Running in Bun
}

if (process.versions.bun) {
  // Also works
}
```
