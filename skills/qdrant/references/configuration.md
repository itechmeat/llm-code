# Qdrant Configuration — overview (ingested: configuration guide)

Source: https://qdrant.tech/documentation/guides/configuration/

This note summarizes the **Configuration guide** with an emphasis on patterns you’ll actually use in real deployments.

## How configuration is supplied (practical)

- Qdrant supports file-based configuration and environment variable overrides.
- File formats mentioned: YAML (commonly used), and also TOML/JSON/INI.
- Environment variables have the **highest priority**.

### Env var mapping pattern (high value)

- Prefix: `QDRANT__`
- Nested keys are separated by double underscores.
  - Example: `QDRANT__SERVICE__API_KEY=...`

## Precedence / load order (high value)

The guide describes a layered override model (least → most significant):
1) embedded defaults
2) `config/config.yaml`
3) `config/{RUN_MODE}.yaml`
4) `config/local.yaml`
5) explicit `--config-path` file (overrides other files)
6) environment variables (override everything)

Practical pattern:
- keep stable defaults in file-based config
- keep secrets and env-specific overrides in env vars or the orchestrator (Kubernetes)

## Settings that matter most in production

### Networking / service

- HTTP: typically `6333`; gRPC: typically `6334`.
- gRPC can be disabled if configured accordingly.
- Bind address/host is configurable.
- The internal cluster listener has its own bind address (`cluster.p2p.host`), so it can be moved off the public interface; it defaults to `service.host`.

### Security

- API keys and read-only API keys are config-driven.
- TLS can be enabled at the service level; optional mutual TLS is supported.
- TLS cert rotation can be handled via periodic reload (`tls.cert_ttl`).
- The internal (p2p) gRPC API can require the read-write key (`service.enforce_internal_auth`).

### Storage / snapshots

- storage path and snapshots path are explicit configuration.
- snapshots can be stored locally or in object storage — S3, GCS or Azure Blob Storage — each with its own `*_config` block and an optional key `prefix` under `storage.snapshots_config`.
- WAL has tunables (capacity/segments) that matter under write load.

### Performance (avoid premature tuning)

- Search/indexing thread controls exist; defaults are usually fine until measured.
- HNSW/index parameters are configurable; only tune with benchmarks.

### Distributed cluster

- Cluster enablement and peer-to-peer settings are configurable.
- Peer TLS can be enabled.
- Transfer limits and shard transfer methods can be configured.

## Operational recommendations (portable)

- Treat config as an explicit artifact: commit non-secret defaults, inject secrets at deploy time.
- Prefer “small number of well-understood knobs” over changing many settings without measurement.
- Validate a restart path: invalid config should fail fast at startup.
- Read the startup warnings: they flag empty API keys, distributed deployments that leave the internal API unauthenticated, and snapshot-storage config blocks that are ignored because they do not match the selected backend.

