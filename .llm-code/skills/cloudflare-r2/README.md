# Cloudflare R2 Skill

This skill provides guidance for working with Cloudflare R2 object storage.

## Topics Covered

- Bucket creation and management
- Workers Binding API (R2Bucket)
- S3 API compatibility
- Presigned URLs for direct access
- Multipart uploads for large objects
- CORS configuration
- Lifecycle policies (expiration, transitions)
- Storage classes (Standard, Infrequent Access)
- Event notifications with Queues
- Public buckets and custom domains
- Data migration (Super Slurper, Sippy)
- Pricing and limits

## When to Use

- Storing files, media, backups
- Serving static assets from Workers/Pages
- Migrating from S3 or other object storage
- Building file upload/download APIs
- Processing files with event-driven workflows

## Related Skills

- [cloudflare-workers](../cloudflare-workers/SKILL.md) — Worker development
- [cloudflare-pages](../cloudflare-pages/SKILL.md) — Static sites with R2
- [cloudflare-queues](../cloudflare-queues/SKILL.md) — Event consumers
- [cloudflare-d1](../cloudflare-d1/SKILL.md) — SQL database
