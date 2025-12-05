# Domain Availability Skill

## Intention: Check domain name availability

Check if domain names are available for registration using the WhoAPI Domain Availability API. WhoAPI offers 10,000 free API requests (one-time, 30-day limit) with support for 500+ million domain names across top gTLDs and ccTLDs.

**API:** WhoAPI Domain Availability API  
**Free Tier:** 10,000 requests (one-time, expires after 30 days)  
**Cost:** Free tier available, paid plans start at $23/month for 40,000 requests

## Quick Reference

**Check single domain:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "http://api.whoapi.com/?domain=example.com&r=taken&apikey=$WHOAPI_API_KEY" | jq .
```

## API Details

**Base URL:** `http://api.whoapi.com/`  
**Authentication:** API key as query parameter  
**API Key:** Store in `.env` as `WHOAPI_API_KEY`

**Get API Key:** Sign up at https://my.whoapi.com/user/signup
- Requires a "high quality" email address (not Gmail, Yahoo, Outlook, iCloud, or temporary emails)
- Free tier: 10,000 requests, expires after 30 days
- No credit card required for free tier

## Common Operations

### Check Domain Availability

**Single domain check:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
DOMAIN="example.com" && \
curl -s "http://api.whoapi.com/?domain=$DOMAIN&r=taken&apikey=$WHOAPI_API_KEY" | jq .
```

**Response format:**
```json
{
  "status": "0",
  "status_desc": "Request successful!",
  "taken": "1",
  "requests_available": 9999
}
```

**Response fields:**
- `status`: Status code (0 = success, see error codes below)
- `status_desc`: Human-readable status description
- `taken`: "1" = domain is taken/not available, "0" = domain is available
- `requests_available`: Number of API requests remaining

**Check multiple domains (loop):**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
for domain in example.com test.com mydomain.io; do
  echo "Checking $domain..."
  RESPONSE=$(curl -s "http://api.whoapi.com/?domain=$domain&r=taken&apikey=$WHOAPI_API_KEY")
  TAKEN=$(echo "$RESPONSE" | jq -r '.taken')
  if [ "$TAKEN" = "1" ]; then
    echo "$domain: Taken"
  else
    echo "$domain: Available"
  fi
done
```

**Check with specific TLD:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
DOMAIN="example.io" && \
curl -s "http://api.whoapi.com/?domain=$DOMAIN&r=taken&apikey=$WHOAPI_API_KEY" | jq .
```

**Get XML output instead of JSON:**
```bash
set -a && source "$PROJECT_ROOT/.env" && set +a && \
curl -s "http://api.whoapi.com/?domain=example.com&r=taken&apikey=$WHOAPI_API_KEY&asxml"
```

### Error Handling

**Check for API errors:**
```bash
RESPONSE=$(curl -s "http://api.whoapi.com/?domain=example.com&r=taken&apikey=$WHOAPI_API_KEY")
STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" != "0" ]; then
  echo "⚠️ API Error: $(echo $RESPONSE | jq -r '.status_desc')"
fi
```

**Common status codes:**
- `0` - Request successful
- `10` - API key invalid (check `WHOAPI_API_KEY` in `.env`)
- `17` - Query limit exceeded (free tier: 10,000 requests)
- `33` - Can't make requests on free account (need to upgrade)
- `34` - Free account has ended (30-day limit expired)
- `35` - Free requests exhausted (upgrade required)
- `1-9` - Domain validation errors (invalid characters, format, etc.)

**Surface errors to user:**
- Always check `status` field - if not "0", display `status_desc`
- If status 17/33/34/35, inform user about free tier limits
- If status 10, check API key configuration

## Best Practices

1. **Batch checks:** When checking multiple domains, add small delays between requests to avoid rate limiting
2. **Cache results:** Domain availability doesn't change frequently - consider caching results
3. **Validate domains:** Ensure domain format is valid before making API calls
4. **Error handling:** Always check `status` field - if not "0", display `status_desc` to user
5. **Rate limits:** Free tier allows 10,000 requests total (not per month) - expires after 30 days
6. **Monitor usage:** Check `requests_available` in response to track remaining requests

## Rate Limits

- **Free tier:** 10,000 requests total (one-time, expires after 30 days)
- **Freelancers:** 40,000 requests/month ($23/month)
- **Startups:** 200,000 requests/month ($49/month)
- **Business:** 1,000,000 requests/month ($99/month)
- **Enterprise:** 5,000,000 requests/month ($399/month)

## Notes

- WhoAPI supports top gTLDs and ccTLDs (500+ million domain names)
- Free tier requires a "high quality" email (not Gmail, Yahoo, Outlook, iCloud, or temporary emails)
- Free tier is one-time only (10,000 requests, expires after 30 days)
- API documentation: https://whoapi.com/api-documentation/
- API console for testing: https://my.whoapi.com/api/console (requires login)

## Alternative APIs

If WhoAPI is unavailable or credits exhausted:
- **Fastly Domain Research API:** 10,000 free requests/month - https://www.fastly.com/products/domain-research-api
- **WhoisXML API:** 100 free queries - https://domain-availability.whoisxmlapi.com/
