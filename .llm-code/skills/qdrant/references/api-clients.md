# API Clients (REST, gRPC, Python SDK)

Qdrant API interfaces and client library patterns.

## Interfaces

| Protocol | Port | Use Case |
|----------|------|----------|
| REST | 6333 | Development, debugging, human-readable |
| gRPC | 6334 | Production, high throughput, lower latency |

**Recommendation**: Start with REST for prototyping, switch to gRPC for production performance.

## Python SDK

```bash
pip install qdrant-client
# Optional: local embeddings
pip install qdrant-client[fastembed]
```

### Sync Client

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
```

### Async Client

```python
from qdrant_client import AsyncQdrantClient

async_client = AsyncQdrantClient(url="http://localhost:6333")
```

### Connection Options

- **Local/memory**: `QdrantClient(":memory:")`
- **Remote**: `QdrantClient(url="http://host:6333")`
- **Cloud**: `QdrantClient(url="https://your-cluster.qdrant.cloud", api_key="...")`

## Key Features

- Type definitions for all Qdrant API
- Sync and async requests
- Helper methods for common operations
- Supports REST and gRPC protocols

## Docker Port Exposure

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## gRPC + Multiprocessing Gotcha

**Error**: `sendmsg: Socket operation on non-socket (88)` when using multiprocessing with gRPC.

**Cause**: multiprocessing copies gRPC channels, sharing sockets; parent close breaks children.

**Fix**:
```python
import multiprocessing
multiprocessing.set_start_method("forkserver")  # or "spawn"
```

**Alternative**: Use REST API, async client, or built-in parallelization (`qdrant.upload_points(...)`).
