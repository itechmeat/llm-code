# Perplexity Search Filters

Comprehensive guide to filtering search results.

## Domain Filtering

### Basic Usage

```python
# Allowlist: include ONLY these domains
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "climate research"}],
    search_domain_filter=["nature.com", "science.org"]
)

# Denylist: EXCLUDE these domains (prefix with -)
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "tech news"}],
    search_domain_filter=["-reddit.com", "-pinterest.com"]
)
```

### Domain Filter Rules

| Rule                  | Example                | Description                       |
| --------------------- | ---------------------- | --------------------------------- |
| Allowlist (no prefix) | `["wikipedia.org"]`    | Include only these domains        |
| Denylist (- prefix)   | `["-gettyimages.com"]` | Exclude these domains             |
| Root domain matching  | `["example.com"]`      | Includes subdomains               |
| TLD filtering         | `[".gov", ".edu"]`     | Filter by domain extension        |
| Maximum entries       | 20                     | Per request limit                 |
| Mix modes?            | **FORBIDDEN**          | Cannot mix allowlist and denylist |

### Common Patterns

```python
# Academic sources only
search_domain_filter=["arxiv.org", "nature.com", "science.org", ".edu", ".gov"]

# Exclude stock photo sites (for image searches)
search_domain_filter=["-gettyimages.com", "-shutterstock.com", "-istockphoto.com"]

# News from government sources
search_domain_filter=[".gov"]
```

## Language Filtering

Filter results by ISO 639-1 language codes.

```python
# Single language
response = client.search.create(
    query="artificial intelligence",
    search_language_filter=["en"]
)

# Multiple languages (max 10)
response = client.search.create(
    query="renewable energy",
    search_language_filter=["en", "de", "fr"]
)
```

### Common Language Codes

| Language | Code | Language   | Code |
| -------- | ---- | ---------- | ---- |
| English  | en   | Portuguese | pt   |
| Spanish  | es   | Russian    | ru   |
| French   | fr   | Chinese    | zh   |
| German   | de   | Japanese   | ja   |
| Italian  | it   | Korean     | ko   |
| Arabic   | ar   | Hindi      | hi   |

### Validation

```python
import re

def validate_language_code(code: str) -> bool:
    return bool(re.match(r'^[a-z]{2}$', code))

# Must be lowercase: "en" not "EN"
# Maximum: 10 language codes per request
```

## Date/Time Filtering

### Recency Filter (Simple)

```python
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "AI news"}],
    search_recency_filter="week"  # day, week, month, year
)
```

### Date Range Filtering (Precise)

```python
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "climate research"}],
    search_after_date_filter="01/01/2024",   # Format: %m/%d/%Y
    search_before_date_filter="12/31/2024"
)
```

### Last Updated Filters

```python
# Filter by when content was last updated (not published)
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "API documentation"}],
    last_updated_after_filter="01/01/2024",
    last_updated_before_filter="06/30/2024"
)
```

## User Location Filtering

Refine results by geographic context.

### Full Location (Recommended)

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "coffee shops nearby"}],
    web_search_options={
        "user_location": {
            "country": "US",
            "region": "California",
            "city": "San Francisco",
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }
)
```

### Country Only

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "political news"}],
    web_search_options={
        "user_location": {"country": "US"}
    }
)
```

### Location Rules

- `latitude`/`longitude` REQUIRE `country` parameter
- ISO 3166-1 alpha-2 country codes (US, GB, DE)
- `city` and `region` significantly improve accuracy
- Latitude: -90 to 90; Longitude: -180 to 180

## Search Context Size

Control how much web content is retrieved.

```python
completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "simple fact question"}],
    web_search_options={"search_context_size": "low"}  # low, medium, high
)
```

| Size   | Cost    | Best For                          |
| ------ | ------- | --------------------------------- |
| low    | Lowest  | Simple facts, cost-critical       |
| medium | Default | General queries                   |
| high   | Highest | Deep research, citations critical |

## Search Modes

### Academic Mode

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "neural network research"}],
    search_mode="academic"  # Prioritizes scholarly sources
)
```

### SEC Filings Mode

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Apple 10-K filing"}],
    search_mode="sec"  # Prioritizes SEC EDGAR database
)
```

## Search Control

### Search Classifier

Let AI decide when to search:

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    enable_search_classifier=True  # Skips search for math
)
```

### Disable Search

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Write a poem"}],
    disable_search=True  # Uses only training data
)
```

## Combining Filters

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "climate policy"}],
    search_domain_filter=["nature.com", ".gov"],
    search_language_filter=["en", "de"],
    search_recency_filter="month",
    web_search_options={
        "search_context_size": "high",
        "user_location": {"country": "US"}
    }
)
```

## Filter Limits Summary

| Filter              | Limit        |
| ------------------- | ------------ |
| domain_filter       | 20 entries   |
| language_filter     | 10 languages |
| image_domain_filter | 10 entries   |
| image_format_filter | 10 entries   |
