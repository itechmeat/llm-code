# Plugins

Universal plugin API for Bun runtime and bundler.

## Plugin Structure

```typescript
import type { BunPlugin } from "bun";

const myPlugin: BunPlugin = {
  name: "my-plugin",
  setup(build) {
    // Register hooks here
  },
};
```

## Usage

### With Bundler

```typescript
await Bun.build({
  entrypoints: ["./app.ts"],
  outdir: "./dist",
  plugins: [myPlugin],
});
```

### With Runtime (preload)

```typescript
// plugins.ts
import { plugin } from "bun";

plugin({
  name: "yaml-loader",
  setup(build) {
    // ...
  },
});
```

```toml
# bunfig.toml
preload = ["./plugins.ts"]
```

## Lifecycle Hooks

### onStart

Run when bundle starts:

```typescript
build.onStart(() => {
  console.log("Bundle started!");
});

// Async supported
build.onStart(async () => {
  await setup();
});
```

### onResolve

Intercept module resolution:

```typescript
build.onResolve({ filter: /^images\// }, (args) => {
  return {
    path: args.path.replace("images/", "./public/images/"),
  };
});
```

### onLoad

Transform module contents:

```typescript
build.onLoad({ filter: /\.yaml$/ }, async (args) => {
  const text = await Bun.file(args.path).text();
  const data = parseYAML(text);
  return {
    contents: `export default ${JSON.stringify(data)}`,
    loader: "js",
  };
});
```

## Available Loaders

`js`, `jsx`, `ts`, `tsx`, `json`, `jsonc`, `toml`, `yaml`, `text`, `css`, `html`, `file`, `napi`, `wasm`

## Examples

### Environment Variables Plugin

```typescript
plugin({
  name: "env-plugin",
  setup(build) {
    build.onLoad({ filter: /^env$/ }, () => ({
      contents: `export default ${JSON.stringify(process.env)}`,
      loader: "js",
    }));
  },
});

// Usage: import env from "env";
```

### YAML Loader

```typescript
import YAML from "yaml";

plugin({
  name: "yaml-loader",
  setup(build) {
    build.onLoad({ filter: /\.ya?ml$/ }, async ({ path }) => {
      const text = await Bun.file(path).text();
      return {
        contents: `export default ${JSON.stringify(YAML.parse(text))}`,
        loader: "js",
      };
    });
  },
});
```

### Virtual Module

```typescript
plugin({
  name: "virtual-module",
  setup(build) {
    build.onResolve({ filter: /^virtual:config$/ }, () => ({
      path: "virtual:config",
      namespace: "virtual",
    }));

    build.onLoad({ filter: /.*/, namespace: "virtual" }, () => ({
      contents: `export const version = "1.0.0"`,
      loader: "js",
    }));
  },
});
```

## Namespaces

| Namespace | Description                 |
| --------- | --------------------------- |
| `file`    | Default, local files        |
| `bun`     | Bun modules (`bun:sqlite`)  |
| `node`    | Node.js modules (`node:fs`) |
| custom    | Your own namespace          |

## Deferred Loading

Wait for all other modules to load first:

```typescript
build.onLoad({ filter: /stats\.json/ }, async ({ defer }) => {
  await defer(); // Wait for all modules
  return {
    contents: JSON.stringify(collectedStats),
    loader: "json",
  };
});
```

## Native Plugins (Rust/C)

For maximum performance, write plugins as NAPI modules:

```typescript
import nativeAddon from "./my-addon.node";

plugin({
  name: "native-plugin",
  setup(build) {
    build.onBeforeParse(
      { filter: "**/*.tsx" },
      { napiModule: nativeAddon, symbol: "transform" }
    );
  },
});
```

Native plugins run on multiple threads — significantly faster than JS plugins.
