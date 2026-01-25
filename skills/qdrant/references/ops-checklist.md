# Operations Checklist (Monitoring, Performance, Troubleshooting)

Operational guidance for Qdrant: monitoring, performance tuning, and common issues.

---

## Monitoring

### Key Endpoints

| Endpoint | Purpose | Notes |
|----------|---------|-------|
| `/metrics` | Prometheus metrics | Scrape per node |
| `/telemetry` | State info (vectors, shards) | Debugging |
| `/healthz`, `/livez`, `/readyz` | Kubernetes health | Always accessible |

### Essential Metrics

**Collections**:
- `collections_total`, `collection_points`, `collection_vectors`

**API Performance**:
- `rest_responses_total/fail_total`
- `rest_responses_duration_seconds` (histogram)

**Memory**:
- `memory_allocated_bytes`, `memory_resident_bytes`

**Process**:
- `process_open_fds`, `process_threads`

**Cluster** (distributed):
- `cluster_peers_total`, `cluster_pending_operations_total`

**Optimizations**:
- `collection_running_optimizations`

### Configuration

- Prefix metrics: `QDRANT__SERVICE__METRICS_PREFIX`
- Hardware IO: `service.hardware_reporting: true`

---

## Performance Checklist

### Scenario 1: High-Speed Search, Low Memory

- Vectors `on_disk: true`
- Scalar quantization `int8` with `always_ram: true`
- Optional: `quantization.rescore: false` (slight precision loss)

### Scenario 2: High Precision, Low Memory

- Vectors and HNSW `on_disk: true`
- Increase HNSW: `m: 64`, `ef_construct: 512`
- Use inline storage (v1.16+) with quantization
- Check disk IOPS

### Scenario 3: High Precision, High-Speed

- Keep vectors in RAM
- Scalar quantization with rescoring
- Tune search: higher `hnsw_ef`, `exact: true` for ground truth

### General Tuning

| Goal | Setting |
|------|---------|
| Minimize latency | `default_segment_number` = CPU cores |
| Maximize throughput | `default_segment_number: 2`, `max_segment_size: 5M` |

### Checklist

- [ ] Index payload fields used in filters
- [ ] Choose quantization (scalar/binary) based on precision needs
- [ ] Monitor memory/disk via `/metrics`
- [ ] Adjust HNSW params (m, ef_construct, on_disk)
- [ ] Use named vectors for multi-modal
- [ ] Run optimizer after bulk inserts

---

## Troubleshooting

### Too many files open (OS error 24)

**Cause**: Each collection segment requires open files.

**Fix**:
```bash
# Docker
docker run --ulimit nofile=10000:10000 qdrant/qdrant

# Shell
ulimit -n 10000
```

### Incompatible file system (data corruption risk)

**Cause**: Qdrant requires POSIX-compatible filesystem; non-POSIX (FUSE, HFS+, WSL mounts) can corrupt data.

**Symptoms**:
- `OutputTooSmall { expected: 4, actual: 0 }`
- Vectors zeroed after restart

**Fix**: Use Docker named volumes instead of bind mounts to Windows folders (WSL issue).

### Can't open Collections meta Wal (distributed)

**Error**: `Resource temporarily unavailable`

**Cause**: WAL files locked by another Qdrant instance (shared storage).

**Fix**: Each node must have its own storage directory. Cluster handles data sharing internally.

### gRPC + Multiprocessing Socket Error

**Error**: `sendmsg: Socket operation on non-socket (88)`

**Fix**:
```python
import multiprocessing
multiprocessing.set_start_method("forkserver")  # or "spawn"
```

Or use REST API / async client.

---

## Quick Fixes Summary

| Issue | Fix |
|-------|-----|
| File limit errors | `--ulimit nofile=10000:10000` |
| Data corruption on WSL | Use Docker named volumes |
| Slow filtered search | Index payload fields |
| High memory usage | Enable `on_disk` for vectors/HNSW |
| Low recall | Increase `hnsw_ef`, `ef_construct` |
