# Rolldown Integration

Actionable notes from the Rolldown integration guide.

## What Rolldown is

- Rust bundler designed as a Rollup drop-in replacement.
- Goals: speed, plugin compatibility, and advanced optimizations.

## Why Vite is migrating

- Unify dependency optimization and build under one bundler.
- Improve performance and capabilities (chunking, HMR, module federation).

## Trying `rolldown-vite`

- Alias `vite` to `rolldown-vite` in `package.json`.
- Pin versions; it’s experimental.
- Use package manager overrides when Vite is a peer dep.

## Known limitations

- Some Rollup options are unsupported; expect validation warnings.
- `manualChunks` is deprecated in favor of `advancedChunks`.
- `build.rollupOptions` / `worker.rollupOptions` are deprecated in favor of `build.rolldownOptions` / `worker.rolldownOptions` during the transition.

## Bundled dev mode (`experimental.bundledDev`)

- A boundary-less edit (no module in the update path calls `hot.accept`) reloads the page exactly once: the client tells the server to rebuild first, then the server sends `full-reload` once the fresh bundle is ready. Previously the client navigated immediately, hit the "bundling in progress" fallback page, then reloaded a second time once the bundle finished.
- If the rebuild fails, the request stays pending and the error overlay is shown instead of reloading onto a stale bundle; the reload is sent once a later build succeeds.
- Worker files (`new Worker(new URL('./worker.js', import.meta.url))`, `?worker`/`?sharedworker` imports) are now re-emitted through HMR patches, not only through a full `generateBundle`, so an edited worker no longer serves stale content when its importer is an HMR boundary (e.g. under Fast Refresh).
- Client-side HMR handling from the updated Rolldown dependency is integrated into this mode.

## Performance knobs

- Native plugins enabled by default (`experimental.enableNativePlugin`).
- `@vitejs/plugin-react` uses Oxc refresh transform for speed.
- Use `withFilter` wrapper to reduce hook overhead.

## Plugin author notes

- Detect `rolldown-vite` via `this.meta.rolldownVersion` or `vite.rolldownVersion`.
- Vite `8.0.15` bumped Rolldown to `1.0.3` (`8.0.14` shipped `1.0.2`); Vite `8.2.0` bumps it further to `~1.2.0`. Re-check any workaround that targeted older Rolldown quirks before keeping it in build guidance.
- If you use `transformWithEsbuild`, add `esbuild` as a dependency or switch to `transformWithOxc`.
- Set `moduleType: 'js'` when transforming non-JS content.
- If you catch build errors programmatically, expect `BundleError` with a nested `.errors` array instead of assuming a single raw plugin exception.
