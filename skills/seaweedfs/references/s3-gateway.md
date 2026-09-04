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

## Patch-level audit note (4.28)

- `4.28` populates requester identity more consistently for GET/HEAD and IAM-related S3 operations. If you depend on SeaweedFS audit logs for investigations or compliance, refresh dashboards/parsers after upgrade so they ingest the richer requester field instead of assuming only write-path attribution.

## Patch-level S3 notes (4.29 -> 4.30)

- `4.29` routes more S3 object mutations to the owning filer through filer-side `ObjectTransaction` and `ObjectTransactionBatch` flows, including versioned puts, copy/delete-marker handling, multipart completion, object-lock writes, and metadata-only self-copy. Expect less pressure on distributed locks, but retest multi-filer object-write concurrency before removing downstream serialization.
- Bucket configuration writes now use field-level filer patches, and object-lock paths gained extended-attribute guard clauses. Revalidate bucket/object-lock automation that previously rewrote whole config documents.
- IAM/OIDC trust-policy examples now use the `oidc:` condition prefix. Keep local examples aligned so web-identity role assumption tests match upstream semantics.
- `4.30` rejects `..` in S3/Iceberg URL path variables, validates ownership-control rules, honors `MetadataDirective=REPLACE` for system metadata on `CopyObject`, and authenticates JWT unsigned-streaming uploads. Treat this as both a compatibility and security regression-test target.
- Anonymous unsigned-streaming `PutObject` is allowed only through the intended unauthenticated path; do not confuse that with a recommendation to expose unsigned uploads on production gateways.

## Patch-level S3 notes (4.40)

- Role trust policy is now enforced on direct OIDC bearer-token requests, not only on requests that went through a formal `AssumeRoleWithWebIdentity` STS call. Treat any client that authenticates by passing an OIDC bearer token straight to the S3 API as newly subject to trust-policy checks, and re-test that flow after upgrading.
- `CopyObject` against a missing source object now returns the standard `NoSuchKey` or `NoSuchBucket` error instead of a misleading one; update error-handling logic that special-cased the old behavior.
- Invalid tagging supplied on `CopyObject` now returns `InvalidTag` instead of the unrelated `InvalidCopySource`, giving clients an accurate signal to fix the tag set rather than the copy source.
- `PutObjectAcl` and object-tagging requests for nested keys (paths containing `/`) now write back to the correct object; previously these could silently update the wrong object when the key had a directory-like prefix.
- Raw, non-percent-encoded semicolons in query strings are now accepted, improving compatibility with clients or proxies that pass semicolons through unescaped.

## Patch-level S3 notes (4.41 -> 4.45)

- **Manifest chunks on the direct write path (`4.41`)**: large chunk lists fold into a manifest chunk during direct-write uploads, and manifest blob ownership is tracked through multipart completion so metadata-only copies get their own chunks. Single-object uploads now chunk at the filer's `maxMB` instead of a hardcoded size. Expect fewer, larger chunk records for big objects; re-check any tooling that assumes one chunk per upload part.
- **Bucket-policy write gate (`4.41`)**: writing a bucket policy now requires a `PutBucketPolicy`-style bucket-policy action in the caller's identity; anonymous or under-privileged clients can no longer replace bucket policies.
- **Identity vs static config (`4.41`)**: filer identity changes now apply even when identities come from a static config file, so editing accounts in the admin UI takes effect without a restart.
- **Versioning correctness (`4.41`)**: list markers stay exclusive for versioned objects, a key deleted during versioning still leaves the listing, copying an object onto itself is allowed in a versioned bucket, suspended-versioning multipart completion can replace the null delete marker and the marker is only retired once the PUT commits, directory markers keep their version history and are not listed as versioned objects, and a versioned metadata-only copy carries its own chunks.
- **Listing/API fixes (`4.41`)**: prefixes whose objects are all delete-marked stop being listed, storage class rides in cached listing metadata, a peer that goes away is reported as `ClientDisconnected` instead of `IncompleteBody`, and an identity's inline account is registered (not collapsed into admin), with the bucket owner honored when recorded as an identity.
- **Lifecycle (`4.41`)**: the daily-replay pass is bounded so a quiet cluster no longer wedges the lifecycle job, and the S3 expiry metadata is applied through the filer path.
- **`4.42`**: adds the `RenameObject` endpoint, fixes `ListObjectsV2` dropping objects under a partial prefix, takes bucket sizes from the master's summary, and adds an option to disable bucket auto-creation on upload (prefer explicit provisioning for multi-tenant or policy-governed gateways).
- **`4.43`**: unrouted bucket subresources (for example `allow-unordered`) are no longer answered with a directory listing, `PutObject`/copy entries get the gateway's own uid/gid, multipart part chunks are placed by the destination object's storage rule, and `allow-unordered` is treated as a listing parameter.
- **`4.44`**: S3 can optionally serve remote-mounted objects from the remote mount when the local read fails, and configuration credentials can come from the environment so the Helm chart can point at an existing secret instead of baking keys in.
- **Range requests (`4.45`)**: the server returns `416` only when no requested range overlaps, includes `Content-Range` on the response, and rejects a Range start offset equal to the file size, with the Rust volume server mirroring the behavior. Retest segmented downloads after upgrade.
- **Transient retries (`4.45`)**: multipart upload/part listings, metadata listings, and callbacks retry transient filer failures, and the S3 API no longer fails over to another filer after a callback has consumed part of a response.

## Patch-level IAM notes (4.41 -> 4.45)

- **Document-style policies (`4.41`)**: the advanced IAM config now loads document-style (JSON) policies, in addition to the existing compact form, and an attached IAM policy can list the buckets it grants (`ListBuckets` scope derives from the policy rather than only from explicit bucket assignments).
- **Admin role scoping (`4.41`)**: an admin's role session stays scoped to the assumed role instead of reverting to full admin authority, and the assumed-role principal plus the STS caller are both surfaced in audit logs.
- **IAM-management actions (`4.41`)**: creating and altering IAM users, groups, and policies are now authorized as IAM actions in their own right rather than slipping through bucket-level checks; re-test provisioning scripts that assumed otherwise.
- **Admin UI policy editing (`4.45`)**: the admin UI adds a visual IAM policy editor and supports managing bucket policies through the UI, complementing the programmatic/policy-file paths.
