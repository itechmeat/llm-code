# Bun Spawn

Spawn child processes with `Bun.spawn()` (async) or `Bun.spawnSync()` (blocking).

## Basic Usage

```ts
const proc = Bun.spawn(["bun", "--version"]);
await proc.exited; // Wait for process to finish
console.log(proc.exitCode); // 0
```

## Options

```ts
const proc = Bun.spawn(["command", "arg1"], {
  cwd: "./path/to/dir",
  env: { ...process.env, FOO: "bar" },
  timeout: 5000,           // Kill after 5s
  killSignal: "SIGKILL",   // Signal for timeout/abort
  signal: abortController.signal,
  onExit(proc, exitCode, signalCode, error) {
    console.log("Exited:", exitCode);
  },
});
```

## Input (stdin)

```ts
// From fetch Response
Bun.spawn(["cat"], {
  stdin: await fetch("https://example.com"),
});

// From file
Bun.spawn(["cat"], {
  stdin: Bun.file("input.txt"),
});

// Incremental write with pipe
const proc = Bun.spawn(["cat"], {
  stdin: "pipe",
});
proc.stdin.write("hello ");
proc.stdin.write("world");
proc.stdin.flush();
proc.stdin.end();

// From ReadableStream
Bun.spawn(["cat"], {
  stdin: new ReadableStream({
    start(controller) {
      controller.enqueue("Hello");
      controller.close();
    },
  }),
});

// From Buffer/TypedArray
Bun.spawn(["cat"], {
  stdin: Buffer.from("data"),
});
```

### stdin Options

| Value                 | Description                  |
| --------------------- | ---------------------------- |
| `null`                | No input (default)           |
| `"pipe"`              | Returns FileSink for writing |
| `"inherit"`           | Use parent's stdin           |
| `Bun.file()`          | Read from file               |
| `Response`            | Use response body            |
| `ReadableStream`      | Stream input                 |
| `Buffer`/`TypedArray` | Binary data                  |
| `number`              | File descriptor              |

## Output (stdout/stderr)

```ts
const proc = Bun.spawn(["echo", "hello"]);

// Read as text
const text = await proc.stdout.text();

// Read as bytes
const bytes = await proc.stdout.bytes();

// Read as JSON
const json = await proc.stdout.json();

// Stream
for await (const chunk of proc.stdout) {
  console.log(chunk);
}
```

### stdout/stderr Options

| Value        | Description                            |
| ------------ | -------------------------------------- |
| `"pipe"`     | Default stdout; returns ReadableStream |
| `"inherit"`  | Default stderr; use parent's stream    |
| `"ignore"`   | Discard output                         |
| `Bun.file()` | Write to file                          |
| `number`     | File descriptor                        |

```ts
Bun.spawn(["command"], {
  stdout: Bun.file("out.log"),
  stderr: Bun.file("err.log"),
});
```

## Exit Handling

```ts
const proc = Bun.spawn(["command"]);

// Wait for exit
await proc.exited;

// Properties after exit
proc.exitCode;    // number | null
proc.signalCode;  // "SIGTERM" | null
proc.killed;      // boolean
```

## Killing Processes

```ts
proc.kill();          // Default signal
proc.kill("SIGTERM"); // By name
proc.kill(15);        // By number
```

## Process Lifecycle

```ts
// Detach from parent (don't block parent exit)
proc.unref();

// Re-attach
proc.ref();
```

## Resource Usage

```ts
await proc.exited;
const usage = proc.resourceUsage();

console.log(usage.maxRSS);           // Max memory (bytes)
console.log(usage.cpuTime.user);     // User CPU time (µs)
console.log(usage.cpuTime.system);   // System CPU time (µs)
```

## AbortSignal

```ts
const controller = new AbortController();

const proc = Bun.spawn({
  cmd: ["sleep", "100"],
  signal: controller.signal,
});

// Later
controller.abort();
```

## Timeout

```ts
const proc = Bun.spawn({
  cmd: ["sleep", "10"],
  timeout: 5000,         // Kill after 5 seconds
  killSignal: "SIGKILL", // Signal to send
});
```

## Inter-Process Communication (IPC)

### Parent Process

```ts
const child = Bun.spawn(["bun", "child.ts"], {
  ipc(message, childProc) {
    console.log("From child:", message);
    childProc.send("Response from parent");
  },
  serialization: "json", // Required for Node.js compat
});

child.send("Hello child");

// Later
child.disconnect();
```

### Child Process

```ts
// child.ts
process.on("message", (message) => {
  console.log("From parent:", message);
});

process.send("Hello parent");
process.send({ type: "data", value: 42 });
```

### Serialization Options

| Value        | Description                          |
| ------------ | ------------------------------------ |
| `"advanced"` | Default; JSC serialize (more types)  |
| `"json"`     | JSON.stringify; required for Node.js |

## Terminal (PTY) Support

**POSIX only** (Linux, macOS)

```ts
const proc = Bun.spawn(["bash"], {
  terminal: {
    cols: 80,
    rows: 24,
    data(terminal, data) {
      process.stdout.write(data);
    },
  },
});

// Write to terminal
proc.terminal.write("echo hello\n");

// Resize
proc.terminal.resize(120, 40);

// Raw mode
proc.terminal.setRawMode(true);

await proc.exited;
proc.terminal.close();
```

### Reusable Terminal

```ts
await using terminal = new Bun.Terminal({
  cols: 80,
  rows: 24,
  data(term, data) {
    process.stdout.write(data);
  },
});

const proc1 = Bun.spawn(["echo", "first"], { terminal });
await proc1.exited;

const proc2 = Bun.spawn(["echo", "second"], { terminal });
await proc2.exited;
```

## Synchronous API

```ts
const result = Bun.spawnSync(["echo", "hello"]);

result.success;   // boolean
result.exitCode;  // number
result.stdout;    // Buffer
result.stderr;    // Buffer

console.log(result.stdout.toString()); // "hello\n"
```

### maxBuffer (spawnSync only)

```ts
const result = Bun.spawnSync({
  cmd: ["yes"],
  maxBuffer: 100, // Kill after 100 bytes output
});
```

## Practical Patterns

### Run Command and Get Output

```ts
async function run(cmd: string[]): Promise<string> {
  const proc = Bun.spawn(cmd, {
    stdout: "pipe",
    stderr: "pipe",
  });

  const exitCode = await proc.exited;
  if (exitCode !== 0) {
    throw new Error(await proc.stderr.text());
  }

  return proc.stdout.text();
}

const version = await run(["git", "--version"]);
```

### Pipe Between Processes

```ts
const proc1 = Bun.spawn(["cat", "file.txt"]);
const proc2 = Bun.spawn(["grep", "pattern"], {
  stdin: proc1.stdout,
});

const result = await proc2.stdout.text();
```

### Long-Running Process with Timeout

```ts
const proc = Bun.spawn({
  cmd: ["long-running-task"],
  timeout: 30000,
  killSignal: "SIGTERM",
});

try {
  await proc.exited;
} catch (err) {
  if (proc.killed) {
    console.log("Process timed out");
  }
}
```

### Interactive Shell Session

```ts
const proc = Bun.spawn(["bash"], {
  terminal: {
    cols: 80,
    rows: 24,
    data(_, data) {
      process.stdout.write(data);
    },
  },
});

// Forward user input
process.stdin.on("data", (chunk) => {
  proc.terminal.write(chunk);
});

await proc.exited;
```

## Performance

- Uses `posix_spawn(3)` under the hood
- `spawnSync` is 60% faster than Node.js `child_process`
