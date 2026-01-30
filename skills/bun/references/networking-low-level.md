````markdown
# Low-Level Networking

High-performance TCP and UDP APIs for custom protocols.

## TCP

### Server

```typescript
const server = Bun.listen({
  hostname: "localhost",
  port: 8080,
  socket: {
    open(socket) { console.log("Connected"); },
    data(socket, data) { socket.write(`Echo: ${data}`); },
    close(socket, error) {},
    drain(socket) {},  // Socket ready for more data
    error(socket, error) {},
  },
});

server.stop();       // Keep existing connections
server.stop(true);   // Close all
server.unref();      // Don't keep process alive
```
````

### Client

```typescript
const socket = await Bun.connect({
  hostname: "localhost",
  port: 8080,
  socket: {
    open(socket) { socket.write("Hello server!"); },
    data(socket, data) { console.log("Received:", data); },
    close(socket, error) {},
    drain(socket) {},
    error(socket, error) {},
    connectError(socket, error) {},  // Connection failed
    end(socket) {},                  // Server closed
    timeout(socket) {},
  },
});
```

### Per-Socket Data

```typescript
type SocketData = { sessionId: string };

Bun.listen<SocketData>({
  hostname: "localhost",
  port: 8080,
  socket: {
    open(socket) {
      socket.data = { sessionId: crypto.randomUUID() };
    },
    data(socket, data) {
      console.log(`${socket.data.sessionId}: ${data}`);
    },
  },
});
```

### TLS

```typescript
// Server
Bun.listen({
  port: 443,
  socket: { /* handlers */ },
  tls: {
    key: Bun.file("./key.pem"),
    cert: Bun.file("./cert.pem"),
  },
});

// Client
await Bun.connect({
  hostname: "example.com",
  port: 443,
  tls: true,
  socket: { /* handlers */ },
});
```

### Hot Reload

```typescript
server.reload({
  socket: {
    data(socket, data) { /* new handler */ },
  },
});
```

### Buffering Best Practice

```typescript
// ❌ Slow - multiple syscalls
socket.write("h"); socket.write("e"); socket.write("l");

// ✅ Fast - single syscall
socket.write("hello");
```

### Socket Methods

```typescript
socket.write(data);           // Send data
socket.end();                 // Close gracefully
socket.terminate();           // Close immediately
socket.flush();               // Flush buffer
socket.timeout(seconds);      // Set timeout
socket.ref() / socket.unref();
```

---

## UDP

### Create & Send

```typescript
// Create socket
const socket = await Bun.udpSocket({ port: 41234 });

// Send datagram (no DNS - use IP)
socket.send("Hello", 41234, "127.0.0.1");
```

### Receive

```typescript
const server = await Bun.udpSocket({
  socket: {
    data(socket, buf, port, addr) {
      console.log(`From ${addr}:${port}: ${buf.toString()}`);
    },
  },
});
```

### Connected Socket

```typescript
const client = await Bun.udpSocket({
  connect: {
    hostname: "127.0.0.1",
    port: 41234,
  },
});

client.send("Hello");  // No destination needed
```

### Batch Sending

```typescript
// Unconnected: [data, port, addr, ...]
socket.sendMany(["Hello", 41234, "127.0.0.1", "World", 53, "1.1.1.1"]);

// Connected: [data, ...]
connectedSocket.sendMany(["foo", "bar", "baz"]);
```

### Multicast

```typescript
socket.addMembership("224.0.0.1");
socket.dropMembership("224.0.0.1");
socket.setMulticastTTL(2);
socket.setMulticastLoopback(true);
```

---

## Key Points

| Aspect      | TCP                 | UDP               |
| ----------- | ------------------- | ----------------- |
| Connection  | Connection-oriented | Connectionless    |
| Reliability | Guaranteed delivery | Best effort       |
| Use case    | HTTP, DB, files     | Real-time, gaming |
| Buffering   | Manual batching     | Auto per datagram |
| DNS         | Resolved            | IP addresses only |

**Common rules:**

- Use `drain` handler for backpressure
- Batch writes for performance
- `socket.data` for per-connection state (TCP)
- `unref()` to not block process exit

```

```
