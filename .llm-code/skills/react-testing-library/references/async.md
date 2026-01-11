# Async Utilities Reference

## Overview

| Method                      | Use Case                      |
| --------------------------- | ----------------------------- |
| `findBy*`                   | Wait for element to appear    |
| `waitFor`                   | Wait for any condition        |
| `waitForElementToBeRemoved` | Wait for element to disappear |

Always use `await` with async utilities!

---

## findBy Queries

`findBy*` = `waitFor` + `getBy*`

```ts
// Wait for element to appear
const button = await screen.findByRole("button", { name: /submit/i });

// With timeout
const element = await screen.findByText("Loaded", {}, { timeout: 5000 });
```

### Options

```ts
await screen.findByText(
  'text',           // query matcher
  { exact: false }, // query options
  {                 // waitFor options
    timeout: 1000,
    interval: 50,
    onTimeout: (error) => error,
    mutationObserverOptions: { ... },
  }
)
```

---

## waitFor()

Retry callback until it succeeds or times out:

```ts
import { waitFor, screen } from "@testing-library/react";

// Wait for assertion
await waitFor(() => {
  expect(screen.getByText("Loaded")).toBeInTheDocument();
});

// Wait for mock to be called
await waitFor(() => {
  expect(mockFn).toHaveBeenCalled();
});

// Wait with custom timeout
await waitFor(() => expect(element).toBeVisible(), { timeout: 5000, interval: 100 });
```

### Options

| Option                    | Default                                                                   | Description              |
| ------------------------- | ------------------------------------------------------------------------- | ------------------------ |
| `container`               | document                                                                  | DOM container to observe |
| `timeout`                 | 1000                                                                      | Max wait time (ms)       |
| `interval`                | 50                                                                        | Retry interval (ms)      |
| `onTimeout`               | -                                                                         | Error transformer        |
| `mutationObserverOptions` | `{subtree: true, childList: true, attributes: true, characterData: true}` | MutationObserver config  |

### Common Patterns

```ts
// Wait for loading to finish
await waitFor(() => {
  expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
});

// Wait for API call
await waitFor(() => {
  expect(mockApi).toHaveBeenCalledTimes(1);
});

// Wait for DOM change
await waitFor(() => {
  expect(screen.getByRole("list").children).toHaveLength(5);
});
```

### ⚠️ Anti-patterns

```ts
// ❌ Don't use waitFor with findBy (findBy already waits)
await waitFor(() => screen.findByText("Hello"));

// ✅ Just use findBy
const element = await screen.findByText("Hello");

// ❌ Don't wrap getBy in waitFor if element exists
await waitFor(() => screen.getByText("Static"));

// ✅ Use getBy directly
const element = screen.getByText("Static");

// ❌ Empty waitFor callback
await waitFor(() => {});

// ✅ Always assert something
await waitFor(() => expect(something).toBe(true));
```

---

## waitForElementToBeRemoved()

Wait for element to be removed from DOM:

```ts
import { waitForElementToBeRemoved, screen } from "@testing-library/react";

// Pass element directly
const loader = screen.getByText("Loading...");
await waitForElementToBeRemoved(loader);

// Pass callback
await waitForElementToBeRemoved(() => screen.queryByText("Loading..."));

// With timeout
await waitForElementToBeRemoved(() => screen.queryByText("Loading..."), { timeout: 5000 });
```

### Important Notes

```ts
// ❌ Element must exist when calling
await waitForElementToBeRemoved(screen.queryByText("Not there"));
// Error: Element not found

// ✅ Element must exist initially
const element = screen.getByText("Loading...");
await waitForElementToBeRemoved(element);
```

---

## Async Test Patterns

### Loading State

```tsx
test("shows loading then data", async () => {
  render(<DataFetcher />);

  // Loading appears
  expect(screen.getByText("Loading...")).toBeInTheDocument();

  // Wait for data to load
  await waitForElementToBeRemoved(() => screen.queryByText("Loading..."));

  // Data appears
  expect(screen.getByText("Data loaded")).toBeInTheDocument();
});
```

### Form Submission

```tsx
test("submits form and shows success", async () => {
  const user = userEvent.setup();
  render(<ContactForm />);

  await user.type(screen.getByLabelText("Email"), "test@example.com");
  await user.click(screen.getByRole("button", { name: "Submit" }));

  // Wait for success message
  expect(await screen.findByText("Thank you!")).toBeInTheDocument();
});
```

### Multiple Async Operations

```tsx
test("loads and updates data", async () => {
  render(<Dashboard />);

  // Wait for initial load
  await screen.findByText("Dashboard");

  // Trigger refresh
  await userEvent.click(screen.getByRole("button", { name: "Refresh" }));

  // Wait for loading indicator to appear and disappear
  await waitFor(() => {
    expect(screen.queryByText("Refreshing...")).not.toBeInTheDocument();
  });

  // Verify updated content
  expect(screen.getByText("Updated")).toBeInTheDocument();
});
```

### Testing Error States

```tsx
test("shows error on failure", async () => {
  server.use(
    rest.get("/api/data", (req, res, ctx) => {
      return res(ctx.status(500));
    })
  );

  render(<DataComponent />);

  // Wait for error
  expect(await screen.findByRole("alert")).toHaveTextContent("Error loading data");
});
```

---

## Timeout Configuration

### Global Default

```ts
import { configure } from "@testing-library/react";

configure({
  asyncUtilTimeout: 5000, // 5 seconds
});
```

### Per-Query

```ts
await screen.findByText("Slow content", {}, { timeout: 10000 });

await waitFor(() => expect(element).toBeVisible(), { timeout: 10000 });
```

---

## Best Practices

1. **Use findBy for async elements**

   ```ts
   const element = await screen.findByText("Loaded");
   ```

2. **Use waitFor for assertions**

   ```ts
   await waitFor(() => expect(mockFn).toHaveBeenCalled());
   ```

3. **Don't mix waitFor with findBy**

   ```ts
   // ❌ Bad
   await waitFor(() => screen.findByText("x"));

   // ✅ Good
   await screen.findByText("x");
   ```

4. **Always await async operations**

   ```ts
   // ❌ Missing await
   screen.findByText("Hello");

   // ✅ Correct
   await screen.findByText("Hello");
   ```

5. **Use queryBy for disappearance checks**
   ```ts
   await waitFor(() => {
     expect(screen.queryByText("Loading")).not.toBeInTheDocument();
   });
   ```
