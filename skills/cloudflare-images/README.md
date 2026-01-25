# Cloudflare Images Skill

Agent Skill for working with Cloudflare Images — an end-to-end solution for storing, transforming, and delivering optimized images at scale.

## Overview

This skill provides guidance for:

- **Image Storage**: Upload images to Cloudflare's global network
- **Transformations**: Resize, crop, format convert on-the-fly
- **Variants**: Pre-defined transformation presets
- **Workers Integration**: Images binding for programmatic control
- **Polish**: Automatic origin image optimization
- **Security**: Signed URLs for private images

## Skill Structure

```
cloudflare-images/
├── SKILL.md              # Main instructions and quick reference
├── README.md             # This file
└── references/
    ├── upload.md         # Upload methods (API, Worker, Direct Upload)
    ├── transformations.md # URL and Worker transformation options
    ├── variants.md       # Named variants and flexible variants
    ├── binding.md        # Workers Images binding API
    ├── polish.md         # Automatic image optimization
    ├── security.md       # Signed URLs and access control
    └── pricing.md        # Billing model and cost optimization
```

## Key Concepts

### Two Usage Modes

1. **Storage Mode**: Upload images to Cloudflare, deliver via variants
2. **Transform Mode**: Optimize images from any origin (R2, S3, etc.)

### Transformation URL Format

```
https://example.com/cdn-cgi/image/width=400,format=auto/path/to/image.jpg
```

### Image Delivery URL

```
https://imagedelivery.net/<ACCOUNT_HASH>/<IMAGE_ID>/<VARIANT_NAME>
```

## Common Use Cases

- Responsive images with multiple sizes
- Format optimization (WebP, AVIF)
- Watermarking via Workers binding
- User-uploaded content optimization
- CDN-accelerated image delivery

## Related Skills

- `cloudflare-workers` — Serverless compute platform
- `cloudflare-pages` — Full-stack application hosting
- `cloudflare-r2` — Object storage (planned)

## Resources

- [Cloudflare Images Documentation](https://developers.cloudflare.com/images/)
- [Images API Reference](https://developers.cloudflare.com/api/resources/images/)
- [Pricing Calculator](https://dash.cloudflare.com/)
