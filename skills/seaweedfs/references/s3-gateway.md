# S3 Gateway

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Amazon-S3-API
- https://github.com/seaweedfs/seaweedfs/wiki/S3-Configuration
- https://github.com/seaweedfs/seaweedfs/wiki/S3-Credentials
- https://github.com/seaweedfs/seaweedfs/wiki/OIDC-Integration

## Amazon S3 API

### What this page is about

- It explains how `weed s3` exposes an S3-compatible gateway backed by filer.
- It covers bucket-to-collection mapping, multi-node deployment, reverse-proxy behavior, and authentication modes.

### Actionable takeaways

- Treat the S3 gateway as a stateless protocol layer over filer, not as an independent storage plane.
- Remember that each bucket maps to `/buckets/<bucket_name>` and its own collection, which makes bucket deletion efficient but amplifies volume planning needs.
- Lower `-volumeSizeLimitMB` and configure `/buckets/` path behavior when the environment will host many buckets.
- Run multiple S3 nodes against one or more filers when horizontal scaling is needed; colocating filer and S3 is the simplest multi-node pattern.
- Plan reverse-proxy deployments around forwarded-host, forwarded-port, and forwarded-prefix handling so SigV4 validation remains correct.
- Understand the auth mode switch: no credentials means `Allow All`, any configured identity means authenticated mode.
- Use static config, dynamic `s3.configure`, Admin UI, or OIDC/IAM config according to the deployment's identity lifecycle.
- Scope actions per bucket whenever possible instead of handing out broad global permissions.

### Gotchas / prohibitions

- Do not expose the default unauthenticated S3 mode outside trusted environments.
- Do not ignore bucket-per-collection volume growth when sizing multi-tenant S3 clusters.
- Do not put S3 behind a reverse proxy without testing forwarded-header and signature behavior.

## S3 Configuration

### What this page is about

- It separates SeaweedFS S3 auth into two systems: basic credentials and advanced IAM/STS.
- It explains zero-config behavior, config precedence, reverse-proxy handling, and key fallback rules for IAM mode.

### Actionable takeaways

- Choose `-s3.config` for static access-key style users and `-s3.iam.config` for OIDC, STS, roles, and policy documents.
- Treat zero-config mode as convenience, not security: it enables open access unless policies explicitly default to deny.
- Remember that in-memory policy storage is ephemeral unless IAM config uses persistent filer-backed storage.
- Use `-s3.externalUrl` or correct forwarded headers when the S3 gateway sits behind proxies and SigV4 validation depends on public URL shape.
- Keep basic identities out of `-s3.iam.config`; that file is for IAM/STS structures, not `identities`.
- Use both config systems together when static access-key users and OIDC/STS users must coexist.
- Understand STS signing-key fallback order so cluster key management stays predictable.

### Gotchas / prohibitions

- Do not mistake zero configuration for secure-by-default behavior.
- Do not put `identities` into IAM config and expect them to load.
- Do not rely on default in-memory policies if persistence across restarts matters.

## S3 Credentials

### What this page is about

- It details the basic access-key credential system used by `-s3.config`.
- It covers config precedence, Admin UI integration, environment-variable fallback, and bucket-scoped permissions.

### Actionable takeaways

- Prefer a dedicated config file for production-grade static credentials.
- Use filer-backed credential storage or Admin UI when you need live updates without restarting S3 nodes.
- Treat environment variables as fallback convenience, not the main production control plane.
- Leverage bucket-scoped actions or wildcard bucket patterns to keep user permissions narrow.
- Remember that higher-priority config sources override lower-priority ones completely; SeaweedFS does not merge them.
- Use multiple credentials per identity when key rotation or multiple clients must map to the same logical user.

### Gotchas / prohibitions

- Do not expect config file, filer config, and env vars to merge.
- Do not grant global `Admin` when a bucket-scoped permission set is enough.
- Do not rely on fallback env vars if an older filer-backed config may still override them.

## OIDC Integration

### What this page is about

- It explains advanced IAM mode for OIDC, STS, role mapping, and IAM-style policies.
- It documents provider configuration, trust policies, and group/claim-to-role mapping.

### Actionable takeaways

- Use `-s3.iam.config` when identity comes from OIDC providers such as Keycloak, Okta, Auth0, Azure AD, Google, or Cognito.
- Model the configuration around four pieces: `sts`, `providers`, `policies`, and `roles`.
- Use role-mapping rules on claims such as `groups` to map IdP identities onto SeaweedFS IAM roles.
- Keep TLS validation explicit with CA certificates and avoid `tlsInsecureSkipVerify` outside testing.
- Define trust policies tightly so only the intended issuer and web-identity flow can assume a role.
- Keep a default role only when the security model truly wants an implicit fallback.

### Gotchas / prohibitions

- Do not mix static access-key identities into IAM config.
- Do not disable TLS verification for a real IdP deployment.
- Do not use overly broad trust policies if the IdP serves multiple applications or realms.

### How to apply in a real repo

- Publish one auth decision tree: open test mode, static credentials, or full IAM/STS/OIDC.
- Keep proxy-aware S3 endpoint configuration in the same place as TLS and public URL settings.
- Standardize one production credential-management path: file-based or filer/Admin-UI-backed.
- Use bucket-scoped permissions by default for tenant isolation.
- Align IdP claim design, SeaweedFS role names, and IAM policy scope before rollout.
- Validate the full login-to-role-assumption path in staging, including JWKS refresh and token expiry behavior.

## Patch-level IAM notes (4.20)

- Embedded IAM now supports `ListUserPolicies` and group inline policy actions, which reduces the need for external policy bookkeeping when operating many S3 identities.
- User-policy round trips preserve the exact policy document more reliably, and `GetUserPolicy` fallback no longer drops actions/resources.
- `DeleteBucket` now prunes bucket-scoped IAM actions tied to that bucket, so cleanup is safer after tenant teardown.
- In S3 failover flows, `ErrNotFound` is no longer treated as filer health failure by itself; treat missing objects differently from actual filer unavailability.
