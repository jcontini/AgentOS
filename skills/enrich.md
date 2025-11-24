# Enrich Skill

## Intention: Enrich person or company information

When you need to lookup contact details, company info, or validate emails/domains/LinkedIn profiles:

### Actions

Use the enrich script at `/Users/joe/dev/ai/scripts/enrich.sh`:

- **Email to profile:** `/Users/joe/dev/ai/scripts/enrich.sh --email "user@domain.com"` (default)
- **Email to phone:** `/Users/joe/dev/ai/scripts/enrich.sh --email "user@domain.com" --type phone`
- **Check disposable email:** `/Users/joe/dev/ai/scripts/enrich.sh --email "user@domain.com" --type disposable`
- **Domain to company:** `/Users/joe/dev/ai/scripts/enrich.sh --domain "company.com"` (default)
- **Domain to logo:** `/Users/joe/dev/ai/scripts/enrich.sh --domain "company.com" --type logo`
- **IP to company:** `/Users/joe/dev/ai/scripts/enrich.sh --ip "1.2.3.4"`
- **LinkedIn person profile:** `/Users/joe/dev/ai/scripts/enrich.sh --linkedin "linkedin.com/in/username"` (default: person)
- **LinkedIn company profile:** `/Users/joe/dev/ai/scripts/enrich.sh --linkedin "linkedin.com/company/companyname" --type company`

### Output

JSON data to stdout (parse for structured information)

### Requirements

ENRICH_SO_API_KEY set in .env file


