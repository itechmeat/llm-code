# Vitest Browser Mode Reference

Run tests in real browsers for accurate DOM testing.

## Why Browser Mode?

- **Real browser environment** - No simulation (jsdom/happy-dom) discrepancies
- **Native browser APIs** - Access to window, document, and browser-specific features
- **Component testing** - Test React, Vue, Svelte, etc. in actual browsers
- **Visual regression** - Screenshot and compare UI changes

## Installation

### Quick Setup

```bash
npx vitest init browser
```

### Manual Setup

```bash
# For Playwright (recommended)
npm install -D vitest @vitest/browser-playwright

# For WebdriverIO
npm install -D vitest @vitest/browser-webdriverio

# For preview only (not for CI)
npm install -D vitest @vitest/browser-preview
```

## Configuration

### Basic Setup

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config";
import { playwright } from "@vitest/browser-playwright";

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      provider: playwright(),
      instances: [{ browser: "chromium" }],
    },
  },
});
```

### With Framework (React Example)

```ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { playwright } from "@vitest/browser-playwright";

export default defineConfig({
  plugins: [react()],
  test: {
    browser: {
      enabled: true,
      provider: playwright(),
      instances: [{ browser: "chromium" }],
    },
  },
});
```

### Multi-Browser Testing

```ts
{
  browser: {
    enabled: true,
    provider: playwright(),
    instances: [
      { browser: 'chromium' },
      { browser: 'firefox' },
      { browser: 'webkit' },
    ],
  },
}
```

### Headless Mode

```ts
{
  browser: {
    enabled: true,
    provider: playwright(),
    headless: true, // Run without UI
    instances: [{ browser: 'chromium' }],
  },
}
```

### Mixed Node + Browser Projects

```ts
export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: "unit",
          include: ["tests/unit/**/*.test.ts"],
          environment: "node",
        },
      },
      {
        test: {
          name: "browser",
          include: ["tests/browser/**/*.test.ts"],
          browser: {
            enabled: true,
            provider: playwright(),
            instances: [{ browser: "chromium" }],
          },
        },
      },
    ],
  },
});
```

## Available Browsers

**Playwright:**

- `chromium`
- `firefox`
- `webkit`

**WebdriverIO:**

- `chrome`
- `firefox`
- `edge`
- `safari`

## Writing Browser Tests

### Basic Test

```ts
import { expect, test } from "vitest";
import { page } from "vitest/browser";

test("renders content", async () => {
  document.body.innerHTML = "<div>Hello World</div>";

  await expect.element(page.getByText("Hello World")).toBeInTheDocument();
});
```

### With Locators

```ts
import { page, userEvent } from "vitest/browser";

test("form interaction", async () => {
  // Find elements
  const input = page.getByLabelText(/username/i);
  const button = page.getByRole("button", { name: /submit/i });

  // Interact
  await input.fill("john");
  await button.click();

  // Assert
  await expect.element(page.getByText("Welcome, john")).toBeVisible();
});
```

### Locator Methods

```ts
import { page } from "vitest/browser";

// By role (recommended)
page.getByRole("button", { name: "Submit" });
page.getByRole("textbox", { name: /email/i });
page.getByRole("heading", { level: 1 });

// By text
page.getByText("Hello World");
page.getByText(/hello/i); // regex

// By label
page.getByLabelText("Username");

// By placeholder
page.getByPlaceholder("Enter email");

// By test ID
page.getByTestId("submit-button");

// By title
page.getByTitle("Close dialog");

// By alt text
page.getByAltText("Profile picture");

// CSS selector (escape hatch)
page.elementLocator(document.querySelector(".my-class"));
```

### User Events

```ts
import { userEvent, page } from "vitest/browser";

// Typing
await userEvent.type(input, "Hello");
await input.fill("Hello"); // Alternative

// Clicking
await userEvent.click(button);
await button.click(); // Alternative

// Keyboard
await userEvent.keyboard("{Enter}");

// Hover
await userEvent.hover(element);

// Focus
await userEvent.focus(input);

// Select
await userEvent.selectOptions(select, ["option1"]);

// File upload
await userEvent.upload(fileInput, file);

// Drag and drop
await userEvent.dragAndDrop(source, target);
```

### Browser Assertions

```ts
import { expect } from "vitest";
import { page } from "vitest/browser";

// Element exists
await expect.element(page.getByText("Hello")).toBeInTheDocument();

// Visibility
await expect.element(locator).toBeVisible();
await expect.element(locator).not.toBeVisible();

// Enabled/Disabled
await expect.element(button).toBeEnabled();
await expect.element(button).toBeDisabled();

// Value
await expect.element(input).toHaveValue("text");

// Text content
await expect.element(heading).toHaveTextContent("Title");

// Attribute
await expect.element(link).toHaveAttribute("href", "/home");

// Class
await expect.element(element).toHaveClass("active");

// Focus
await expect.element(input).toBeFocused();
```

## Component Testing

### React

```bash
npm install -D vitest-browser-react
```

```tsx
import { render } from "vitest-browser-react";
import { expect, test } from "vitest";
import Button from "./Button";

test("button click", async () => {
  const screen = render(<Button>Click me</Button>);

  await screen.getByRole("button").click();

  await expect.element(screen.getByText("Clicked!")).toBeVisible();
});
```

### Vue

```bash
npm install -D vitest-browser-vue
```

```ts
import { render } from "vitest-browser-vue";
import Component from "./Component.vue";

test("v-model works", async () => {
  const screen = render(Component);

  await screen.getByLabelText(/username/i).fill("Bob");

  await expect.element(screen.getByText("Hi, Bob")).toBeInTheDocument();
});
```

### Svelte

```bash
npm install -D vitest-browser-svelte
```

```ts
import { render } from "vitest-browser-svelte";
import Counter from "./Counter.svelte";

test("counter increments", async () => {
  const screen = render(Counter);

  await screen.getByRole("button").click();

  await expect.element(screen.getByText("1")).toBeVisible();
});
```

## Visual Regression Testing

```ts
import { page } from "vitest/browser";

test("visual snapshot", async () => {
  // Full page screenshot
  await expect(page.screenshot()).toMatchImageSnapshot();

  // Element screenshot
  const element = page.getByTestId("card");
  await expect(element.screenshot()).toMatchImageSnapshot();
});
```

## Viewport Control

```ts
import { page } from "vitest/browser";

test("responsive design", async () => {
  // Set viewport
  await page.viewport(375, 667); // iPhone SE
  await expect.element(page.getByTestId("mobile-menu")).toBeVisible();

  await page.viewport(1920, 1080); // Desktop
  await expect.element(page.getByTestId("desktop-nav")).toBeVisible();
});
```

## Running Browser Tests

```bash
# Run with browser mode
vitest --browser.enabled

# Specific browser
vitest --browser.name=chromium

# Headless
vitest --browser.headless

# With UI
vitest --browser.ui
```

## Limitations

### No vi.spyOn on Imports

```ts
// ❌ Doesn't work in browser mode
import * as module from "./module";
vi.spyOn(module, "method");

// ✅ Use vi.mock with spy option
vi.mock("./module", { spy: true });
```

### Blocking Dialogs Mocked

`alert()`, `confirm()`, `prompt()` are automatically mocked because they block execution. Mock them explicitly for predictable behavior.

## Best Practices

1. **Use Playwright provider** for CI - supports parallel execution
2. **Use locators by role** - most resilient selectors
3. **Use `expect.element()`** - waits for element automatically
4. **Avoid `testing-library/user-event`** - use `vitest/browser` instead
5. **Use headless mode** in CI
6. **Separate browser tests** into their own project
