# Troubleshooting

Actionable notes from the troubleshooting guide.

## CLI / config

- Windows paths containing `&` break npm shims; remove `&` or switch package manager.
- ESM-only deps in config: use ESM config (`type: module` or `.mjs/.mts`).

## Dev server issues

- Stalled requests on Linux: raise file descriptor and inotify limits.
- Self-signed certs in Chrome break caching; use trusted cert.
- 431 errors: reduce header size or increase `--max-http-header-size`.
- Dev containers: set `server.host: '0.0.0.0'` so forwarded ports are reachable (using `127.0.0.1` limits access to the container's localhost only).

## HMR issues

- Case mismatch in imports prevents HMR; fix file casing.
- Circular deps can trigger full reload; use `vite --debug hmr`.

## Build issues

- Opening `dist` via `file://` causes CORS errors; use `vite preview`.
- Case-sensitive FS errors: fix import casing.
- Dynamic import fetch errors: handle version skew or missing chunks.

## Optimized deps

- Linked deps may need `vite --force` to re-optimize.

## Other notes

- Vite does not polyfill Node built-ins in browser code.
- Strict-mode only; patch dependencies if they rely on sloppy mode.
