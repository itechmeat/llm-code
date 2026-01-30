````markdown
# TypeScript & JSX

Bun runs TypeScript and JSX natively without configuration.

## TypeScript

### Zero Config

```typescript
// index.ts — just run it
bun run index.ts
```
````

Bun transpiles internally, **no separate type checking**. Use IDE or `tsc --noEmit`.

### tsconfig.json

Bun reads `tsconfig.json` or `jsconfig.json` automatically.

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "types": ["bun-types"],
    "strict": true,
    "noEmit": true
  }
}
```

### Type Checking

```bash
# Install types
bun add -d bun-types typescript

# Type check
bunx tsc --noEmit

# Watch mode
bunx tsc --noEmit --watch
```

### Bun-Specific Types

```typescript
/// <reference types="bun-types" />

import type { Server } from "bun";

const server: Server = Bun.serve({
  fetch(req) {
    return new Response("Hello");
  },
});
```

---

## JSX

### Default (React)

```tsx
// React JSX (default)
const element = <div className="foo">Hello</div>;
// → React.createElement("div", { className: "foo" }, "Hello")
```

### JSX Pragma

```tsx
// Override for specific file
/** @jsx h */
import { h } from "preact";

const element = <div>Preact</div>;
```

### Configuration

**tsconfig.json:**

```json
{
  "compilerOptions": {
    "jsx": "react-jsx", // Modern React 17+
    "jsxImportSource": "react" // Source for jsx-runtime
  }
}
```

**JSX modes:**

| Mode           | Description                         |
| -------------- | ----------------------------------- |
| `react`        | Classic `React.createElement`       |
| `react-jsx`    | Modern auto-import from jsx-runtime |
| `react-jsxdev` | Development mode with extra checks  |
| `preserve`     | Keep JSX, don't transform           |

### Fragment Pragma

```tsx
/** @jsxFrag Fragment */
import { Fragment } from "react";

const element = <>Content</>;
```

### Preact Example

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "preact"
  }
}
```

```tsx
// Uses preact/jsx-runtime automatically
const App = () => <div>Preact App</div>;
```

### Solid.js Example

```json
{
  "compilerOptions": {
    "jsx": "preserve",
    "jsxImportSource": "solid-js"
  }
}
```

---

## File Extensions

| Extension      | Behavior               |
| -------------- | ---------------------- |
| `.ts`          | TypeScript             |
| `.tsx`         | TypeScript + JSX       |
| `.jsx`         | JavaScript + JSX       |
| `.mts`, `.cts` | ES/CommonJS TypeScript |

---

## Key Points

- **No compilation step** — run `.ts`/`.tsx` directly
- **No type checking** at runtime — use `tsc --noEmit`
- `jsx: "react-jsx"` for modern React (auto-imports)
- `jsxImportSource` to switch frameworks (Preact, Solid)
- File pragmas (`@jsx`, `@jsxFrag`) override per-file

```

```
