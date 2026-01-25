# Dependency Pre-Bundling

Actionable notes from the dependency pre-bundling guide.

## Why it exists

- Converts CJS/UMD deps to ESM for dev server compatibility.
- Collapses large ESM dep graphs into single modules to reduce browser requests.
- Uses esbuild for speed; production uses Rollup + commonjs plugin instead.

## Automatic discovery

- Vite scans source for bare imports and pre-bundles them on first run.
- Newly discovered deps trigger a re-bundle + page reload.

## Monorepos and linked deps

- Linked packages are treated as source, not deps.
- If linked deps are CJS, add to `optimizeDeps.include` and `build.commonjsOptions.include`.
- Restart dev server with `--force` after linked dep changes.

## Tuning behavior

- Use `optimizeDeps.include` / `exclude` for imports not visible in source.
- Use `optimizeDeps.esbuildOptions` for special handling.

## Caching

- Cache in `node_modules/.vite` is invalidated by lockfile, patches, config, or `NODE_ENV`.
- Browser cache is aggressive; disable cache + restart with `--force` when debugging deps.
