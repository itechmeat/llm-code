# Debugging Reference

## screen.debug()

Print current DOM state:

```ts
import { screen } from "@testing-library/react";

// Print entire document
screen.debug();

// Print specific element
screen.debug(screen.getByRole("button"));

// Print multiple elements
screen.debug(screen.getAllByRole("listitem"));

// With max length
screen.debug(undefined, 20000);

// With options
screen.debug(undefined, 10000, { highlight: false });
```

---

## prettyDOM()

Convert DOM to string:

```ts
import { prettyDOM } from "@testing-library/react";

const div = document.createElement("div");
div.innerHTML = "<h1>Hello</h1>";

console.log(prettyDOM(div));
// <div>
//   <h1>Hello</h1>
// </div>

// With max length
prettyDOM(element, 5000);

// With options
prettyDOM(element, undefined, {
  highlight: false,
  filterNode: (node) => node.tagName !== "SCRIPT",
});
```

### Options

| Option       | Description                                 |
| ------------ | ------------------------------------------- |
| `highlight`  | Syntax highlighting (default: true in node) |
| `filterNode` | Function to exclude nodes                   |

---

## logRoles()

Show all ARIA roles in DOM:

```ts
import { logRoles } from "@testing-library/react";

const { container } = render(<Navigation />);
logRoles(container);

// Output:
// navigation:
// <nav />
// --------------------------------------------------
// list:
// <ul />
// --------------------------------------------------
// listitem:
// <li />
// <li />
```

Use when `getByRole` fails to help identify correct role.

---

## screen.logTestingPlaygroundURL()

Generate Testing Playground link:

```ts
render(<MyComponent />);

// Log URL for entire document
screen.logTestingPlaygroundURL();
// https://testing-playground.com/#markup=...

// Log URL for specific element
screen.logTestingPlaygroundURL(screen.getByRole("form"));
```

Open URL in browser to interactively find queries.

---

## Automatic Error Logging

When `getBy*` fails, DOM is automatically logged:

```
Unable to find an element with the text: Goodbye.
Here is the state of your container:
<div>
  <h1>Hello World</h1>
</div>
```

### Increase Output Length

```bash
# macOS/Linux
DEBUG_PRINT_LIMIT=20000 npm test

# Windows (with cross-env)
cross-env DEBUG_PRINT_LIMIT=20000 npm test
```

### Disable Colors

```bash
COLORS=false npm test
```

---

## Debugging Tips

### 1. Print Before Assertion

```ts
screen.debug();
expect(screen.getByText("Hello")).toBeInTheDocument();
```

### 2. Use logRoles for Role Queries

```ts
const { container } = render(<MyComponent />);
logRoles(container);
// Then use correct role in getByRole()
```

### 3. Check Element Properties

```ts
const button = screen.getByRole("button");
console.log({
  text: button.textContent,
  disabled: button.disabled,
  visible: button.style.display,
  classes: button.className,
});
```

### 4. Inspect Async State

```ts
// Before async action
screen.debug()

await user.click(button)

// After async action
await waitFor(() => {
  screen.debug() // See state at each retry
  expect(...).toBe(...)
})
```

### 5. Check What Queries Return

```ts
// See what's found
console.log(screen.queryAllByRole("button"));

// Check accessible name
const buttons = screen.getAllByRole("button");
buttons.forEach((b) => console.log(b.textContent, b.getAttribute("aria-label")));
```

---

## Common Debugging Scenarios

### Can't Find Element

```ts
// 1. Print DOM
screen.debug();

// 2. Check all roles
logRoles(container);

// 3. Try different queries
screen.queryByText("...");
screen.queryByRole("...");
screen.queryByTestId("...");
```

### Element Not Visible

```ts
// Include hidden elements
screen.getByRole("button", { hidden: true });

// Check visibility
const el = screen.getByText("Hidden");
console.log(window.getComputedStyle(el).display);
console.log(window.getComputedStyle(el).visibility);
```

### Async Element Not Appearing

```ts
// Add debug in waitFor
await waitFor(
  () => {
    screen.debug();
    expect(element).toBeInTheDocument();
  },
  { timeout: 5000 }
);
```

### Multiple Elements Found

```ts
// See all matching elements
screen.debug(screen.getAllByRole("button"));

// Be more specific
screen.getByRole("button", { name: /submit/i });
```

---

## Testing Playground

Interactive tool at [testing-playground.com](https://testing-playground.com):

1. Paste HTML markup
2. Click elements to see suggested queries
3. Get query recommendations based on priority

### Browser Extension

Install "Testing Playground" Chrome extension:

- Inspect elements in DevTools
- Get query suggestions
- See accessibility tree
