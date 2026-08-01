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

## Top-level `input` option

- `input: string | string[] | { [entryAlias: string]: string }`, resolved relative to the project root.
- Declares the app's entry point(s) once and becomes the default for `build.rolldownOptions.input` (`build.rollupOptions.input`), `build.lib.entry`, `build.ssr` (when set to `true`), and `optimizeDeps.entries`, whenever those options are left unset.
- Setting one of those options explicitly still overrides `input` for that option only (e.g. `build.rolldownOptions.input` overrides `input` for the build only, while dev keeps using the top-level value).
- Mainly useful for apps that do not use `index.html` as an entry; otherwise `build.rollupOptions.input` for multi-page HTML apps is still the common path.
- The resolved `input` paths are added to `server.fs.allow`, the same way imported modules already are.

## Environment variables in config

- `.env*` files are loaded **after** config is resolved.
- Use `loadEnv(mode, envDir, prefix)` if config needs `.env` values.

## Config loader

- Default loader bundles config with esbuild.
- `--configLoader runner` uses module runner (no temp file, no CJS config).
- `--configLoader native` uses native runtime; no auto-restart for imports.
- Compatibility warnings for `configLoader: 'native'` report `file:line:column` for each unsupported feature, not just the line.
- Virtual modules (ids starting with `\0`) are excluded from the native-config compatibility check, so plugin-generated virtual files no longer produce false-positive warnings.

## Debugging config

- Use VS Code `resolveSourceMapLocations` to debug config when using bundled loader.

## Type-safe PostCSS config

- Vite exports `PostcssUserConfig` (re-exported from `postcss-load-config`'s `Config` type) for typing `postcss.config.js`/`.ts`:

```ts
import type { PostcssUserConfig } from "vite";

const config: PostcssUserConfig = { plugins: [] };
export default config;
```

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

## Vite 8 migration notes

- `build.rollupOptions` and `worker.rollupOptions` are deprecated in favor of `build.rolldownOptions` / `worker.rolldownOptions`.
- `build.commonjsOptions` is now effectively a no-op in the Rolldown path.
- If CommonJS default-import behavior regresses for a dependency, use `legacy.inconsistentCjsInterop: true` only as a temporary migration shim.
