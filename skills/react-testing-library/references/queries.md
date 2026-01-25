# Queries Reference

## Query Types Summary

| Type            | No Match | 1 Match        | >1 Match | Async |
| --------------- | -------- | -------------- | -------- | ----- |
| `getBy...`      | throw    | return element | throw    | No    |
| `queryBy...`    | null     | return element | throw    | No    |
| `findBy...`     | throw    | return element | throw    | Yes   |
| `getAllBy...`   | throw    | array          | array    | No    |
| `queryAllBy...` | []       | array          | array    | No    |
| `findAllBy...`  | throw    | array          | array    | Yes   |

## When to Use

- **getBy\*** — element should exist
- **queryBy\*** — element may not exist (use for negative assertions)
- **findBy\*** — element appears asynchronously

---

## Query Priority (Best → Worst)

### 1. Accessible to Everyone (Preferred)

#### `getByRole` — Best choice for most queries

```ts
// Buttons
getByRole("button", { name: /submit/i });

// Form fields
getByRole("textbox", { name: /email/i });
getByRole("checkbox", { name: /remember me/i });
getByRole("combobox", { name: /country/i });

// Headings
getByRole("heading", { name: /welcome/i });
getByRole("heading", { level: 2 });

// Navigation
getByRole("link", { name: /home/i });
getByRole("navigation");

// Lists
getByRole("list");
getByRole("listitem");

// Dialogs
getByRole("dialog");
getByRole("alertdialog");
```

**Role Options:**

```ts
getByRole("button", {
  name: /submit/i, // accessible name (text, aria-label)
  description: /text/, // aria-describedby content
  hidden: true, // include hidden elements (default: false)
  selected: true, // aria-selected state
  checked: true, // checkbox/radio checked state
  pressed: true, // toggle button pressed state
  expanded: true, // aria-expanded state
  current: "page", // aria-current value
  busy: false, // aria-busy state
  level: 2, // heading level (h1=1, h2=2, etc.)
  value: { now: 50, min: 0, max: 100 }, // slider/spinbutton value
  queryFallbacks: true, // include fallback roles
});
```

#### `getByLabelText` — Best for form fields

```ts
getByLabelText("Username");
getByLabelText(/email/i);
getByLabelText("Password", { selector: "input" });
```

#### `getByPlaceholderText` — When no label available

```ts
getByPlaceholderText("Enter email");
```

#### `getByText` — For non-interactive content

```ts
getByText("Welcome back!");
getByText(/loading/i);
getByText((content, element) => content.startsWith("Hello"));
```

#### `getByDisplayValue` — Current form value

```ts
getByDisplayValue("john@example.com");
```

### 2. Semantic Queries

#### `getByAltText` — Images

```ts
getByAltText("Company logo");
getByAltText(/avatar/i);
```

#### `getByTitle` — Title attribute (less reliable)

```ts
getByTitle("Close");
```

### 3. Test IDs (Escape Hatch)

#### `getByTestId` — Last resort

```ts
getByTestId("submit-button");
getByTestId("custom-element");
```

---

## TextMatch

Queries accept strings, regex, or functions:

```ts
// Exact string
getByText("Hello World");

// Substring (case-insensitive)
getByText("hello", { exact: false });

// Regex
getByText(/hello world/i);
getByText(/^hello/i); // starts with

// Custom function
getByText((content, element) => {
  return element.tagName === "SPAN" && content.includes("Hello");
});
```

### Options

```ts
getByText("text", {
  exact: false, // substring match, case-insensitive
  normalizer: (str) => str.trim().toLowerCase(), // custom normalizer
});

// Default normalizer options
import { getDefaultNormalizer } from "@testing-library/react";
getByText("text", {
  normalizer: getDefaultNormalizer({ trim: false, collapseWhitespace: true }),
});
```

---

## Using `screen`

Always prefer `screen` over destructuring:

```ts
import { render, screen } from "@testing-library/react";

render(<MyComponent />);

// ✅ Recommended
screen.getByRole("button");

// ❌ Avoid (unless scoping)
const { getByRole } = render(<MyComponent />);
```

---

## Query Within Elements

```ts
import { within, screen } from "@testing-library/react";

const modal = screen.getByRole("dialog");
const submitBtn = within(modal).getByRole("button", { name: /submit/i });

// Alternative
const form = screen.getByRole("form");
within(form).getByLabelText("Email");
```

---

## Common Roles Reference

| Element                   | Default Role |
| ------------------------- | ------------ |
| `<button>`                | button       |
| `<a href="...">`          | link         |
| `<input type="text">`     | textbox      |
| `<input type="checkbox">` | checkbox     |
| `<input type="radio">`    | radio        |
| `<select>`                | combobox     |
| `<ul>`, `<ol>`            | list         |
| `<li>`                    | listitem     |
| `<table>`                 | table        |
| `<tr>`                    | row          |
| `<img>`                   | img          |
| `<h1>`-`<h6>`             | heading      |
| `<nav>`                   | navigation   |
| `<main>`                  | main         |
| `<article>`               | article      |
| `<dialog>`                | dialog       |
| `<form>`                  | form         |

**Note:** `<input type="password">` has no implicit role — use `getByLabelText`.

---

## Performance Tip

`getByRole` can be slow on large DOMs. For performance-critical tests:

```ts
// Faster alternatives when accessibility isn't the focus
getByLabelText("Email"); // faster than getByRole('textbox', { name: 'Email' })
getByText("Submit"); // faster than getByRole('button', { name: 'Submit' })

// Or skip visibility checks
getByRole("button", { hidden: true });
```
