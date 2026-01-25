# JavaScript API

Actionable notes from the JS API guide.

## Core entry points

- `createServer()` for dev server usage (supports middleware mode).
- `build()` for production builds.
- `preview()` for serving `dist` locally.

## Server objects

- `ViteDevServer` exposes `middlewares`, `ws`, `moduleGraph`, `transformRequest`, and SSR helpers.
- `PreviewServer` exposes `middlewares`, `httpServer`, `printUrls`, and `bindCLIShortcuts`.

## Config helpers

- `resolveConfig(inlineConfig, command, ...)` to resolve config programmatically.
- `mergeConfig(defaults, overrides)` for deep merges (objects only).
- `loadConfigFromFile()` to load config with esbuild.

## Env helpers

- `loadEnv(mode, envDir, prefixes)` loads `.env` files.
- `normalizePath()` for plugin path comparisons.

## Transform helpers

- `transformWithEsbuild()` for plugin transforms.
- `preprocessCSS()` (experimental) to pre-process CSS.

## Important caveats

- When using `createServer` and `build` in one process, align `mode`/`NODE_ENV`.
- Middleware mode with WS proxy requires passing the parent server to `middlewareMode`.
