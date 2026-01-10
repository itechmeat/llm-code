# Deployment (Installation, Docker, Kubernetes)

Sources:
- https://qdrant.tech/documentation/guides/installation/

This note consolidates the practical deployment constraints and options.

## Recommended paths (high level)

- Production:
  - Qdrant Cloud (managed)
  - Kubernetes (Helm chart or enterprise operator, depending on requirements)
- Development/testing:
  - Docker (single container) or Docker Compose

## Storage constraints (high value)

- Qdrant persistence expects **block-level access** with a **POSIX-compatible filesystem**.
- **NFS is not supported** for Qdrant storage.
- SSD/NVMe is recommended for vector-heavy workloads.
- Be careful with Windows Docker/WSL mounts (docs warn about filesystem issues / data loss).

## Networking / ports

- `6333`: HTTP API (and health/metrics endpoints)
- `6334`: gRPC API
- `6335`: distributed deployment / cluster communication

Operational rule of thumb:
- Clients typically need `6333`/`6334`.
- Cluster nodes must reach each other on all required ports.

## Docker quickstart (practical)

Pull:

```bash
docker pull qdrant/qdrant
```

Run with persistence:

```bash
docker run -p 6333:6333 \
    -v $(pwd)/path/to/data:/qdrant/storage \
    qdrant/qdrant
```

Override config:

```bash
docker run -p 6333:6333 \
    -v $(pwd)/path/to/data:/qdrant/storage \
    -v $(pwd)/custom_config.yaml:/qdrant/config/production.yaml \
    qdrant/qdrant
```

## Kubernetes (Helm chart) notes

- Helm chart is community-supported.
- The docs highlight limitations compared to Qdrant Cloud/enterprise operator:
  - no zero-downtime upgrades
  - no automatic shard rebalancing
  - no full backup/recovery automation

If you self-host on K8s, you must design:
- backup/restore
- upgrades
- monitoring/logging
- HA + load balancing

## Production checklist (minimum)

- Persistent storage is configured and compatible (no NFS).
- Network exposure is intentional (do not expose internal cluster comms publicly).
- Security boundary is defined (auth + TLS termination).
- Monitoring and backups are in place.
