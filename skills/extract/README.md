# Extract Skill

## Intention: Extract content from URLs / Read webpages / Scrape content

Extract content from known URLs. Uses a two-tier approach:
1. **Exa** (primary) - Fast, cheaper, works for most sites
2. **Firecrawl** (fallback) - JS-heavy sites, when Exa fails, or when you need more content

API keys in `.env`: `EXA_API_KEY`, `FIRECRAWL_API_KEY`

**Cost:** Exa ~$0.001/page | Firecrawl ~$0.009/page

## Quick Reference

### Exa Extraction (Try First)

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

### Firecrawl Extraction (Fallback)

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

## Decision Tree: When to Use Which

```
Start with Exa extraction
    ↓
Did it succeed with good content?
    YES → Done ✓
    NO  → Use Firecrawl fallback
         ↓
         Reasons to use Firecrawl:
         • Exa returned CRAWL_UNKNOWN_ERROR
         • JS-heavy site (Notion, React apps, SPAs)
         • Exa returned limited/truncated content
         • Dynamic content requiring browser rendering
```

## Exa Extraction Details

**⚠️ Always use `livecrawl: "always"` to get fresh content (not stale cache).**

**Multiple URLs:**
```bash
curl -s -X POST "https://api.exa.ai/contents" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://site1.com", "https://site2.com", "https://site3.com"],
    "text": true,
    "livecrawl": "always"
  }' | jq .
```

**Livecrawl options:**
- `"always"` - Fresh content (RECOMMENDED)
- `"fallback"` - Use cache if live fails
- `"never"` - Cache only

**Exa parameters:**
| Parameter | Description |
|-----------|-------------|
| `urls` | Array of URLs to extract |
| `text` | Return text content (boolean) |
| `livecrawl` | Freshness: `always`, `fallback`, `never` |
| `subpages` | Include linked pages |

## Firecrawl Extraction Details

**Firecrawl excels at:**
- JavaScript-heavy sites (Notion, React, Vue, Angular)
- Single-page applications (SPAs)
- Dynamic content requiring browser rendering
- Getting 2-5x more content than Exa on complex pages

**Simple markdown extraction:**
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

**Firecrawl parameters:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| `url` | URL to scrape | required |
| `formats` | Output formats: `markdown`, `html` | `["markdown"]` |
| `onlyMainContent` | Skip headers/footers | `true` |
| `includeTags` | Only include these HTML tags | all |
| `excludeTags` | Exclude these HTML tags | none |

## Error Handling

### Exa Errors

```bash
# Check response for errors
RESPONSE=$(curl -s -X POST "https://api.exa.ai/contents" ...)
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
  echo "⚠️ Exa Error: $(echo $RESPONSE | jq -r '.error')"
  echo "Falling back to Firecrawl..."
  # Use Firecrawl instead
fi
```

**Common Exa errors:**
- `CRAWL_UNKNOWN_ERROR` - Site blocked/JS-heavy → **Use Firecrawl**
- `401 Unauthorized` - Check `EXA_API_KEY`
- `402 Payment Required` - Credits exhausted at exa.ai
- `429 Too Many Requests` - Rate limited

### Firecrawl Errors

```bash
RESPONSE=$(curl -s -X POST "https://api.firecrawl.dev/v1/scrape" ...)
if [ "$(echo $RESPONSE | jq -r '.success')" != "true" ]; then
  echo "⚠️ Firecrawl Error: $(echo $RESPONSE | jq -r '.error // .message')"
fi
```

**Common Firecrawl errors:**
- `401 Unauthorized` - Check `FIRECRAWL_API_KEY`
- `402 Payment Required` - Credits exhausted at firecrawl.dev
- `429 Too Many Requests` - Rate limited
- Timeout errors - Very large/slow pages

### Surface All Errors to User

**⚠️ CRITICAL: Always surface API errors to the user, including:**
- Credit exhaustion (402 errors)
- Rate limiting (429 errors)
- Authentication failures (401 errors)
- Any extraction failures

Don't silently fail - tell the user what went wrong so they can fix it.

## Crawling Multiple Pages

**Firecrawl can crawl entire sites:**
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

## Raw HTML Fallback

If both APIs fail, use raw curl:
```bash
curl -s "https://example.com" | grep -o '<title>[^<]*</title>'
```

Useful for: footer content, embedded links, metadata, social media links.

## Notes

- When presenting results, show the source URL
- For finding URLs first, use the `search/` skill
- Prefer Exa for cost efficiency, Firecrawl for reliability on complex sites


