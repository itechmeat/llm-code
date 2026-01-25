# Server-Side Rendering (SSR)

Actionable notes from the SSR guide.

## Project structure

- `entry-client` mounts the app; `entry-server` renders to HTML.
- `index.html` includes an SSR outlet placeholder and `entry-client` module.

## Dev server integration

- Use Vite in middleware mode (`server.middlewareMode: true`, `appType: 'custom'`).
- Use `vite.transformIndexHtml()` for HTML transforms.

### Legacy: `ssrLoadModule`

- `vite.ssrLoadModule()` — deprecated, use ModuleRunner instead.
- `vite.ssrFixStacktrace()` — not needed with ModuleRunner.
- Set `future.removeSsrLoadModule: 'warn'` to see warnings.

### ModuleRunner API (recommended)

- Each environment has a `ModuleRunner` for importing modules.
- Use `moduleRunner.import(url)` instead of `ssrLoadModule`.
- Stack traces automatically fixed (unless `sourcemapInterceptor: false`).
- Works with custom environments running in separate threads/processes.

```js
// Example with RunnableDevEnvironment
const environment = server.environments.ssr;
if (environment instanceof RunnableDevEnvironment) {
  const runner = environment.runner;
  const mod = await runner.import("/src/entry-server.js");
}
```

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
- `ssr.resolve.mainFields` — customize main fields resolution for SSR.
- `ssr.resolve.conditions` — customize export conditions for SSR.

## Plugin hooks

- `options.ssr` in hooks — deprecated.
- Use `this.environment.config.consumer === 'server'` instead.
- Set `future.removePluginHookSsrArgument: 'warn'` for warnings.

## Targets and bundling

- Default SSR target is Node; `ssr.target: 'webworker'` for worker runtimes.
- `ssr.noExternal: true` bundles all deps and forbids Node built-ins.
