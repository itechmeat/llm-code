# Bun Workers

Web Workers API for running JavaScript/TypeScript on separate threads.

**Status**: Experimental (termination still being improved).

## Basic Usage

### Main Thread

```ts
const worker = new Worker("./worker.ts");

worker.postMessage("hello");

worker.onmessage = (event) => {
  console.log(event.data); // "world"
};
```

### Worker Thread

```ts
declare var self: Worker; // Prevents TS errors

self.onmessage = (event: MessageEvent) => {
  console.log(event.data); // "hello"
  postMessage("world");
};
```

## Creating Workers

```ts
// From file
const worker = new Worker("./worker.ts");

// From blob URL
const blob = new Blob([`postMessage("hi")`], {
  type: "application/typescript",
});
const worker = new Worker(URL.createObjectURL(blob));

// From File object (with TypeScript support)
const file = new File([code], "worker.ts");
const worker = new Worker(URL.createObjectURL(file));
```

## Worker Options

```ts
const worker = new Worker("./worker.ts", {
  ref: false,           // Don't keep main process alive
  smol: true,           // Reduced memory mode
  preload: ["./sentry.js"], // Load modules before worker starts
});
```

## Messages

### Sending

```ts
// Main thread
worker.postMessage({ key: "value" });

// Worker thread
postMessage({ result: 42 });
```

### Receiving

```ts
// Main thread
worker.onmessage = (event) => {
  console.log(event.data);
};

// Worker thread
self.onmessage = (event) => {
  console.log(event.data);
};

// Or with addEventListener
worker.addEventListener("message", (event) => {
  console.log(event.data);
});
```

## Performance Fast Paths

Bun optimizes `postMessage` for common types:

**String fast path** — no serialization:

```ts
postMessage("Hello"); // 2-241x faster
```

**Simple object fast path** — optimized for primitives:

```ts
postMessage({
  message: "Hello",
  count: 42,
  enabled: true,
}); // Fast path
```

Complex objects use standard structured clone:

```ts
postMessage({
  nested: { deep: true },
  date: new Date(),
  buffer: new ArrayBuffer(8),
}); // Standard path
```

## Events

### Open (Bun-specific)

```ts
worker.addEventListener("open", () => {
  console.log("Worker ready");
});
```

Note: Messages are auto-queued until ready.

### Close (Bun-specific)

```ts
worker.addEventListener("close", (event) => {
  console.log("Exit code:", event.code);
});
```

### Error

```ts
worker.onerror = (error) => {
  console.error("Worker error:", error);
};
```

## Termination

### From Main Thread

```ts
worker.terminate(); // Force terminate
```

### From Worker

```ts
process.exit(0); // Self-terminate
```

Workers auto-terminate when event loop is empty.

## Lifecycle Management

### Keep/Don't Keep Process Alive

```ts
// Don't keep main process alive
worker.unref();

// Re-enable keeping alive
worker.ref();

// Set at creation
const worker = new Worker("./worker.ts", {
  ref: false,
});
```

## Memory Optimization

`smol` mode reduces memory at cost of performance:

```ts
const worker = new Worker("./worker.ts", {
  smol: true, // Smaller heap
});
```

## Preload Modules

```ts
// Load monitoring before worker code
const worker = new Worker("./worker.ts", {
  preload: ["./sentry.js", "./datadog.js"],
});

// Single module
const worker = new Worker("./worker.ts", {
  preload: "./init.js",
});
```

## Environment Data

Share data between threads:

```ts
import {
  setEnvironmentData,
  getEnvironmentData,
} from "worker_threads";

// Main thread
setEnvironmentData("config", { apiUrl: "https://api.example.com" });

// Worker thread
const config = getEnvironmentData("config");
```

## Check Thread Context

```ts
if (Bun.isMainThread) {
  console.log("Main thread");
} else {
  console.log("Worker thread");
}
```

## Listen for Worker Creation

```ts
process.on("worker", (worker) => {
  console.log("New worker:", worker.threadId);
});
```

## Practical Patterns

### Worker Pool

```ts
// main.ts
const pool = Array.from({ length: 4 }, () =>
  new Worker("./worker.ts")
);

let current = 0;

function dispatch(task: unknown) {
  const worker = pool[current++ % pool.length];

  return new Promise((resolve) => {
    worker.onmessage = (e) => resolve(e.data);
    worker.postMessage(task);
  });
}

// Usage
const result = await dispatch({ compute: [1, 2, 3] });
```

### CPU-Intensive Task

```ts
// main.ts
const worker = new Worker("./hash-worker.ts");

worker.postMessage({ data: largeData });

worker.onmessage = (e) => {
  console.log("Hash:", e.data.hash);
};

// hash-worker.ts
declare var self: Worker;

self.onmessage = async (event) => {
  const hasher = new Bun.CryptoHasher("sha256");
  hasher.update(event.data.data);
  postMessage({ hash: hasher.digest("hex") });
};
```

### Background Processing

```ts
// main.ts
const worker = new Worker("./background.ts", {
  ref: false, // Don't block shutdown
});

worker.postMessage({ task: "process" });

// background.ts
declare var self: Worker;

self.onmessage = async (event) => {
  // Long-running task
  await processData(event.data);
  process.exit(0);
};
```

## Features

| Feature           | Supported         |
| ----------------- | ----------------- |
| TypeScript/JSX    | ✅                |
| ES Modules        | ✅                |
| CommonJS          | ✅                |
| postMessage       | ✅                |
| Structured Clone  | ✅                |
| SharedArrayBuffer | ✅                |
| blob: URLs        | ✅                |
| terminate()       | ✅ (experimental) |
| ref/unref         | ✅                |
| smol mode         | ✅                |
| preload           | ✅                |
