

# Building a Zapier Clone: End-to-End Comprehensive Guide

---

## PHASE 0: DEEPLY UNDERSTAND WHAT ZAPIER ACTUALLY IS

Before writing a single line, you need to internalize the mental model.

### Core Concept
Zapier is a **workflow orchestration engine**. It connects apps via their APIs. A user creates a "Zap" which says:

> "When **THIS** happens in App A (Trigger), do **THAT** in App B (Action), then do **THAT** in App C (Action)."

### Fundamental Building Blocks

```
TRIGGER → FILTER (optional) → ACTION → ACTION → ...
   ↑                            ↑
   |                            |
 "When new email arrives"    "Create a Trello card"
```

**Trigger**: An event detection mechanism. Two types:
- **Webhook-based (instant)**: The external app pushes data to your system (e.g., Stripe sends a webhook when payment happens)
- **Polling-based (scheduled)**: Your system periodically hits an external API and checks "anything new since last time?" (e.g., checking Google Sheets every 5 mins)

**Action**: An outbound API call to do something in another app (send email, create record, post message).

**Filter/Conditional Logic**: Between steps — "only continue if amount > $100"

**Data Mapping**: Output of Step 1 becomes input of Step 2. A user maps fields: `{{trigger.email}}` → Trello card description.

---

## PHASE 1: ARCHITECTURE DEEP DIVE

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  ┌──────────┐ ┌──────────────┐ ┌─────────────────────┐  │
│  │  Auth UI  │ │ Workflow     │ │ Integration         │  │
│  │  Pages    │ │ Builder      │ │ Marketplace/Browser │  │
│  │          │ │ (Drag & Drop)│ │                     │  │
│  └──────────┘ └──────────────┘ └─────────────────────┘  │
│  ┌──────────────────┐ ┌──────────────────────────────┐  │
│  │  Execution Logs   │ │  Connection Manager          │  │
│  │  & History        │ │  (OAuth flows, API keys)     │  │
│  └──────────────────┘ └──────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ REST / GraphQL
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  API GATEWAY / BACKEND                    │
│                                                          │
│  ┌────────────────┐  ┌────────────────┐                  │
│  │  Auth Service   │  │  Workflow CRUD │                  │
│  │  (JWT/Session)  │  │  Service       │                  │
│  └────────────────┘  └────────────────┘                  │
│  ┌────────────────┐  ┌────────────────┐                  │
│  │  Webhook        │  │  Connection/   │                  │
│  │  Receiver       │  │  Credential    │                  │
│  │  Service        │  │  Service       │                  │
│  └────────────────┘  └────────────────┘                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │           Integration Definition Engine             │  │
│  │  (Knows how to talk to Gmail, Slack, Sheets, etc.) │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                EXECUTION ENGINE (The Heart)               │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Scheduler    │  │  Task Queue  │  │  Workflow     │   │
│  │  (Cron/Poll)  │──▶│  (Bull/      │──▶│  Executor    │   │
│  │              │  │  RabbitMQ)   │  │  (Step by    │   │
│  └──────────────┘  └──────────────┘  │  Step Runner) │   │
│                                       └──────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                             │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  PostgreSQL   │  │  Redis        │  │  Encrypted   │   │
│  │  (Workflows,  │  │  (Queue,      │  │  Vault       │   │
│  │  Users, Logs) │  │  Caching,     │  │  (API keys,  │   │
│  │              │  │  Dedup)       │  │  Tokens)     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## PHASE 2: TECH STACK SELECTION (with reasoning)

### Recommended Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | React + TypeScript + Tailwind CSS | Component-driven, huge ecosystem, great for complex UIs |
| **Workflow Builder UI** | React Flow (reactflow.dev) | Purpose-built for node-based visual editors — this is THE library for this |
| **State Management** | Zustand or Redux Toolkit | Complex UI state for the builder |
| **Backend** | Node.js (Express or Fastify) + TypeScript | Async I/O is perfect for an integration platform making tons of API calls |
| **Database** | PostgreSQL | Relational integrity for workflows, JSONB for flexible step configs |
| **Task Queue** | BullMQ (Redis-backed) | Battle-tested, supports delayed jobs, retries, rate limiting — critical for polling and execution |
| **Cache / Pub-Sub** | Redis | Session cache, deduplication store, queue backend |
| **Auth** | Passport.js + JWT or NextAuth | OAuth flows for both your app AND integration connections |
| **Encryption** | Node crypto / libsodium | You MUST encrypt stored credentials |
| **Webhook Delivery** | Express routes + ngrok (dev) | Receive incoming webhooks from external services |
| **Containerization** | Docker + Docker Compose | Run all services locally, impressive for portfolio |
| **Deployment** | Railway / Render / AWS EC2 | Free tiers available |

### Alternative: If You Prefer Python
Use **FastAPI** for backend, **Celery + Redis** for task queue, **SQLAlchemy** for ORM. The concepts are identical.

---

## PHASE 3: DATABASE DESIGN (Critical Foundation)

### Core Entities and Their Relationships

```
USERS
├── id
├── email
├── password_hash
├── created_at
│
├── has many → CONNECTIONS
│   ├── id
│   ├── user_id
│   ├── integration_id (e.g., "google", "slack")
│   ├── credentials_encrypted (access_token, refresh_token, api_key)
│   ├── status (active/expired/revoked)
│   ├── metadata (account name, email shown in UI)
│   └── created_at
│
├── has many → WORKFLOWS (Zaps)
│   ├── id
│   ├── user_id
│   ├── name
│   ├── status (draft / active / paused / error)
│   ├── created_at
│   ├── last_run_at
│   │
│   ├── has many → WORKFLOW_STEPS (ordered)
│   │   ├── id
│   │   ├── workflow_id
│   │   ├── step_order (1, 2, 3...)
│   │   ├── step_type (trigger / action / filter)
│   │   ├── integration_id (e.g., "gmail")
│   │   ├── operation_id (e.g., "new_email" or "send_email")
│   │   ├── connection_id (which user connection to use)
│   │   ├── config (JSONB — field mappings, parameters)
│   │   │   Example: {
│   │   │     "to": "{{steps.1.sender_email}}",
│   │   │     "subject": "Re: {{steps.1.subject}}",
│   │   │     "body": "Got it, thanks!"
│   │   │   }
│   │   └── created_at
│   │
│   └── has many → WORKFLOW_RUNS (execution history)
│       ├── id
│       ├── workflow_id
│       ├── status (running / success / failed)
│       ├── started_at
│       ├── completed_at
│       ├── error_message
│       │
│       └── has many → STEP_RUNS
│           ├── id
│           ├── workflow_run_id
│           ├── workflow_step_id
│           ├── status (pending / running / success / failed / skipped)
│           ├── input_data (JSONB — what went INTO this step)
│           ├── output_data (JSONB — what came OUT)
│           ├── error_message
│           ├── started_at
│           └── completed_at
│
INTEGRATION_DEFINITIONS (can be in DB or config files)
├── id (e.g., "gmail", "slack", "notion")
├── name
├── icon_url
├── auth_type (oauth2 / api_key / basic)
├── auth_config (JSONB — client_id, scopes, auth_url, token_url)
├── base_url
│
├── has many → OPERATIONS
│   ├── id (e.g., "new_email", "send_email")
│   ├── integration_id
│   ├── type (trigger / action)
│   ├── trigger_type (webhook / polling) — only for triggers
│   ├── name ("New Email", "Send Email")
│   ├── description
│   ├── input_schema (JSON Schema — what fields the user configures)
│   ├── output_schema (JSON Schema — what data this step produces)
│   ├── api_endpoint
│   └── api_method
```

---

## PHASE 4: THE INTEGRATION DEFINITION SYSTEM

This is what makes or breaks your project. You need a **declarative way to define integrations** so adding a new one doesn't require rewriting logic.

### The Concept: Integration as Configuration

Each integration is a **JSON/YAML definition file** + a thin adapter layer.

Think of it like a plugin system:

```
/integrations
  /gmail
    ├── definition.json      (metadata, auth config, operations)
    ├── triggers/
    │   └── new_email.ts     (polling logic or webhook handler)
    └── actions/
        └── send_email.ts    (execution logic)
  /slack
    ├── definition.json
    ├── triggers/
    │   └── new_message.ts
    └── actions/
        └── send_message.ts
  /discord
    ├── definition.json
    ...
```

### What a Definition File Contains

Conceptually for Gmail:

- **Auth**: OAuth2, scopes needed (`gmail.readonly`, `gmail.send`), Google's auth URL, token URL
- **Triggers**:
  - "New Email" → polling type, hits Gmail API `GET /messages?q=after:{timestamp}`, returns `{id, subject, body, sender, date}`
  - "New Labeled Email" → polling, adds label filter
- **Actions**:
  - "Send Email" → `POST /messages/send`, needs `{to, subject, body}`
  - "Add Label" → `POST /messages/{id}/modify`
- **Input/Output Schemas**: JSON Schema definitions so the UI can dynamically render forms

### The Executor Pattern

Each operation implements a simple interface:

```
Interface for a Trigger:
  - poll(credentials, lastPollTimestamp, config) → returns array of new items
  - or: setupWebhook(credentials, webhookUrl) / handleWebhook(payload)

Interface for an Action:
  - execute(credentials, inputData, config) → returns output data
```

This is how you keep things uniform. The execution engine doesn't care if it's Gmail or Slack — it just calls `execute()`.

---

## PHASE 5: THE EXECUTION ENGINE (The Brain)

### How a Workflow Actually Runs

```
User turns on workflow
        │
        ▼
   ┌─────────────┐
   │  Is trigger  │
   │  polling or  │
   │  webhook?    │
   └──────┬──────┘
          │
    ┌─────┴──────┐
    ▼            ▼
POLLING       WEBHOOK
    │            │
    │            │  External service sends
    │            │  POST to your endpoint
    │            │
    ▼            ▼
Scheduler     Webhook receiver
adds job to   immediately adds
queue every   job to queue
5 minutes     
    │            │
    └─────┬──────┘
          ▼
   ┌──────────────┐
   │  TASK QUEUE   │  (BullMQ)
   │  picks up job │
   └──────┬───────┘
          ▼
   ┌──────────────────────────────┐
   │  WORKFLOW EXECUTOR           │
   │                              │
   │  1. Load workflow definition │
   │  2. Create workflow_run      │
   │                              │
   │  FOR EACH STEP:              │
   │    a. Resolve input data     │
   │       (template variables    │
   │        from previous steps)  │
   │    b. Decrypt credentials    │
   │    c. Call operation.execute │
   │    d. Store output in        │
   │       step_run               │
   │    e. If filter → evaluate   │
   │       condition, skip rest   │
   │       if false               │
   │    f. If error → retry or    │
   │       mark failed            │
   │                              │
   │  3. Mark workflow_run done   │
   └──────────────────────────────┘
```

### The Template/Variable Resolution System

This is crucial. When a user configures Step 3, they reference data from Steps 1 and 2:

```
"Send Slack message: Hey, {{steps.1.sender_name}} sent an email about {{steps.1.subject}}"
```

Your executor must:
1. Maintain a **context object** that accumulates outputs from each step
2. Before executing each step, **resolve all template variables** in that step's config
3. Support nested access: `{{steps.2.data.rows[0].name}}`

This is essentially a mini template engine. You can use:
- Handlebars/Mustache style parsing
- Or write a simple `{{path}}` resolver using lodash `_.get()`

### Deduplication (Critical for Polling Triggers)

When you poll Gmail every 5 minutes, you'll get the same emails repeatedly. You must:
- Store the ID of every item you've already processed (per workflow)
- Use Redis SET: `dedup:{workflow_id}` → set of processed item IDs
- Only process items with IDs not in the set
- Expire old entries after some time

---

## PHASE 6: AUTHENTICATION & CREDENTIAL MANAGEMENT

### Two Layers of Auth

1. **User auth for YOUR platform**: Login/signup to your app (JWT, sessions)
2. **User auth for EXTERNAL services**: "Connect your Gmail" — this involves OAuth flows

### The OAuth2 Connection Flow

```
User clicks "Connect Gmail"
        │
        ▼
Frontend redirects to:
  https://accounts.google.com/o/oauth2/v2/auth?
    client_id=YOUR_GOOGLE_CLIENT_ID&
    redirect_uri=https://yourapp.com/api/auth/callback/google&
    scope=gmail.readonly gmail.send&
    state={userId, integrationId}&  ← so you know who this is for
    response_type=code
        │
        ▼
User grants permission on Google's page
        │
        ▼
Google redirects to YOUR callback URL with ?code=xxx
        │
        ▼
Your backend exchanges code for access_token + refresh_token
        │
        ▼
ENCRYPT tokens and store in CONNECTIONS table
        │
        ▼
User now has a "Gmail Connection" they can use in workflows
```

### Credential Security

- **NEVER store tokens in plaintext**
- Use AES-256-GCM encryption with a master key from environment variables
- When executing a step, decrypt just-in-time, use, then discard from memory
- Implement token refresh logic (access tokens expire)

### For Portfolio: Free/Easy Integrations

Not every service requires complex OAuth. Start with:

| Integration | Auth Type | Difficulty |
|------------|----------|------------|
| **Webhooks (Generic)** | None | Easiest — just receive data |
| **Discord** | Bot Token or Webhook URL | Easy |
| **Telegram** | Bot Token | Easy |
| **Slack** | Bot Token or Webhook | Easy-Medium |
| **Google Sheets** | OAuth2 | Medium |
| **Gmail** | OAuth2 | Medium |
| **Notion** | OAuth2 | Medium |
| **GitHub** | OAuth2 or PAT | Easy-Medium |
| **Airtable** | API Key / PAT | Easy |
| **OpenAI / ChatGPT** | API Key | Easy |
| **Twilio (SMS)** | API Key + Secret | Easy |
| **HTTP/REST (Generic)** | Configurable | Medium |

---

## PHASE 7: FRONTEND — THE WORKFLOW BUILDER

### This is what makes the portfolio IMPRESSIVE

The visual builder is the centerpiece. Use **React Flow** library.

### UI Components You Need

**1. Dashboard Page**
- List of user's workflows
- Status toggle (active/paused)
- Last run time, success/fail indicators
- Create new workflow button

**2. Workflow Builder Page (THE star of the show)**
- Canvas area (React Flow) with nodes and edges
- Each node = a step (trigger or action)
- Left sidebar: integration browser (click to add)
- Right sidebar/panel: configuration for selected node
  - Choose integration
  - Choose operation
  - Choose connection (or create new)
  - Configure fields (dynamic form based on operation's input_schema)
  - Map fields from previous steps (show available variables)

**3. The Field Mapper UI**
- This is the "magic" part
- When user configures an action's input field, they can:
  - Type static text
  - Insert variables from previous steps (dropdown/autocomplete)
  - Example: A rich text input that shows pills/chips for `{{steps.1.email}}`

**4. Test/Preview Feature**
- "Test this step" button
- Executes just that one step with sample data
- Shows output
- This is HUGELY impressive in a portfolio

**5. Execution History Page**
- List of all runs for a workflow
- Click into a run → see step-by-step execution
- For each step: input data, output data, status, timing
- Error messages with details

**6. Connections Manager Page**
- List all connected accounts
- "Connect new account" button per integration
- Show connection status
- Reconnect / delete

### UI/UX Tips for Portfolio Impact

- Use a **dark mode** design (looks professional)
- Smooth animations on the canvas
- Color-coded nodes by integration (Gmail = red, Slack = purple, etc.)
- Show integration logos/icons prominently
- Loading states, empty states, error states — polish matters

---

## PHASE 8: STEP-BY-STEP BUILD ORDER

This is the order I'd actually build things in:

### Sprint 1: Foundation (Week 1-2)
```
□ Set up monorepo (Turborepo or just /frontend + /backend)
□ Set up backend: Express + TypeScript + PostgreSQL + Prisma ORM
□ Set up frontend: React + TypeScript + Tailwind + React Router
□ Implement user auth (signup, login, JWT)
□ Basic dashboard layout (empty state)
□ Docker Compose for PostgreSQL + Redis
```

### Sprint 2: Integration Definition System (Week 2-3)
```
□ Design and create the integration plugin architecture
□ Build 2 simple integrations as proof of concept:
  - "Webhook" trigger (receive arbitrary data)
  - "Discord Webhook" action (send message via webhook URL)
□ Store integration definitions (file-based or DB)
□ API endpoints to list integrations and their operations
□ Connection CRUD endpoints
□ Build a simple connection creation flow (API key type first)
```

### Sprint 3: Workflow CRUD + Basic Builder (Week 3-4)
```
□ Workflow CRUD API endpoints
□ Basic React Flow canvas
□ Add nodes (trigger + actions) to canvas
□ Select integration and operation for each node
□ Save/load workflow from database
□ Basic field configuration (static values first)
```

### Sprint 4: Execution Engine (Week 4-5)
```
□ Set up BullMQ
□ Build the workflow executor (step-by-step runner)
□ Template variable resolution ({{steps.1.field}})
□ Webhook receiver endpoint (triggers workflow on incoming webhook)
□ Execution logging (workflow_runs + step_runs)
□ Execution history UI
□ Test: Webhook received → Discord message sent (end to end!)
```

### Sprint 5: Polling + More Integrations (Week 5-6)
```
□ Polling scheduler (cron-like, adds jobs to queue periodically)
□ Deduplication system
□ Add OAuth2 flow (Google as first OAuth integration)
□ Google Sheets trigger ("new row") + action ("add row")
□ Gmail trigger + action
□ Slack integration
```

### Sprint 6: Advanced Features + Polish (Week 6-8)
```
□ Filter/conditional steps
□ Field mapper UI with variable insertion (pills/chips)
□ "Test step" functionality
□ Error handling and retry logic
□ More integrations (GitHub, Notion, etc.)
□ Dashboard polish — run counts, last run, status indicators
□ Responsive design
□ Landing page
```

### Sprint 7: Deployment + Demo (Week 8-9)
```
□ Dockerize everything
□ Deploy to Railway / Render / AWS
□ Set up demo workflows that visitors can see
□ Record a demo video / GIF for README
□ Write comprehensive README
□ Create architecture diagram
```

---

## PHASE 9: CRITICAL TECHNICAL CHALLENGES & HOW TO SOLVE THEM

### Challenge 1: Dynamic Form Generation
Each operation has different fields. Gmail's "Send Email" needs `to, subject, body`. Slack's "Send Message" needs `channel, text`.

**Solution**: Store input schemas as JSON Schema. Build a `<DynamicForm schema={operation.inputSchema} />` component that renders the right form fields based on the schema. Libraries like `react-jsonschema-form` can help, or build your own for more control.

### Challenge 2: Variable Resolution Between Steps
**Solution**: 
- Each step's output is stored in a context map: `{ "steps": { "1": {...output}, "2": {...output} } }`
- Use regex to find `{{steps.X.path.to.field}}` patterns
- Replace with actual values using deep object access
- Show available variables in UI by inspecting previous steps' output schemas

### Challenge 3: Handling OAuth Token Refresh
Access tokens expire (usually 1 hour for Google).
**Solution**: 
- Before each execution, check if token is expired
- If expired, use refresh_token to get new access_token
- Update stored credentials
- THEN execute the step
- If refresh fails → mark connection as expired, notify user

### Challenge 4: Reliable Execution
What if your server crashes mid-workflow?
**Solution**: 
- BullMQ persists jobs in Redis
- Failed jobs auto-retry with exponential backoff
- Each step_run has a status, so you can resume from where it failed
- Idempotency keys for actions (don't send duplicate Slack messages)

### Challenge 5: Rate Limiting
External APIs have rate limits. 
**Solution**:
- Use BullMQ's built-in rate limiter
- Per-integration rate limit configs
- Backoff on 429 responses

---

## PHASE 10: WHAT MAKES THIS PORTFOLIO-WORTHY

### Must-Have Features for Impressiveness
1. **Visual workflow builder** — this is the WOW factor
2. **At least 5-7 working integrations** — shows breadth
3. **Real end-to-end execution** — not just UI mockups
4. **Execution history with step-by-step detail** — shows engineering depth
5. **Proper error handling** — retries, error messages, failed state handling
6. **Clean architecture** — plugin system for integrations
7. **Docker setup** — shows DevOps awareness
8. **Comprehensive README** — architecture diagrams, setup instructions, screenshots

### Nice-to-Have Features That Set You Apart
- Multi-step workflows (not just trigger → action, but trigger → action → action → action)
- Conditional/filter logic with a UI
- Delay steps ("wait 5 minutes, then...")
- Transformation steps ("format date", "extract text", etc.)
- Workflow templates ("Start from template")
- Real-time execution status (WebSocket updates)
- Usage analytics dashboard
- Rate limiting per user

### Demo Strategy
Create **3-4 pre-built demo workflows** that visitors can see:
1. "When GitHub star → Send Slack notification"
2. "When Webhook received → Add row to Google Sheet → Send Discord message"
3. "Every hour → Fetch weather API → Send Telegram summary"
4. "When new Gmail email from boss → Create Notion task"

---

## PHASE 11: FREE SERVICES / APIs FOR INTEGRATIONS

| Service | Free Tier | Good For |
|---------|----------|----------|
| Gmail API | 15,000 requests/day | Email trigger/action |
| Google Sheets API | 60 requests/min | Database-like CRUD |
| Discord Webhooks | Unlimited | Send messages |
| Slack API | Free for dev workspace | Messages, channels |
| GitHub API | 5,000 requests/hr | Repo events |
| Telegram Bot API | Unlimited | Messages |
| Notion API | Free | Pages, databases |
| Airtable API | 5 calls/sec | Structured data |
| OpenAI API | $5 free credit | AI-powered steps |
| Webhook.site | Free | Testing webhooks |
| JSONPlaceholder | Unlimited | Mock API for testing |
| OpenWeatherMap | 60 calls/min | Weather data (demo) |

---

## PHASE 12: LEARNING RESOURCES & REFERENCE MATERIAL

### Study These Open-Source Projects
- **n8n** (n8n.io) — Open-source Zapier alternative. Study its node system architecture. This is your BEST reference.
- **Activepieces** — Another open-source automation tool. Clean codebase.
- **Automatisch** — Simpler, good for understanding basics.
- **Pipedream** — Has open-source components worth studying.

### Key Concepts to Research
- Event-driven architecture
- Message queues and job processing
- OAuth 2.0 flow (read the RFC, understand thoroughly)
- JSON Schema (for dynamic forms)
- Webhook architecture
- Node-based UI editors (React Flow documentation)
- Data encryption at rest
- Idempotency in API design

---

## PHASE 13: PROJECT NAMING & PRESENTATION

Give it a real product name. Not "Zapier Clone." Call it something like:
- **FlowForge**
- **AutoBridge**
- **SyncFlow**
- **ChainLink** (check if taken)
- **PipeFlow**

### For Your Resume, describe it as:

> "Built a full-stack workflow automation platform enabling users to connect 7+ services (Gmail, Slack, GitHub, etc.) through a visual drag-and-drop builder. Features include OAuth2 integration management, a Redis-backed execution engine with retry logic, polling & webhook-based triggers, dynamic form generation, and step-by-step execution logging. Architected with a plugin-based integration system for extensibility."

That single bullet point will generate questions in every interview.

---

## FINAL MENTAL MODEL

Think of your system as having exactly **5 engines**:

```
1. DEFINITION ENGINE    → "What integrations exist and what can they do?"
2. CONNECTION ENGINE    → "How do I authenticate with each service?"
3. BUILDER ENGINE       → "How does the user wire things together?"
4. EXECUTION ENGINE     → "How do I actually run the workflow?"
5. MONITORING ENGINE    → "What happened when it ran?"
```

Build them in roughly that order. Each is a standalone concern. Each is impressive on its own. Together, they form a system that will genuinely stand out in any portfolio.

Start today. Build the database schema. Get the first trigger-action pair working end-to-end (webhook in → Discord message out). Everything else is iteration on that core loop.