# Backend Integration

Actionable notes from the backend integration guide.

## Dev setup

- Enable CORS or proxy asset requests to the Vite dev server.
- Inject Vite client and entry script from `http://localhost:5173`.
- For React, add the refresh preamble script before Vite client scripts.

## Build setup

- Enable `build.manifest: true` and set `build.rollupOptions.input` to your entry.
- Import `vite/modulepreload-polyfill` if the polyfill is enabled.

## Using the manifest

- Manifest maps entry points to hashed files, CSS, and imports.
- Render tags in this order for best performance:
  1. Entry CSS files
  2. CSS for imported chunks
  3. Entry JS file
  4. Optional modulepreload links for imported JS chunks

## Key options

- `server.origin` can point generated asset URLs at the backend domain.
- Use manifest data to generate HTML tags in your server templates.
