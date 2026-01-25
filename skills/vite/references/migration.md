# Migration from v6

Actionable notes from the migration guide.

## Node support

- Node.js 18 is dropped; require Node 20.19+ or 22.12+.

## Browser target defaults

- Default `build.target` now aligns with Baseline widely available browsers.
- Old `modules` target removed; new default is `baseline-widely-available`.

## Removed or changed features

- Sass legacy API removed; drop `css.preprocessorOptions.*.api` legacy settings.
- `splitVendorChunkPlugin` removed; use `build.rollupOptions.output.manualChunks`.
- `transformIndexHtml` hook now uses `{ order, handler }` instead of `enforce/transform`.

## Advanced removals

- Deprecated SSR/resolve properties removed; review custom tooling.
- `optimizeDeps.entries` treats values as globs.
- Some middlewares are applied before `configureServer`/`configurePreviewServer`.

## Upgrade path

- Follow v5 → v6 migration guide first if coming from v5.
