# R2 Presigned URLs

Presigned URLs provide temporary access to R2 objects without exposing API credentials.

## Overview

- Grant temporary GET, PUT, HEAD, or DELETE access
- Expiration: 1 second to 7 days
- Work with S3 API endpoint only (not custom domains)
- Require CORS configuration for browser use

---

## Generate Presigned URLs

### Setup S3 Client

```typescript
import { S3Client } from "@aws-sdk/client-s3";

const S3 = new S3Client({
  region: "auto",
  endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: ACCESS_KEY_ID,
    secretAccessKey: SECRET_ACCESS_KEY,
  },
});
```

### Download URL (GET)

```typescript
import { GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const downloadUrl = await getSignedUrl(
  S3,
  new GetObjectCommand({
    Bucket: "my-bucket",
    Key: "file.pdf",
  }),
  { expiresIn: 3600 } // 1 hour
);
```

### Upload URL (PUT)

```typescript
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const uploadUrl = await getSignedUrl(
  S3,
  new PutObjectCommand({
    Bucket: "my-bucket",
    Key: "uploads/file.pdf",
    ContentType: "application/pdf",
  }),
  { expiresIn: 3600 }
);
```

### Delete URL

```typescript
import { DeleteObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const deleteUrl = await getSignedUrl(
  S3,
  new DeleteObjectCommand({
    Bucket: "my-bucket",
    Key: "file.pdf",
  }),
  { expiresIn: 600 } // 10 minutes
);
```

---

## Browser Integration

### 1. Configure CORS

```json
[
  {
    "AllowedOrigins": ["https://example.com"],
    "AllowedMethods": ["GET", "PUT"],
    "AllowedHeaders": ["Content-Type"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

```bash
npx wrangler r2 bucket cors set my-bucket --file cors.json
```

### 2. Upload from Browser

```typescript
// Get presigned URL from your API
const { uploadUrl } = await fetch("/api/get-upload-url").then((r) => r.json());

// Upload file directly to R2
const response = await fetch(uploadUrl, {
  method: "PUT",
  body: file,
  headers: {
    "Content-Type": file.type,
  },
});

if (response.ok) {
  console.log("Upload successful");
}
```

### 3. Download in Browser

```typescript
// Get presigned URL from your API
const { downloadUrl } = await fetch("/api/get-download-url").then((r) => r.json());

// Option 1: Open in new tab
window.open(downloadUrl, "_blank");

// Option 2: Force download
const a = document.createElement("a");
a.href = downloadUrl;
a.download = "filename.pdf";
a.click();

// Option 3: Fetch content
const response = await fetch(downloadUrl);
const blob = await response.blob();
```

---

## Worker API Endpoint

```typescript
import { S3Client, GetObjectCommand, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

export interface Env {
  ACCOUNT_ID: string;
  ACCESS_KEY_ID: string;
  SECRET_ACCESS_KEY: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    const S3 = new S3Client({
      region: "auto",
      endpoint: `https://${env.ACCOUNT_ID}.r2.cloudflarestorage.com`,
      credentials: {
        accessKeyId: env.ACCESS_KEY_ID,
        secretAccessKey: env.SECRET_ACCESS_KEY,
      },
    });

    if (url.pathname === "/api/get-upload-url") {
      const key = url.searchParams.get("key");
      const contentType = url.searchParams.get("contentType") || "application/octet-stream";

      const uploadUrl = await getSignedUrl(
        S3,
        new PutObjectCommand({
          Bucket: "my-bucket",
          Key: key,
          ContentType: contentType,
        }),
        { expiresIn: 3600 }
      );

      return Response.json({ uploadUrl });
    }

    if (url.pathname === "/api/get-download-url") {
      const key = url.searchParams.get("key");

      const downloadUrl = await getSignedUrl(
        S3,
        new GetObjectCommand({
          Bucket: "my-bucket",
          Key: key,
        }),
        { expiresIn: 3600 }
      );

      return Response.json({ downloadUrl });
    }

    return new Response("Not Found", { status: 404 });
  },
};
```

---

## Security Best Practices

### Validate file types

```typescript
const ALLOWED_TYPES = ["image/jpeg", "image/png", "application/pdf"];

if (!ALLOWED_TYPES.includes(contentType)) {
  return new Response("Invalid file type", { status: 400 });
}
```

### Validate file size (via Content-Length)

```typescript
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

// Include Content-Length condition in PUT
const uploadUrl = await getSignedUrl(
  S3,
  new PutObjectCommand({
    Bucket: "my-bucket",
    Key: key,
    ContentType: contentType,
    ContentLength: expectedSize, // Must match exactly
  }),
  { expiresIn: 3600 }
);
```

### Use unique keys

```typescript
const key = `uploads/${userId}/${crypto.randomUUID()}/${filename}`;
```

### Short expiration for sensitive data

```typescript
const downloadUrl = await getSignedUrl(
  S3,
  new GetObjectCommand({ Bucket: "my-bucket", Key: key }),
  { expiresIn: 60 } // 1 minute
);
```

---

## Common Issues

### CORS errors

- Ensure AllowedOrigins includes your domain
- Include all required headers in AllowedHeaders
- Check browser DevTools for specific CORS error

### 403 Forbidden

- Check API token permissions
- Verify bucket name
- Ensure token is not expired

### Custom domain not working

Presigned URLs only work with S3 endpoint:

```
https://<ACCOUNT_ID>.r2.cloudflarestorage.com
```

Not with custom domains or r2.dev.
