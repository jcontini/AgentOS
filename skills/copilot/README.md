# Copilot Money Skill

## Intention: Query financial data from Copilot Money's local database

Read-only access to accounts, balances, and transactions. Copilot Money stores all data locally in SQLite.

## Database Location

```bash
COPILOT_DB="$HOME/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite"
```

## Schema

### Transactions

| Field | Type | Description |
|-------|------|-------------|
| `id` | TEXT | Primary key |
| `account_id` | TEXT | Links to account |
| `name` | TEXT | Merchant/transaction name (cleaned) |
| `original_name` | TEXT | Original merchant name from bank |
| `amount` | DOUBLE | Negative = debit, positive = credit |
| `date` | DATE | Transaction date |
| `category_id` | TEXT | Copilot category ID |
| `plaid_category_id` | TEXT | Plaid category ID |
| `plaid_category_strings` | TEXT | JSON array of category strings (e.g., `["Shops","Clothing"]`) |
| `pending` | BOOLEAN | 0/1 |
| `recurring` | BOOLEAN | 0/1 |
| `recurring_id` | TEXT | ID linking recurring transactions |
| `user_note` | TEXT | User-added notes |
| `type` | TEXT | Transaction type (e.g., "regular") |

### accountDailyBalance

| Field | Type | Description |
|-------|------|-------------|
| `date` | TEXT | Balance date |
| `account_id` | TEXT | Account identifier |
| `current_balance` | DOUBLE | Current balance |
| `available_balance` | DOUBLE | Available balance |
| `limit` | DOUBLE | Credit limit (if applicable) |

## Account Metadata

Account names are in JSON files (not the database):

```bash
# Credit accounts
cat ~/Library/Group\ Containers/group.com.copilot.production/widget-data/widgets-account-credit_accounts.json

# Other accounts (checking, savings, investment)
cat ~/Library/Group\ Containers/group.com.copilot.production/widget-data/widgets-account-other_accounts.json
```

Format: `[{"name": "Account Name", "id": "account_id_here"}, ...]`

## Query Patterns

### Recent Transactions

```bash
sqlite3 "$COPILOT_DB" -json "SELECT id, account_id, name, amount, date, pending FROM Transactions ORDER BY date DESC LIMIT 20;"
```

### Search by Merchant

```bash
sqlite3 "$COPILOT_DB" -json "SELECT name, amount, date FROM Transactions WHERE name LIKE '%COSTCO%' ORDER BY date DESC;"
```

### Spending by Month

```bash
sqlite3 "$COPILOT_DB" "SELECT strftime('%Y-%m', date) as month, SUM(amount) as total FROM Transactions WHERE amount < 0 GROUP BY month ORDER BY month DESC;"
```

### Spending by Category

```bash
sqlite3 "$COPILOT_DB" "SELECT category_id, COUNT(*) as count, SUM(amount) as total FROM Transactions WHERE amount < 0 GROUP BY category_id ORDER BY total ASC;"
```

### Spending by Plaid Category (Better Category Names)

```bash
sqlite3 "$COPILOT_DB" -json "SELECT plaid_category_strings, COUNT(*) as count, SUM(amount) as total FROM Transactions WHERE amount < 0 AND plaid_category_strings IS NOT NULL GROUP BY plaid_category_strings ORDER BY total ASC;" | jq -r '.[] | "\(.plaid_category_strings) | $\(.total | tostring | ltrimstr("-") | tonumber | floor) | \(.count) txns"'
```

### Actual Spending (Excluding Payments & Transfers)

**Get all actual merchant spending, excluding credit card payments and investment transfers:**

```bash
COPILOT_DB="$HOME/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite"
sqlite3 "$COPILOT_DB" -json "
SELECT 
  name,
  amount,
  date,
  plaid_category_strings,
  category_id,
  account_id
FROM Transactions 
WHERE amount < 0 
  AND date >= date('now', '-3 months')
  AND name NOT LIKE '%AUTOPAY%'
  AND name NOT LIKE '%AUTOMATIC PAYMENT%'
  AND name NOT LIKE '%SCHWAB%'
  AND name NOT LIKE '%FEDWIRE%'
  AND name NOT LIKE '%MONEYLINK%'
  AND name NOT LIKE '%ZELLE%'
ORDER BY date DESC;
" | jq -r '.[] | "\(.date | split(" ")[0]) | \(.name) | $\(.amount | tostring | ltrimstr("-")) | \(.plaid_category_strings // "uncategorized")"'
```

### Spending Analysis by Merchant

**Group spending by merchant name:**

```bash
COPILOT_DB="$HOME/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite"
sqlite3 "$COPILOT_DB" -json "
SELECT 
  name,
  SUM(amount) as total_spending,
  COUNT(*) as transaction_count,
  MIN(date) as first_seen,
  MAX(date) as last_seen
FROM Transactions 
WHERE amount < 0 
  AND date >= date('now', '-3 months')
  AND name NOT LIKE '%AUTOPAY%'
  AND name NOT LIKE '%AUTOMATIC PAYMENT%'
  AND name NOT LIKE '%SCHWAB%'
  AND name NOT LIKE '%FEDWIRE%'
  AND name NOT LIKE '%MONEYLINK%'
  AND name NOT LIKE '%ZELLE%'
GROUP BY name 
ORDER BY total_spending ASC;
" | jq -r '.[] | "\(.name) | $\(.total_spending | tostring | ltrimstr("-") | tonumber | floor) | \(.transaction_count) txns | \(.first_seen | split(" ")[0]) - \(.last_seen | split(" ")[0])"'
```

### Comprehensive Spending Breakdown

**Complete spending analysis with account names and categories:**

```bash
COPILOT_DB="$HOME/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite"
ACCOUNTS_DIR="$HOME/Library/Group Containers/group.com.copilot.production/widget-data"
CREDIT=$(cat "$ACCOUNTS_DIR/widgets-account-credit_accounts.json" 2>/dev/null || echo "[]")
OTHER=$(cat "$ACCOUNTS_DIR/widgets-account-other_accounts.json" 2>/dev/null || echo "[]")
ALL_ACCOUNTS=$(echo "$CREDIT $OTHER" | jq -s 'add')

sqlite3 "$COPILOT_DB" -json "
SELECT 
  name,
  amount,
  date,
  account_id,
  plaid_category_strings,
  category_id,
  recurring
FROM Transactions 
WHERE amount < 0 
  AND date >= date('now', '-3 months')
  AND name NOT LIKE '%AUTOPAY%'
  AND name NOT LIKE '%AUTOMATIC PAYMENT%'
  AND name NOT LIKE '%SCHWAB%'
  AND name NOT LIKE '%FEDWIRE%'
  AND name NOT LIKE '%MONEYLINK%'
  AND name NOT LIKE '%ZELLE%'
ORDER BY date DESC;
" | jq --argjson accounts "$ALL_ACCOUNTS" '
  ($accounts | map({(.id): .name}) | add) as $nameMap |
  [.[] | . + {
    account_name: ($nameMap[.account_id] // "Unknown"),
    category: (if .plaid_category_strings then (.plaid_category_strings | fromjson | join(" > ")) else "uncategorized" end)
  }]
  | map({
      date: (.date | split(" ")[0]),
      merchant: .name,
      amount: .amount,
      account: .account_name,
      category: .category,
      recurring: (.recurring == 1)
    })
'
```

### Monthly Spending Summary

**Monthly totals excluding payments and transfers:**

```bash
COPILOT_DB="$HOME/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite"
sqlite3 "$COPILOT_DB" -json "
SELECT 
  strftime('%Y-%m', date) as month,
  COUNT(*) as transaction_count,
  SUM(amount) as total_spending
FROM Transactions 
WHERE amount < 0 
  AND date >= date('now', '-3 months')
  AND name NOT LIKE '%AUTOPAY%'
  AND name NOT LIKE '%AUTOMATIC PAYMENT%'
  AND name NOT LIKE '%SCHWAB%'
  AND name NOT LIKE '%FEDWIRE%'
  AND name NOT LIKE '%MONEYLINK%'
  AND name NOT LIKE '%ZELLE%'
GROUP BY month 
ORDER BY month DESC;
" | jq -r '.[] | "\(.month): \(.transaction_count) transactions, $\(.total_spending | tostring | ltrimstr("-") | tonumber | floor)"'
```

### Account Balances (Latest)

```bash
sqlite3 "$COPILOT_DB" -json "SELECT account_id, date, current_balance, available_balance FROM accountDailyBalance WHERE date = (SELECT MAX(date) FROM accountDailyBalance WHERE account_id = accountDailyBalance.account_id);"
```

### Transactions with Account Names

```bash
COPILOT_DB="$HOME/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite"
ACCOUNTS_DIR="$HOME/Library/Group Containers/group.com.copilot.production/widget-data"
CREDIT=$(cat "$ACCOUNTS_DIR/widgets-account-credit_accounts.json")
OTHER=$(cat "$ACCOUNTS_DIR/widgets-account-other_accounts.json")
ALL_ACCOUNTS=$(echo "$CREDIT $OTHER" | jq -s 'add')

sqlite3 "$COPILOT_DB" -json "SELECT id, account_id, name, amount, date FROM Transactions ORDER BY date DESC LIMIT 10;" | \
jq --argjson accounts "$ALL_ACCOUNTS" '[.[] | . + {account_name: ($accounts | map(select(.id == .account_id)) | .[0].name // "Unknown")}]'
```

### Net Worth Calculation

**One-shot query for net worth with account breakdown:**

```bash
COPILOT_DB="$HOME/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite"
ACCOUNTS_DIR="$HOME/Library/Group Containers/group.com.copilot.production/widget-data"
CREDIT=$(cat "$ACCOUNTS_DIR/widgets-account-credit_accounts.json" 2>/dev/null || echo "[]")
OTHER=$(cat "$ACCOUNTS_DIR/widgets-account-other_accounts.json" 2>/dev/null || echo "[]")
ALL_ACCOUNTS=$(echo "$CREDIT $OTHER" | jq -s 'add')

sqlite3 "$COPILOT_DB" -json "SELECT account_id, date, current_balance, available_balance, \"limit\" FROM accountDailyBalance WHERE date = (SELECT MAX(date) FROM accountDailyBalance WHERE account_id = accountDailyBalance.account_id);" | \
jq --argjson creditAccounts "$CREDIT" --argjson allAccounts "$ALL_ACCOUNTS" '
  ($allAccounts | map({(.id): .name}) | add) as $nameMap |
  ($creditAccounts | map(.id)) as $creditIds |
  [.[] | .account_id as $aid | . + {
    account_name: ($nameMap[$aid] // "Unknown"),
    account_type: (if ($creditIds | index($aid)) != null then "credit" else "asset" end)
  }]
  | map({
      account_name: .account_name,
      current_balance: (.current_balance // 0),
      available_balance: .available_balance,
      limit: .limit,
      account_type: .account_type
    })
  | sort_by(.account_name)
  | . as $accounts |
  {
    accounts: $accounts,
    summary: {
      assets: ($accounts | map(select(.account_type == "asset") | .current_balance) | add // 0),
      liabilities: ($accounts | map(select(.account_type == "credit") | .current_balance) | add // 0),
      net_worth: (($accounts | map(select(.account_type == "asset") | .current_balance) | add // 0) - ($accounts | map(select(.account_type == "credit") | .current_balance) | add // 0))
    }
  }'
```

**Key points:**
- **Account type detection:** Uses source JSON file (`credit_accounts.json` = liability, `other_accounts.json` = asset), NOT the `limit` field
- **Charge cards:** Handled correctly - accounts in `credit_accounts.json` are liabilities regardless of limit value (charge cards like Amex Platinum may have `limit: 0` or `null`)
- **Credit card balances:** 
  - Positive balance = debt owed (liability)
  - Negative balance = credit/overpayment (reduces liability, effectively an asset)
  - Net worth = assets - liabilities (negative credit balances reduce total liabilities)

## Spending Analysis Best Practices

### Filtering Out Non-Spending Transactions

When analyzing spending, exclude:
- **Credit card payments:** `name LIKE '%AUTOPAY%' OR name LIKE '%AUTOMATIC PAYMENT%'`
- **Investment transfers:** `name LIKE '%SCHWAB%' OR name LIKE '%MONEYLINK%'`
- **Wire transfers:** `name LIKE '%FEDWIRE%'`
- **P2P payments:** `name LIKE '%ZELLE%'`

These represent transfers/payments, not actual spending. The credit card payments are paying off spending that happened earlier, but individual merchant charges may not be visible if Copilot only syncs payment summaries.

### Using Plaid Categories

`plaid_category_strings` contains JSON arrays like `["Shops","Clothing"]` - parse with `jq` to get readable category names:
```bash
.plaid_category_strings | fromjson | join(" > ")
```

### Getting Account Names

Account names aren't in the database - load from JSON files and join:
```bash
ACCOUNTS_DIR="$HOME/Library/Group Containers/group.com.copilot.production/widget-data"
CREDIT=$(cat "$ACCOUNTS_DIR/widgets-account-credit_accounts.json")
OTHER=$(cat "$ACCOUNTS_DIR/widgets-account-other_accounts.json")
ALL_ACCOUNTS=$(echo "$CREDIT $OTHER" | jq -s 'add')
```

## Notes

- **Amount signs:** Negative = spending, positive = income/refunds
- **Booleans:** Stored as 0/1 integers
- **Date format:** `YYYY-MM-DD HH:MM:SS.000`
- **Read-only:** Database is managed by Copilot app
- **JSON output:** Use `-json` flag for easier parsing with jq
- **Category data:** Use `plaid_category_strings` for better category names than `category_id`

