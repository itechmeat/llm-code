# Qdrant Security — overview (ingested: security guide)

Source: https://qdrant.tech/documentation/guides/security/

This note summarizes the **Security guide** with an emphasis on actionable, production-relevant controls.

## Baseline warning (high value)

- Qdrant instances can be **unsecured by default**. Do not expose a node to untrusted networks without adding security controls.

## Network model & threat surfaces

- Qdrant exposes REST and gRPC APIs and can also run in distributed mode.
- In distributed mode, there is an **internal cluster port** (not meant for public exposure).
- Practical implication: treat the cluster network as a trusted private network segment even when auth is enabled.

`1.18.0` note:

- Internal gRPC endpoints now enforce API key/JWT authentication as well. That closes an older trust gap, but it also means internal callers and sidecars must be validated during upgrades instead of assuming private networking alone is enough.

`1.19.1` note:

- Collection names that are `.` or `..` are rejected, closing a path-based traversal risk. Do not rely on names alone to sanitize storage paths; keep the storage root scoped to its own directory.

`1.19.2` notes:

- **Internal gRPC accepts read-write keys only.** With `service.enforce_internal_auth: true`, the internal (p2p) gRPC API accepts `service.api_key` and `service.alt_api_key` only — the read-only key and JWT tokens are rejected, because peers that join consensus and move shards must hold the read-write key. `alt_api_key` is now actually forwarded on internal calls, so a rolling key rotation no longer breaks peer traffic.
- **Rolling-upgrade order:** keep `enforce_internal_auth` off while any peer is still on an older release (those peers do not attach a key yet), then enable it once every node is upgraded.
- **Startup warnings are now explicit.** Qdrant logs a warning when a distributed deployment runs without any API key (the internal p2p API is then unauthenticated and `enforce_internal_auth` cannot be enabled), when a key is configured but `enforce_internal_auth` is off, and when `enforce_internal_auth` is on while only `read_only_api_key` is set (peers would not be able to reach each other).
- **An empty key is an unset key.** `api_key`, `alt_api_key` or `read_only_api_key` set to an empty string is treated as unset, so authentication is silently disabled. Qdrant warns about this case too — treat an empty secret as a failed deployment, not as "no auth needed".
- **Bind the internal listener separately.** `cluster.p2p.host` (env: `QDRANT__CLUSTER__P2P__HOST`) binds the internal gRPC listener to a different interface than the public API, keeping the cluster port off the externally reachable interface. It defaults to `service.host`.
- **Snapshot upload no longer logs server-side paths.** Uploading a snapshot without a collection configuration used to write the local path into the logs; that is fixed in `1.19.2`.

## Authentication options

### Static API key

- Intended as a straightforward gate for API access.
- Provided via config (`service.api_key`) or env (`QDRANT__SERVICE__API_KEY`).
- Clients send it via an `api-key` header.
- Security guide stresses: use **TLS** to avoid leaking the API key.

### Read-only API key

- Separate key for read-only access.
- Config: `service.read_only_api_key` or env: `QDRANT__SERVICE__READ_ONLY_API_KEY`.

### Secondary API key (rotation) (v1.17.0)

Qdrant v1.17.0 adds support for a **secondary API key** to enable **zero-downtime key rotation**.

Operational pattern:

1. Configure the secondary key in Qdrant.
2. Roll client updates to use the secondary key.
3. Promote/replace the primary key (and revoke the old key) once all clients have switched.

Use this when you need to rotate credentials without a coordinated “all clients at once” cutover.

### JWT-based RBAC

- Provides finer-grained authorization (including per-collection access).
- Enabled via `service.jwt_rbac: true` and an API key used for signing/verifying tokens.
- Operationally important: anyone who knows the signing key can generate tokens offline; key rotation invalidates existing tokens.

## TLS

- The guide describes enabling TLS for REST/gRPC and (optionally) inter-node cluster connections.
- Operational notes:
  - certificate rotation is supported by periodic reload (tunable via `tls.cert_ttl`).
  - you can also terminate TLS via a reverse proxy, but still must isolate internal cluster ports.

## Hardening patterns (practical)

- Run as non-root (unprivileged image or explicit user IDs).
- Make container root filesystem read-only where feasible; mount persistent storage separately.
- Network isolation:
  - Docker internal networks for “no public ingress/egress” patterns.
  - Kubernetes NetworkPolicy to restrict ingress/egress (while allowing required inter-node traffic).

## Concrete guidance worth enforcing in projects

- Always keep internal cluster traffic private (never expose the internal cluster port publicly).
- In a cluster, configure `service.api_key` and, once every node is on the same release, `service.enforce_internal_auth: true`; bind the internal listener to a private interface with `cluster.p2p.host`.
- If using API keys/JWT, do not run without TLS unless you have a trusted, private network boundary.
- Prefer least privilege (read-only key or collection-scoped JWT) for read-heavy workloads.
- If you do not need remote snapshot restore, disable restore-from-URL in hardened environments to reduce the remote-input attack surface.

## Audit access logging (v1.17.0)

Qdrant v1.17.0 adds **audit access logging** for API access.

Practical guidance:

- Enable audit logging when you need security visibility (who accessed what, when).
- Treat audit logs as security data: ship them off-host, control access, and set retention.
