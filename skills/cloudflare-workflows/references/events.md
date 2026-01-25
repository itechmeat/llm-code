# Workflow Events

## Overview

Workflows can wait for external events using `step.waitForEvent`. Events can be sent via Worker bindings or REST API.

## Wait for Event

```typescript
const result = await step.waitForEvent<PayloadType>("event name", {
  type: "approval", // Event type to match (max 100 chars)
  timeout: "7 days", // Optional, default: 24 hours
});
```

## Send Event via Binding

```typescript
const instance = await env.MY_WORKFLOW.get(instanceId);

await instance.sendEvent({
  type: "approval", // Must match waitForEvent type
  payload: {
    approved: true,
    approvedBy: "user@example.com",
  },
});
```

## Send Event via REST API

```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/workflows/{workflow_name}/instances/{instance_id}/events" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "approval",
    "payload": {
      "approved": true
    }
  }'
```

## Event Buffering

Events can be sent before Workflow reaches `waitForEvent`:

```typescript
// 1. Create instance
const instance = await env.MY_WORKFLOW.create({ params: { orderId: 123 } });

// 2. Send event immediately (before workflow reaches waitForEvent)
await instance.sendEvent({
  type: "payment_confirmed",
  payload: { transactionId: "abc123" },
});

// 3. Workflow will receive event when it reaches matching waitForEvent
```

## Timeout Handling

Default timeout is 24 hours. On timeout, Workflow throws error and fails.

### Continue on Timeout

```typescript
try {
  const event = await step.waitForEvent("optional approval", {
    type: "manager_approval",
    timeout: "1 hour",
  });
  await processApproval(event);
} catch (e) {
  // Timeout occurred, continue with default behavior
  await processDefault();
}
```

## Multiple Events

Wait for different event types in sequence:

```typescript
async run(event: WorkflowEvent<Params>, step: WorkflowStep) {
  // Wait for first event
  const orderConfirmed = await step.waitForEvent("order confirmation", {
    type: "order_confirmed",
    timeout: "1 day"
  });

  // Wait for second event
  const paymentReceived = await step.waitForEvent("payment", {
    type: "payment_received",
    timeout: "7 days"
  });

  // Continue processing
  await step.do("fulfill order", async () => {
    // ...
  });
}
```

## Webhook Integration

```typescript
// Webhook handler Worker
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { instanceId, status } = await request.json();

    const instance = await env.MY_WORKFLOW.get(instanceId);
    await instance.sendEvent({
      type: "webhook_callback",
      payload: { status },
    });

    return new Response("OK");
  },
};
```

## Event Payload Limits

- Maximum event payload size: 1 MiB
- Event type: max 100 characters
- Payload must be JSON-serializable

## Best Practices

1. Use descriptive, unique event types
2. Always handle timeout cases with try-catch
3. Include correlation IDs in payloads for debugging
4. Send events as soon as external action completes
5. Use buffering for async event sources
