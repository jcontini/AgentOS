# Web Search Skill

## Intention: Search the web / Search the internet

Use Exa API for web search. API key stored in `.env` as `EXA_API_KEY`. Use curl to call Exa APIs directly.

**⚠️ CRITICAL: Do NOT include time periods (e.g., "January 2025", "2025", "this year") in search queries unless explicitly requested by the user.** Search engines return recent results by default, and adding dates can bias results toward that specific time period rather than the most current information.

**⚠️ IMPORTANT: Use `/search` with `contents` parameter for combined search + extraction in a single call.** This is more efficient than separate search and contents calls, with the same cost.

**Web Search with Content Extraction (Recommended):**
```bash
# See boot.md for environment variable sourcing pattern
([ -z "$EXA_API_KEY" ] && set -a && source /Users/joe/dev/ai/.env && set +a); \
curl -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search query",
    "num_results": 5,
    "type": "keyword",
    "contents": {
      "text": true
    }
  }'
```

**Note:** Use `contents: {text: true}` (object format), not `text: true` (boolean). The boolean format only returns metadata.

## Intention: Read a specific URL

**URL Content Extraction (when you already have URLs):**
```bash
# See boot.md for environment variable sourcing pattern
([ -z "$EXA_API_KEY" ] && set -a && source /Users/joe/dev/ai/.env && set +a); \
curl -X POST "https://api.exa.ai/contents" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"], "text": true}'
```

Use `/contents` endpoint only when:
- You already have specific URLs to extract
- You need advanced features like `livecrawl`, `subpages`, or `extras.imageLinks`
- You need per-URL error handling via `statuses` array

**Fallback:** If Exa API doesn't work:
- Use `curl -s [URL]` to get raw HTML
- Pipe through `grep` or other text processing tools
- Useful for: footer content, embedded links, metadata, social media links

## Notes

When using a tool to create or find any external resource (task, event, webpage, etc), show the URL in the response so it can be clicked easily.

