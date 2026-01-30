````markdown
# Module System

Module resolution, auto-install, and file type handling.

## Import Resolution

```typescript
// Extension optional
import { hello } from "./hello";      // Tries .tsx, .ts, .js, etc.
import { hello } from "./hello.ts";   // Explicit
import { hello } from "./hello.js";   // Also resolves to .ts
```
````

**Resolution order:** `.tsx` → `.jsx` → `.ts` → `.mjs` → `.js` → `.cjs` → `.json` → `index.*`

## ES Modules vs CommonJS

```typescript
// ESM (recommended)
import { foo } from "./foo";
export const bar = 1;

// CommonJS (supported)
const { foo } = require("./foo");
module.exports = { bar: 1 };

// Can mix
import { stuff } from "./module.cjs";
const other = require("./other");
```

## Package Resolution

```typescript
import { z } from "zod";
```

Bun scans up for `node_modules/zod`, reads `package.json` exports:

```json
{
  "exports": {
    "bun": "./index.ts", // Bun-specific (can ship TS!)
    "import": "./index.mjs", // ESM
    "require": "./index.cjs", // CommonJS
    "default": "./index.js"
  }
}
```

## Path Aliases

**tsconfig.json:**

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@config": ["./config.ts"]
    }
  }
}
```

```typescript
import { db } from "@/db";
import config from "@config";
```

**package.json (subpath imports):**

```json
{
  "imports": {
    "#config": "./config.ts",
    "#utils/*": "./src/utils/*"
  }
}
```

---

## Auto-Install

When no `node_modules` exists, Bun auto-installs packages:

```typescript
import { z } from "zod";        // Auto-installs latest
import { z } from "zod@3.22.0"; // Exact version
import { z } from "zod@^3.20";  // Semver range
```

**Version resolution:**

1. `bun.lock` (locked version)
2. `package.json` (specified range)
3. `latest`

**Configure in bunfig.toml:**

```toml
[install]
auto = "auto"      # Default: auto if no node_modules
auto = "force"     # Always auto-install
auto = "disable"   # Never
auto = "fallback"  # Check node_modules first
```

**Portable script example:**

```typescript
#!/usr/bin/env bun
// No package.json needed!
import { Hono } from "hono@4.0.0";
const app = new Hono();
export default app;
```

---

## File Types & Loaders

| Extension         | Loader      | Returns      |
| ----------------- | ----------- | ------------ |
| `.ts`, `.tsx`     | TypeScript  | Module       |
| `.js`, `.jsx`     | JavaScript  | Module       |
| `.json`           | JSON        | Object       |
| `.toml`           | TOML        | Object       |
| `.txt`            | Text        | String       |
| `.wasm`           | WebAssembly | Module       |
| `.node`           | N-API       | Native addon |
| `.db` (with type) | SQLite      | Database     |

**Import examples:**

```typescript
import pkg from "./package.json";
import config from "./bunfig.toml";
import readme from "./README.txt";
import db from "./my.db" with { type: "sqlite" };
```

**Custom loaders (bunfig.toml):**

```toml
[loader]
".csv" = "text"
".graphql" = "text"
".mdx" = "jsx"
```

**Type declarations for custom extensions:**

```typescript
// global.d.ts
declare module "*.svg" {
  const content: string;
  export default content;
}
```

---

## Key Points

- **No extension needed** — Bun resolves `.ts`, `.tsx`, etc.
- **ESM + CJS** — can mix in same project
- **`"bun"` condition** — ship TypeScript to npm directly
- **Auto-install** — no `npm install` for quick scripts
- **Top-level await** — supported in ESM
- **TypeScript** — transpiled, not type-checked

```

```
