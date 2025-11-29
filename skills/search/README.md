# Search Skill

## Intention: Search the web / Find information / Discover URLs

Use Exa API for semantic web search. Exa excels at neural/semantic search, finding niche content that traditional search engines miss (vital records providers, genealogists, specialized services).

API key stored in `.env` as `EXA_API_KEY`.

**Cost:** ~$5/1k searches

## Quick Reference

**Search with content extraction (most common):**
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
      "text": true
    }
  }' | jq .
```

**Search only (just URLs, no content):**
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

## Search Types

- `"auto"` - Let Exa choose (recommended)
- `"neural"` - Semantic/meaning-based search (best for niche content)
- `"keyword"` - Traditional keyword matching

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query (natural language works well) | required |
| `num_results` | Number of results (1-100) | 10 |
| `type` | Search type: `auto`, `neural`, `keyword` | `auto` |
| `contents` | Include content extraction | omit for URLs only |
| `includeDomains` | Limit to specific domains | none |
| `excludeDomains` | Exclude specific domains | none |
| `startPublishedDate` | Filter by publish date (ISO format) | none |

## Best Practices

**⚠️ Do NOT include time periods in queries** unless explicitly requested:
```bash
# ❌ BAD: "best genealogists 2025" - biases results
# ✅ GOOD: "best genealogists" - gets current results naturally
```

**Use `contents` parameter for combined search + extraction** - same cost, one API call:
```json
{
  "query": "italian citizenship by descent lawyers",
  "num_results": 5,
  "contents": { "text": true }
}
```

**Filter by domain when you know sources:**
```json
{
  "query": "vital records services",
  "includeDomains": ["reddit.com", "trustpilot.com"]
}
```

## Error Handling

**Check for API errors:**
```bash
# Store response and check for errors
RESPONSE=$(curl -s -X POST "https://api.exa.ai/search" ...)
echo "$RESPONSE" | jq -e '.error' && echo "⚠️ API Error: $(echo $RESPONSE | jq -r '.error')"
```

**Common errors:**
- `401 Unauthorized` - Invalid API key, check `EXA_API_KEY`
- `402 Payment Required` - Credits exhausted, need to add credits at exa.ai
- `429 Too Many Requests` - Rate limited, wait and retry
- `500 Server Error` - Exa service issue, try again later

**If search returns poor results:**
1. Try different search type (`neural` vs `keyword`)
2. Rephrase query with more context
3. Use `includeDomains` to target known good sources

## When to Use This vs Extract

| Task | Use |
|------|-----|
| Find information/discover URLs | **search/** (this skill) |
| Get content from known URLs | `extract/` skill |
| Research a topic | **search/** with `contents` |
| Read a specific webpage | `extract/` skill |

## Notes

- When presenting results, show clickable URLs
- Exa search is excellent for finding niche/specialized content
- For extracting content from URLs you already have, use the `extract/` skill instead


