# Durable Objects Alarms

## Overview

Each Durable Object can schedule a single alarm for background processing. Alarms provide guaranteed at-least-once execution with automatic retries.

## Basic Usage

### Set Alarm

```typescript
// Schedule 1 hour from now
await this.ctx.storage.setAlarm(Date.now() + 60 * 60 * 1000);

// Schedule at specific time
await this.ctx.storage.setAlarm(new Date("2024-12-31T00:00:00Z"));
```

### Handle Alarm

```typescript
export class MyDO extends DurableObject<Env> {
  async alarm(info?: AlarmInfo): Promise<void> {
    console.log(`Alarm! Retry: ${info?.isRetry}, count: ${info?.retryCount}`);
    await this.processScheduledWork();
  }
}
```

### Alarm Methods

```typescript
// Set/overwrite alarm
await this.ctx.storage.setAlarm(timestampMs);

// Get scheduled time (ms) or null
const time = await this.ctx.storage.getAlarm();

// Cancel alarm
await this.ctx.storage.deleteAlarm();
```

## Retry Behavior

- Alarms retry automatically on exceptions
- Exponential backoff starting at 2 seconds
- Up to 6 retries before failure
- `deleteAlarm()` inside handler may prevent retries (best-effort)

## AlarmInfo

```typescript
interface AlarmInfo {
  readonly isRetry: boolean; // True if this is a retry
  readonly retryCount: number; // Number of previous attempts
}
```

## Patterns

### Recurring Task

```typescript
export class Scheduler extends DurableObject<Env> {
  async alarm(): Promise<void> {
    await this.runScheduledTask();

    // Schedule next run
    await this.ctx.storage.setAlarm(Date.now() + 60 * 60 * 1000); // 1 hour
  }
}
```

### Multiple Events with Single Alarm

```typescript
export class EventScheduler extends DurableObject<Env> {
  async scheduleEvent(eventId: string, runAt: number): Promise<void> {
    await this.ctx.storage.put(`event:${runAt}:${eventId}`, { eventId, runAt });

    const nextAlarm = await this.ctx.storage.getAlarm();
    if (!nextAlarm || runAt < nextAlarm) {
      await this.ctx.storage.setAlarm(runAt);
    }
  }

  async alarm(): Promise<void> {
    const now = Date.now();
    const events = await this.ctx.storage.list({ prefix: "event:" });

    for (const [key, event] of events) {
      if (event.runAt <= now) {
        await this.processEvent(event);
        await this.ctx.storage.delete(key);
      }
    }

    // Schedule next alarm for remaining events
    const remaining = await this.ctx.storage.list({ prefix: "event:", limit: 1 });
    if (remaining.size > 0) {
      const [[, nextEvent]] = remaining;
      await this.ctx.storage.setAlarm(nextEvent.runAt);
    }
  }
}
```

### Delayed Processing

```typescript
export class DelayedProcessor extends DurableObject<Env> {
  async queueItem(item: any, delayMs: number): Promise<void> {
    const runAt = Date.now() + delayMs;
    await this.ctx.storage.put(`queue:${runAt}:${crypto.randomUUID()}`, item);

    const nextAlarm = await this.ctx.storage.getAlarm();
    if (!nextAlarm || runAt < nextAlarm) {
      await this.ctx.storage.setAlarm(runAt);
    }
  }

  async alarm(): Promise<void> {
    const now = Date.now();
    const items = await this.ctx.storage.list({ prefix: "queue:" });

    for (const [key, item] of items) {
      const runAt = parseInt(key.split(":")[1]);
      if (runAt <= now) {
        await this.processItem(item);
        await this.ctx.storage.delete(key);
      }
    }

    // Reschedule for remaining items
    await this.scheduleNextAlarm();
  }
}
```

### Retry with Exponential Backoff

```typescript
export class RetryProcessor extends DurableObject<Env> {
  async alarm(info?: AlarmInfo): Promise<void> {
    try {
      await this.processWork();
    } catch (error) {
      if (info && info.retryCount < 5) {
        // Let automatic retry handle it
        throw error;
      }
      // Max retries reached, handle failure
      await this.handleFailure(error);
    }
  }
}
```

## Best Practices

1. **Single alarm per DO**: Use storage to track multiple events
2. **Idempotent handlers**: Alarms may retry, design for at-least-once
3. **Check alarm state**: Use `getAlarm()` before setting new alarm
4. **Handle failures**: Log or store failed items for later processing
5. **Avoid long-running work**: Break into smaller chunks if needed

## Billing Notes

- `setAlarm()` counts as a storage write
- `getAlarm()` counts as a storage read
- Alarm execution = 1 request + duration billing
