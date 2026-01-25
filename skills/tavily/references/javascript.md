# Tavily JavaScript SDK Reference

## Installation

```bash
npm i @tavily/core
# or
yarn add @tavily/core
# or
pnpm add @tavily/core
```

## Client Setup

```javascript
import { tavily } from "@tavily/core";

// From environment variable TAVILY_API_KEY
const client = tavily();

// Explicit key
const client = tavily({ apiKey: "tvly-YOUR_API_KEY" });

// With proxy (axios proxy config)
const client = tavily({
  apiKey: "tvly-YOUR_API_KEY",
  httpClient: {
    proxy: {
      host: "proxy.example.com",
      port: 8080,
    },
  },
});
```

---

## search()

```javascript
const response = await client.search(query, {
  // Search behavior
  searchDepth: "basic", // "basic"|"advanced"|"fast"|"ultra-fast"
  topic: "general", // "general"|"news"|"finance"
  autoParameters: false, // Auto-configure based on query

  // Time filtering
  timeRange: "day", // "day"|"week"|"month"|"year"
  startDate: "2024-01-01", // YYYY-MM-DD format
  endDate: "2024-12-31", // YYYY-MM-DD format

  // Results configuration
  maxResults: 5, // 0-20
  chunksPerSource: 3, // 1-3, requires searchDepth="advanced"

  // Content options
  includeAnswer: false, // true|"basic"|"advanced"
  includeRawContent: false, // true|"markdown"|"text"
  includeImages: false,
  includeImageDescriptions: false,
  includeFavicon: false,

  // Domain filtering
  includeDomains: ["example.com"], // Max 300
  excludeDomains: ["spam.com"], // Max 150

  // Regional
  country: "US", // Boost results from country

  // Usage tracking
  includeUsage: false,
});
```

### Response Structure

```typescript
{
  query: string;
  answer?: string;
  results: Array<{
    title: string;
    url: string;
    content: string;
    score: number;
    rawContent?: string;
    publishedDate?: string;
    favicon?: string;
  }>;
  images?: Array<{url: string; description?: string}>;
  responseTime: number;
  usage?: {credits: number};
  requestId: string;
}
```

---

## extract()

```javascript
const response = await client.extract(urls, {
  // urls: string or string[] (max 20)

  // Extraction options
  extractDepth: "basic", // "basic"|"advanced"
  format: "markdown", // "markdown"|"text"
  includeImages: false,
  includeFavicon: false,

  // Relevance filtering
  query: "specific question", // Rerank chunks by relevance
  chunksPerSource: 3, // 1-5, requires query

  // Timing
  timeout: 30, // 1-60 seconds

  includeUsage: false,
});
```

### Response Structure

```typescript
{
  results: Array<{
    url: string;
    rawContent: string;
    images?: string[];
    favicon?: string;
  }>;
  failedResults: Array<{
    url: string;
    error: string;
  }>;
  responseTime: number;
  usage?: {credits: number};
  requestId: string;
}
```

---

## crawl()

```javascript
const response = await client.crawl(url, {
  // Scope control
  maxDepth: 1, // 1-5 levels
  maxBreadth: 20, // Links per page
  limit: 50, // Total pages

  // AI guidance (doubles credit cost)
  instructions: "Focus on API docs",

  // Path filtering (regex patterns)
  selectPaths: ["/docs/.*"], // Only crawl matching paths
  excludePaths: ["/private/.*"], // Skip matching paths

  // Domain filtering (regex patterns)
  selectDomains: ["example\\.com"],
  excludeDomains: ["ads\\..*"],
  allowExternal: true, // Follow external links

  // Extraction options
  extractDepth: "basic", // "basic"|"advanced"
  format: "markdown", // "markdown"|"text"
  includeImages: false,
  includeFavicon: false,
  chunksPerSource: 3, // 1-5, with instructions

  // Timing
  timeout: 150, // 10-150 seconds

  includeUsage: false,
});
```

### Response Structure

```typescript
{
  baseUrl: string;
  results: Array<{
    url: string;
    rawContent: string;
    images?: string[];
    favicon?: string;
  }>;
  responseTime: number;
  usage?: {credits: number};
  requestId: string;
}
```

---

## map()

```javascript
const response = await client.map(url, {
  // Scope control
  maxDepth: 1, // 1-5 levels
  maxBreadth: 20, // Links per page
  limit: 50, // Total URLs

  // AI guidance (doubles credit cost)
  instructions: "Find all API endpoints",

  // Path filtering (regex patterns)
  selectPaths: ["/api/.*"],
  excludePaths: ["/internal/.*"],

  // Domain filtering (regex patterns)
  selectDomains: ["api\\.example\\.com"],
  excludeDomains: ["beta\\..*"],
  allowExternal: true,

  // Timing
  timeout: 150, // 10-150 seconds

  includeUsage: false,
});
```

### Response Structure

```typescript
{
  baseUrl: string;
  results: string[];                 // List of URLs (no content)
  responseTime: number;
  usage?: {credits: number};
  requestId: string;
}
```

---

## TypeScript Types

```typescript
import type { TavilySearchOptions, TavilySearchResponse, TavilyExtractOptions, TavilyExtractResponse, TavilyCrawlOptions, TavilyCrawlResponse, TavilyMapOptions, TavilyMapResponse } from "@tavily/core";
```

---

## Error Handling

```javascript
import { tavily } from "@tavily/core";

const client = tavily();

try {
  const response = await client.search("query");
} catch (error) {
  if (error.status === 401) {
    console.error("Invalid API key");
  } else if (error.status === 429) {
    console.error("Rate limit or credits exceeded");
  } else {
    console.error(`Request failed: ${error.message}`);
  }
}
```

---

## Best Practices

```javascript
// ✅ Parallel searches with Promise.all
const queries = ["AI", "ML", "LLM"];
const results = await Promise.all(queries.map((q) => client.search(q)));

// ✅ Domain filtering for quality
const response = await client.search("python tutorials", {
  includeDomains: ["python.org", "realpython.com"],
  excludeDomains: ["medium.com"],
});

// ✅ Auto-configure for unknown queries
const response = await client.search(userInput, {
  autoParameters: true,
});

// ✅ Get structured answers for RAG
const response = await client.search("What is quantum computing?", {
  includeAnswer: "advanced",
  includeRawContent: "markdown",
});

// ✅ Crawl with path filtering
const docs = await client.crawl("https://docs.example.com", {
  selectPaths: ["/api/.*", "/guides/.*"],
  excludePaths: ["/blog/.*"],
  maxDepth: 2,
});
```

---

## Parameter Naming Convention

JavaScript SDK uses **camelCase** (Python SDK uses **snake_case**):

| Python              | JavaScript        |
| ------------------- | ----------------- |
| search_depth        | searchDepth       |
| max_results         | maxResults        |
| include_answer      | includeAnswer     |
| include_raw_content | includeRawContent |
| include_images      | includeImages     |
| include_domains     | includeDomains    |
| exclude_domains     | excludeDomains    |
| time_range          | timeRange         |
| start_date          | startDate         |
| end_date            | endDate           |
| chunks_per_source   | chunksPerSource   |
| auto_parameters     | autoParameters    |
| include_favicon     | includeFavicon    |
| include_usage       | includeUsage      |
| extract_depth       | extractDepth      |
| max_depth           | maxDepth          |
| max_breadth         | maxBreadth        |
| select_paths        | selectPaths       |
| exclude_paths       | excludePaths      |
| select_domains      | selectDomains     |
| exclude_domains     | excludeDomains    |
| allow_external      | allowExternal     |
