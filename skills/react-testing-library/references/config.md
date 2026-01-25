# Configuration Reference

## configure()

```ts
import { configure } from "@testing-library/react";

configure({
  testIdAttribute: "data-testid",
  asyncUtilTimeout: 1000,
  defaultHidden: false,
  throwSuggestions: false,
  getElementError: (message, container) => new Error(message),
  // React Testing Library specific
  reactStrictMode: false,
});
```

---

## Options

### testIdAttribute

Custom attribute for `getByTestId`:

```ts
configure({ testIdAttribute: "data-my-test-id" });

// Now queries use data-my-test-id
// <div data-my-test-id="my-element">
screen.getByTestId("my-element");
```

Default: `'data-testid'`

---

### asyncUtilTimeout

Global timeout for async utilities:

```ts
configure({ asyncUtilTimeout: 5000 }); // 5 seconds

// Affects findBy*, waitFor, waitForElementToBeRemoved
await screen.findByText("Slow content"); // waits up to 5s
```

Default: `1000` (1 second)

---

### defaultHidden

Include hidden elements in `getByRole` by default:

```ts
configure({ defaultHidden: true });

// Now includes aria-hidden elements
screen.getByRole("button"); // includes hidden buttons
```

Default: `false`

---

### throwSuggestions (experimental)

Fail tests when better queries exist:

```ts
configure({ throwSuggestions: true });

// This will throw an error suggesting getByRole
screen.getByTestId("submit-button");
// Error: A better query is available: getByRole('button', { name: /submit/i })
```

Disable per query:

```ts
screen.getByTestId("element", { suggest: false });
```

Default: `false`

---

### defaultIgnore

Elements to ignore in queries and error output:

```ts
configure({ defaultIgnore: "script, style, svg" });
```

Default: `'script, style'`

---

### getElementError

Custom error formatting:

```ts
configure({
  getElementError: (message, container) => {
    const error = new Error([message, prettyDOM(container), "Custom debug info here"].join("\n\n"));
    error.name = "TestingLibraryError";
    return error;
  },
});
```

---

### showOriginalStackTrace

Show full stack trace in waitFor errors:

```ts
configure({ showOriginalStackTrace: true });
```

Default: `false` (cleaned up stack trace)

---

### computedStyleSupportsPseudoElements

Enable pseudo-element support in `getComputedStyle`:

```ts
configure({ computedStyleSupportsPseudoElements: true });
```

Set to `true` in real browsers, `false` for jsdom.

Default: `false`

---

## React Testing Library Specific

### reactStrictMode

Wrap renders in React StrictMode:

```ts
configure({ reactStrictMode: true });

// All renders now use StrictMode
render(<MyComponent />);
// Equivalent to: render(<StrictMode><MyComponent /></StrictMode>)
```

Override per render:

```ts
render(<Component />, { reactStrictMode: false });
```

Default: `false`

---

## Setup File

Apply configuration globally:

```ts
// setupTests.ts
import { configure } from "@testing-library/react";
import "@testing-library/jest-dom";

configure({
  testIdAttribute: "data-test-id",
  asyncUtilTimeout: 3000,
});
```

Jest config:

```js
// jest.config.js
module.exports = {
  setupFilesAfterEnv: ["<rootDir>/setupTests.ts"],
};
```

Vitest config:

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    setupFiles: ["./setupTests.ts"],
  },
});
```

---

## Environment Variables

### DEBUG_PRINT_LIMIT

Max characters in debug output:

```bash
DEBUG_PRINT_LIMIT=20000 npm test
```

Default: `7000`

### COLORS

Enable/disable colored output:

```bash
COLORS=false npm test
```

### RTL_SKIP_AUTO_CLEANUP

Disable automatic cleanup:

```bash
RTL_SKIP_AUTO_CLEANUP=true npm test
```

Or import:

```ts
import "@testing-library/react/dont-cleanup-after-each";
```

---

## Jest Configuration

### jsdom Environment

```js
// jest.config.js
module.exports = {
  testEnvironment: "jsdom", // Required for Jest 27+
};
```

Or per file:

```ts
/**
 * @jest-environment jsdom
 */
```

### Module Resolution

```js
// jest.config.js
module.exports = {
  moduleDirectories: ["node_modules", "utils"],
  moduleNameMapper: {
    "^test-utils$": "<rootDir>/utils/test-utils",
  },
};
```

---

## Vitest Configuration

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true, // Enables auto-cleanup
    setupFiles: ["./setupTests.ts"],
  },
});
```

### Manual Cleanup (if globals: false)

```ts
// setupTests.ts
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(cleanup);
```
