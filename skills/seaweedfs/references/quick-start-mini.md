# Quick Start with weed mini

Source: https://github.com/seaweedfs/seaweedfs/wiki/Quick-Start-with-weed-mini

## What this page is about

- It documents the all-in-one `weed mini` command for learning, prototyping, and small deployments.
- It explains which services start automatically, how S3 credentials work, and which web interfaces become available.
- It adds practical flags for ports, directories, reverse proxies, and IAM configuration.

## Actionable takeaways

- Use `weed mini -dir=/data` when you need a single-process SeaweedFS sandbox with master, volume, filer, S3, WebDAV, Admin UI, and maintenance worker enabled together.
- Expect these default endpoints during local work: master `:9333`, filer `:8888`, S3 `:8333`, WebDAV `:7333`, Admin UI `:23646`, and volume `:9340`.
- Change data paths with `-dir`, and override ports explicitly with flags such as `-master.port` and `-s3.port` instead of relying on hard-coded defaults in scripts.
- If SeaweedFS sits behind Nginx, Cloudflare Tunnel, or another reverse proxy, set `-s3.externalUrl` so S3 request signing uses the externally visible URL.
- The page states that embedded IAM is available in `mini`, so it is viable for local S3 auth experiments without a separate IAM service.
- If no S3 credentials are configured, the S3 gateway starts in "Allow All" mode; this is convenient for development but unsafe for shared environments.
- Authentication turns on automatically as soon as any credentials are configured, whether through environment variables, `-s3.config`, Admin UI, or `weed shell`.
- For local credential bootstrap, set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `S3_ENDPOINT` before starting `weed mini`.
- The Admin UI can be used after startup to create or rotate identities dynamically.
- AWS CLI access patterns differ based on auth mode: use `--no-sign-request` only when the endpoint is intentionally unauthenticated.
- Keep `-s3.iam.config` or `-s3.config` under explicit configuration management when you need reproducible local or demo environments.
- Treat the performance section as a boundary marker: separate components, tune volume sizes, configure replication, and add monitoring before promoting a workload beyond `mini`.

## Gotchas / prohibitions

- Do not promote `weed mini` to production; the page repeats that it is for learning, development, and testing.
- Do not expose the default unauthenticated S3 mode outside a trusted environment.
- Do not put SeaweedFS behind a reverse proxy without setting `-s3.externalUrl` if clients use signed S3 requests.
- Do not assume adding credentials is a no-op; it changes the gateway from open access to authenticated mode.

## How to apply in a real repo

- Offer `weed mini` only as a developer bootstrap or CI smoke-test profile, never as the main production recipe.
- Write local runbooks that call out endpoint URLs, auth mode, and where credentials are sourced from.
- Include a reverse-proxy checklist for `s3.externalUrl`, TLS termination, and endpoint testing with signed requests.
- Make the transition path from `mini` to multi-component deployment explicit in the skill and any operator notes.
