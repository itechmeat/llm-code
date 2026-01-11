# Perplexity Media Handling

Guide to images, videos, and file attachments.

## Returning Images

### Enable Image Returns

```python
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "Mount Everest images"}],
    return_images=True
)
```

### Image Domain Filtering

```python
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "historical images"}],
    return_images=True,
    image_domain_filter=["wikimedia.org"],  # Allow only
    # OR
    image_domain_filter=["-gettyimages.com", "-shutterstock.com"]  # Exclude
)
```

### Image Format Filtering

```python
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "funny cat gif"}],
    return_images=True,
    image_format_filter=["gif"]  # gif, jpg, png, webp
)
```

### Image Limits

- Maximum 30 images per response
- Maximum 10 entries in `image_domain_filter`
- Maximum 10 entries in `image_format_filter`
- Formats: lowercase, no dot prefix (`gif` not `.gif`)

### Common Stock Photo Exclusions

```python
image_domain_filter=[
    "-gettyimages.com",
    "-shutterstock.com",
    "-istockphoto.com",
    "-pinterest.com"
]
```

## Returning Videos

### Enable Video Returns

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "2024 Olympics highlights"}],
    media_response={
        "overrides": {
            "return_videos": True
        }
    }
)
```

### Combined Media Response

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Mars rover discoveries"}],
    media_response={
        "overrides": {
            "return_videos": True,
            "return_images": True
        }
    }
)
```

### Video Response Structure

```json
{
  "videos": [
    {
      "url": "https://www.youtube.com/watch?v=...",
      "duration": null,
      "thumbnail_width": 480,
      "thumbnail_height": 360,
      "thumbnail_url": "..."
    }
  ]
}
```

## Image Attachments (Input)

Analyze images by uploading them.

### Via HTTPS URL

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://example.com/image.jpg"
                }
            }
        ]
    }]
)
```

### Via Base64

```python
import base64

with open("image.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What text is in this screenshot?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                }
            }
        ]
    }]
)
```

### Image Attachment Limits

- Maximum size: **50 MB** per image
- Supported formats: PNG, JPEG, WEBP, GIF
- **NOT supported**: `sonar-deep-research` model

### Image Pricing Formula

$$
tokens = \frac{width\ px \times height\ px}{750}
$$

Examples:

- 1024×768 image = 1,048 tokens
- 512×512 image = 349 tokens

## File Attachments

Analyze documents (PDF, DOC, DOCX, TXT, RTF).

### Via URL

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Summarize this document"},
            {
                "type": "file_url",
                "file_url": {
                    "url": "https://example.com/document.pdf"
                }
            }
        ]
    }]
)
```

### Via Base64

```python
import base64

with open("report.pdf", "rb") as f:
    file_data = base64.b64encode(f.read()).decode()

completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Extract key findings"},
            {
                "type": "file_url",
                "file_url": {
                    "url": file_data  # No prefix for base64
                },
                "file_name": "report.pdf"
            }
        ]
    }]
)
```

### File Attachment Limits

- Maximum size: **50 MB** per file
- Maximum files: **30** per request
- Maximum processing time: 60 seconds
- Supported: PDF, DOC, DOCX, TXT, RTF
- **NOT supported**: Scanned images (not OCR)

### Base64 Important Notes

- For files: provide **only** the base64 string, **no** `data:` URI prefix
- For images: use full data URI format `data:image/png;base64,...`

## Common Use Cases

### Screenshot Analysis

```python
messages=[{
    "role": "user",
    "content": [
        {"type": "text", "text": "Extract all text from this screenshot"},
        {"type": "image_url", "image_url": {"url": "..."}}
    ]
}]
```

### PDF Summarization

```python
messages=[{
    "role": "user",
    "content": [
        {"type": "text", "text": "Summarize key points and recommendations"},
        {"type": "file_url", "file_url": {"url": "https://example.com/report.pdf"}}
    ]
}]
```

### Combining Document with Web Search

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Compare this paper's findings with recent studies"},
            {"type": "file_url", "file_url": {"url": "https://example.com/paper.pdf"}}
        ]
    }]
)
```

## Error Handling

| Error              | Cause                   | Solution                                  |
| ------------------ | ----------------------- | ----------------------------------------- |
| Invalid URL        | URL not accessible      | Verify URL returns file directly          |
| File too large     | Exceeds 50MB            | Compress or split document                |
| Processing timeout | Document too complex    | Simplify question or use smaller sections |
| Invalid base64     | Malformed base64 string | Check encoding, no prefix for files       |
| Invalid format     | Unsupported file type   | Use PDF, DOC, DOCX, TXT, or RTF           |
