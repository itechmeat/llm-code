# Pull Consumers (HTTP API)

Pull consumers allow consuming queue messages from outside Cloudflare Workers via HTTP API.

## Enable Pull Consumer

```jsonc
// wrangler.jsonc
{
  "queues": {
    "consumers": [
      {
        "queue": "my-queue",
        "type": "http_pull",
        "visibility_timeout_ms": 30000,
        "max_retries": 5,
        "dead_letter_queue": "my-dlq"
      }
    ]
  }
}
```

## Configuration

| Setting                 | Default  | Range                  | Description             |
| ----------------------- | -------- | ---------------------- | ----------------------- |
| `type`                  | `worker` | `worker` / `http_pull` | Consumer type           |
| `visibility_timeout_ms` | 30000    | 1000-43200000          | Time before re-delivery |
| `max_retries`           | 3        | 0-100                  | Retries before DLQ      |
| `dead_letter_queue`     | none     | —                      | DLQ name                |

## API Endpoints

Base URL: `https://api.cloudflare.com/client/v4/accounts/{account_id}/queues/{queue_id}/messages`

### Pull Messages

```bash
curl -X POST ".../messages/pull" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_size": 10,
    "visibility_timeout_ms": 30000
  }'
```

**Response**:

```json
{
  "result": {
    "messages": [
      {
        "id": "msg-abc123",
        "body": "{\"task\":\"process\"}",
        "timestamp_ms": 1699000000000,
        "attempts": 1,
        "lease_id": "lease-xyz789",
        "metadata": {
          "content-type": "application/json"
        }
      }
    ]
  }
}
```

### Acknowledge Messages

```bash
curl -X POST ".../messages/ack" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "acks": [
      { "lease_id": "lease-xyz789" }
    ],
    "retries": [
      { "lease_id": "lease-abc456", "delay_seconds": 60 }
    ]
  }'
```

## Visibility Timeout

When pulled, message becomes invisible for `visibility_timeout_ms`.

- If not acknowledged: re-delivered after timeout
- Ack before timeout: permanently deleted
- Retry: re-queued with optional delay

## Content Types

**Warning**: `v8` content type cannot be decoded by external consumers.

| Content-Type Header        | Body Format    |
| -------------------------- | -------------- |
| `application/json`         | JSON string    |
| `text/plain`               | UTF-8 text     |
| `application/octet-stream` | Base64 encoded |

## Python Example

```python
import requests

ACCOUNT_ID = "..."
QUEUE_ID = "..."
API_TOKEN = "..."

BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/queues/{QUEUE_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Pull messages
resp = requests.post(f"{BASE_URL}/pull", headers=HEADERS, json={"batch_size": 10})
messages = resp.json()["result"]["messages"]

# Process and acknowledge
acks = []
for msg in messages:
    process(msg["body"])
    acks.append({"lease_id": msg["lease_id"]})

requests.post(f"{BASE_URL}/ack", headers=HEADERS, json={"acks": acks})
```

## Required Permissions

API Token needs:

- `com.cloudflare.api.account.queues.pull` — Read messages
- `com.cloudflare.api.account.queues.ack` — Acknowledge messages
