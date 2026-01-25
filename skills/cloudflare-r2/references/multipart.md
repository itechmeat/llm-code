# R2 Multipart Uploads

For large files (>100 MB recommended), use multipart upload.

## Overview

- Split file into parts (5 MiB – 5 GiB each)
- Upload parts in parallel
- Complete or abort upload
- Maximum object size: ~5 TiB
- Maximum parts: 10,000

---

## Workers API

### Create Multipart Upload

```typescript
const mpu = await env.MY_BUCKET.createMultipartUpload("large-file.zip", {
  httpMetadata: {
    contentType: "application/zip",
  },
  customMetadata: {
    uploadedBy: "user-123",
  },
});

// Save for resuming
const uploadId = mpu.uploadId;
const key = mpu.key;
```

### Upload Parts

```typescript
// Part numbers start at 1
// Minimum part size: 5 MiB (except last part)
const part1 = await mpu.uploadPart(1, chunk1);
const part2 = await mpu.uploadPart(2, chunk2);
const part3 = await mpu.uploadPart(3, chunk3);

// Each part returns { partNumber, etag }
```

### Complete Upload

```typescript
const uploadedParts = [part1, part2, part3];
const object = await mpu.complete(uploadedParts);
// object: R2Object
```

### Abort Upload

```typescript
await mpu.abort();
```

### Resume Upload

```typescript
const mpu = env.MY_BUCKET.resumeMultipartUpload(key, uploadId);
const nextPart = await mpu.uploadPart(4, chunk4);
```

---

## Chunked Upload API (Worker Routes)

```typescript
export interface Env {
  MY_BUCKET: R2Bucket;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const key = url.searchParams.get("key");

    // Create multipart upload
    if (url.pathname === "/mpu/create" && request.method === "POST") {
      const mpu = await env.MY_BUCKET.createMultipartUpload(key!);
      return Response.json({
        key: mpu.key,
        uploadId: mpu.uploadId,
      });
    }

    // Upload part
    if (url.pathname === "/mpu/upload-part" && request.method === "PUT") {
      const uploadId = url.searchParams.get("uploadId");
      const partNumber = parseInt(url.searchParams.get("partNumber")!);

      const mpu = env.MY_BUCKET.resumeMultipartUpload(key!, uploadId!);
      const part = await mpu.uploadPart(partNumber, request.body!);

      return Response.json(part);
    }

    // Complete upload
    if (url.pathname === "/mpu/complete" && request.method === "POST") {
      const uploadId = url.searchParams.get("uploadId");
      const { parts } = await request.json();

      const mpu = env.MY_BUCKET.resumeMultipartUpload(key!, uploadId!);
      const object = await mpu.complete(parts);

      return Response.json({
        key: object.key,
        size: object.size,
        etag: object.etag,
      });
    }

    // Abort upload
    if (url.pathname === "/mpu/abort" && request.method === "DELETE") {
      const uploadId = url.searchParams.get("uploadId");

      const mpu = env.MY_BUCKET.resumeMultipartUpload(key!, uploadId!);
      await mpu.abort();

      return new Response(null, { status: 204 });
    }

    return new Response("Not Found", { status: 404 });
  },
};
```

---

## Browser Client

```typescript
const CHUNK_SIZE = 10 * 1024 * 1024; // 10 MiB

async function uploadLargeFile(file: File, key: string): Promise<void> {
  // 1. Create multipart upload
  const createRes = await fetch(`/mpu/create?key=${encodeURIComponent(key)}`, {
    method: "POST",
  });
  const { uploadId } = await createRes.json();

  // 2. Upload parts
  const parts: Array<{ partNumber: number; etag: string }> = [];
  const totalParts = Math.ceil(file.size / CHUNK_SIZE);

  for (let i = 0; i < totalParts; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);
    const partNumber = i + 1;

    const partRes = await fetch(`/mpu/upload-part?key=${encodeURIComponent(key)}&uploadId=${uploadId}&partNumber=${partNumber}`, {
      method: "PUT",
      body: chunk,
    });

    const part = await partRes.json();
    parts.push(part);

    console.log(`Uploaded part ${partNumber}/${totalParts}`);
  }

  // 3. Complete upload
  await fetch(`/mpu/complete?key=${encodeURIComponent(key)}&uploadId=${uploadId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ parts }),
  });

  console.log("Upload complete!");
}
```

---

## Parallel Uploads

```typescript
const CHUNK_SIZE = 10 * 1024 * 1024;
const CONCURRENCY = 3;

async function uploadParallel(file: File, key: string): Promise<void> {
  const { uploadId } = await createMultipartUpload(key);

  const chunks: Array<{ partNumber: number; start: number; end: number }> = [];
  const totalParts = Math.ceil(file.size / CHUNK_SIZE);

  for (let i = 0; i < totalParts; i++) {
    chunks.push({
      partNumber: i + 1,
      start: i * CHUNK_SIZE,
      end: Math.min((i + 1) * CHUNK_SIZE, file.size),
    });
  }

  // Upload in parallel batches
  const parts: Array<{ partNumber: number; etag: string }> = [];

  for (let i = 0; i < chunks.length; i += CONCURRENCY) {
    const batch = chunks.slice(i, i + CONCURRENCY);
    const results = await Promise.all(
      batch.map(async (chunk) => {
        const blob = file.slice(chunk.start, chunk.end);
        return uploadPart(key, uploadId, chunk.partNumber, blob);
      })
    );
    parts.push(...results);
  }

  // Sort by part number before completing
  parts.sort((a, b) => a.partNumber - b.partNumber);

  await completeMultipartUpload(key, uploadId, parts);
}
```

---

## S3 API Multipart

```typescript
import { S3Client, CreateMultipartUploadCommand, UploadPartCommand, CompleteMultipartUploadCommand, AbortMultipartUploadCommand } from "@aws-sdk/client-s3";

const S3 = new S3Client({
  region: "auto",
  endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: { accessKeyId: ACCESS_KEY_ID, secretAccessKey: SECRET_ACCESS_KEY },
});

// Create
const { UploadId } = await S3.send(
  new CreateMultipartUploadCommand({
    Bucket: "my-bucket",
    Key: "large-file.zip",
  })
);

// Upload parts
const part1 = await S3.send(
  new UploadPartCommand({
    Bucket: "my-bucket",
    Key: "large-file.zip",
    UploadId,
    PartNumber: 1,
    Body: chunk1,
  })
);

// Complete
await S3.send(
  new CompleteMultipartUploadCommand({
    Bucket: "my-bucket",
    Key: "large-file.zip",
    UploadId,
    MultipartUpload: {
      Parts: [{ PartNumber: 1, ETag: part1.ETag }],
    },
  })
);
```

---

## Limits

| Parameter                | Value            |
| ------------------------ | ---------------- |
| Minimum part size        | 5 MiB            |
| Maximum part size        | 5 GiB            |
| Maximum parts            | 10,000           |
| Maximum object size      | ~5 TiB           |
| Incomplete upload expiry | 7 days (default) |

---

## Lifecycle for Incomplete Uploads

```bash
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "abort-incomplete" \
  --abort-incomplete-days 1
```

Aborts incomplete multipart uploads after 1 day.
