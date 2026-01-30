# Bun Transpiler

Programmatic access to Bun's internal transpiler for TypeScript/JSX transformation.

## Basic Usage

```ts
const transpiler = new Bun.Transpiler({
  loader: "tsx", // "js" | "jsx" | "ts" | "tsx"
});

const code = `
import React from 'react';
export function Home(props: {title: string}) {
  return <p>{props.title}</p>;
}
`;

const result = transpiler.transformSync(code);
// Returns vanilla JavaScript string
```

## Methods

### transformSync()

Synchronous transpilation (same thread):

```ts
const transpiler = new Bun.Transpiler({ loader: "tsx" });

const js = transpiler.transformSync(code);

// Override loader for specific code
transpiler.transformSync("<div>hi</div>", "jsx");
```

### transform()

Async transpilation (worker threadpool):

```ts
const js = await transpiler.transform(code);

// Override loader
await transpiler.transform(code, "tsx");
```

**Note**: For most cases, `transformSync` is faster due to threadpool overhead.

### scan()

Analyze imports and exports:

```ts
const code = `
import React from 'react';
import type {ReactNode} from 'react';
const val = require('./cjs.js');
import('./loader');
export const name = "hello";
`;

const result = transpiler.scan(code);
// {
//   exports: ["name"],
//   imports: [
//     { path: "react", kind: "import-statement" },
//     { path: "./cjs.js", kind: "require-call" },
//     { path: "./loader", kind: "dynamic-import" }
//   ]
// }
```

### scanImports()

Faster import scanning (slightly less accurate):

```ts
const imports = transpiler.scanImports(code);
// [
//   { path: "react", kind: "import-statement" },
//   { path: "./cjs.js", kind: "require-call" },
//   { path: "./loader", kind: "dynamic-import" }
// ]
```

## Import Kinds

| Kind                 | Example                |
| -------------------- | ---------------------- |
| `"import-statement"` | `import x from 'y'`    |
| `"require-call"`     | `require('y')`         |
| `"require-resolve"`  | `require.resolve('y')` |
| `"dynamic-import"`   | `import('y')`          |
| `"import-rule"`      | `@import 'y.css'`      |
| `"url-token"`        | `url('y.png')`         |

## Options

```ts
const transpiler = new Bun.Transpiler({
  // Default loader
  loader: "tsx",

  // Target platform
  target: "bun", // "browser" | "bun" | "node"

  // Define constants
  define: {
    "process.env.NODE_ENV": '"production"',
  },

  // Custom tsconfig
  tsconfig: {
    compilerOptions: {
      jsx: "react-jsx",
      jsxImportSource: "preact",
    },
  },

  // Remove unused imports
  trimUnusedImports: true,

  // Inline constant values
  inline: true, // default

  // Whitespace minification
  minifyWhitespace: false,

  // Export manipulation
  exports: {
    eliminate: ["debugOnly"],
    replace: { "oldName": "newName" },
  },
});
```

## Custom JSX

### Preact

```ts
const transpiler = new Bun.Transpiler({
  loader: "tsx",
  tsconfig: JSON.stringify({
    compilerOptions: {
      jsx: "react-jsx",
      jsxImportSource: "preact",
    },
  }),
});
```

### Emotion

```ts
const transpiler = new Bun.Transpiler({
  loader: "tsx",
  tsconfig: JSON.stringify({
    compilerOptions: {
      jsx: "react-jsx",
      jsxImportSource: "@emotion/react",
    },
  }),
});
```

## Macros

Replace imports with macro implementations:

```ts
const transpiler = new Bun.Transpiler({
  loader: "tsx",
  macro: {
    "react-relay": {
      graphql: "bun-macro-relay/bun-macro-relay.tsx",
    },
  },
});
```

## Practical Examples

### Build-Time Transform

```ts
const transpiler = new Bun.Transpiler({
  loader: "tsx",
  target: "browser",
  define: {
    "process.env.NODE_ENV": '"production"',
    "__DEV__": "false",
  },
  trimUnusedImports: true,
  minifyWhitespace: true,
});

const source = await Bun.file("src/app.tsx").text();
const output = transpiler.transformSync(source);
await Bun.write("dist/app.js", output);
```

### Dependency Analysis

```ts
const transpiler = new Bun.Transpiler({ loader: "tsx" });

async function getDependencies(file: string) {
  const code = await Bun.file(file).text();
  const { imports } = transpiler.scan(code);

  return imports
    .filter(i => i.kind === "import-statement")
    .map(i => i.path);
}

const deps = await getDependencies("src/index.ts");
console.log("Dependencies:", deps);
```

### Hot Module Replacement

```ts
const transpiler = new Bun.Transpiler({
  loader: "tsx",
  target: "browser",
});

Bun.serve({
  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname.endsWith(".tsx")) {
      const file = `.${url.pathname}`;
      const source = await Bun.file(file).text();
      const code = transpiler.transformSync(source);

      return new Response(code, {
        headers: { "Content-Type": "application/javascript" },
      });
    }

    return new Response("Not found", { status: 404 });
  },
});
```

## Performance Notes

- `transformSync` runs in main thread — best for small files
- `transform` uses worker pool — better for many large files
- `scanImports` is faster than `scan` for just listing imports
- Type-only imports are automatically ignored
