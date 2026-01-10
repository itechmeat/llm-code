# Qdrant Security — overview (ingested: security guide)

Source: https://qdrant.tech/documentation/guides/security/

This note summarizes the **Security guide** with an emphasis on actionable, production-relevant controls.

## Baseline warning (high value)

- Qdrant instances can be **unsecured by default**. Do not expose a node to untrusted networks without adding security controls.

## Network model & threat surfaces

- Qdrant exposes REST and gRPC APIs and can also run in distributed mode.
- In distributed mode, there is an **internal cluster port** (not meant for public exposure). The guide highlights that **internal channels are not protected by API keys/bearer tokens**, so network isolation is mandatory.
- Practical implication: treat the cluster network as a trusted private network segment.

## Authentication options

### Static API key

- Intended as a straightforward gate for API access.
- Provided via config (`service.api_key`) or env (`QDRANT__SERVICE__API_KEY`).
- Clients send it via an `api-key` header.
- Security guide stresses: use **TLS** to avoid leaking the API key.

### Read-only API key

- Separate key for read-only access.
- Config: `service.read_only_api_key` or env: `QDRANT__SERVICE__READ_ONLY_API_KEY`.

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
- If using API keys/JWT, do not run without TLS unless you have a trusted, private network boundary.
- Prefer least privilege (read-only key or collection-scoped JWT) for read-heavy workloads.

