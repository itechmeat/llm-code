# Security

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Security-Overview
- https://github.com/seaweedfs/seaweedfs/wiki/Security-Configuration

## Security Overview

### What this page is about

- It separates SeaweedFS security into control-plane gRPC mTLS and data-plane HTTP/HTTPS plus JWT controls.
- It explains how masters, filers, volumes, and S3 interact under that security model.

### Actionable takeaways

- Secure gRPC and HTTP independently; they are different communication planes with different configuration blocks.
- Use mutual TLS for gRPC between masters, volumes, filers, S3, and other clients when cluster trust boundaries matter.
- Use JWT on volume writes and optionally reads when direct volume access must be controlled.
- Use filer JWT keys when filer HTTP must be protected and S3 still needs to proxy through it.
- Keep short JWT lifetimes in mind; volume-file tokens are intentionally brief and file-id-scoped.
- Disable unnecessary HTTP surfaces or directory metadata exposure if public access is not intended.

### Gotchas / prohibitions

- Do not enable HTTPS on filer or volume without also enabling the matching client-side HTTPS config.
- Do not expose filer UI or directory metadata casually on public endpoints.
- Do not assume unknown file ids alone are an adequate security boundary once services are internet-facing.

## Security Configuration

### What this page is about

- It documents `security.toml`, JWT keys, TLS settings, and environment-variable overrides.
- It serves as the concrete configuration map for the security model above.

### Actionable takeaways

- Generate `security.toml` with `weed scaffold -config=security` and version-control only the non-secret parts.
- Prefer environment variables for JWT keys and TLS secret paths when deployment config is stored in Git or templates.
- Keep the same relevant JWT config synchronized across all services that must mint or validate those tokens.
- Use the guard whitelist and CORS settings deliberately; they are not substitutes for real auth, but they narrow exposure.
- Treat the filer signing key as security-sensitive beyond filer auth because it also participates in STS fallback behavior.

### Gotchas / prohibitions

- Do not leave JWT keys empty when you intend the associated protections to be active.
- Do not forget to distribute the same security config to all participating services that validate a given token type.
- Do not store plaintext secrets in committed config when env var overrides are available.

### How to apply in a real repo

- Publish one security baseline covering mTLS, JWT write/read controls, HTTPS, UI exposure, and secret injection.
- Keep separate environment templates for local, internal production, and internet-facing deployments.
- Test every enabled security layer end-to-end, including S3-to-filer HTTPS/JWT flows.
