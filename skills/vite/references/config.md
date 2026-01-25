# Config Reference

Actionable notes from the Vite config index.

## Config file basics

- Vite auto-resolves `vite.config.*` from project root.
- Config can be ESM even without `type: module`.
- Use `defineConfig()` for IntelliSense.
- `import.meta.resolve` supported in ESM config (bundle loader).

## Conditional/async config

- Export a function to branch on `command`, `mode`, `isSsrBuild`, `isPreview`.
- Export async config if you need async values.

## Environment variables in config

- `.env*` files are loaded **after** config is resolved.
- Use `loadEnv(mode, envDir, prefix)` if config needs `.env` values.

## Config loader

- Default loader bundles config with esbuild.
- `--configLoader runner` uses module runner (no temp file, no CJS config).
- `--configLoader native` uses native runtime; no auto-restart for imports.

## Debugging config

- Use VS Code `resolveSourceMapLocations` to debug config when using bundled loader.

## Future deprecations (`future`)

- `future: Record<string, 'warn' | undefined>` — opt-in warnings for next major.
- Enable warnings for deprecations you use:

```js
export default defineConfig({
  future: {
    removePluginHookSsrArgument: "warn", // options.ssr → this.environment
    removePluginHookHandleHotUpdate: "warn", // handleHotUpdate → hotUpdate
    removeSsrLoadModule: "warn", // ssrLoadModule → ModuleRunner
    removeServerPluginContainer: "warn",
    removeServerReloadModule: "warn",
    removeServerHot: "warn",
  },
});
```
