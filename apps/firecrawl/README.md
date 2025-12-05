# Firecrawl

> Web scraping and content extraction for JS-heavy sites

## Skills Provided

- **extract** (action) — Fallback extraction when Exa fails or for JS-heavy sites

## Auth

API key in `.env` as `FIRECRAWL_API_KEY`

**Cost:** ~$0.009/page (use as fallback to Exa)

---

## When to Use Firecrawl

Use Firecrawl when:
- Exa returns `CRAWL_UNKNOWN_ERROR`
- JS-heavy site (Notion, React, Vue, Angular, SPAs)
- Exa returned limited/truncated content
- Dynamic content requiring browser rendering

**Always try Exa first** — it's cheaper. See `apps/exa/README.md`.

---

## Extract Content

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": ["markdown"]
  }' | jq .
```

**Get just the markdown:**
```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": ["markdown"]
  }' | jq -r '.data.markdown'
```

**With options:**
```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": ["markdown", "html"],
    "onlyMainContent": true,
    "excludeTags": ["nav", "footer", "aside"]
  }' | jq .
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `url` | URL to scrape | required |
| `formats` | `markdown`, `html` | `["markdown"]` |
| `onlyMainContent` | Skip headers/footers | `true` |
| `includeTags` | Only include these HTML tags | all |
| `excludeTags` | Exclude these HTML tags | none |

**Note:** Firecrawl always fetches fresh content (no caching).

---

## Search (Fallback)

When Exa credits are exhausted (402), use Firecrawl search:

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.firecrawl.dev/v1/search" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search query",
    "limit": 10
  }' | jq .
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query | required |
| `limit` | Number of results | 10 |
| `lang` | Language code (e.g., "en") | none |
| `country` | Country code (e.g., "us") | none |

**Cost:** ~$0.01/search

---

## Crawl Multiple Pages

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/crawl" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "limit": 10,
    "formats": ["markdown"]
  }' | jq .
```

---

## Error Handling

**Common errors:**
- `401 Unauthorized` - Check `FIRECRAWL_API_KEY`
- `402 Payment Required` - Credits exhausted
- `429 Too Many Requests` - Rate limited
- Timeout errors - Very large/slow pages

**⚠️ Always surface API errors to the user.** Don't silently fail.
