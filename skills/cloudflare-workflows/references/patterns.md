# Workflow Patterns

## Saga Pattern (Compensating Transactions)

```typescript
async run(event: WorkflowEvent<Params>, step: WorkflowStep) {
  const reservation = await step.do("reserve inventory", async () => {
    return await reserveItems(event.payload.items);
  });

  try {
    const payment = await step.do("charge payment", async () => {
      return await chargeCard(event.payload.paymentMethod);
    });

    await step.do("confirm order", async () => {
      return await confirmOrder(reservation.id, payment.id);
    });
  } catch (error) {
    // Compensating transaction
    await step.do("release inventory", async () => {
      await releaseReservation(reservation.id);
    });
    throw error;
  }
}
```

## Approval Workflow

```typescript
async run(event: WorkflowEvent<Params>, step: WorkflowStep) {
  await step.do("send approval request", async () => {
    await sendSlackMessage(event.payload.approverEmail);
  });

  const approval = await step.waitForEvent<{ approved: boolean }>("wait for approval", {
    type: "manager_approval",
    timeout: "7 days"
  });

  if (approval.approved) {
    await step.do("execute action", async () => { /* ... */ });
  } else {
    await step.do("notify rejection", async () => { /* ... */ });
  }
}
```

## Scheduled Reminders

```typescript
async run(event: WorkflowEvent<Params>, step: WorkflowStep) {
  for (let i = 0; i < 3; i++) {
    await step.do(`send reminder ${i + 1}`, async () => {
      await sendReminder(event.payload.userId);
    });
    await step.sleep(`wait ${i + 1}`, "1 day");
  }
}
```

## Retry with Exponential Backoff

```typescript
async run(event: WorkflowEvent<Params>, step: WorkflowStep) {
  const result = await step.do("call flaky API", {
    retries: {
      limit: 10,
      delay: "1 second",
      backoff: "exponential"  // 1s, 2s, 4s, 8s...
    },
    timeout: "30 seconds"
  }, async () => {
    return await flakyApiCall();
  });
}
```

## Fan-Out / Fan-In

```typescript
async run(event: WorkflowEvent<Params>, step: WorkflowStep) {
  const items = event.payload.items;

  // Fan-out: process each item
  const results = [];
  for (const item of items) {
    const result = await step.do(`process ${item.id}`, async () => {
      return await processItem(item);
    });
    results.push(result);
  }

  // Fan-in: aggregate
  const summary = await step.do("aggregate results", async () => {
    return { total: results.length, success: results.filter(r => r.ok).length };
  });

  return summary;
}
```

## Webhook Callback

```typescript
async run(event: WorkflowEvent<Params>, step: WorkflowStep) {
  // Start async job
  const jobId = await step.do("start job", async () => {
    const resp = await fetch("https://api.example.com/jobs", {
      method: "POST",
      body: JSON.stringify({ callbackInstanceId: event.instanceId })
    });
    return (await resp.json()).jobId;
  });

  // Wait for callback
  const result = await step.waitForEvent<{ status: string }>("wait for job", {
    type: "job_complete",
    timeout: "1 hour"
  });

  return { jobId, status: result.status };
}

// Webhook handler Worker
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { instanceId, status } = await request.json();
    const instance = await env.MY_WORKFLOW.get(instanceId);
    await instance.sendEvent({ type: "job_complete", payload: { status } });
    return new Response("OK");
  }
};
```

## Timeout with Fallback

```typescript
async run(event: WorkflowEvent<Params>, step: WorkflowStep) {
  let response;

  try {
    response = await step.waitForEvent<ApiResponse>("wait for API", {
      type: "api_response",
      timeout: "5 minutes"
    });
  } catch (e) {
    // Timeout: use cached/default value
    response = await step.do("get fallback", async () => {
      return await getCachedValue(event.payload.key);
    });
  }

  return response;
}
```
