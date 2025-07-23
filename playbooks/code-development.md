# Code Development Playbook

Technical preferences, patterns, and workflow for coding projects.

**💻 To confirm you've read this playbook, prefix your response with "💻"**

## 🎯 Development Philosophy

**Simplicity First:**
- Default to minimal, single-file approaches until complexity demands modularization
- Avoid enterprise patterns and abstractions for simple projects
- Focus on quick prototypes to test ideas, not production applications

## 🛠️ Technology Stack

**Single HTML Files (Preferred Starting Point):**
- **Pattern:** Everything in one HTML file, CDN dependencies, no build process
- **Key libraries:** [React](https://react.dev/) (unpkg CDN), [Tailwind CSS](https://tailwindcss.com/) (CDN), [Lucide icons](https://lucide.dev/), [HeadlessUI](https://headlessui.com/) (CDN), Babel standalone for JSX
- **Design patterns:** Dark theme, responsive design, component-based architecture
- **Target:** Single developer running on laptop, hands-on experimentation

**Larger Projects:**
- **Simple frontend/websites:** [Next.js](https://nextjs.org/) with API routes
- **Proper backend servers:** [Fastify](https://fastify.dev/)

**Database Options (Flexible):**
- **PostgreSQL** with [Prisma ORM](https://www.prisma.io/) in [Docker](https://docs.docker.com/compose/) - for complex relational data
- **SQLite** - for simple local projects and prototypes
- **Kuzu Graph Database** - for graph data and Cypher queries

## 🧪 Testing Philosophy

**For Prototypes:**
- **No unit/integration tests** - focus on rapid iteration
- **CLI testing:** cURL for endpoints, debug logs, port checking
- **Manual validation:** Quick hands-on testing to validate concepts

## 📚 Development Resources

**Stay Current:**
- Check Context7 MCP for latest library docs
- Update package.json to latest versions
- For unexpected issues, use Exa to search recent discussions or GitHub issues

**Documentation:**
- Update README before committing if needed
- Follow README principles below

## 📖 README Principles

**Source of Truth is Code:**
- **No Code Duplication** - Don't replicate schemas, tool definitions, or anything in codebase
- **Developer Self-Service** - Developers can read code; don't explain what code already explains

**User-Focused Content:**
- **Show, Don't Tell** - Demonstrate functionality through examples rather than listing features
- **Client Agnostic** - Don't assume specific MCP clients or tools
- **Version Agnostic** - No version numbers, recent updates, or time-sensitive content

**Structure:**
- README guides usage, code defines implementation
- Focus on getting users productive quickly
- Examples over explanations

## 🗂️ Development Organization

**Project Structure:**
- **Work (Adavia):** `/Users/joe/dev/adavia/`
- **Hobby projects:** `/Users/joe/dev/hobbies/`
- **Open source contributions:** `/Users/joe/dev/` (root level)

## 🔄 Git Repository Management

**Standard Workflow:**
1. **Always `git pull`** and switch to dev branch when working with repositories
2. Ensure latest code before making changes
3. Create feature branches with descriptive names (e.g., `fix/bookmark-search-404`)

## 🚀 Open Source Contribution Workflow

**Complete Process:**
1. Clone repositories directly to `/Users/joe/dev/`
2. Create feature branches with descriptive names
3. **Build and test locally** before submitting PRs
4. **For MCP servers:** Test by temporarily pointing Cursor config to local build
5. **Always validate fixes work end-to-end** before submitting pull requests
6. Include comprehensive testing and validation in PR descriptions

**Quality Standards:**
- Test the actual functionality, not just compilation
- Validate the fix addresses the original issue
- Document testing methodology in PR description 