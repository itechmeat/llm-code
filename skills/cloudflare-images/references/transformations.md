# Image Transformations

Transform images on-the-fly using URL format or Cloudflare Workers.

## Enable Transformations

1. Dashboard → Images → Transformations
2. Select zone → Enable for zone

## URL Format

```
https://<ZONE>/cdn-cgi/image/<OPTIONS>/<SOURCE-IMAGE>
```

Example:

```html
<img src="/cdn-cgi/image/width=400,quality=80,format=auto/uploads/hero.jpg" />
```

## Core Options

### Dimensions

| Option   | Description          | Example      |
| -------- | -------------------- | ------------ |
| `width`  | Max width in pixels  | `width=800`  |
| `height` | Max height in pixels | `height=600` |
| `dpr`    | Device pixel ratio   | `dpr=2`      |

### Fit Modes

| Mode         | Behavior                                     |
| ------------ | -------------------------------------------- |
| `scale-down` | Shrink only, never enlarge (default)         |
| `contain`    | Fit within dimensions, preserve aspect ratio |
| `cover`      | Fill dimensions, crop if needed              |
| `crop`       | Like cover but never enlarges                |
| `pad`        | Fit within, fill remaining with background   |
| `squeeze`    | Exact dimensions, distorts aspect ratio      |

### Format

| Value           | Output                        |
| --------------- | ----------------------------- |
| `auto`          | WebP or AVIF based on browser |
| `avif`          | AVIF (fallback to WebP)       |
| `webp`          | WebP                          |
| `jpeg`          | Progressive JPEG              |
| `baseline-jpeg` | Baseline JPEG                 |
| `json`          | Image info in JSON            |

### Quality

```
quality=85        # 1-100, default 85
quality=low       # Perceptual: low, medium-low, medium-high, high
```

### Gravity (Crop Focus)

| Value     | Focus Point                  |
| --------- | ---------------------------- |
| `auto`    | Saliency detection (smart)   |
| `face`    | Detected faces               |
| `left`    | Left edge                    |
| `right`   | Right edge                   |
| `top`     | Top edge                     |
| `bottom`  | Bottom edge                  |
| `0.5x0.2` | Custom coordinates (0.0-1.0) |

Face gravity with zoom:

```
gravity=face,zoom=0.5
```

### Visual Adjustments

| Option       | Range          | Example          |
| ------------ | -------------- | ---------------- |
| `blur`       | 1-250          | `blur=50`        |
| `sharpen`    | 0-10           | `sharpen=1`      |
| `brightness` | factor         | `brightness=1.2` |
| `contrast`   | factor         | `contrast=1.1`   |
| `gamma`      | factor         | `gamma=0.9`      |
| `saturation` | factor (0=b&w) | `saturation=0`   |

### Rotation & Flip

```
rotate=90         # 90, 180, 270 degrees
flip=h            # horizontal
flip=v            # vertical
flip=hv           # both
```

### Trim

Remove pixels from edges:

```
trim=20;30;20;0           # top;right;bottom;left
trim.border.color=#000000 # Auto-trim by color
trim.border.tolerance=5
```

### Metadata

```
metadata=none      # Discard all (default for WebP/PNG)
metadata=copyright # Keep copyright + C2PA
metadata=keep      # Preserve most EXIF
```

## Workers Integration

### Fetch Options

```js
fetch(imageURL, {
  cf: {
    image: {
      width: 800,
      height: 600,
      fit: "cover",
      gravity: "face",
      format: "avif",
      quality: 85,
    },
  },
});
```

### Format Negotiation

```js
const accept = request.headers.get("Accept");
let format = "jpeg";

if (/image\/avif/.test(accept)) format = "avif";
else if (/image\/webp/.test(accept)) format = "webp";

return fetch(imageURL, {
  cf: { image: { format, width: 800 } },
});
```

## Transform Remote Images

Any publicly accessible URL can be transformed:

```
/cdn-cgi/image/width=400/https://external.com/photo.jpg
```

### Allowed Origins

Configure in Dashboard → Images → Transformations → Sources:

- **Allowed origins**: Whitelist specific domains
- **Any origin**: Allow any URL (less secure)

## Responsive Images

### srcset Pattern

```html
<img srcset="/cdn-cgi/image/width=320,format=auto/photo.jpg 320w, /cdn-cgi/image/width=640,format=auto/photo.jpg 640w, /cdn-cgi/image/width=1280,format=auto/photo.jpg 1280w" sizes="(max-width: 640px) 100vw, 640px" src="/cdn-cgi/image/width=640,format=auto/photo.jpg" />
```

### width=auto

Automatically serves optimal size based on device:

```
/cdn-cgi/image/width=auto/photo.jpg
```

Serves one of: 320, 768, 960, 1200 pixels based on client hints.

Enable client hints:

```html
<meta http-equiv="Delegate-CH" content="sec-ch-dpr https://example.com; sec-ch-viewport-width https://example.com" />
```

## Error Handling

### onerror=redirect

Falls back to original image on transformation error:

```
/cdn-cgi/image/width=400,onerror=redirect/photo.jpg
```

**Note:** Only works with URL transformations, not Workers.

## Caching

- Transformed images cached for 1 hour minimum
- Source image cached per normal HTTP rules
- Purge source URL to clear all variants
- `/cdn-cgi/` URLs cannot be purged directly

## Limits

| Constraint       | Limit                         |
| ---------------- | ----------------------------- |
| Max file size    | 70 MB                         |
| Max dimension    | 12,000 pixels                 |
| Max area         | 100 megapixels                |
| AVIF output      | 1,200 px (soft), 1,600 (hard) |
| Animation frames | 50 megapixels total           |

## SVG Handling

- SVGs are sanitized but **not resized** (inherently scalable)
- All transform parameters ignored for SVG
- Sanitization removes scripts, external references
