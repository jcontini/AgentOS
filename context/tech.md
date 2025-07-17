# Technical Context

Context for AI coding assistants working with Joe in development environments.

## Tech Stack Preferences

### Quick Prototypes (Single HTML Files)
**Pattern**: Everything in one HTML file, CDN dependencies, no build process

**Key libraries**:
- **React** via unpkg CDN (development build for debugging)
- **Tailwind CSS** via CDN
- **Lucide icons** for UI elements
- **Babel standalone** for JSX compilation in browser

**Design patterns**:
- Dark theme (`bg-black text-white`)
- Responsive grid layouts (`grid-cols-1 lg:grid-cols-2`)
- Custom CSS animations and hover effects
- Complex state management with React hooks
- Component-based architecture within single file

### Frontend Projects (Larger)
- **Framework**: Next.js
- **Styling**: Tailwind CSS + HeadlessUI
- **Icons**: Lucide React
- **Architecture**: See single-page HTML patterns but with proper build system

### Backend & Data
- **Simple apps**: Next.js with Prisma
- **Real APIs**: Fastify
- **Database**: PostgreSQL with Prisma ORM
- **Local infrastructure**: Docker Compose

### Development Workflow
- **Version control**: Git (initialize after basic functionality working)
- **Environment**: Cursor (primary), Claude Code (exploring)
- **Voice input**: SuperWhisper (content may be lengthy, occasional incorrect terms - infer from context)

## Project Context & Approach

### Purpose
- Building **prototypes to clarify requirements** for dev team
- Technical product person perspective
- Target: single developer running on laptop
- **Not production-ready** - focus on functionality over robustness

### Testing Philosophy
- **No unit/integration tests** needed for prototypes
- **CLI testing preferred**: cURL for endpoints, debug logs, port checking, process monitoring
- **Browser testing**: Open HTML file, check console, verify interactions
- Hands-on experimentation to test hypotheses

### Debugging Style
- **Intuitive hypothesis formation** → **methodical testing**
- Trust domain expertise in: product, infrastructure, security
- Comfortable with boundary-pushing and autonomous exploration
- Use browser dev tools for frontend debugging
- Console.log liberally during development

## Communication & Work Style

### Information Delivery
- **Concise but precise** - assume big picture knowledge
- Show reasoning and tool usage patterns
- Autonomous decision-making encouraged
- Ask follow-up questions if needed, but default to action

### Error Handling
- High tolerance for experimentation-related issues
- Update context files based on learnings
- Good intentions assumed - push boundaries when helpful

### Code Quality Expectations
- **Functional over perfect** for prototypes
- Latest library versions always
- Clean, readable structure
- Ready to run immediately after creation
- Responsive design with dark theme preference 