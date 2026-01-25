# Workflows API Reference

## WorkflowEntrypoint

```typescript
import { WorkflowEntrypoint, WorkflowStep, WorkflowEvent } from "cloudflare:workers";

export class MyWorkflow extends WorkflowEntrypoint<Env, Params> {
  async run(event: WorkflowEvent<Params>, step: WorkflowStep): Promise<T> {
    // Workflow logic
    return optionalResult;
  }
}
```

## WorkflowEvent

```typescript
interface WorkflowEvent<T> {
  payload: Readonly<T>; // Immutable params passed on create
  timestamp: Date; // Instance creation timestamp
  instanceId: string; // Unique instance identifier
}
```

## WorkflowStep

```typescript
interface WorkflowStep {
  // Execute durable step
  do<T>(name: string, callback: () => Promise<T>): Promise<T>;
  do<T>(name: string, config: WorkflowStepConfig, callback: () => Promise<T>): Promise<T>;

  // Sleep for duration
  sleep(name: string, duration: WorkflowDuration): Promise<void>;

  // Sleep until timestamp
  sleepUntil(name: string, timestamp: Date | number): Promise<void>;

  // Wait for external event
  waitForEvent<T>(name: string, options: WaitForEventOptions): Promise<T>;
}
```

## WorkflowStepConfig

```typescript
interface WorkflowStepConfig {
  retries?: {
    limit: number; // Max attempts (supports Infinity)
    delay: string | number; // Delay between retries
    backoff?: "constant" | "linear" | "exponential";
  };
  timeout?: string | number; // Per-attempt timeout
}
```

**Defaults**:

```typescript
{
  retries: { limit: 5, delay: 10000, backoff: 'exponential' },
  timeout: '10 minutes'
}
```

## WorkflowDuration

Accepts `number` (milliseconds) or human-readable string:

```typescript
type WorkflowDuration = number | string;

// Examples
("1 second");
("30 seconds");
("5 minutes");
("2 hours");
("1 day");
("1 week");
("1 month");
("1 year");
```

## WaitForEventOptions

```typescript
interface WaitForEventOptions {
  type: string; // Event type (max 100 chars)
  timeout?: WorkflowDuration; // Default: 24 hours (max: 365 days)
}
```

## NonRetryableError

```typescript
import { NonRetryableError } from "cloudflare:workflows";

// Immediately fail step without retries
throw new NonRetryableError("Validation failed", "ValidationError");
```

## Workflow Binding

```typescript
interface Workflow<Params = unknown> {
  // Create single instance
  create(options?: WorkflowInstanceCreateOptions<Params>): Promise<WorkflowInstance>;

  // Create up to 100 instances
  createBatch(batch: WorkflowInstanceCreateOptions<Params>[]): Promise<WorkflowInstance[]>;

  // Get existing instance
  get(id: string): Promise<WorkflowInstance>;
}

interface WorkflowInstanceCreateOptions<Params> {
  id?: string; // Custom ID (max 100 chars)
  params?: Params; // JSON-serializable params
}
```

## WorkflowInstance

```typescript
interface WorkflowInstance {
  readonly id: string;

  pause(): Promise<void>;
  resume(): Promise<void>;
  terminate(): Promise<void>;
  restart(): Promise<void>;
  status(): Promise<InstanceStatus>;
  sendEvent(options: SendEventOptions): Promise<void>;
}

interface SendEventOptions {
  type: string; // Must match waitForEvent type
  payload?: unknown; // JSON-serializable data
}
```

## InstanceStatus

```typescript
interface InstanceStatus {
  status: "queued" | "running" | "paused" | "waiting" | "waitingForPause" | "complete" | "errored" | "terminated" | "unknown";
  error?: {
    name: string;
    message: string;
  };
  output?: unknown; // Return value from run()
}
```

## wrangler.jsonc

```jsonc
{
  "name": "my-worker",
  "main": "src/index.ts",
  "workflows": [
    {
      "name": "my-workflow", // Workflow name
      "binding": "MY_WORKFLOW", // Env binding name
      "class_name": "MyWorkflow" // Exported class name
    }
  ],
  "limits": {
    "cpu_ms": 300000 // Max 5 minutes CPU (optional)
  }
}
```

## Step Name Rules

- Max 256 characters
- Must be deterministic (no `Date.now()`, `Math.random()`)
- Acts as cache key for step state
- Duplicate names reuse cached result
