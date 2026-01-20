# Server-Side Rendering (SSR)

Actionable notes from the SSR guide.

## Project structure

- `entry-client` mounts the app; `entry-server` renders to HTML.
- `index.html` includes an SSR outlet placeholder and `entry-client` module.

## Dev server integration

- Use Vite in middleware mode (`server.middlewareMode: true`, `appType: 'custom'`).
- Use `vite.transformIndexHtml()` and `vite.ssrLoadModule()` during dev.
- Call `vite.ssrFixStacktrace()` for errors.

## Production build

- Build client and server separately (`vite build --ssr`).
- Use `dist/client/index.html` as the template.
- Import the SSR bundle directly (no `ssrLoadModule`).

## SSR manifest

- Use `--ssrManifest` on the **client** build to map module IDs to assets.
- Pass manifest to `entry-server` to generate preload directives.

## Externals

- SSR externalizes deps by default.
- Use `ssr.noExternal` for deps that need Vite transforms.
- Use `ssr.external` to force externalization for linked deps.

## Plugin hooks

- SSR-specific transforms get `options.ssr` in plugin hooks.

## Targets and bundling

- Default SSR target is Node; `ssr.target: 'webworker'` for worker runtimes.
- `ssr.noExternal: true` bundles all deps and forbids Node built-ins.
