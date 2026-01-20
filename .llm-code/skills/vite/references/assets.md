# Static Asset Handling

Actionable notes from the static assets guide.

## Importing assets

- Importing an asset returns its resolved public URL.
- Assets are hashed and included in the build graph.
- `assetsInlineLimit` controls base64 inlining.

## Explicit queries

- `?url` forces URL import.
- `?inline` or `?no-inline` controls inlining.
- `?raw` loads the asset as a string.
- `?worker` / `?sharedworker` for worker imports.

## `public` directory

- Use `public/` for assets that must keep filenames or aren’t imported.
- Reference public assets with absolute paths (e.g. `/icon.png`).
- `publicDir` config changes the folder name.

## `new URL(..., import.meta.url)`

- Works in browser with static URL strings; Vite rewrites during build.
- Dynamic or non-static URLs are not transformed.
- Not suitable for SSR because `import.meta.url` semantics differ in Node.

## Gotchas

- For CSS `url()` with SVGs in JS strings, wrap in double quotes.
- Add `vite/client` types when TypeScript complains about asset imports.
