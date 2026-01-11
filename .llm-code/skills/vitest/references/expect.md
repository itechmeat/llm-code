# Vitest Expect API Reference

Assertion matchers and utilities.

## Basic Matchers

```ts
import { expect } from "vitest";

// Identity (Object.is)
expect(value).toBe(expected);
expect(obj).not.toBe(otherObj); // Different references

// Deep equality
expect(obj).toEqual({ a: 1, b: { c: 2 } });

// Strict equality (respects types and object properties)
expect({ a: undefined }).not.toStrictEqual({}); // undefined !== missing
expect(new MyClass()).not.toStrictEqual({ prop: true }); // class !== plain object

// Type checks
expect(value).toBeDefined();
expect(value).toBeUndefined();
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeNaN();
expect(value).toBeTypeOf("number"); // typeof check
expect(obj).toBeInstanceOf(MyClass);
```

## Number Matchers

```ts
expect(value).toBeGreaterThan(3);
expect(value).toBeGreaterThanOrEqual(3);
expect(value).toBeLessThan(3);
expect(value).toBeLessThanOrEqual(3);

// Floating point (avoids rounding errors)
expect(0.1 + 0.2).toBeCloseTo(0.3, 5); // numDigits default: 5
```

## String Matchers

```ts
expect("hello world").toContain("world");
expect("hello").toMatch(/^hel/);
expect("hello").toMatch("ell");
```

## Array/Object Matchers

```ts
// Contains item
expect(["a", "b", "c"]).toContain("b");
expect("hello").toContain("ell");

// Contains item with deep equality
expect([{ a: 1 }]).toContainEqual({ a: 1 });

// Has length
expect([1, 2, 3]).toHaveLength(3);
expect("hello").toHaveLength(5);

// Has property
expect(obj).toHaveProperty("a.b.c");
expect(obj).toHaveProperty("a.b", "value");
expect(obj).toHaveProperty(["a", "b"], "value"); // key array

// Partial object match
expect({ a: 1, b: 2 }).toMatchObject({ a: 1 });
expect([{ a: 1 }, { b: 2 }]).toMatchObject([{ a: 1 }, { b: 2 }]);
```

## Error Matchers

```ts
// Throws error
expect(() => throwFn()).toThrow();
expect(() => throwFn()).toThrow("message");
expect(() => throwFn()).toThrow(/regex/);
expect(() => throwFn()).toThrow(ErrorClass);
expect(() => throwFn()).toThrowError(expected); // alias for toThrow
```

## Snapshot Matchers

```ts
// External snapshot file
expect(data).toMatchSnapshot();
expect(data).toMatchSnapshot("custom hint");
expect(data).toMatchSnapshot({ optional: true }); // optional shape

// Inline snapshot (auto-updates)
expect(data).toMatchInlineSnapshot();
expect(data).toMatchInlineSnapshot(`
{
  "foo": "bar"
}
`);

// File snapshot (saves to separate file)
expect(data).toMatchFileSnapshot("./output.txt");
```

## Mock Matchers

```ts
import { vi, expect } from "vitest";

const mock = vi.fn();

// Called
expect(mock).toHaveBeenCalled();
expect(mock).toHaveBeenCalledTimes(2);

// Arguments
expect(mock).toHaveBeenCalledWith("arg1", "arg2");
expect(mock).toHaveBeenLastCalledWith("arg");
expect(mock).toHaveBeenNthCalledWith(2, "arg"); // 2nd call

// Return values
expect(mock).toHaveReturned();
expect(mock).toHaveReturnedTimes(2);
expect(mock).toHaveReturnedWith("value");
expect(mock).toHaveLastReturnedWith("value");
expect(mock).toHaveNthReturnedWith(2, "value");
```

## Async Matchers

```ts
// Promise resolution
await expect(Promise.resolve("ok")).resolves.toBe("ok");
await expect(Promise.resolve(obj)).resolves.toEqual({ a: 1 });

// Promise rejection
await expect(Promise.reject("error")).rejects.toBe("error");
await expect(Promise.reject(new Error())).rejects.toThrow();

// Polling (retries until passes or times out)
await expect.poll(() => fetchStatus()).toBe("ready");
await expect
  .poll(() => result, {
    interval: 50, // check interval (default: 50ms)
    timeout: 5000, // max wait (default: 1000ms)
    message: "custom error message",
  })
  .toBe("expected");
```

## Soft Assertions

```ts
// Continue test even if assertion fails
expect.soft(value).toBe(1);
expect.soft(other).toBe(2);
// Test fails at end if any soft assertion failed
```

## Assertion Counting

```ts
test("has correct assertions", () => {
  expect.assertions(2); // exactly 2 assertions must run
  expect.hasAssertions(); // at least 1 assertion must run

  // Unreachable (utility)
  if (condition) {
    expect.unreachable("should not reach here");
  }
});
```

## Custom Matchers

```ts
import { expect } from "vitest";

expect.extend({
  toBeEven(received) {
    const pass = received % 2 === 0;
    return {
      pass,
      message: () => (pass ? `expected ${received} not to be even` : `expected ${received} to be even`),
    };
  },
});

// TypeScript
interface CustomMatchers<R = unknown> {
  toBeEven(): R;
}
declare module "vitest" {
  interface Assertion<T> extends CustomMatchers<T> {}
  interface AsymmetricMatchersContaining extends CustomMatchers {}
}

// Usage
expect(4).toBeEven();
expect(3).not.toBeEven();
```

## Asymmetric Matchers

```ts
// Match anything (not null/undefined)
expect(fn).toHaveBeenCalledWith(expect.anything());

// Match by type
expect(fn).toHaveBeenCalledWith(expect.any(Number));
expect(fn).toHaveBeenCalledWith(expect.any(String));

// Partial array
expect(arr).toEqual(expect.arrayContaining([1, 2]));

// Partial object
expect(obj).toEqual(expect.objectContaining({ key: "value" }));

// String patterns
expect(obj).toEqual({
  name: expect.stringContaining("John"),
  email: expect.stringMatching(/@/),
});

// Negation
expect(arr).toEqual(expect.not.arrayContaining([4]));
expect(str).not.toEqual(expect.stringContaining("foo"));

// Closeness for numbers
expect(arr).toEqual([expect.closeTo(10.1, 1)]);
```

## Modifier: not

```ts
// Negate any matcher
expect(value).not.toBe(other);
expect(arr).not.toContain(item);
expect(fn).not.toHaveBeenCalled();
```

## Important Notes

- **Floating point**: Use `toBeCloseTo` for float comparisons
- **Reference equality**: `toBe` uses `Object.is`, not `===`
- **Undefined vs missing**: `toStrictEqual` distinguishes them
- **Concurrent tests**: Use `expect` from context for reliable snapshots
- **Mock assertions**: Only work with spy functions from `vi.fn()` or `vi.spyOn()`
