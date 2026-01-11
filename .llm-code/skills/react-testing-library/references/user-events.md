# User Events Reference

## Installation

```bash
npm install --save-dev @testing-library/user-event
```

## Setup

Always use `userEvent.setup()` before render:

```ts
import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/react";

test("example", async () => {
  const user = userEvent.setup();
  render(<MyComponent />);

  await user.click(screen.getByRole("button"));
});
```

### Setup with Custom Options

```ts
const user = userEvent.setup({
  delay: null, // no delay between events (faster tests)
  advanceTimers: jest.advanceTimersByTime, // for fake timers
  pointerEventsCheck: 0, // disable pointer-events check
  skipHover: true, // skip hover before click
});
```

---

## Why userEvent over fireEvent?

| fireEvent             | userEvent                         |
| --------------------- | --------------------------------- |
| Triggers single event | Simulates full interaction        |
| No visibility checks  | Checks element is visible/enabled |
| Synchronous           | Async (returns Promise)           |
| Low-level             | User-centric                      |

```ts
// fireEvent — just triggers click event
fireEvent.click(button);

// userEvent — hovers, focuses, triggers mousedown/up/click
await user.click(button);
```

---

## Convenience APIs

### Click Events

```ts
// Single click
await user.click(element);

// Double click
await user.dblClick(element);

// Triple click (selects text)
await user.tripleClick(element);
```

### Hover

```ts
await user.hover(element);
await user.unhover(element);
```

### Keyboard Navigation

```ts
// Tab through elements
await user.tab();
await user.tab({ shift: true }); // Shift+Tab
```

---

## Utility APIs

### type() — Input Text

```ts
await user.type(input, "Hello World");

// With options
await user.type(input, "text", {
  skipClick: true, // don't click before typing
  skipAutoClose: true, // don't release keys at end
  initialSelectionStart: 0, // set cursor position
  initialSelectionEnd: 5, // select text range
});
```

### clear() — Clear Input

```ts
await user.clear(input);
// Equivalent to: select all + delete
```

### selectOptions() / deselectOptions()

```ts
// Select by value
await user.selectOptions(select, ["option1", "option2"]);

// Select by text content
await user.selectOptions(select, ["Apple", "Banana"]);

// Select by element
const option = screen.getByRole("option", { name: "Apple" });
await user.selectOptions(select, option);

// Deselect (multi-select only)
await user.deselectOptions(select, "option1");
```

### upload() — File Upload

```ts
const file = new File(["content"], "file.png", { type: "image/png" });
const input = screen.getByLabelText(/upload/i);

await user.upload(input, file);

expect(input.files[0]).toBe(file);
expect(input.files).toHaveLength(1);

// Multiple files
const files = [new File(["a"], "a.png", { type: "image/png" }), new File(["b"], "b.png", { type: "image/png" })];
await user.upload(input, files);
```

---

## Keyboard API

### Basic Keys

```ts
// Press Enter
await user.keyboard("{Enter}");

// Press Tab
await user.keyboard("{Tab}");

// Press Escape
await user.keyboard("{Escape}");

// Press Backspace
await user.keyboard("{Backspace}");

// Press Delete
await user.keyboard("{Delete}");

// Arrow keys
await user.keyboard("{ArrowUp}");
await user.keyboard("{ArrowDown}");
await user.keyboard("{ArrowLeft}");
await user.keyboard("{ArrowRight}");
```

### Modifier Keys

```ts
// Hold Shift (key down, no release)
await user.keyboard("{Shift>}");

// Release Shift
await user.keyboard("{/Shift}");

// Shift + A (hold, press a, release)
await user.keyboard("{Shift>}A{/Shift}");

// Ctrl + A (select all)
await user.keyboard("{Control>}a{/Control}");

// Ctrl + C (copy)
await user.keyboard("{Control>}c{/Control}");

// Ctrl + V (paste)
await user.keyboard("{Control>}v{/Control}");
```

### Type Text

```ts
// Type literal text
await user.keyboard("Hello World");

// Special characters need escaping
await user.keyboard("Hello {{World}}"); // types "Hello {World}"
await user.keyboard("Hello [[World]]"); // types "Hello [World]"
```

---

## Pointer API

### Basic Pointer Actions

```ts
// Click
await user.pointer({ keys: "[MouseLeft]", target: element });

// Right-click
await user.pointer({ keys: "[MouseRight]", target: element });

// Double-click
await user.pointer({ keys: "[MouseLeft][MouseLeft]", target: element });

// Move to element
await user.pointer({ target: element });
```

### Drag and Drop

```ts
await user.pointer([
  { keys: "[MouseLeft>]", target: source }, // Press down on source
  { target: destination }, // Move to destination
  { keys: "[/MouseLeft]" }, // Release
]);
```

---

## Clipboard API

```ts
// Copy selected text
await user.copy();

// Cut selected text
await user.cut();

// Paste from clipboard
await user.paste();

// Paste specific text
await user.paste("pasted text");
```

---

## Complete Example

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("form submission", async () => {
  const user = userEvent.setup();
  const handleSubmit = jest.fn();

  render(<LoginForm onSubmit={handleSubmit} />);

  // Fill form
  await user.type(screen.getByLabelText(/username/i), "john");
  await user.type(screen.getByLabelText(/password/i), "secret123");

  // Check remember me
  await user.click(screen.getByRole("checkbox", { name: /remember/i }));

  // Submit
  await user.click(screen.getByRole("button", { name: /submit/i }));

  expect(handleSubmit).toHaveBeenCalledWith({
    username: "john",
    password: "secret123",
    remember: true,
  });
});
```

---

## Options Reference

| Option               | Default | Description                 |
| -------------------- | ------- | --------------------------- |
| `delay`              | 0       | Delay between events (ms)   |
| `advanceTimers`      | -       | Function to advance timers  |
| `skipHover`          | false   | Skip hover before click     |
| `skipClick`          | false   | Skip click before type      |
| `skipAutoClose`      | false   | Don't release keys at end   |
| `pointerEventsCheck` | 1       | Check pointer-events CSS    |
| `applyAccept`        | true    | Filter files by accept attr |
