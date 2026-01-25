# Vitest Configuration Reference

Complete configuration options for vitest.config.ts or vite.config.ts.

## Config File Setup

### Standalone vitest.config.ts (Recommended)

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // test options here
  },
});
```

### Using vite.config.ts

```ts
/// <reference types="vitest/config" />
import { defineConfig } from "vite";

export default defineConfig({
  test: {
    // test options here
  },
});
```

### Extending Vite Config

```ts
import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      exclude: ["packages/template/*"],
    },
  })
);
```

### Using Defaults

```ts
import { configDefaults, defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    exclude: [...configDefaults.exclude, "packages/template/*"],
  },
});
```

## Essential Options

### Test File Patterns

```ts
{
  // Files to include (glob patterns)
  include: ['**/*.{test,spec}.?(c|m)[jt]s?(x)'],

  // Files to exclude
  exclude: ['**/node_modules/**', '**/.git/**'],

  // In-source testing
  includeSource: ['src/**/*.{js,ts}'],
}
```

### Globals

```ts
{
  // Enable global test APIs (test, expect, describe, etc.)
  globals: true,
}

// Add to tsconfig.json for TypeScript:
// { "compilerOptions": { "types": ["vitest/globals"] } }
```

### Environment

```ts
{
  // 'node' | 'jsdom' | 'happy-dom' | 'edge-runtime' | string
  environment: 'jsdom',

  // Environment options
  environmentOptions: {
    jsdom: {
      url: 'http://localhost:3000',
    },
  },
}

// Per-file environment (docblock at top of file):
// /** @vitest-environment jsdom */
```

### Pool (Test Runner)

```ts
{
  // 'threads' | 'forks' | 'vmThreads' | 'vmForks'
  pool: 'forks', // default

  // Pool-specific options
  poolOptions: {
    threads: {
      singleThread: true,
    },
    forks: {
      singleFork: true,
    },
  },
}
```

**Pool Types:**

- `threads` - Worker threads (fast, but can't use `process.chdir()`)
- `forks` - Child process (default, supports process APIs)
- `vmThreads` - VM context in threads (fastest, but unstable ESM)
- `vmForks` - VM context in forks

## Timeouts

```ts
{
  testTimeout: 5000,     // Per-test timeout (default: 5000ms)
  hookTimeout: 10000,    // Setup/teardown timeout (default: 10000ms)
  teardownTimeout: 10000, // Global teardown timeout
}
```

## Setup Files

```ts
{
  // Run before each test file
  setupFiles: ['./test/setup.ts'],

  // Run once before all tests
  globalSetup: ['./test/global-setup.ts'],
}
```

## Mock Configuration

```ts
{
  clearMocks: true,     // Clear mock calls before each test
  mockReset: true,      // Reset mock implementations before each test
  restoreMocks: true,   // Restore original implementations before each test
  unstubEnvs: true,     // Restore env vars after each test
  unstubGlobals: true,  // Restore globals after each test
}
```

## Coverage

```ts
{
  coverage: {
    enabled: true,
    provider: 'v8',        // 'v8' | 'istanbul'
    reporter: ['text', 'json', 'html'],
    reportsDirectory: './coverage',

    // Files to include/exclude
    include: ['src/**/*.ts'],
    exclude: ['**/*.test.ts', '**/*.d.ts'],

    // Thresholds (fail if below)
    thresholds: {
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80,
      perFile: true,       // Check per file
      autoUpdate: true,    // Auto-update thresholds
      100: false,          // Require 100% coverage
    },

    // Skip files with 100% coverage in report
    skipFull: false,

    // Generate report even if tests fail
    reportOnFailure: true,
  },
}
```

## Reporters

```ts
{
  // Built-in reporters
  reporters: ['default'],
  // Options: 'basic', 'default', 'verbose', 'dot', 'json', 'html',
  //          'junit', 'github-actions', 'blob', 'tap', 'tap-flat'

  // With options
  reporters: [
    ['json', { outputFile: './test-results.json' }],
    ['junit', { outputFile: './junit.xml' }],
  ],

  // Output file shorthand
  outputFile: {
    json: './test-results.json',
    junit: './junit.xml',
  },
}
```

## Watch Mode

```ts
{
  watch: true,           // Enable watch mode (default in dev)

  // Patterns that force full rerun
  forceRerunTriggers: ['**/package.json', '**/*.config.*'],

  // Watch-specific patterns
  watchTriggerPatterns: ['src/**', 'test/**'],
}
```

## Test Filtering

```ts
{
  // Filter by test name pattern
  testNamePattern: /should.*work/,

  // Allow test.only in CI
  allowOnly: false,      // default: !process.env.CI

  // Pass with no test files
  passWithNoTests: false,
}
```

## Parallelism

```ts
{
  // Run test files in parallel
  fileParallelism: true,

  // Max concurrent test files
  maxWorkers: 4,

  // Max concurrent tests within a file
  maxConcurrency: 5,

  // Isolate test files
  isolate: true,
}
```

## Sequences

```ts
{
  sequence: {
    // Hook execution order: 'stack' | 'list' | 'parallel'
    hooks: 'parallel',

    // Shuffle tests
    shuffle: false,
    seed: 123,           // Shuffle seed
  },
}
```

## Snapshots

```ts
{
  // Snapshot format options
  snapshotFormat: {
    printBasicPrototype: false,
  },

  // Custom serializers
  snapshotSerializers: ['./custom-serializer.ts'],

  // Custom snapshot path resolver
  resolveSnapshotPath: (path, ext) => path.replace('src', '__snapshots__') + ext,
}
```

## Retry & Bail

```ts
{
  retry: 2,              // Retry failed tests N times
  bail: 1,               // Stop after N failures (0 = no bail)
}
```

## Typecheck

```ts
{
  typecheck: {
    enabled: true,
    checker: 'tsc',       // 'tsc' | 'vue-tsc'
    include: ['**/*.{test,spec}-d.?(c|m)[jt]s?(x)'],
  },
}
```

## Fake Timers

```ts
{
  fakeTimers: {
    // Which APIs to mock
    toFake: ['setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'Date'],

    // Loop limit for runAllTimers
    loopLimit: 10000,
  },
}
```

## Benchmarks

```ts
{
  benchmark: {
    include: ['**/*.{bench,benchmark}.?(c|m)[jt]s?(x)'],
    exclude: ['**/node_modules/**'],

    outputFile: './bench/results.json',

    reporters: ['default'],
  },
}
```

## UI

```ts
{
  ui: true,              // Enable Vitest UI
  open: true,            // Auto-open in browser

  api: {
    port: 51204,
    strictPort: true,
  },
}
```

## Multi-Project Configuration

```ts
{
  projects: [
    {
      name: 'unit',
      include: ['test/unit/**/*.test.ts'],
      environment: 'node',
    },
    {
      name: 'browser',
      include: ['test/browser/**/*.test.ts'],
      browser: {
        enabled: true,
        provider: 'playwright',
        instances: [{ browser: 'chromium' }],
      },
    },
  ],
}
```

## Browser Mode

```ts
{
  browser: {
    enabled: true,
    provider: 'playwright',  // 'playwright' | 'webdriverio' | 'preview'

    instances: [
      { browser: 'chromium' },
      { browser: 'firefox' },
      { browser: 'webkit' },
    ],

    headless: true,
    viewport: { width: 1280, height: 720 },

    // Screenshot on failure
    screenshotFailures: true,
    screenshotDirectory: './screenshots',
  },
}
```

## CLI Options

```bash
# Run tests
vitest
vitest run              # Run once (no watch)
vitest watch            # Watch mode

# Filtering
vitest src/utils        # Run tests in path
vitest --testNamePattern="should work"
vitest --exclude "**/*.integration.test.ts"

# Coverage
vitest --coverage
vitest --coverage.enabled --coverage.provider=istanbul

# Environment
vitest --environment jsdom
vitest --pool threads

# Other
vitest --ui             # Open UI
vitest --reporter=json  # Change reporter
vitest bench            # Run benchmarks
vitest typecheck        # Run type checking
vitest --bail 1         # Stop on first failure
vitest --retry 2        # Retry failed tests
```

## OpenTelemetry (Experimental)

Enable distributed tracing for test execution. Requires `@opentelemetry/sdk-node`.

```bash
npm install @opentelemetry/sdk-node
```

```ts
// otel-setup.ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";

export async function setup() {
  const sdk = new NodeSDK({
    traceExporter: new OTLPTraceExporter({
      url: "http://localhost:4318/v1/traces",
    }),
  });
  sdk.start();
  return async () => await sdk.shutdown();
}
```

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    experimental: {
      openTelemetry: {
        enabled: true,
        sdkPath: "./otel-setup.ts",
      },
    },
  },
});
```

### Browser Mode OpenTelemetry

```ts
{
  browser: {
    enabled: true,
    // ...
  },
  experimental: {
    openTelemetry: {
      enabled: true,
      sdkPath: './otel-setup-node.ts',      // Node.js SDK
      browserSdkPath: './otel-setup-browser.ts', // Browser SDK
    },
  },
}
```

### CI/CD Context Propagation

Pass trace context via environment variables:

```bash
TRACEPARENT="00-<trace-id>-<span-id>-01" vitest run
TRACESTATE="key=value" vitest run
```

This links test spans to parent CI pipeline traces.

## Config Hierarchy

1. CLI flags (highest priority)
2. `vitest.config.ts`
3. `vite.config.ts`
4. Defaults

**Note:** Configuration options marked with 🚫 in docs can only be set at root level, not in project configs.
