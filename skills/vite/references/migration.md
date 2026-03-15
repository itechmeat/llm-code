# Migration to v8

Actionable notes for upgrading to Vite 8.

## Node support

- Node.js 18 is dropped; require Node 20.19+ or 22.12+.

## Browser target defaults

- Default `build.target` now aligns with Baseline widely available browsers.
- Old `modules` target removed; new default is `baseline-widely-available`.

## Removed or changed features

- Sass legacy API removed; drop `css.preprocessorOptions.*.api` legacy settings.
- `splitVendorChunkPlugin` removed; use `build.rollupOptions.output.manualChunks`.
- `transformIndexHtml` hook now uses `{ order, handler }` instead of `enforce/transform`.

## Vite 8-specific migration items

- `build.target: 'baseline-widely-available'` now maps to newer browser baselines (Chrome/Edge 111, Firefox 114, Safari 16.4).
- Default import interop for CommonJS is more consistent; if a dependency breaks, use the temporary `legacy.inconsistentCjsInterop: true` escape hatch while you fix or patch the package.
- Module resolution no longer sniffs file contents to choose between `browser` and `module`; it follows `resolve.mainFields` ordering more strictly.
- `build()` in the JS API throws `BundleError`; inspect `.errors` if you need per-error details.
- `build.rollupOptions` and `worker.rollupOptions` are deprecated in favor of `build.rolldownOptions` and `worker.rolldownOptions`.

## Advanced removals

- Deprecated SSR/resolve properties removed; review custom tooling.
- `optimizeDeps.entries` treats values as globs.
- Some middlewares are applied before `configureServer`/`configurePreviewServer`.

## Upgrade path

- Follow older migration guides in sequence if you are skipping majors.
- For Vite 8 upgrades, validate plugin behavior, CJS imports, and custom config/build scripts before rolling out broadly.
