# Pricing

Cloudflare Images billing model and cost optimization.

## Plans

### Free Plan

- 5,000 unique transformations per month
- Transformations only (no storage)
- After limit: new transforms return error 9422
- Cached transforms continue working

### Paid Plan

| Metric             | Price                            |
| ------------------ | -------------------------------- |
| Images Transformed | First 5,000 free + $0.50 / 1,000 |
| Images Stored      | $5.00 / 100,000 images / month   |
| Images Delivered   | $1.00 / 100,000 images / month   |

## Billing Concepts

### Images Transformed

Charged for **remote images** (not stored in Cloudflare Images).

- Each unique transformation = 1 billable request
- Unique = original image URL + transformation parameters
- 30-day sliding window: same transformation free for 30 days
- `format=auto` counts as 1 transform regardless of actual format served

**Example:**

```
/cdn-cgi/image/width=100/photo.jpg    → 1 transform
/cdn-cgi/image/width=200/photo.jpg    → 1 transform (different size)
/cdn-cgi/image/width=100/photo.jpg    → 0 (same, within 30 days)
```

### Images Stored

Charged for images uploaded to Cloudflare Images storage.

- Only original uploads count
- Variants don't increase storage count
- Limit: 100,000 images per $5 tier

### Images Delivered

Charged for serving images from Cloudflare Images storage.

- Every browser request = 1 delivery
- Does not apply to transformed remote images

## Cost Examples

### Example 1: Remote Image Optimization

2,000 remote images served in 5 sizes each = 10,000 unique transformations

| Metric          | Usage  | Free  | Billable | Cost  |
| --------------- | ------ | ----- | -------- | ----- |
| Transformations | 10,000 | 5,000 | 5,000    | $2.50 |

### Example 2: R2 + Image Transformations

5,000 images in R2 (5 MB avg), serving 2,000 in 5 sizes:

| Metric          | Usage  | Free  | Billable | Cost      |
| --------------- | ------ | ----- | -------- | --------- |
| R2 Storage      | 25 GB  | 10 GB | 15 GB    | $0.22     |
| R2 Class A      | 5,000  | 1M    | 0        | $0.00     |
| R2 Class B      | 10,000 | 10M   | 0        | $0.00     |
| Transformations | 10,000 | 5,000 | 5,000    | $2.50     |
| **Total**       |        |       |          | **$2.72** |

### Example 3: Stored Images

Product page with 10 images, 10,000 page views:

| Metric           | Usage   | Cost   |
| ---------------- | ------- | ------ |
| Images Stored    | 10      | ~$0.00 |
| Images Delivered | 100,000 | $1.00  |

## Optimize Costs

### Use Caching

Transformed images are cached at edge. Repeated requests don't incur new transform costs.

### Minimize Unique Transforms

```
# Fewer variants = lower cost
/cdn-cgi/image/width=320/photo.jpg   # Mobile
/cdn-cgi/image/width=800/photo.jpg   # Tablet
/cdn-cgi/image/width=1280/photo.jpg  # Desktop

# vs. many specific sizes
/cdn-cgi/image/width=347/photo.jpg   # More expensive
/cdn-cgi/image/width=412/photo.jpg
/cdn-cgi/image/width=583/photo.jpg
```

### Use R2 Instead of Images Storage

If you need storage + transforms:

- Store originals in R2 ($0.015/GB/month)
- Use transformations for delivery
- May be cheaper than Images Stored + Delivered

### Leverage 30-Day Window

Same transformation free for 30 days:

- First request: billed
- Subsequent requests (same params): free
- Different params: new billing

## Free Tier Limits

After exceeding 5,000 unique transformations:

1. Cached transforms continue working
2. New transforms return error 9422
3. Use `onerror=redirect` to fall back to original:

```html
<img src="/cdn-cgi/image/width=400,onerror=redirect/photo.jpg" />
```

## Monitor Usage

Dashboard → Images → Overview

Shows:

- Transformations used
- Storage count
- Delivery count
- Billing period usage

## Comparison: Polish vs Transformations

| Feature      | Polish           | Transformations |
| ------------ | ---------------- | --------------- |
| Availability | Pro+ plans       | All plans       |
| Billing      | Included in plan | Per-transform   |
| Resizing     | No               | Yes             |
| Format       | WebP             | WebP, AVIF      |

For simple optimization without resize: Consider Polish (included in Pro+).

## Legacy Image Resizing

If you have legacy Image Resizing subscription:

- Switch to Images subscription in dashboard
- Required for Images Binding in Workers

Error 9432 indicates legacy billing blocking binding usage.
