# Breaking Changes

Actionable notes from the breaking changes index.

## Planned (next major)

- `options.ssr` in hooks → `this.environment`
- `handleHotUpdate` hook → `hotUpdate` hook
- `server.ssrLoadModule` → ModuleRunner API
- `server.warmupRequest` → `environment.warmupRequest`
- `server.pluginContainer` → `environment.pluginContainer`
- `server.moduleGraph` → `environment.moduleGraph`
- `server.hot` → `environment.hot`
- `server.reloadModule` → `environment.reloadModule`

## Deprecation warnings via `future`

Enable warnings in `vite.config.js` to prepare for migration:

```js
export default defineConfig({
  future: {
    removePluginHookSsrArgument: "warn",
    removePluginHookHandleHotUpdate: "warn",
    removeSsrLoadModule: "warn",
    removeServerPluginContainer: "warn",
    removeServerReloadModule: "warn",
    removeServerHot: "warn",
    removeServerWarmupRequest: "warn",
    removeServerModuleGraph: "warn",
  },
});
```

## Considering (experimental)

- Per-environment APIs
- Shared plugins during build

## Practical guidance

- Treat items here as forward-looking; prefer stable APIs.
- Use `future` config option for opt-in warnings.
- Monitor linked discussions when you rely on these APIs.
