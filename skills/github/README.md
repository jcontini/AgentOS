# GitHub Skill

## Intention: Manage GitHub issues, PRs, and repos via the `gh` CLI

### Requirements

Requires GitHub CLI (`gh`) to be installed and authenticated:

```bash
# Check if installed
which gh || echo "Not installed"

# Install if needed
brew install gh        # macOS
# or: sudo apt install gh   # Ubuntu/Debian
# or: winget install GitHub.cli  # Windows

# Authenticate (one-time setup)
gh auth login
```

### Common Operations

#### Issues

```bash
# List issues
gh issue list
gh issue list --state open --limit 20

# View an issue
gh issue view 123

# Create an issue
gh issue create --title "Title" --body "Description"
gh issue create --title "Bug: ..." --body "..." --label "bug"
gh issue create --title "Feature: ..." --body "..." --label "enhancement"

# Close an issue
gh issue close 123

# Reopen an issue
gh issue reopen 123

# Add comment to issue
gh issue comment 123 --body "Comment text"

# Search issues
gh issue list --search "keyword"
```

#### Pull Requests

```bash
# List PRs
gh pr list

# View a PR
gh pr view 123

# Create a PR
gh pr create --title "Title" --body "Description"

# Checkout a PR locally
gh pr checkout 123

# Merge a PR
gh pr merge 123

# Review a PR
gh pr review 123 --approve
gh pr review 123 --comment --body "Looks good!"
```

#### Repository

```bash
# View repo info
gh repo view

# Clone a repo
gh repo clone owner/repo

# Fork a repo
gh repo fork owner/repo

# Create a repo
gh repo create my-repo --public
```

### Filing Feedback/Issues for AgentOS

To file feedback, bugs, or feature requests for AgentOS:

```bash
# Bug report
gh issue create --repo jcontini/AgentOS --title "Bug: [description]" --body "..." --label "bug"

# Feature request
gh issue create --repo jcontini/AgentOS --title "Feature: [description]" --body "..." --label "enhancement"

# Question/feedback
gh issue create --repo jcontini/AgentOS --title "[topic]" --body "..."
```

### Tips

- Use `--help` on any command for options: `gh issue create --help`
- JSON output: Add `--json field1,field2` to most commands
- Web view: Add `--web` to open in browser instead of terminal


