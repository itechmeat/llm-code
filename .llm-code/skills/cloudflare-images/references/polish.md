# Polish

Automatic image optimization for images served from your origin.

## What is Polish?

Polish automatically optimizes images from your origin server without requiring code changes. It:

- Strips unnecessary metadata
- Applies lossy or lossless compression
- Optionally converts to WebP

## Polish vs Images Transformations

| Feature        | Polish                 | Transformations          |
| -------------- | ---------------------- | ------------------------ |
| Source         | Origin server images   | Any URL or stored images |
| Configuration  | One-click enable       | URL/Worker parameters    |
| Resizing       | No                     | Yes                      |
| Format control | WebP only              | WebP, AVIF, JPEG, PNG    |
| Use case       | Automatic optimization | Dynamic transformation   |

**Do not use both simultaneously** — transformations already include compression.

## Availability

| Plan       | Polish Available |
| ---------- | ---------------- |
| Free       | ❌               |
| Pro        | ✅               |
| Business   | ✅               |
| Enterprise | ✅               |

## Enable Polish

1. Dashboard → Account Home → Select domain
2. Speed → Settings → Image Optimization
3. Under Polish, select mode:

   - **Lossy**: Greater file size savings (recommended)
   - **Lossless**: No quality loss

4. Optional: Enable **WebP** conversion

## Compression Modes

### Lossless

- No quality degradation
- Smaller file size reduction
- Re-compresses PNG/JPEG without quality loss
- Strips metadata

### Lossy

- Greater file size savings
- Imperceptible quality reduction
- Recommended for most use cases

### WebP Conversion

Additional optimization converting PNG/JPEG to WebP:

- ~26% reduction for PNG
- ~17% reduction for JPEG (varies)

**Requirements:**

- Browser must send `Accept: image/webp` header
- WebP version must be significantly smaller

**Disable origin WebP conversion** when using Polish WebP.

## Cf-Polished Header

Response header indicates Polish status:

| Value                  | Meaning                                   |
| ---------------------- | ----------------------------------------- |
| (not present)          | Polish not applied, check Cache-Control   |
| `input_too_large`      | Image too large (>4000px or >20MB)        |
| `not_compressed`       | Already optimized, no further compression |
| `webp_bigger`          | WebP was larger, serving original format  |
| `cannot_optimize`      | Corrupted or incomplete image             |
| `format_not_supported` | Unsupported format (BMP, TIFF, etc.)      |
| `vary_header_present`  | Origin sent incompatible Vary header      |

## Troubleshooting

### Polish Not Applied

1. Check `Cf-Polished` header
2. Purge cache and retry
3. Verify `Cache-Control` allows caching
4. Ensure correct `Content-Type` from origin

### WebP Not Serving

- Check browser sends `Accept: image/webp`
- WebP version may be larger (check `webp_bigger` status)
- Low-quality source JPEG may compress better than WebP
- Disable other image optimization tools at origin

### Vary Header Issues

Polish skips images with `Vary` header containing values other than `accept-encoding`.

## Best Practices

1. **Use Lossy mode** for most sites
2. **Enable WebP** for broad browser support
3. **Serve high-quality JPEG** (80-90) at origin for best WebP conversion
4. **Don't double-optimize**: Disable origin image tools when using Polish
5. **Purge cache** after changing Polish settings

## Configuration Rules

Apply Polish to specific hostnames instead of entire zone:

1. Rules → Configuration Rules
2. Create rule for specific hostnames
3. Set Polish options

## Polish with Transformations

**Warning:** Do not use both.

- Transformed images already have lossy compression
- Polish is skipped for `/cdn-cgi/image/` URLs
- Use `format=auto` in transformations for WebP/AVIF

## Metadata Handling

Polish strips metadata with some exceptions:

- Color profiles are preserved and applied
- EXIF rotation is applied
- Copyright may be preserved in Lossy mode

Metadata stripping is best-effort — caching status may affect results.

## Limits

| Constraint | Recommendation          |
| ---------- | ----------------------- |
| Image size | < 20 MB                 |
| Dimensions | < 4,000 pixels per side |
| Format     | PNG, JPEG, GIF, WebP    |
