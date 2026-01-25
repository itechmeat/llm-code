# Command Line Interface

Actionable notes from the Vite CLI page.

## Dev server

- `vite` starts the dev server; `vite dev` and `vite serve` are aliases.
- Common options: `--host`, `--port`, `--open`, `--cors`, `--strictPort`.
- `--force` forces dependency re-bundling.
- `-m, --mode` selects the env mode.

## Build

- `vite build` produces production output.
- Common options: `--target`, `--outDir`, `--assetsDir`, `--assetsInlineLimit`.
- `--ssr` builds an SSR entry; `--ssrManifest` emits SSR manifest.
- `--sourcemap` supports `inline` and `hidden`.
- `--minify` accepts `esbuild`, `terser`, or `false`.

## Preview

- `vite preview` serves the built output from `dist` by default.
- Useful for local verification; not meant as a production server.

## Optimize (deprecated)

- `vite optimize` triggers dependency pre-bundling but is deprecated.

## Shared CLI behavior

- `-c, --config <file>` sets a config file.
- `--base <path>` sets the public base.
- `--configLoader` controls how config is loaded (experimental variants).
- `-d, --debug` and `-f, --filter` for debugging.
