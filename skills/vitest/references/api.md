# Vitest Test API Reference

Core testing functions and hooks.

## Test Functions

### test / it

```ts
import { expect, test } from "vitest";

test("should work", () => {
  expect(Math.sqrt(4)).toBe(2);
});

// With timeout (default 5s, configurable via testTimeout)
test("async operation", async () => {
  // ...
}, 10000);

// With options object
test("with options", { timeout: 10000, retry: 2 }, () => {
  // ...
});
```

### test.skip / test.only / test.todo

```ts
test.skip("skipped test", () => {});
test.only("only this runs", () => {});
test.todo("implement later");

// Dynamic skip
test("conditional", (context) => {
  context.skip(condition, "optional reason");
});
```

### test.skipIf / test.runIf

```ts
const isDev = process.env.NODE_ENV === "development";

test.skipIf(isDev)("prod only", () => {});
test.runIf(isDev)("dev only", () => {});
```

### test.concurrent / test.sequential

```ts
// Run tests in parallel
test.concurrent("concurrent 1", async () => {});
test.concurrent("concurrent 2", async () => {});

// Force sequential in concurrent context
test.sequential("must run alone", async () => {});
```

### test.each / test.for

```ts
// Parameterized tests
test.each([
  [1, 1, 2],
  [1, 2, 3],
])("add(%i, %i) -> %i", (a, b, expected) => {
  expect(a + b).toBe(expected);
});

// With object parameters
test.each([
  { a: 1, b: 1, expected: 2 },
  { a: 1, b: 2, expected: 3 },
])("add($a, $b) -> $expected", ({ a, b, expected }) => {
  expect(a + b).toBe(expected);
});

// test.for - keeps array intact (recommended)
test.for([
  [1, 1, 2],
  [1, 2, 3],
])("add(%i, %i) -> %i", ([a, b, expected]) => {
  expect(a + b).toBe(expected);
});
```

### test.extend (Custom Fixtures)

```ts
const myTest = test.extend({
  todos: async ({ task }, use) => {
    const todos = [1, 2, 3];
    await use(todos);
    // cleanup
  },
});

myTest("with fixture", ({ todos }) => {
  expect(todos.length).toBe(3);
});
```

## describe (Suites)

```ts
describe("group", () => {
  test("test 1", () => {});
  test("test 2", () => {});
});

// Nested
describe("outer", () => {
  describe("inner", () => {
    test("nested test", () => {});
  });
});
```

### describe modifiers

```ts
describe.skip('skipped suite', () => {})
describe.only('only this suite', () => {})
describe.todo('implement later')
describe.concurrent('parallel tests', () => {})
describe.sequential('sequential tests', () => {})
describe.shuffle('random order', () => {})
describe.each([...])('parameterized', (params) => {})
```

## Setup and Teardown

```ts
import { beforeAll, afterAll, beforeEach, afterEach } from "vitest";

beforeAll(async () => {
  // once before all tests
  await setupDatabase();

  // cleanup function (equivalent to afterAll)
  return async () => {
    await teardownDatabase();
  };
});

afterAll(async () => {
  // once after all tests
});

beforeEach(async () => {
  // before each test
});

afterEach(async () => {
  // after each test
});
```

## Test Hooks (Inside Test)

```ts
import { test, onTestFinished, onTestFailed } from "vitest";

test("with cleanup", () => {
  const db = connectDb();
  onTestFinished(() => db.close());

  onTestFailed(({ task }) => {
    console.log("Failed:", task.result.errors);
  });

  db.query("SELECT * FROM users");
});

// For concurrent tests, use context
test.concurrent("concurrent", ({ onTestFinished }) => {
  onTestFinished(() => cleanup());
});
```

## Benchmark

```ts
import { bench, describe } from "vitest";

bench(
  "normal sorting",
  () => {
    const x = [1, 5, 4, 2, 3];
    x.sort((a, b) => a - b);
  },
  { time: 1000, iterations: 100 }
);

describe("benchmarks", () => {
  bench.skip("skipped", () => {});
  bench.only("only this", () => {});
  bench.todo("implement later");
});
```

## Test Options

```ts
interface TestOptions {
  timeout?: number; // max execution time (default 5s)
  retry?: number; // retry count on failure (default 0)
  repeats?: number; // repeat count even on success
}
```

## Important Notes

- **Concurrent tests**: Use `expect` from context for snapshots
  ```ts
  test.concurrent("test", async ({ expect }) => {
    expect(foo).toMatchSnapshot();
  });
  ```
- **Type checker mode**: `.concurrent`, `.skipIf`, `.runIf`, `.each`, `.fails` not supported
- **Default timeout**: 5 seconds (configurable via `testTimeout` config)
