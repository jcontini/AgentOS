# Raindrop Skill

## Intention: Manage bookmarks and collections in Raindrop.io

Create collections, folders, and add bookmarks to Raindrop.io via API.

---

## Setup

**Get API Token:**
1. Go to https://app.raindrop.io/settings/integrations
2. Scroll to "Test token" section
3. Click "Create new token"
4. Copy the token

**Add to .env:**
```bash
RAINDROP_API_TOKEN=your_token_here
```

---

## Collections

**List all collections:**
```bash
curl -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  "https://api.raindrop.io/rest/v1/collections" | jq
```

**Get collection by ID:**
```bash
curl -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  "https://api.raindrop.io/rest/v1/collections/${COLLECTION_ID}" | jq
```

**Create collection:**
```bash
curl -X POST \
  -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Collection Name","public":false}' \
  "https://api.raindrop.io/rest/v1/collections" | jq
```

**Create collection in parent (folder):**
```bash
curl -X POST \
  -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Folder Name\",\"parent\":{\"$id\":${PARENT_ID}},\"public\":false}" \
  "https://api.raindrop.io/rest/v1/collections" | jq
```

---

## Raindrops (Bookmarks)

**Add bookmark:**
```bash
curl -X POST \
  -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"link\":\"https://example.com\",\"collectionId\":${COLLECTION_ID}}" \
  "https://api.raindrop.io/rest/v1/raindrops" | jq
```

**Add bookmark with title:**
```bash
curl -X POST \
  -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"link\":\"https://example.com\",\"title\":\"Custom Title\",\"collectionId\":${COLLECTION_ID}}" \
  "https://api.raindrop.io/rest/v1/raindrops" | jq
```

**Add multiple bookmarks:**
```bash
curl -X POST \
  -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"items\":[{\"link\":\"https://example.com\"},{\"link\":\"https://example2.com\"}],\"collectionId\":${COLLECTION_ID}}" \
  "https://api.raindrop.io/rest/v1/raindrops/batch" | jq
```

**List bookmarks in collection:**
```bash
curl -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  "https://api.raindrop.io/rest/v1/raindrops/${COLLECTION_ID}" | jq
```

---

## Workflow: Create Collection Structure

**1. Find or create parent collection:**
```bash
# List all collections to find parent
curl -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  "https://api.raindrop.io/rest/v1/collections" | \
  jq '.items[] | select(.title == "My Collection") | ._id'
```

**2. Create folder in parent:**
```bash
PARENT_ID=1234567890
curl -X POST \
  -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Research\",\"parent\":{\"$id\":${PARENT_ID}},\"public\":false}" \
  "https://api.raindrop.io/rest/v1/collections" | jq '._id'
```

**3. Create subfolder:**
```bash
RESEARCH_ID=1234567891
curl -X POST \
  -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Project Name\",\"parent\":{\"$id\":${RESEARCH_ID}},\"public\":false}" \
  "https://api.raindrop.io/rest/v1/collections" | jq '._id'
```

**4. Add bookmarks:**
```bash
PROJECT_ID=1234567892
for url in \
  "https://example.com/article1" \
  "https://example.com/article2" \
  "https://example.com/resource"; do
  curl -X POST \
    -H "Authorization: Bearer ${RAINDROP_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"link\":\"$url\",\"collectionId\":${PROJECT_ID}}" \
    "https://api.raindrop.io/rest/v1/raindrops" | jq -r '.item.link'
done
```

---

## API Reference

**Base URL:** `https://api.raindrop.io/rest/v1`

**Authentication:** `Authorization: Bearer ${RAINDROP_API_TOKEN}`

**Collections:** `/collections`
**Raindrops:** `/raindrops`
**Batch:** `/raindrops/batch`

**Documentation:** https://developer.raindrop.io

---

*Quick reference for Raindrop.io API operations.*

