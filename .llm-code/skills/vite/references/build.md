# Building for Production

Actionable notes from the build guide.

## Browser compatibility

- Default targets: modern Baseline widely available browsers.
- Customize via `build.target` (lowest is `es2015`).
- Vite does syntax transforms only; add polyfills separately or use `@vitejs/plugin-legacy`.

## Public base path

- Set `base` to deploy under a subpath; works for JS, CSS, and HTML assets.
- Use `import.meta.env.BASE_URL` for dynamic base URL in code (must be exact).
- Relative base (`"./"` or `""`) requires `import.meta` support.

## Build customization

- Use `build.rollupOptions` for custom outputs and build-only plugins.
- Use `build.rollupOptions.output.manualChunks` for chunk splitting.

## Operational hooks

- Listen for `vite:preloadError` to handle stale chunk errors after deploys.
- Use `vite build --watch` or `build.watch` for rebuild-on-change.

## Multi-page apps

- Provide multiple HTML entries via `build.rollupOptions.input`.
- The resolved HTML file path determines output structure.

## Library mode

- Use `build.lib` to produce library bundles (ES + UMD/CJS).
- Externalize dependencies in `rollupOptions.external`.
- CSS for libraries is extracted to a single file; export it in `package.json`.

## Advanced base options (experimental)

- Use `experimental.renderBuiltUrl` for custom CDN or split public paths.
