# Variants

Pre-defined transformation presets for stored images.

## What Are Variants?

Variants are named transformation configurations applied to images stored in Cloudflare Images. Instead of specifying dimensions in URLs, you reference a variant name.

## Delivery URL

```
https://imagedelivery.net/<ACCOUNT_HASH>/<IMAGE_ID>/<VARIANT_NAME>
```

Example:

```
https://imagedelivery.net/ZWd9g1K7eljCn_KDTu_MWA/083eb7b2-5392-4565-b69e-aff66acddd00/thumbnail
```

## Default Variant

Every account has a `public` variant by default, serving the original image.

## Limits

- Maximum 100 variants per account
- Only original uploaded images count toward storage (not variants)

## Create Variant (Dashboard)

1. Dashboard → Images → Hosted Images → Delivery tab
2. Click "Create variant"
3. Configure:
   - Name
   - Width/Height
   - Fit mode
   - Metadata handling
   - Blur (optional)

## Create Variant (API)

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/variants" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{
    "id": "thumbnail",
    "options": {
      "fit": "scale-down",
      "width": 200,
      "height": 200,
      "metadata": "none"
    },
    "neverRequireSignedURLs": false
  }'
```

## Variant Options

| Option                   | Description                                   |
| ------------------------ | --------------------------------------------- |
| `fit`                    | Resize mode: scale-down, contain, cover, etc. |
| `width`                  | Max width in pixels                           |
| `height`                 | Max height in pixels                          |
| `metadata`               | none, keep, copyright                         |
| `blur`                   | Blur radius 1-250                             |
| `neverRequireSignedURLs` | Always allow public access                    |
| `browser_ttl`            | Cache time in seconds                         |

## Flexible Variants

Dynamic resizing without pre-defined variants.

### Enable

Dashboard → Images → Hosted Images → Delivery → Enable "Flexible variants"

Or via API:

```bash
curl --request PATCH \
  "https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/config" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{"flexible_variants": true}'
```

### Usage

```
https://imagedelivery.net/<ACCOUNT_HASH>/<IMAGE_ID>/w=400,h=300,fit=cover
```

### Flexible Variant Parameters

Same as transformation options:

```
w=400          # width
h=300          # height
fit=cover      # fit mode
blur=20        # blur
sharpen=1      # sharpen
```

### Limitations

- **Cannot use with signed URLs** (`requireSignedURLs=true`)
- SVG parameters are ignored (SVG passthrough only)

## Delete Variant

### Dashboard

Hosted Images → Delivery → Find variant → Delete

### API

```bash
curl --request DELETE \
  "https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/variants/{variant_name}" \
  --header "Authorization: Bearer <API_TOKEN>"
```

**Note:** The `public` variant cannot be deleted.

## Browser TTL

Control how long images stay in browser cache.

### Default

Browser TTL is determined by Cloudflare's edge cache settings.

### Per-Variant TTL

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/variants" \
  --header "Authorization: Bearer <API_TOKEN>" \
  --data '{
    "id": "avatar",
    "options": {
      "width": 100,
      "browser_ttl": 86400
    }
  }'
```

Results in: `Cache-Control: public, max-age=86400, stale-while-revalidate=7200`

**Note:** Private images (signed URLs) ignore TTL settings.

## Public Access Override

Set a variant to always be publicly accessible, even for private images:

```json
{
  "id": "thumbnail",
  "options": { "width": 100 },
  "neverRequireSignedURLs": true
}
```

## Blur Variant

Create blurred versions for preview/placeholder:

1. Create variant with blur setting
2. Use for LQIP (Low Quality Image Placeholder)

```
/thumbnail-blur  → blur=50, width=32, quality=30
```

## Serving from Custom Domain

```
https://example.com/cdn-cgi/imagedelivery/<ACCOUNT_HASH>/<IMAGE_ID>/<VARIANT_NAME>
```

## SVG with Variants

SVGs are not resized but can use variants as placeholders:

```
https://imagedelivery.net/<ACCOUNT_HASH>/<SVG_ID>/public
```

Use named variants (not flexible variants) with SVG.
