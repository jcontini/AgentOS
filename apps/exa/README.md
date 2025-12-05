# Exa

> Semantic web search and content extraction

## Skills Provided

- **search** (action) — Semantic web search, discover URLs
- **extract** (action) — Extract content from URLs (primary, with firecrawl fallback)

## Auth

API key in `.env` as `EXA_API_KEY`

**Cost:** ~$5/1k searches | ~$0.001/page extraction

---

## Search

Exa excels at neural/semantic search, finding niche content that traditional search engines miss.

### Search with content extraction (most common)

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search query",
    "num_results": 5,
    "type": "auto",
    "contents": {
      "text": true,
      "livecrawl": "always"
    }
  }' | jq .
```

### Search only (just URLs)

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search query",
    "num_results": 10,
    "type": "auto"
  }' | jq .
```

**⚠️ IMPORTANT:** Always use `contents.livecrawl: "always"` when extracting content for fresh results.

### Search Types

- `"auto"` - Let Exa choose (recommended)
- `"neural"` - Semantic/meaning-based (best for niche content)
- `"keyword"` - Traditional keyword matching

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query (natural language works well) | required |
| `num_results` | Number of results (1-100) | 10 |
| `type` | `auto`, `neural`, `keyword` | `auto` |
| `contents` | Include content extraction | omit for URLs only |
| `contents.livecrawl` | `"always"`, `"preferred"`, `"fallback"`, `"never"` | `"never"` (⚠️ use `"always"`) |
| `includeDomains` | Limit to specific domains | none |
| `excludeDomains` | Exclude specific domains | none |

---

## Extract

Extract content from known URLs.

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.exa.ai/contents" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com"],
    "text": true,
    "livecrawl": "always"
  }' | jq .
```

**Multiple URLs:**
```bash
curl -s -X POST "https://api.exa.ai/contents" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://site1.com", "https://site2.com"],
    "text": true,
    "livecrawl": "always"
  }' | jq .
```

| Parameter | Description |
|-----------|-------------|
| `urls` | Array of URLs to extract |
| `text` | Return text content (boolean) |
| `livecrawl` | `always` (recommended), `fallback`, `never` |

---

## Error Handling

**Common errors:**
- `401 Unauthorized` - Invalid API key
- `402 Payment Required` - Credits exhausted → **Use firecrawl fallback**
- `429 Too Many Requests` - Rate limited
- `CRAWL_UNKNOWN_ERROR` - Site blocked/JS-heavy → **Use firecrawl**

---

## When to Use Exa vs Firecrawl

| Scenario | Use |
|----------|-----|
| Most searches/extractions | Exa (cheaper, faster) |
| Exa returns error | Firecrawl |
| JS-heavy site (Notion, React) | Firecrawl |
| Need more content | Firecrawl |

See `apps/firecrawl/README.md` for fallback usage.
