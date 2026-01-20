# Plugin API

Actionable notes from the plugin API guide.

## Authoring basics

- Prefer existing features or plugins before writing a new plugin.
- Plugin names: `vite-plugin-*` for Vite-only, `rollup-plugin-*` for compatible.
- Use factory functions for configuration.

## Key Vite hooks

- `config` and `configResolved` for config adjustments.
- `configureServer` / `configurePreviewServer` for middleware.
- `transformIndexHtml` for HTML transforms (use `order: 'pre' | 'post'`).
- `handleHotUpdate` for custom HMR handling.

## Ordering and conditions

- Use `enforce: 'pre' | 'post'` for ordering.
- Use `apply: 'serve' | 'build'` to scope a plugin to dev/build.

## Virtual modules

- Use `virtual:*` ids and resolve to `\0virtual:*`.
- Avoid `\0` for modules derived from real files (SFC submodules).

## Rollup compatibility

- Rollup plugins that don’t rely on `moduleParsed` or output hooks usually work.
- Build-only plugins can go in `build.rollupOptions.plugins`.

## Filtering and normalization

- Use `createFilter` from `@rollup/pluginutils` (re-exported by Vite).
- Normalize paths with `normalizePath` before matching.
- Hook filters (Rollup 4.38+ / Vite 6.3+) can reduce overhead.

## Client/server events

- Use `server.ws.send` to broadcast, and `import.meta.hot.on` to receive.
- Use `import.meta.hot.send` for client-to-server events.
- Extend `vite/types/customEvent.d.ts` for typed payloads.
