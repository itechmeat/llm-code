# Deploying a Static Site

Actionable notes from the static deploy guide.

## General flow

- Build with `npm run build` → deploy `dist`.
- Test locally with `npm run preview` (not a production server).
- Set `base` for subpath deployments (GitHub Pages/GitLab Pages).

## Platform highlights

- GitHub Pages: set `base` to `/` for user site, or `/<repo>/` for project site; deploy via Actions.
- GitLab Pages: similar `base` rules; use `.gitlab-ci.yml` to build and publish.
- Netlify/Vercel: import repository; Vite preset auto-detected.
- Cloudflare Pages: deploy via Wrangler (`wrangler pages deploy dist`) or Git integration.
- Firebase/Surge/Azure/Render: configure `dist` as output directory.

## Key cautions

- `vite preview` is for local verification only.
- Ensure `base` matches the deployment URL to avoid broken assets.
