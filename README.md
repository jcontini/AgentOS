# AgentOS

Supercharge your AI assistant with real-world skills via terminal access.

## Available Skills

### <img src="https://lkcomputers.com/wp-content/uploads/2015/02/Apple-Glass-Logo.png" width="28" height="28" style="vertical-align:text-bottom"> macOS Native
*Direct access to local apps*

| Skill | What it does |
|-------|--------------|
| <img src="https://upload.wikimedia.org/wikipedia/commons/1/1c/MacOSCalendar.png" width="18" height="18" style="vertical-align:text-bottom"> [Calendar](skills/apple-calendar/README.md) | Read & manage calendar events |
| <img src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Contacts_%28iOS%29.png" width="18" height="18" style="vertical-align:text-bottom"> [Contacts](skills/apple-contacts/README.md) | Search, read & manage contacts |
| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/IMessage_logo.svg/1200px-IMessage_logo.svg.png" width="18" height="18" style="vertical-align:text-bottom"> [iMessages](skills/imessages/README.md) | Read messages & conversations |
| <img src="https://www.google.com/s2/favicons?domain=whatsapp.com&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [WhatsApp](skills/whatsapp/README.md) | Read WhatsApp messages & conversations |
| <img src="https://www.google.com/s2/favicons?domain=copilot.money&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [Copilot Money](skills/copilot/README.md) | Balances, transactions, net worth |

### ☁️ Cloud APIs
*Requires internet & API keys*

| Skill | What it does |
|-------|--------------|
| <img src="https://img.icons8.com/fluency/48/gmail.png" width="18" height="18" style="vertical-align:text-bottom"> [Gmail](skills/gmail/README.md) | Read emails, search, draft messages |
| <img src="https://img.icons8.com/fluency/48/google-drive.png" width="18" height="18" style="vertical-align:text-bottom"> [Google Drive](skills/google-drive/README.md) | List, search & read files |
| <img src="https://cdn.simpleicons.org/todoist" width="18" height="18" style="vertical-align:text-bottom"> [Todoist](skills/todoist/README.md) | Personal task management |
| <img src="https://cdn.simpleicons.org/linear" width="18" height="18" style="vertical-align:text-bottom"> [Linear](skills/linear/README.md) | Work project & issue tracking |
| <img src="https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" width="18" height="18" style="vertical-align:text-bottom"> [GitHub](skills/github/README.md) | Issues, PRs, repo management |
| <img src="https://raindrop.io/favicon.ico" width="18" height="18" style="vertical-align:text-bottom"> [Raindrop](skills/raindrop/README.md) | Bookmark management |
| <img src="https://www.google.com/s2/favicons?domain=exa.ai&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [Exa](skills/exa/README.md) | Semantic web search & extraction |
| <img src="https://www.google.com/s2/favicons?domain=firecrawl.dev&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [Firecrawl](skills/firecrawl/README.md) | Extract content from JS-heavy URLs |
| <img src="https://cdn.simpleicons.org/youtube" width="18" height="18" style="vertical-align:text-bottom"> [YouTube](skills/youtube/README.md) | Video transcription |
| ✈️ [Flights](skills/google-flights/README.md) | Search & compare flights |
| <img src="https://images.g2crowd.com/uploads/product/image/b0a53bb6a5db8829772a32d63c3d41b7/enrich-labs-enrich-so.png" width="18" height="18" style="vertical-align:text-bottom"> [Enrich](skills/enrich-so/README.md) | Email/phone/domain lookup |
| <img src="https://www.google.com/s2/favicons?domain=apollo.io&sz=64" width="18" height="18" style="vertical-align:text-bottom"> [Apollo CRM](skills/apollo/README.md) | Accounts, contacts, deals, sequences |

## Setup

Paste this into your AI chat ([Cursor](https://cursor.com/) agent, or any AI with terminal access):

```
Clone AgentOS, read the README, and guide me through setup:
git clone https://github.com/jcontini/AgentOS.git && cat AgentOS/README.md
```

That's it. The AI handles the rest.

## How It Works

1. You ask your AI to do something ("check my email", "search for X")
2. The AI reads `boot.md` to see what skills are available
3. It picks the right skill and runs it via terminal
4. Your API keys and personal data stay local — never sent to us

## License

[MIT](LICENSE)

---

## For AI Assistants

```bash
[ -f .env ] && [ -f user/profile.md ] && echo "READY" || echo "NEEDS_SETUP"
```

- **NEEDS_SETUP:** Read `utils/setup.md` and guide user through setup
- **READY:** Read `boot.md` for skills, `user/profile.md` for context
