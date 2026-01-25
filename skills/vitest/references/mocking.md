# Vitest Mocking Reference

Comprehensive guide to mocking functions, modules, timers, and globals.

## Creating Mocks

### vi.fn() - Mock Function

```ts
import { vi, expect } from "vitest";

// Empty mock (returns undefined)
const mock = vi.fn();

// With implementation
const mockFn = vi.fn((x: number) => x + 1);

// Assertions
mockFn(5);
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith(5);
expect(mockFn).toHaveReturnedWith(6);
```

### vi.spyOn() - Spy on Method

```ts
const cart = {
  getApples: () => 42,
};

const spy = vi.spyOn(cart, "getApples");
cart.getApples();

expect(spy).toHaveBeenCalled();
expect(spy).toHaveReturnedWith(42);

// With replacement
spy.mockImplementation(() => 100);
expect(cart.getApples()).toBe(100);

// Restore original
spy.mockRestore();
```

### vi.mockObject() (v3.2.0+)

```ts
const original = {
  simple: () => "value",
  nested: { method: () => "real" },
  prop: "foo",
};

const mocked = vi.mockObject(original);
mocked.simple.mockReturnValue("mocked");

// With spy mode (keep implementations)
const spied = vi.mockObject(original, { spy: true });
```

## Mock Properties

```ts
const mock = vi.fn();
mock("arg1", "arg2");
mock("arg3");

// All calls
mock.mock.calls; // [['arg1', 'arg2'], ['arg3']]
mock.mock.lastCall; // ['arg3']
mock.mock.results; // [{ type: 'return', value: undefined }, ...]
mock.mock.settledResults; // For async - { type: 'fulfilled'/'rejected', value }
mock.mock.instances; // Instances when called with `new`
mock.mock.contexts; // `this` values
mock.mock.invocationCallOrder; // [1, 2, ...]
```

## Mock Return Values

```ts
const mock = vi.fn();

// Always return value
mock.mockReturnValue(42);

// Return value once (chainable)
mock.mockReturnValueOnce("first").mockReturnValueOnce("second").mockReturnValue("default");

// For promises
mock.mockResolvedValue({ data: "ok" });
mock.mockResolvedValueOnce({ data: "first" });
mock.mockRejectedValue(new Error("fail"));
mock.mockRejectedValueOnce(new Error("once"));

// Return this
mock.mockReturnThis();
```

## Mock Implementations

```ts
const mock = vi.fn();

// Permanent implementation
mock.mockImplementation((x) => x * 2);

// One-time implementations
mock.mockImplementationOnce(() => "first").mockImplementationOnce(() => "second");

// Temporary implementation
mock.withImplementation(
  () => "temp",
  () => {
    mock(); // 'temp'
  }
);
mock(); // back to original
```

## Reset/Clear/Restore

```ts
// Clear call history only
mock.mockClear();

// Clear history + reset implementation
mock.mockReset();

// Clear + reset + restore original (for spies)
mock.mockRestore();

// Global versions
vi.clearAllMocks(); // clearMocks config
vi.resetAllMocks(); // mockReset config
vi.restoreAllMocks(); // restoreMocks config
```

## Module Mocking

### vi.mock() - Hoisted

```ts
import { myFunc } from "./module";

// Automock (returns undefined for all exports)
vi.mock("./module");

// Factory (hoisted to top)
vi.mock("./module", () => ({
  myFunc: vi.fn(() => "mocked"),
  default: { key: "value" }, // for default export
}));

// With spy mode (keeps implementation)
vi.mock("./module", { spy: true });

// Access original inside factory
vi.mock("./module", async (importOriginal) => {
  const mod = await importOriginal();
  return { ...mod, myFunc: vi.fn() };
});
```

### vi.doMock() - Not Hoisted

```ts
// For dynamic imports (not hoisted)
vi.doMock("./module", () => ({ myFunc: () => "mocked" }));
const { myFunc } = await import("./module");
```

### vi.unmock() / vi.doUnmock()

```ts
vi.unmock("./module"); // Hoisted
vi.doUnmock("./module"); // Not hoisted
```

### vi.hoisted() - Define Variables Before Imports

```ts
// Variables defined in vi.hoisted are available in vi.mock
const mocks = vi.hoisted(() => ({
  myFunc: vi.fn(),
}));

vi.mock("./module", () => ({
  myFunc: mocks.myFunc,
}));

mocks.myFunc.mockReturnValue(100);
```

### Helper Functions

```ts
// Import original (bypass mock)
const original = await vi.importActual("./module");

// Import with auto-mock
const mocked = await vi.importMock("./module");

// Type helper
vi.mocked(myFunc).mockReturnValue("typed");
vi.mocked(myFunc, { deep: true }); // Deep mock types

// Check if mocked
vi.isMockFunction(myFunc); // boolean
```

### **mocks** Folder

```
project/
├── __mocks__/
│   └── axios.js          # Mock for node_modules
├── src/
│   ├── __mocks__/
│   │   └── utils.js      # Mock for ./utils
│   └── utils.js
```

```ts
// Auto-uses __mocks__/axios.js
vi.mock("axios");
```

## Fake Timers

### Enable/Disable

```ts
// Enable fake timers
vi.useFakeTimers();

// Restore real timers
vi.useRealTimers();

// Check if fake timers active
vi.isFakeTimers(); // boolean
```

### Advance Time

```ts
vi.useFakeTimers();

setTimeout(() => console.log("done"), 1000);

// Advance by milliseconds
vi.advanceTimersByTime(1000);

// Advance to next timer
vi.advanceTimersToNextTimer();

// Run all timers
vi.runAllTimers();

// Run only pending (not new ones)
vi.runOnlyPendingTimers();

// For requestAnimationFrame
vi.advanceTimersToNextFrame();

// Async versions (for async callbacks)
await vi.advanceTimersByTimeAsync(1000);
await vi.runAllTimersAsync();
```

### System Time

```ts
vi.useFakeTimers();

// Set system time
vi.setSystemTime(new Date(2024, 0, 1));
expect(Date.now()).toBe(new Date(2024, 0, 1).valueOf());

// Get mocked time
vi.getMockedSystemTime(); // Date | null

// Get real time even with fake timers
vi.getRealSystemTime(); // number
```

### Timer Utilities

```ts
// Count pending timers
vi.getTimerCount();

// Clear all scheduled timers
vi.clearAllTimers();

// Run all microtasks (process.nextTick)
vi.runAllTicks();
```

## Environment & Globals

### vi.stubEnv()

```ts
vi.stubEnv("NODE_ENV", "production");
process.env.NODE_ENV === "production";
import.meta.env.NODE_ENV === "production";

// Restore all
vi.unstubAllEnvs();
```

### vi.stubGlobal()

```ts
vi.stubGlobal("innerWidth", 1024);
vi.stubGlobal("IntersectionObserver", MockObserver);

// Restore all
vi.unstubAllGlobals();
```

## Utilities

### vi.waitFor() - Poll Until Success

```ts
await vi.waitFor(
  () => {
    if (!server.isReady) throw new Error("Not ready");
  },
  { timeout: 5000, interval: 100 }
);
```

### vi.waitUntil() - Poll Until Truthy

```ts
const element = await vi.waitUntil(() => document.querySelector(".loaded"), { timeout: 5000 });
```

### vi.dynamicImportSettled()

```ts
// Wait for all dynamic imports to resolve
function renderComponent() {
  import("./component").then(({ render }) => render());
}

renderComponent();
await vi.dynamicImportSettled();
```

### vi.setConfig() / vi.resetConfig()

```ts
vi.setConfig({
  testTimeout: 10000,
  clearMocks: true,
  fakeTimers: { now: new Date(2024, 0, 1) },
});

vi.resetConfig(); // Restore original
```

## Common Patterns

### Auto-restore Mocks

```ts
// vitest.config.ts
export default {
  test: {
    clearMocks: true, // mockClear before each
    mockReset: true, // mockReset before each
    restoreMocks: true, // mockRestore before each
    unstubEnvs: true, // unstubAllEnvs after each
    unstubGlobals: true, // unstubAllGlobals after each
  },
};
```

### Using Statement (Auto-cleanup)

```ts
// With explicit resource management
it('test', () => {
  using spy = vi.spyOn(console, 'log')
  // spy.mockRestore() called automatically at block end
})
```

### Module Reset Between Tests

```ts
beforeEach(() => {
  vi.resetModules();
});

test("test", async () => {
  const { state } = await import("./module");
  // Fresh module instance
});
```
