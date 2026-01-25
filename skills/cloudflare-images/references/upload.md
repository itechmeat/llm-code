# Upload Methods

Methods for uploading images to Cloudflare Images storage.

## Upload via API

```bash
curl --request POST \
  https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1 \
  --header "Authorization: Bearer <API_TOKEN>" \
  --header "Content-Type: multipart/form-data" \
  --form file=@./image.jpg \
  --form 'metadata={"key":"value"}' \
  --form 'requireSignedURLs=false'
```

## Upload via URL

```bash
curl --request POST \
  https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1 \
  --header "Authorization: Bearer <API_TOKEN>" \
  --form 'url=https://example.com/image.jpg' \
  --form 'metadata={"key":"value"}'
```

**Note:** `--form 'file=...'` and `--form 'url=...'` are mutually exclusive.

## Direct Creator Upload

Allows end users to upload images without exposing your API credentials.

### 1. Request One-Time Upload URL

```bash
curl --request POST \
  https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v2/direct_upload \
  --header "Authorization: Bearer <API_TOKEN>" \
  --form 'requireSignedURLs=true' \
  --form 'metadata={"user":"123"}'
```

### 2. Response

```json
{
  "result": {
    "id": "2cdc28f0-017a-49c4-9ed7-87056c83901",
    "uploadURL": "https://upload.imagedelivery.net/..."
  }
}
```

### 3. Client-Side Upload

```html
<form action="INSERT_UPLOAD_URL_HERE" method="post" enctype="multipart/form-data">
  <input type="file" name="file" />
  <button type="submit">Upload</button>
</form>
```

### Expiration

- Default: 30 minutes
- Custom: `--data '{"expiry":"2024-01-14T16:00:00Z"}'` (2 min to 6 hours)

## Upload via Worker

```ts
const API_URL = "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/images/v1";
const TOKEN = "<API_TOKEN>";

const image = await fetch("https://example.com/image.png");
const bytes = await image.bytes();

const formData = new FormData();
formData.append("file", new File([bytes], "image.png"));

const response = await fetch(API_URL, {
  method: "POST",
  headers: { Authorization: `Bearer ${TOKEN}` },
  body: formData,
});
```

## Upload AI-Generated Images

```ts
const stream = await env.AI.run("@cf/bytedance/stable-diffusion-xl-lightning", { prompt: "A beautiful sunset" });

const bytes = await(new Response(stream)).bytes();
const formData = new FormData();
formData.append("file", new File([bytes], "image.jpg"));

await fetch(API_URL, {
  method: "POST",
  headers: { Authorization: `Bearer ${TOKEN}` },
  body: formData,
});
```

## Custom ID Paths

Use custom paths instead of auto-generated UUIDs:

```bash
curl --request POST \
  https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1 \
  --header "Authorization: Bearer <API_TOKEN>" \
  --form 'url=https://example.com/image.jpg' \
  --form 'id=products/shoes/nike-air-max.jpg'
```

**Limitations:**

- Up to 1,024 characters
- UTF-8 supported
- **Cannot use with signed URL tokens** (`requireSignedURLs=true`)
- `%` chars must be encoded as `%25` in delivery URLs

## Batch API

For high-volume operations bypassing global rate limits.

### Get Batch Token

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/batch_token" \
  --header "Authorization: Bearer <API_TOKEN>"
```

### Use Batch Endpoint

```bash
# Instead of api.cloudflare.com/client/v4/accounts/...
curl "https://batch.imagedelivery.net/images/v1" \
  --header "Authorization: Bearer <BATCH_TOKEN>"
```

Rate limit: 200 requests/second per token.

## Supported Formats

| Format | Upload | Notes                                  |
| ------ | ------ | -------------------------------------- |
| PNG    | ✅     |                                        |
| JPEG   | ✅     |                                        |
| GIF    | ✅     | Including animations                   |
| WebP   | ✅     | Including animations                   |
| SVG    | ✅     | Sanitized, not resized                 |
| HEIC   | ✅     | Ingested, served as AVIF/WebP/JPEG/PNG |

## Upload Limits

| Constraint        | Limit          |
| ----------------- | -------------- |
| Max dimension     | 12,000 pixels  |
| Max area          | 100 megapixels |
| Max file size     | 10 MB          |
| Max metadata      | 1,024 bytes    |
| Animated GIF/WebP | 50 megapixels  |

## Webhooks for Uploads

Configure webhooks to receive notifications for direct creator uploads:

1. Dashboard → Notifications → Destinations → Webhooks → Create
2. Create notification for "Images" product
3. Attach webhook

Webhook payload sent on successful upload or failure.
