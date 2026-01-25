# Testing Workers

Test Workers using Vitest integration or Miniflare API.

## Testing Options

| Approach             | Unit Tests | Integration | Bindings | Isolated Storage |
| -------------------- | ---------- | ----------- | -------- | ---------------- |
| Vitest Integration   | ✅         | ✅          | ✅       | ✅               |
| Miniflare API        | ❌         | ✅          | ✅       | ❌               |
| unstable_startWorker | ❌         | ✅          | ✅       | ❌               |

---

## Vitest Integration (Recommended)

Run tests inside Workers runtime.

### Setup

```bash
npm install -D vitest @cloudflare/vitest-pool-workers
```

### vitest.config.ts

```typescript
import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
        wrangler: { configPath: "./wrangler.toml" },
      },
    },
  },
});
```

### Basic Test

```typescript
// test/worker.test.ts
import { env, createExecutionContext, waitOnExecutionContext } from "cloudflare:test";
import { describe, it, expect } from "vitest";
import worker from "../src/index";

describe("Worker", () => {
  it("responds with Hello World", async () => {
    const request = new Request("https://example.com/");
    const ctx = createExecutionContext();

    const response = await worker.fetch(request, env, ctx);
    await waitOnExecutionContext(ctx);

    expect(response.status).toBe(200);
    expect(await response.text()).toBe("Hello, World!");
  });
});
```

### Testing with Bindings

```typescript
import { env } from "cloudflare:test";
import { describe, it, expect, beforeEach } from "vitest";

describe("KV operations", () => {
  beforeEach(async () => {
    // Each test gets isolated storage
    await env.MY_KV.put("key", "value");
  });

  it("reads from KV", async () => {
    const value = await env.MY_KV.get("key");
    expect(value).toBe("value");
  });

  it("has isolated storage", async () => {
    // This test has fresh KV state
    const value = await env.MY_KV.get("nonexistent");
    expect(value).toBeNull();
  });
});
```

### Testing D1

```typescript
import { env } from "cloudflare:test";
import { describe, it, expect, beforeAll } from "vitest";

describe("D1 operations", () => {
  beforeAll(async () => {
    await env.MY_DB.exec(`
      CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
      INSERT INTO users (name) VALUES ('Alice');
    `);
  });

  it("queries database", async () => {
    const { results } = await env.MY_DB.prepare("SELECT * FROM users").all();

    expect(results).toHaveLength(1);
    expect(results[0].name).toBe("Alice");
  });
});
```

---

## Mocking Outbound Requests

```typescript
import { fetchMock } from "cloudflare:test";
import { describe, it, expect, beforeAll, afterEach } from "vitest";

describe("External API calls", () => {
  beforeAll(() => {
    fetchMock.activate();
    fetchMock.disableNetConnect();
  });

  afterEach(() => {
    fetchMock.assertNoPendingInterceptors();
  });

  it("mocks external API", async () => {
    fetchMock.get("https://api.example.com").intercept({ path: "/data" }).reply(200, { message: "mocked" });

    const response = await fetch("https://api.example.com/data");
    const data = await response.json();

    expect(data.message).toBe("mocked");
  });
});
```

---

## Testing Scheduled Handlers

```typescript
import { env, createScheduledController, waitOnExecutionContext } from "cloudflare:test";
import { describe, it, expect } from "vitest";
import worker from "../src/index";

describe("Scheduled handler", () => {
  it("processes cron trigger", async () => {
    const controller = createScheduledController({
      scheduledTime: Date.now(),
      cron: "0 * * * *",
    });
    const ctx = createExecutionContext();

    await worker.scheduled(controller, env, ctx);
    await waitOnExecutionContext(ctx);

    // Assert side effects (e.g., KV writes)
    const log = await env.MY_KV.get("last-run");
    expect(log).toBeDefined();
  });
});
```

---

## Testing Durable Objects

```typescript
import { env, runInDurableObject } from "cloudflare:test";
import { describe, it, expect } from "vitest";
import { Counter } from "../src/counter";

describe("Durable Object", () => {
  it("increments counter", async () => {
    const id = env.COUNTER.idFromName("test");
    const stub = env.COUNTER.get(id);

    // Direct method call
    await runInDurableObject(stub, async (instance: Counter) => {
      await instance.increment();
      const count = await instance.getCount();
      expect(count).toBe(1);
    });
  });

  it("via fetch", async () => {
    const id = env.COUNTER.idFromName("test");
    const stub = env.COUNTER.get(id);

    const response = await stub.fetch("https://do/increment");
    expect(response.status).toBe(200);
  });
});
```

---

## Integration Tests with Miniflare API

For tests outside Workers runtime:

```typescript
import { Miniflare } from "miniflare";
import { describe, it, expect, beforeAll, afterAll } from "vitest";

describe("Integration", () => {
  let mf: Miniflare;

  beforeAll(async () => {
    mf = new Miniflare({
      script: `
        export default {
          async fetch(request) {
            return new Response("Hello");
          }
        }
      `,
      modules: true,
    });
  });

  afterAll(async () => {
    await mf.dispose();
  });

  it("responds correctly", async () => {
    const response = await mf.dispatchFetch("https://example.com/");
    expect(await response.text()).toBe("Hello");
  });
});
```

---

## Running Tests

```bash
# Run all tests
npx vitest

# Watch mode
npx vitest --watch

# Run specific file
npx vitest test/worker.test.ts

# Coverage
npx vitest --coverage
```

---

## Package.json Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:coverage": "vitest --coverage"
  }
}
```

---

## TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "types": ["@cloudflare/workers-types", "@cloudflare/vitest-pool-workers"]
  }
}
```

---

## Best Practices

1. **Use isolated storage** — Each test gets fresh bindings state
2. **Mock external APIs** — Use fetchMock for predictable tests
3. **Test handlers directly** — Call fetch/scheduled handlers with mocked env
4. **Separate unit and integration** — Unit tests in Vitest pool, integration with Miniflare
5. **Clean up** — Always await waitOnExecutionContext()
