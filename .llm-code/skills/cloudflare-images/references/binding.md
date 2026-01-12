# Images Binding

Transform images directly in Workers using the Images binding.

## Setup

### wrangler.toml

```toml
[images]
binding = "IMAGES"
```

### wrangler.jsonc

```jsonc
{
  "images": {
    "binding": "IMAGES"
  }
}
```

## Requirements

- Images Paid plan required for binding
- Binding enabled per-Worker

## Methods

### `.input(stream)`

Start image processing from a ReadableStream:

```ts
const response = await env.IMAGES.input(imageStream);
```

### `.transform(options)`

Apply transformation options (chainable):

```ts
await env.IMAGES.input(stream).transform({ width: 800 }).transform({ rotate: 90 }).transform({ blur: 20 });
```

### `.draw(image, options)`

Overlay one image on another:

```ts
await env.IMAGES.input(baseImage).draw(overlayStream, { bottom: 10, right: 10, opacity: 0.8 });
```

### `.output(options)`

Specify output format and get response:

```ts
const result = await env.IMAGES.input(stream).output({ format: "image/avif", quality: 85 });

return result.response();
```

### `.info(stream)`

Get image metadata without transformation:

```ts
const info = await env.IMAGES.info(stream);
// { format: "image/jpeg", fileSize: 123456, width: 1920, height: 1080 }
```

## Complete Example

```ts
interface Env {
  IMAGES: ImagesBinding;
  R2: R2Bucket;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const imageKey = url.pathname.slice(1);

    // Get image from R2
    const object = await env.R2.get(imageKey);
    if (!object) return new Response("Not found", { status: 404 });

    // Transform
    const response = (await env.IMAGES.input(object.body).transform({ width: 800, fit: "contain" }).output({ format: "image/webp" })).response();

    return response;
  },
};
```

## Watermark Example

```ts
async fetch(request: Request, env: Env): Promise<Response> {
  // Fetch images
  const [image, watermark] = await Promise.all([
    env.R2.get("photo.jpg"),
    env.ASSETS.fetch(new URL("/watermark.png", request.url))
  ]);

  if (!image || !watermark.ok) {
    return new Response("Image not found", { status: 404 });
  }

  const response = (
    await env.IMAGES.input(image.body)
      .draw(
        env.IMAGES.input(watermark.body)
          .transform({ width: 100, height: 100 }),
        { bottom: 10, right: 10, opacity: 0.75 }
      )
      .output({ format: "image/avif" })
  ).response();

  return response;
}
```

## Draw Options

| Option    | Type    | Description                         |
| --------- | ------- | ----------------------------------- |
| `opacity` | number  | 0 (transparent) to 1 (opaque)       |
| `repeat`  | boolean | Tile the overlay                    |
| `top`     | number  | Distance from top edge in pixels    |
| `bottom`  | number  | Distance from bottom edge in pixels |
| `left`    | number  | Distance from left edge in pixels   |
| `right`   | number  | Distance from right edge in pixels  |

## Output Formats

| Format | MIME Type    |
| ------ | ------------ |
| AVIF   | `image/avif` |
| WebP   | `image/webp` |
| JPEG   | `image/jpeg` |
| PNG    | `image/png`  |
| GIF    | `image/gif`  |

## Transform Options

All standard transformation options available:

```ts
.transform({
  width: 800,
  height: 600,
  fit: "cover",
  gravity: "face",
  blur: 20,
  sharpen: 1,
  rotate: 90,
  brightness: 1.1,
  contrast: 1.2
})
```

## Caching

Images binding responses are **not automatically cached**.

Implement caching manually:

```ts
const cache = await caches.open("images");
const cacheKey = new URL(request.url);

// Check cache
const cached = await cache.match(cacheKey);
if (cached) return cached;

// Transform
const response = (await env.IMAGES.input(stream).transform({ width: 800 }).output({ format: "image/avif" })).response();

// Cache the response
const clonedResponse = response.clone();
ctx.waitUntil(cache.put(cacheKey, clonedResponse));

return response;
```

## Local Development

### High-Fidelity (Online)

```bash
npx wrangler dev
```

Full feature support, connects to Cloudflare.

### Low-Fidelity (Offline)

```bash
npx wrangler dev --experimental-images-local-mode
```

Limited features: `width`, `height`, `rotate`, `format` only.

## Error Handling

```ts
try {
  const response = await env.IMAGES.input(stream).transform({ width: 800 }).output({ format: "image/avif" });
  return response.response();
} catch (error) {
  console.error("Image processing failed:", error);
  // Fall back to original or error response
  return new Response("Image processing failed", { status: 500 });
}
```

## Best Practices

1. **Stream management**: Request body can only be read once. Clone if needed.
2. **Memory limits**: Workers have 128 MB limit. Avoid loading large images multiple times.
3. **Use Streams**: For large files, use ReadableStream instead of ArrayBuffer.
4. **Cache transformed images**: Binding responses aren't cached by default.
5. **Handle errors gracefully**: Fall back to original image on failure.
