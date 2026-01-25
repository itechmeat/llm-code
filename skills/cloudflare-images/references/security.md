# Security

Protecting images with signed URLs and access controls.

## Signed URLs

Serve private images that require token authentication.

### Enable for Image

When uploading:

```bash
curl --request POST \
  https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1 \
  --header "Authorization: Bearer <API_TOKEN>" \
  --form file=@./image.jpg \
  --form 'requireSignedURLs=true'
```

### Get Signing Key

Dashboard → Images → Hosted Images → Keys → Copy key

### Generate Signed URL (Worker)

```js
const KEY = "YOUR_KEY_FROM_IMAGES_DASHBOARD";
const EXPIRATION = 60 * 60 * 24; // 1 day

const bufferToHex = (buffer) => [...new Uint8Array(buffer)].map((x) => x.toString(16).padStart(2, "0")).join("");

async function generateSignedUrl(url) {
  const encoder = new TextEncoder();
  const secretKeyData = encoder.encode(KEY);

  const key = await crypto.subtle.importKey("raw", secretKeyData, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);

  // Add expiration
  const expiry = Math.floor(Date.now() / 1000) + EXPIRATION;
  url.searchParams.set("exp", expiry);

  // Generate signature
  const stringToSign = url.pathname + "?" + url.searchParams.toString();
  const mac = await crypto.subtle.sign("HMAC", key, encoder.encode(stringToSign));
  const sig = bufferToHex(new Uint8Array(mac).buffer);

  // Attach signature
  url.searchParams.set("sig", sig);
  return url.toString();
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const imageDeliveryURL = new URL("https://imagedelivery.net/<ACCOUNT_HASH>/<IMAGE_ID>/public");
    const signedUrl = await generateSignedUrl(imageDeliveryURL);
    return Response.redirect(signedUrl);
  },
};
```

### Signed URL Format

```
https://imagedelivery.net/<ACCOUNT_HASH>/<IMAGE_ID>/<VARIANT>?exp=1631289275&sig=abc123...
```

### Expiration

- `exp` parameter: Unix timestamp
- Minimum: immediate
- Recommended: Short-lived (hours, not days)

## Public Variant Override

Allow specific variants to be public even for private images:

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/variants" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --data '{
    "id": "thumbnail",
    "options": { "width": 100 },
    "neverRequireSignedURLs": true
  }'
```

## Limitations

### Custom IDs

**Images with custom ID paths cannot use signed URLs.**

If you need signed URLs:

- Use auto-generated image IDs
- Or use Direct Creator Upload without custom ID

### Flexible Variants

**Flexible variants cannot be used with signed URLs.**

Use named variants only for private images.

### Private Image TTL

Private images ignore custom Browser TTL settings. Cache time is based on expiration parameter (minimum 1 hour).

## Origin Access Control

### Allowed Origins

Restrict which origins can be used for transformations:

1. Dashboard → Images → Transformations → Sources
2. Add allowed domains

By default: Only same zone allowed.

### Any Origin

Allows transforming images from any URL:

- Less secure
- May allow third parties to use your transformations
- Use with caution

## Authenticated Origins

Transform images from authenticated sources (S3, Azure, GCS):

```js
const signedHeaders = generateSignedHeaders(); // Your auth logic

fetch(private_url, {
  headers: signedHeaders,
  cf: {
    image: {
      format: "auto",
      "origin-auth": "share-publicly",
    },
  },
});
```

### Supported Headers

Passed through to origin:

- `Authorization`
- `Cookie`
- `x-amz-content-sha256`
- `x-amz-date`
- `x-ms-date`
- `x-ms-version`
- `x-sa-date`

**Warning:** Images will be cached publicly. Only use when acceptable.

## Hide Original Image URL

Use Workers to hide the true image location:

```js
export default {
  async fetch(request) {
    const hiddenOrigin = "https://secret.example.com/hidden-bucket";
    const requestURL = new URL(request.url);
    const imageURL = hiddenOrigin + requestURL.pathname;

    return fetch(imageURL, {
      cf: { image: { width: 800, format: "auto" } },
    });
  },
};
```

## Prevent Access to Full-Size Images

Validate size parameters in Worker:

```js
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const width = parseInt(url.searchParams.get("width") || "800");

    if (width > 1920) {
      return new Response("Maximum width is 1920px", { status: 400 });
    }

    return fetch(imageURL, {
      cf: { image: { width, format: "auto" } },
    });
  },
};
```

## Security Products Integration

Enhance protection with:

- **Cloudflare WAF**: Block malicious requests
- **Bot Management**: Prevent automated abuse
- **Rate Limiting**: Control request volume

**Note:** WAF rules cannot directly target `/cdn-cgi/imagedelivery/` path. Use Workers as intermediary for WAF integration.

## Best Practices

1. **Use short expiration times** for signed URLs
2. **Rotate signing keys** periodically
3. **Validate size parameters** in Workers
4. **Use allowed origins** instead of any origin
5. **Hide origin URLs** with Workers
6. **Implement rate limiting** for transformation endpoints
