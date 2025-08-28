#!/bin/bash

# Enrichment Script - Multi-purpose data enrichment using enrich.so API
# Usage: ./enrich.sh --email "user@domain.com" [--type profile|phone|disposable]
#        ./enrich.sh --domain "company.com" [--type company|logo] 
#        ./enrich.sh --ip "1.2.3.4"
#        ./enrich.sh --linkedin "linkedin.com/in/username" [--type person|company]
# Outputs JSON directly to stdout for AI consumption

# Set script directory and find .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

# Load environment variables from .env file
load_env() {
    if [ -f "$ENV_FILE" ]; then
        set -o allexport
        source "$ENV_FILE"
        set +o allexport
    else
        echo "Error: .env file not found at $ENV_FILE" >&2
        echo "Please create a .env file with your ENRICH_SO_API_KEY" >&2
        exit 1
    fi
}

# Function to log with timestamp (to stderr so it doesn't interfere with JSON output)
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

# Function to validate email format
validate_email() {
    local email="$1"
    if [[ ! "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        echo "Error: Invalid email format: $email" >&2
        return 1
    fi
    return 0
}

# Function to validate domain format
validate_domain() {
    local domain="$1"
    if [[ ! "$domain" =~ ^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        echo "Error: Invalid domain format: $domain" >&2
        return 1
    fi
    return 0
}

# Function to validate IP format
validate_ip() {
    local ip="$1"
    if [[ ! "$ip" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo "Error: Invalid IP format: $ip" >&2
        return 1
    fi
    return 0
}

# Function to validate LinkedIn URL format
validate_linkedin() {
    local linkedin_url="$1"
    # Remove protocol if present and normalize
    linkedin_url=$(echo "$linkedin_url" | sed 's|^https\?://||' | sed 's|^www\.||')
    
    # Check for valid LinkedIn URL patterns
    if [[ ! "$linkedin_url" =~ ^linkedin\.com/in/[A-Za-z0-9._-]+/?$ ]] && [[ ! "$linkedin_url" =~ ^linkedin\.com/company/[A-Za-z0-9._-]+/?$ ]]; then
        echo "Error: Invalid LinkedIn URL format: $linkedin_url" >&2
        echo "Expected format: linkedin.com/in/username or linkedin.com/company/companyname" >&2
        return 1
    fi
    return 0
}

# Function to make API call
make_api_call() {
    local endpoint="$1"
    local description="$2"
    
    # Check if API key is set
    if [ -z "$ENRICH_SO_API_KEY" ]; then
        echo "Error: ENRICH_SO_API_KEY not found in environment" >&2
        echo "Please set ENRICH_SO_API_KEY in your .env file" >&2
        return 1
    fi
    
    local base_url="https://api.enrich.so/v1/api"
    local full_url="$base_url$endpoint"
    
    log "$description: $full_url"
    
    # Make API request
    local response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $ENRICH_SO_API_KEY" \
        -H "Content-Type: application/json" \
        "$full_url")
    
    # Extract HTTP status code (last line) and response body
    local http_code=$(echo "$response" | tail -n1)
    local response_body=$(echo "$response" | sed '$d')
    
    # Check if request was successful
    if [ "$http_code" -eq 200 ]; then
        log "SUCCESS: $description completed"
        
        # Add LLM formatting instructions
        echo "=== LLM INSTRUCTIONS ==="
        echo "Format this data as a professional profile card with:"
        echo "- Current role shown as 'Title @ Company' (with company as clickable link)"
        echo "- Summary directly below the title"
        echo "- Contact links as: 📧 [email](mailto:email) | 🔗 [/in/username](linkedin-url) (pipe-separated)"
        echo "- Professional Experience as table with columns: Start | Role @ Company"
        echo "  - Start column shows just the year (e.g., '2023')"
        echo "  - Role @ Company column shows 'Title @ [Company](link)' format"
        echo "- All company and school names as clickable links"
        echo "- Show LinkedIn paths like '/in/username' for easy recognition"
        echo "========================="
        echo ""
        
        # Output raw JSON (no need for jq since LLM can parse it)
        echo "$response_body"
        
        return 0
    else
        log "ERROR: $description failed with status: $http_code"
        echo "Error: API request failed (HTTP $http_code)" >&2
        if [ -n "$response_body" ]; then
            echo "Response: $response_body" >&2
        fi
        return 1
    fi
}

# Email enrichment functions
email_to_profile() {
    local email="$1"
    make_api_call "/person?email=$email&in_realtime=true" "Email to profile lookup"
}

email_to_phone() {
    local email="$1"
    make_api_call "/email-to-mobile?email=$email" "Email to phone lookup"
}

check_disposable_email() {
    local email="$1"
    make_api_call "/disposable-email-check?email=$email" "Disposable email check"
}

# Domain enrichment functions
domain_to_company() {
    local domain="$1"
    make_api_call "/company?domain=$domain" "Domain to company lookup"
}

domain_to_logo() {
    local domain="$1"
    make_api_call "/search-logo?url=$domain" "Domain logo lookup"
}

# IP enrichment function
ip_to_company() {
    local ip="$1"
    make_api_call "/ip-to-company-lookup?ip=$ip" "IP to company lookup"
}

# LinkedIn enrichment function
linkedin_profile_lookup() {
    local linkedin_url="$1"
    local type="$2"
    
    # Remove protocol if present and normalize
    linkedin_url=$(echo "$linkedin_url" | sed 's|^https\?://||' | sed 's|^www\.||')
    
    # URL encode the LinkedIn URL for the API call
    local encoded_url=$(printf '%s' "$linkedin_url" | sed 's| |%20|g')
    
    make_api_call "/linkedin-by-url?url=$encoded_url&type=$type" "LinkedIn profile lookup"
}

# Function to show usage
show_usage() {
    echo "Enrichment Script - Multi-purpose data enrichment using enrich.so API"
    echo ""
    echo "Usage:"
    echo "  $0 --email 'user@domain.com' [--type profile|phone|disposable]"
    echo "  $0 --domain 'company.com' [--type company|logo]"
    echo "  $0 --ip '1.2.3.4'"
    echo "  $0 --linkedin 'linkedin.com/in/username' [--type person|company]"
    echo ""
    echo "Email enrichment:"
    echo "  $0 --email 'john@company.com' --type profile     # Get full profile (default)"
    echo "  $0 --email 'john@company.com' --type phone       # Get phone number"
    echo "  $0 --email 'john@company.com' --type disposable  # Check if disposable/spam"
    echo ""
    echo "Domain enrichment:"
    echo "  $0 --domain 'google.com' --type company          # Get company info (default)"
    echo "  $0 --domain 'google.com' --type logo             # Get company logo"
    echo ""
    echo "IP enrichment:"
    echo "  $0 --ip '86.92.60.221'                           # Get company from IP"
    echo ""
    echo "LinkedIn enrichment:"
    echo "  $0 --linkedin 'linkedin.com/in/williamhgates' --type person    # Get person profile (default)"
    echo "  $0 --linkedin 'linkedin.com/company/microsoft' --type company  # Get company profile"
    echo ""
    echo "Options:"
    echo "  --type TYPE      Specify enrichment type (see examples above)"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Requirements:"
    echo "  - .env file with ENRICH_SO_API_KEY set"
    echo "  - curl command available"
    echo "  - jq command (optional, for pretty JSON formatting)"
    echo ""
    echo "Output: JSON data is written to stdout"
}

# Initialize variables
EMAIL=""
DOMAIN=""
IP=""
LINKEDIN=""
TYPE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --ip)
            IP="$2"
            shift 2
            ;;
        --linkedin)
            LINKEDIN="$2"
            shift 2
            ;;
        --type)
            TYPE="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1" >&2
            show_usage
            exit 1
            ;;
    esac
done

# Validate that exactly one input type is provided
input_count=0
if [ -n "$EMAIL" ]; then ((input_count++)); fi
if [ -n "$DOMAIN" ]; then ((input_count++)); fi
if [ -n "$IP" ]; then ((input_count++)); fi
if [ -n "$LINKEDIN" ]; then ((input_count++)); fi

if [ $input_count -eq 0 ]; then
    echo "Error: Must provide one of --email, --domain, --ip, or --linkedin" >&2
    show_usage
    exit 1
elif [ $input_count -gt 1 ]; then
    echo "Error: Can only provide one of --email, --domain, --ip, or --linkedin" >&2
    show_usage
    exit 1
fi

# Load environment variables
load_env

# Check dependencies
if ! command -v curl &> /dev/null; then
    echo "Error: curl is not installed. Please install curl first." >&2
    exit 1
fi

# Process email enrichment
if [ -n "$EMAIL" ]; then
    if ! validate_email "$EMAIL"; then
        exit 1
    fi
    
    # Set default type if not specified
    if [ -z "$TYPE" ]; then
        TYPE="profile"
    fi
    
    case "$TYPE" in
        profile)
            email_to_profile "$EMAIL"
            ;;
        phone)
            email_to_phone "$EMAIL"
            ;;
        disposable)
            check_disposable_email "$EMAIL"
            ;;
        *)
            echo "Error: Invalid type '$TYPE' for email. Use: profile, phone, disposable" >&2
            exit 1
            ;;
    esac
fi

# Process domain enrichment
if [ -n "$DOMAIN" ]; then
    if ! validate_domain "$DOMAIN"; then
        exit 1
    fi
    
    # Set default type if not specified
    if [ -z "$TYPE" ]; then
        TYPE="company"
    fi
    
    case "$TYPE" in
        company)
            domain_to_company "$DOMAIN"
            ;;
        logo)
            domain_to_logo "$DOMAIN"
            ;;
        *)
            echo "Error: Invalid type '$TYPE' for domain. Use: company, logo" >&2
            exit 1
            ;;
    esac
fi

# Process IP enrichment
if [ -n "$IP" ]; then
    if ! validate_ip "$IP"; then
        exit 1
    fi
    
    # IP only has one enrichment type
    if [ -n "$TYPE" ] && [ "$TYPE" != "company" ]; then
        echo "Warning: IP enrichment only supports company lookup, ignoring --type $TYPE" >&2
    fi
    
    ip_to_company "$IP"
fi

# Process LinkedIn enrichment
if [ -n "$LINKEDIN" ]; then
    if ! validate_linkedin "$LINKEDIN"; then
        exit 1
    fi
    
    # Set default type if not specified
    if [ -z "$TYPE" ]; then
        TYPE="person"
    fi
    
    case "$TYPE" in
        person|company)
            linkedin_profile_lookup "$LINKEDIN" "$TYPE"
            ;;
        *)
            echo "Error: Invalid type '$TYPE' for LinkedIn. Use: person, company" >&2
            exit 1
            ;;
    esac
fi
