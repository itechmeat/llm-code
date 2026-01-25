# Notification Provider Reference

Refine's notification system provides toast notifications for user feedback on CRUD operations.

## NotificationProvider Interface

```ts
interface NotificationProvider {
  open: (params: OpenNotificationParams) => void;
  close: (key: string) => void;
}

interface OpenNotificationParams {
  key?: string;
  message: string;
  description?: string;
  type: "success" | "error" | "progress";
  cancelMutation?: () => void;
  undoableTimeout?: number;
}
```

## Built-in Mantine Notifications

Mantine package includes built-in notification provider:

```tsx
import { Refine } from "@refinedev/core";
import { notificationProvider } from "@refinedev/mantine";
import { NotificationsProvider } from "@mantine/notifications";

function App() {
  return (
    <NotificationsProvider position="top-right">
      <Refine
        notificationProvider={notificationProvider}
        // ...other providers
      >
        {/* Routes */}
      </Refine>
    </NotificationsProvider>
  );
}
```

## useNotification Hook

Access notification methods anywhere in your app:

```tsx
import { useNotification } from "@refinedev/core";

function MyComponent() {
  const { open, close } = useNotification();

  const showSuccess = () => {
    open({
      type: "success",
      message: "Operation completed",
      description: "Record saved successfully",
    });
  };

  const showError = () => {
    open({
      type: "error",
      message: "Operation failed",
      description: "Could not save the record",
    });
  };

  const showProgress = () => {
    open({
      key: "upload-progress",
      type: "progress",
      message: "Uploading...",
      undoableTimeout: 5000,
      cancelMutation: () => {
        console.log("Upload cancelled");
      },
    });
  };

  const closeNotification = () => {
    close("upload-progress");
  };

  return (
    <>
      <button onClick={showSuccess}>Show Success</button>
      <button onClick={showError}>Show Error</button>
      <button onClick={showProgress}>Show Progress</button>
    </>
  );
}
```

## Automatic Notifications

Refine data hooks trigger notifications automatically:

| Hook | Success | Error |
|------|---------|-------|
| useCreate | "Successfully created" | Shows error message |
| useUpdate | "Successfully updated" | Shows error message |
| useDelete | "Successfully deleted" | Shows error message |

### Disable Auto Notifications

```tsx
const { mutate } = useCreate();

mutate({
  resource: "posts",
  values: { title: "New Post" },
  successNotification: false,  // Disable success toast
  errorNotification: false,    // Disable error toast
});
```

### Custom Notification Messages

```tsx
const { mutate } = useCreate();

mutate({
  resource: "posts",
  values: { title: "New Post" },
  successNotification: (data, values, resource) => ({
    message: "Post Created!",
    description: `"${values.title}" was published.`,
    type: "success",
  }),
  errorNotification: (error, values, resource) => ({
    message: "Creation Failed",
    description: error?.message || "Unknown error occurred",
    type: "error",
  }),
});
```

## Undoable Mutations

Enable undo for delete operations:

```tsx
<Refine
  options={{
    mutationMode: "undoable",
    undoableTimeout: 5000, // 5 seconds to undo
  }}
/>
```

With undoable mode:
1. User clicks delete
2. Notification shows with "Undo" button
3. After timeout, mutation executes
4. User can cancel during the timeout

```tsx
const { mutate } = useDelete();

mutate({
  resource: "posts",
  id: 1,
  mutationMode: "undoable", // Per-mutation override
  undoableTimeout: 10000,   // 10 seconds
});
```

## Custom Notification Provider

Create custom provider for React Toastify or other libraries:

```tsx
import { toast, ToastContainer } from "react-toastify";
import type { NotificationProvider } from "@refinedev/core";

const notificationProvider: NotificationProvider = {
  open: ({ key, message, description, type, cancelMutation, undoableTimeout }) => {
    if (type === "progress") {
      toast.loading(message, {
        toastId: key,
        autoClose: false,
      });
      
      if (undoableTimeout && cancelMutation) {
        setTimeout(() => {
          toast.dismiss(key);
        }, undoableTimeout);
      }
      return;
    }

    toast[type](
      <>
        <strong>{message}</strong>
        {description && <p>{description}</p>}
        {cancelMutation && (
          <button onClick={cancelMutation}>Undo</button>
        )}
      </>,
      { toastId: key }
    );
  },
  close: (key) => {
    toast.dismiss(key);
  },
};

// Usage in App
function App() {
  return (
    <>
      <ToastContainer />
      <Refine notificationProvider={notificationProvider} />
    </>
  );
}
```

## Common Patterns

### Manual Success/Error After Custom Logic

```tsx
function CustomAction() {
  const { open } = useNotification();
  const apiUrl = useApiUrl();

  const handleCustomAction = async () => {
    try {
      await fetch(`${apiUrl}/custom-endpoint`, {
        method: "POST",
      });
      
      open({
        type: "success",
        message: "Custom action completed",
      });
    } catch (error) {
      open({
        type: "error",
        message: "Custom action failed",
        description: error.message,
      });
    }
  };

  return <button onClick={handleCustomAction}>Execute</button>;
}
```

### Notification with Key for Updates

```tsx
function ProgressExample() {
  const { open, close } = useNotification();

  const startProgress = () => {
    open({
      key: "file-upload",
      type: "progress",
      message: "Uploading file...",
    });

    // Later, update to success
    setTimeout(() => {
      close("file-upload");
      open({
        type: "success",
        message: "File uploaded successfully",
      });
    }, 3000);
  };

  return <button onClick={startProgress}>Upload</button>;
}
```
