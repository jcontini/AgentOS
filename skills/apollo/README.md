# Apollo CRM Skill

## Intention: Read and manage Apollo CRM data (accounts, contacts, deals, sequences, tasks, calls)

When the user mentions reading Apollo CRM data, accounts, contacts, deals, sequences, tasks, or calls, use the Apollo REST API directly.

### Apollo API Integration

Use the Apollo REST API endpoint: `https://api.apollo.io/api/v1`

**Authentication:** Use API key from `.env` file. The API key should be included in the `X-Api-Key` header (NOT Authorization Bearer).

**Basic Query Pattern:**
```bash
# Unconditional sourcing (simpler and more reliable - see boot.md)
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.apollo.io/api/v1/endpoint" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

**Troubleshooting Auth Errors:**
- If you get authentication errors, verify the key exists: `grep APOLLO_API_KEY "$PROJECT_ROOT/.env"`
- **Use `X-Api-Key` header, NOT `Authorization: Bearer`** - Apollo uses a custom header
- Some endpoints require a master API key (not just a regular API key)
- If auth still fails, try unconditional sourcing pattern above (more reliable than conditional)

**Note:** Many endpoints require a **master API key**. If you receive a `403` response, you need to create a master API key. See [Apollo API docs](https://docs.apollo.io/docs/create-api-key) for details.

### Accounts

#### Search Accounts

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/accounts/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 25
  }' | jq .
```

**Search with filters:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/accounts/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 25,
    "q_keywords": "company name",
    "organization_locations": ["United States"]
  }' | jq .
```

### Contacts

#### Create a Contact

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/contacts" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Cache-Control: no-cache" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "organization_name": "Example Corp",
    "website_url": "https://example.com"
  }' | jq .
```

**With phone numbers:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/contacts" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Cache-Control: no-cache" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "organization_name": "Example Corp",
    "direct_phone": "555-123-4567",
    "mobile_phone": "555-765-4321"
  }' | jq .
```

**Note:** By default, Apollo does not deduplicate contacts. Set `"run_dedupe": true` in the request body to enable deduplication and prevent duplicate contacts.

#### Search Contacts

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/contacts/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 25
  }' | jq .
```

**Search with filters:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/contacts/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 25,
    "q_keywords": "email@example.com",
    "person_titles": ["CEO", "CTO"]
  }' | jq .
```

### Deals

#### List All Deals

**Note:** Requires master API key.

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.apollo.io/api/v1/opportunities/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

**List with pagination:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.apollo.io/api/v1/opportunities/search?page=1&per_page=25" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

#### View Specific Deal

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
DEAL_ID="deal-id-here" && \
curl -s -X GET "https://api.apollo.io/api/v1/opportunities/$DEAL_ID" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

### Sequences

#### Search Sequences

**Note:** Requires master API key.

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/emailer_campaigns/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 25
  }' | jq .
```

**Search with filters:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/emailer_campaigns/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 25,
    "q_keywords": "sequence name"
  }' | jq .
```

### Tasks

#### Search Tasks

**Note:** Requires master API key. Display limit of 50,000 records (100 records per page, up to 500 pages).

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/tasks/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 100
  }' | jq .
```

**Search with filters:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/tasks/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 100,
    "user_ids": ["user-id-here"],
    "due_date": {
      "gte": "2025-01-01",
      "lte": "2025-12-31"
    }
  }' | jq .
```

### Calls

#### Search Calls

**Note:** Requires master API key.

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.apollo.io/api/v1/calls/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

**Search with pagination:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.apollo.io/api/v1/calls/search?page=1&per_page=25" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

### Users

#### Get List of Users

**Note:** Requires master API key.

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.apollo.io/api/v1/users/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

**Use case:** User IDs from this endpoint can be used for other endpoints like creating deals, accounts, and tasks.

### Email Accounts

#### Get List of Email Accounts

**Note:** Requires master API key.

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.apollo.io/api/v1/email_accounts/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

### People Search

#### Search Apollo's People Database

Use Apollo's People API to search their database of 210+ million contacts:

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/mixed_people/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 25,
    "person_titles": ["CEO", "CTO"],
    "organization_locations": ["United States"]
  }' | jq .
```

### Organization Search

#### Search Organizations

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/organizations/search" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "per_page": 25,
    "q_keywords": "company name",
    "organization_locations": ["United States"]
  }' | jq .
```

### Enrichment

#### Enrich Person Data

Enrich a person's data using email or name + company domain:

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/people/match" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "person@example.com"
  }' | jq .
```

**With name and domain:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/people/match" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "organization_name": "Example Corp"
  }' | jq .
```

#### Enrich Organization Data

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X GET "https://api.apollo.io/api/v1/organizations/enrich" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -G \
  -d "domain=example.com" | jq .
```

### API Usage Stats

#### View API Usage Stats and Rate Limits

```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s -X POST "https://api.apollo.io/api/v1/auth/health" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" | jq .
```

### Best Practices

1. **Master API Key:** Many endpoints require a master API key. Create one in Apollo settings if you get 403 errors.
2. **Pagination:** Most endpoints support `page` and `per_page` parameters. Use pagination for large datasets.
3. **Rate Limits:** Apollo has rate limits. Check the response headers for rate limit information.
4. **Filtering:** Use search filters to narrow results and avoid hitting display limits (e.g., tasks have a 50,000 record limit).
5. **Batch Operations:** Use bulk endpoints when available for multiple operations.
6. **Error Handling:** Check HTTP status codes and handle rate limits (429), auth failures (401), and permission errors (403).

### Rate Limits

Apollo API has rate limits based on your plan. Check response headers for:
- `X-RateLimit-Limit`: Maximum requests per time window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

If you receive a `429 Too Many Requests` error, wait before retrying.

### Common Response Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing API key
- `403 Forbidden`: Master API key required or insufficient permissions
- `429 Too Many Requests`: Rate limit exceeded
- `500 Server Error`: Apollo service issue

### Note

For detailed API documentation, use search (see `skills/exa/README.md`) to find Apollo API docs or visit https://docs.apollo.io





