# Live / Realtime

Refine supports real-time data updates via `liveProvider`.

## Provider Interface

```tsx
import type { LiveProvider } from "@refinedev/core";

const liveProvider: LiveProvider = {
  subscribe: ({ channel, types, params, callback }) => {
    // Subscribe to real-time events
    // Return unsubscribe function
    return () => {
      // Cleanup subscription
    };
  },
  unsubscribe: (subscription) => {
    // Unsubscribe from channel
  },
  publish: ({ channel, type, payload, date }) => {
    // Publish event (optional)
  },
};
```

## Usage

```tsx
import { Refine } from "@refinedev/core";
import { liveProvider } from "./liveProvider";

function App() {
  return (
    <Refine
      liveProvider={liveProvider}
      options={{
        liveMode: "auto", // "auto" | "manual" | "off"
      }}
    >
      {/* ... */}
    </Refine>
  );
}
```

## Live Modes

| Mode | Description |
|------|-------------|
| `auto` | Automatically refetch on events |
| `manual` | Call `onLiveEvent` callback, no auto-refetch |
| `off` | Disable live updates |

## Ably Integration

```bash
npm install @refinedev/ably ably
```

```tsx
import { Refine } from "@refinedev/core";
import { liveProvider } from "@refinedev/ably";
import Ably from "ably";

const ablyClient = new Ably.Realtime("YOUR_ABLY_API_KEY");

function App() {
  return (
    <Refine
      liveProvider={liveProvider(ablyClient)}
      options={{ liveMode: "auto" }}
    >
      {/* ... */}
    </Refine>
  );
}
```

## Supabase Realtime

```tsx
import { Refine } from "@refinedev/core";
import { dataProvider, liveProvider } from "@refinedev/supabase";
import { createClient } from "@supabase/supabase-js";

const supabaseClient = createClient(
  "https://your-project.supabase.co",
  "your-anon-key"
);

function App() {
  return (
    <Refine
      dataProvider={dataProvider(supabaseClient)}
      liveProvider={liveProvider(supabaseClient)}
      options={{ liveMode: "auto" }}
    >
      {/* ... */}
    </Refine>
  );
}
```

## Custom WebSocket Provider

```tsx
import type { LiveProvider } from "@refinedev/core";

const createWebSocketLiveProvider = (wsUrl: string): LiveProvider => {
  const ws = new WebSocket(wsUrl);
  const subscribers = new Map<string, Set<Function>>();

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const { channel, type, payload } = data;

    const channelSubscribers = subscribers.get(channel);
    if (channelSubscribers) {
      channelSubscribers.forEach((callback) => {
        callback({ channel, type, payload, date: new Date() });
      });
    }
  };

  return {
    subscribe: ({ channel, types, callback }) => {
      if (!subscribers.has(channel)) {
        subscribers.set(channel, new Set());
        ws.send(JSON.stringify({ action: "subscribe", channel }));
      }
      subscribers.get(channel)?.add(callback);

      return () => {
        subscribers.get(channel)?.delete(callback);
        if (subscribers.get(channel)?.size === 0) {
          subscribers.delete(channel);
          ws.send(JSON.stringify({ action: "unsubscribe", channel }));
        }
      };
    },
    unsubscribe: (unsubscribeFn) => {
      unsubscribeFn();
    },
    publish: ({ channel, type, payload }) => {
      ws.send(JSON.stringify({ action: "publish", channel, type, payload }));
    },
  };
};

const liveProvider = createWebSocketLiveProvider("wss://your-ws-server.com");
```

## Hook-Level Configuration

### useList with Live Updates

```tsx
import { useList } from "@refinedev/core";

const { data } = useList({
  resource: "posts",
  liveMode: "auto",
  onLiveEvent: (event) => {
    console.log("Live event:", event);
    // { channel: "posts", type: "created", payload: {...}, date: Date }
  },
});
```

### useOne with Live Updates

```tsx
import { useOne } from "@refinedev/core";

const { data } = useOne({
  resource: "posts",
  id: 1,
  liveMode: "auto",
  onLiveEvent: (event) => {
    if (event.type === "updated" && event.payload.id === 1) {
      console.log("Post updated:", event.payload);
    }
  },
});
```

## Event Types

| Type | Description |
|------|-------------|
| `created` | New record created |
| `updated` | Record updated |
| `deleted` | Record deleted |
| `*` | All event types |

## useSubscription Hook

For custom subscriptions:

```tsx
import { useSubscription } from "@refinedev/core";

const MyComponent = () => {
  useSubscription({
    channel: "notifications",
    types: ["created"],
    onLiveEvent: (event) => {
      console.log("New notification:", event.payload);
    },
  });

  return <div>Listening for notifications...</div>;
};
```

## usePublish Hook

For publishing events:

```tsx
import { usePublish } from "@refinedev/core";

const MyComponent = () => {
  const publish = usePublish();

  const handleAction = () => {
    publish?.({
      channel: "posts",
      type: "custom-action",
      payload: { message: "Hello!" },
      date: new Date(),
    });
  };

  return <button onClick={handleAction}>Publish Event</button>;
};
```

## Per-Resource Configuration

```tsx
<Refine
  resources={[
    {
      name: "posts",
      list: "/posts",
      meta: {
        liveMode: "auto", // Live updates for this resource
      },
    },
    {
      name: "logs",
      list: "/logs",
      meta: {
        liveMode: "off", // No live updates for logs
      },
    },
  ]}
/>
```
