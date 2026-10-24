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
- Recent `4.24`-`4.25` releases tightened admin auth on destructive/admin endpoints and filer IAM gRPC calls; treat older unauthenticated admin automation as suspect until revalidated.
- If `security.toml` is enabled, explicitly test Admin UI and filer IAM paths together, because the `4.25` line fixed an auth propagation issue there.
- `4.40` closes an OIDC bypass: role trust policy is now enforced even when a bearer token is presented directly to the S3 API instead of going through a full `AssumeRoleWithWebIdentity` call. Revalidate any integration that previously relied on direct bearer-token requests, since a request that should have been denied by trust policy could pass before this fix.
- `4.40` also hardens TUS resumable-upload session authorization on filer: `HEAD`/`PATCH`/`DELETE` are now restricted to the session's own target path, closing a cross-prefix access gap where one session could reach another session's upload path. Revalidate multi-tenant or multi-session TUS deployments after upgrading.

### Gotchas / prohibitions

- Do not enable HTTPS on filer or volume without also enabling the matching client-side HTTPS config.
- Do not expose filer UI or directory metadata casually on public endpoints.
- Do not assume unknown file ids alone are an adequate security boundary once services are internet-facing.
- Do not assume pre-`4.40` OIDC bearer-token requests were trust-policy-checked, or that TUS sessions were prefix-isolated; both gaps are closed only from `4.40` onward.

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
- Recent IAM/S3 updates also harden the default posture: users with no policies are denied, OIDC/web-identity support is broader, and auditability/revocation options increased. Reflect that in runbooks instead of assuming older permissive behavior.

### Gotchas / prohibitions

- Do not leave JWT keys empty when you intend the associated protections to be active.
- Do not forget to distribute the same security config to all participating services that validate a given token type.
- Do not store plaintext secrets in committed config when env var overrides are available.
- Do not assume old admin endpoints remain callable without admin auth; `4.24` tightened several destructive and diagnostic paths.

### How to apply in a real repo

- Publish one security baseline covering mTLS, JWT write/read controls, HTTPS, UI exposure, and secret injection.
- Keep separate environment templates for local, internal production, and internet-facing deployments.
- Test every enabled security layer end-to-end, including S3-to-filer HTTPS/JWT flows.

## Trusted Proxies and Admin Reachability (4.48)

### What changed

- **S3 forwarded client addresses are allowlisted.** `security.toml` gained a `[s3.trusted_proxies]` section:

  ```toml
  [s3.trusted_proxies]
  white_list = "10.10.10.0/24" # comma separated; bare IPs or CIDRs
  ```

  Only when the direct TCP peer is in the allowlist are `X-Forwarded-For` (walked right-to-left, skipping trusted hops) and then `X-Real-Ip` used to derive `aws:SourceIp`. Otherwise the direct peer address is used. The list is applied to the bucket policy engine, the IAM attached-policy engine, and the IAM role/session policy middleware, and is reloaded on `SIGHUP` together with the JWT signing keys.
- **The admin HTTP bind default depends on authentication.** If `-adminPassword` is set or `[https.admin]` mTLS is configured, the `-ip` default auto-upgrades to `0.0.0.0`; without authentication the default stays on loopback so the unauthenticated admin API is never exposed on the network. An explicit `-ip` is always honored.
- **The admin worker/plugin gRPC control plane honors `-ip`.** It used to bind `:port`, wildcard-binding every interface and ignoring the operator's setting - the only gRPC listener that did so. With `-ip=127.0.0.1` the worker gRPC port (HTTP port + 10000) is now loopback-only, matching the master, filer and volume listeners.

### Actionable takeaways

- If you run SeaweedFS behind a reverse proxy and use `IpAddress` / `NotIpAddress` conditions in bucket or IAM policies, add the proxy's address range to `s3.trusted_proxies.white_list`, otherwise every request looks like it came from the proxy.
- After upgrading from `4.47`, re-check that the admin UI is still reachable from where it was reachable before. An authenticated deployment that lost network access after `4.40` now works again without adding `-ip=0.0.0.0`.
- Audit the worker gRPC port (`HTTP port + 10000`) on every host: on older releases it was reachable from the network even when `-ip` was loopback.

### Gotchas / prohibitions

- Do not put a broad range (for example `0.0.0.0/0`) in `s3.trusted_proxies.white_list`; every caller would then be able to claim any `aws:SourceIp`.
- Do not rely on forwarded headers for IP-based policy decisions without configuring the allowlist - the direct peer address is used instead.
- Do not expose the admin HTTP listener without authentication on a shared network; the `0.0.0.0` default only applies when a password or mTLS is configured.
- Do not leave the worker gRPC port open to the internet when the admin API is intended to be private.
