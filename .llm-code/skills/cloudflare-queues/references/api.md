# Queues API Reference

## Queue (Producer)

```typescript
interface Queue<Body = unknown> {
  send(body: Body, options?: QueueSendOptions): Promise<void>;
  sendBatch(messages: Iterable<MessageSendRequest<Body>>, options?: QueueSendBatchOptions): Promise<void>;
}

interface QueueSendOptions {
  contentType?: QueueContentType;
  delaySeconds?: number; // 0-43200 (12 hours)
}

interface QueueSendBatchOptions {
  delaySeconds?: number; // Default for all messages
}

interface MessageSendRequest<Body = unknown> {
  body: Body;
  options?: QueueSendOptions;
}

type QueueContentType = "text" | "bytes" | "json" | "v8";
```

## MessageBatch (Consumer)

```typescript
interface MessageBatch<Body = unknown> {
  readonly queue: string;
  readonly messages: Message<Body>[];
  ackAll(): void;
  retryAll(options?: QueueRetryOptions): void;
}

interface Message<Body = unknown> {
  readonly id: string;
  readonly timestamp: Date;
  readonly body: Body;
  readonly attempts: number;
  ack(): void;
  retry(options?: QueueRetryOptions): void;
}

interface QueueRetryOptions {
  delaySeconds?: number; // 0-43200
}
```

## Content Types

| Type    | Description               | Pull Consumer Support |
| ------- | ------------------------- | --------------------- |
| `json`  | JSON serialized (default) | ✓                     |
| `text`  | Plain UTF-8 text          | ✓                     |
| `bytes` | Raw binary (ArrayBuffer)  | ✓                     |
| `v8`    | V8 internal serialization | ✗                     |

## Send Examples

```typescript
// Basic send
await env.MY_QUEUE.send({ task: "process", id: 123 });

// With delay
await env.MY_QUEUE.send(data, { delaySeconds: 600 });

// With explicit content type
await env.MY_QUEUE.send(text, { contentType: "text" });
await env.MY_QUEUE.send(buffer, { contentType: "bytes" });
```

## Batch Examples

```typescript
// Send batch
await env.MY_QUEUE.sendBatch([{ body: { id: 1 } }, { body: { id: 2 }, options: { delaySeconds: 300 } }]);

// With global options
await env.MY_QUEUE.sendBatch(messages, { delaySeconds: 60 });
```

## Consumer Examples

```typescript
export default {
  async queue(batch: MessageBatch<MyType>, env: Env): Promise<void> {
    for (const msg of batch.messages) {
      console.log(msg.id, msg.attempts, msg.body);
      msg.ack();
    }
  },
};
```

## Acknowledgment Priority

1. Per-message `ack()` / `retry()` calls take precedence
2. Batch-level `ackAll()` / `retryAll()` for remaining
3. No action = implicit retry (uses default delay)
