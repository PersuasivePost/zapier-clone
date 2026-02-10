# Honest Assessment First — Then the Roadmap

## There Are Compatibility Problems in Your Stack

Before jumping in, let me flag real issues that will waste your time if not addressed now.

---

### Problem 1: BullMQ Does NOT Work With Python

BullMQ is a **Node.js-only** library. Your FastAPI backend cannot use it directly.

**Your options:**

| Option                                        | Recommendation                                                  |
| --------------------------------------------- | --------------------------------------------------------------- |
| **Celery + Redis**                            | Industry standard for Python task queues. Use this.             |
| **ARQ**                                       | Async-native, built for FastAPI-like apps. Lighter than Celery. |
| **Dramatiq**                                  | Middle ground — simpler than Celery, more features than ARQ     |
| Run a separate Node.js worker JUST for BullMQ | Overengineered for 2 weeks, skip this                           |

**Go with Celery + Redis.** Interviewers know it, it handles scheduling, retries, everything you need.

---

### Problem 2: "Zoogle" — This Doesn't Exist as a Known Package

I cannot find a recognized npm package called **"zoogle"** for auth. You might be thinking of one of these:

| Package                | What It Is              |
| ---------------------- | ----------------------- |
| **NextAuth / Auth.js** | Auth for Next.js apps   |
| **Firebase Auth**      | Google's auth service   |
| **Clerk**              | Drop-in auth components |
| **Passport.js**        | Node.js auth middleware |
| **Supertokens**        | Open-source auth        |

**My recommendation for YOUR stack:** Don't introduce a separate JS auth service at all. FastAPI has excellent auth support built-in. Use **FastAPI's security utilities + python-jose (JWT) + OAuth2 flows directly in Python.** Adding a separate Node.js service just for auth in a 2-week project is unnecessary complexity.

---

### Problem 3: GraphQL + FastAPI

This works fine, but use the right Python library:

- **Strawberry GraphQL** — modern, type-safe, built for FastAPI integration
- NOT Apollo Server (that's Node.js)

---

## Your Corrected Final Stack

```
Frontend:       React + TypeScript + Tailwind CSS + React Flow
API Layer:      FastAPI + Strawberry (GraphQL) + Uvicorn
Auth:           FastAPI built-in OAuth2 + python-jose (JWT)
Task Queue:     Celery + Redis (with Celery Beat for polling schedules)
Database:       PostgreSQL + SQLAlchemy (async) + Alembic (migrations)
Cache/Broker:   Redis
Encryption:     Python cryptography library (Fernet or AES)
Containerization: Docker + Docker Compose
```

**This is a clean, coherent, impressive stack. No weird cross-language friction.**

---

# THE 14-DAY ROADMAP — Hour by Hour Focus

This is aggressive. You need **6-8 focused hours per day minimum.**

---

## DAY 1: Project Skeleton + Database

**Morning: Project Setup**

```
□ Create project root folder
□ /backend (FastAPI project)
   - Install: fastapi, uvicorn, sqlalchemy[asyncio],
     asyncpg, alembic, celery, redis, python-jose,
     passlib, strawberry-graphql, httpx, cryptography
   - Set up folder structure:
     /app
       /api          (GraphQL resolvers + REST endpoints)
       /core         (config, security, database)
       /models       (SQLAlchemy models)
       /schemas      (Pydantic schemas)
       /services     (business logic)
       /integrations (plugin system)
       /workers      (Celery tasks)
       main.py

□ /frontend (React project)
   - Vite + React + TypeScript
   - Install: tailwindcss, react-flow, react-router-dom,
     @apollo/client, graphql, zustand, lucide-react

□ docker-compose.yml
   - PostgreSQL (port 5432)
   - Redis (port 6379)

□ Spin up docker-compose, verify both services running
```

**Afternoon: Database Models**

```
□ Create ALL SQLAlchemy models:
   - User
   - Connection
   - Workflow
   - WorkflowStep
   - WorkflowRun
   - StepRun

□ Set up Alembic, run first migration
□ Verify tables exist in PostgreSQL
□ Create Pydantic schemas for each model
```

**End of Day 1 Deliverable:** Empty FastAPI server running, database tables created, React app showing hello world.

---

## DAY 2: Authentication System

**Full Day: Auth in FastAPI**

```
□ User registration endpoint
   - Hash passwords with passlib (bcrypt)
   - Store in DB

□ Login endpoint
   - Verify password
   - Generate JWT token (python-jose)
   - Return access_token + refresh_token

□ JWT middleware / dependency
   - get_current_user dependency that extracts
     user from Authorization header
   - Protect all future endpoints with this

□ Frontend:
   - Login page
   - Signup page
   - Store JWT in memory (not localStorage for security,
     but localStorage is fine for portfolio)
   - Axios/fetch interceptor to attach token
   - Protected route wrapper
   - Basic dashboard layout (sidebar + main area)
```

**End of Day 2 Deliverable:** User can sign up, log in, see empty dashboard. Token-protected API working.

---

## DAY 3: Integration Plugin Architecture

**This is the most important architectural day.**

**Morning: Design the Plugin System**

```
□ Create /integrations folder structure:
   /integrations
     /base.py          (abstract base classes)
     /registry.py      (integration registry - discovers all plugins)
     /webhook/
       ├── __init__.py
       ├── definition.py   (metadata: name, icon, auth_type)
       ├── triggers.py     (IncomingWebhook trigger)
       └── actions.py      (none for webhook)
     /discord/
       ├── __init__.py
       ├── definition.py
       ├── triggers.py
       └── actions.py      (SendMessage action)
     /gmail/
       ...

□ Define abstract base classes:

   class IntegrationDefinition:
       name, id, icon_url, auth_type, auth_config
       triggers: list
       actions: list

   class BaseTrigger:
       id, name, input_schema, output_schema
       async def poll(credentials, config, last_poll) → list[dict]
       # OR
       async def handle_webhook(payload) → dict

   class BaseAction:
       id, name, input_schema, output_schema
       async def execute(credentials, config, input_data) → dict
```

**Afternoon: Build First 2 Integrations**

```
□ "Webhook" Integration:
   - Trigger: "Incoming Webhook"
     (your app generates a unique URL, external service POSTs to it)
   - No auth needed
   - Output: whatever JSON was received

□ "Discord" Integration:
   - Action: "Send Message via Webhook"
   - Auth type: none (Discord webhook URLs are self-authenticating)
   - Input: { webhook_url, message_content }
   - Implementation: httpx.post(webhook_url, json={content: message})

□ Build the integration registry
   - Auto-discovers all integrations
   - API endpoint: GET /integrations → returns all available integrations
   - API endpoint: GET /integrations/{id}/triggers
   - API endpoint: GET /integrations/{id}/actions

□ Test Discord action manually via API:
   POST /test-action with a real Discord webhook URL
   → Message appears in Discord
```

**End of Day 3 Deliverable:** Plugin architecture built. Discord message sends successfully via API call. Integration listing endpoint works.

---

## DAY 4: Workflow CRUD + GraphQL Setup

**Morning: GraphQL with Strawberry**

```
□ Set up Strawberry with FastAPI
□ Define GraphQL types:
   - WorkflowType
   - WorkflowStepType
   - IntegrationType
   - OperationType

□ Mutations:
   - createWorkflow(name) → Workflow
   - updateWorkflow(id, name, steps) → Workflow
   - deleteWorkflow(id) → Boolean
   - toggleWorkflow(id, active) → Workflow

□ Queries:
   - workflows → [Workflow]
   - workflow(id) → Workflow
   - integrations → [Integration]
```

**Afternoon: Workflow Steps Logic**

```
□ Saving workflow with steps:
   - Receive step definitions from frontend
   - Each step: { order, type, integration_id, operation_id,
                   connection_id, config }
   - Store config as JSONB
   - Validate step order (trigger must be step 1)

□ API to save full workflow (trigger + actions together)
□ Test via GraphQL playground:
   Create a workflow with 2 steps manually
   Verify it saves and loads correctly
```

**End of Day 4 Deliverable:** Full workflow CRUD via GraphQL. Can create, read, update, delete workflows with steps.

---

## DAY 5: The Execution Engine

**THE most critical day.**

**Morning: Celery Setup + Basic Executor**

```
□ Configure Celery with Redis broker
□ Set up Celery Beat (for scheduled polling)
□ Create the core execution task:

   Task: execute_workflow(workflow_id, trigger_data)

   Logic:
   1. Load workflow + all steps from DB
   2. Create WorkflowRun record (status: running)
   3. context = { "trigger": trigger_data }
   4. For each step (ordered):
      a. Resolve template variables in step config
      b. Get the integration + operation
      c. Get credentials (if needed)
      d. Create StepRun record (status: running)
      e. Call operation.execute(credentials, config, context)
      f. Store output in StepRun
      g. Add output to context: context[f"step_{order}"] = output
      h. If error → mark StepRun failed, mark WorkflowRun failed, stop
   5. Mark WorkflowRun as success
```

**Afternoon: Template Variable Resolution**

```
□ Build the variable resolver:
   Input: "Hello {{trigger.username}}, your email {{trigger.email}}"
   Context: { "trigger": { "username": "John", "email": "j@x.com" } }
   Output: "Hello John, your email j@x.com"

   - Use regex to find {{path.to.value}} patterns
   - Use a deep-get function to resolve from context
   - Handle missing values gracefully

□ Webhook trigger endpoint:
   POST /webhooks/{workflow_id}
   → Receives JSON payload
   → Queues execute_workflow task with payload as trigger_data

□ END TO END TEST:
   1. Create workflow: Webhook trigger → Discord action
   2. Configure Discord step with: "New webhook: {{trigger.message}}"
   3. POST to webhook URL with {"message": "Hello World"}
   4. See Discord message appear

   🎉 If this works, you have a working automation platform.
```

**End of Day 5 Deliverable:** First fully working automation. Webhook in → Discord message out. This is the project's "proof of life" moment.

---

## DAY 6: Frontend — Workflow Builder UI

**Full Day: React Flow Builder**

**Morning:**

```
□ Dashboard page:
   - Fetch workflows via GraphQL (Apollo Client)
   - Display as cards/list
   - Status badge (active/paused/draft)
   - Create new workflow button

□ Builder page — basic canvas:
   - React Flow canvas
   - Initial node: "Add Trigger" placeholder
   - "Add Step" button below
   - Each node shows: integration icon + operation name
```

**Afternoon:**

```
□ Right sidebar / panel when node is clicked:
   - Step 1: Choose integration (show grid of integration cards)
   - Step 2: Choose operation (trigger or action list)
   - Step 3: Configure fields
     - For now: simple input fields based on operation
     - Static values first (variable mapping comes later)

□ Save workflow button:
   - Serialize canvas nodes into workflow steps
   - Send to backend via GraphQL mutation
   - Show success toast

□ Style everything with Tailwind:
   - Dark theme
   - Integration icons/colors per node
   - Clean layout
```

**End of Day 6 Deliverable:** Visual workflow builder where you can add trigger + actions, configure them, and save.

---

## DAY 7: Connection System + More Integrations

**Morning: Connection/Credential Management**

```
□ Connection model + API endpoints:
   - Create connection (store encrypted API key / token)
   - List user's connections
   - Delete connection

□ Encryption service:
   - Use Python's cryptography library (Fernet)
   - Encrypt before storing, decrypt when executing

□ Frontend: Connections page
   - "Add connection" flow
   - For API key type: simple form (paste your API key)
   - For OAuth: redirect flow (do this for Gmail on Day 9)
```

**Afternoon: Add 2-3 More Integrations**

```
□ Slack Integration:
   - Action: Send Message (via webhook URL — easiest)
   - Auth: webhook URL as connection credential

□ HTTP/REST Generic Integration:
   - Action: "Make HTTP Request"
   - Config: { url, method, headers, body }
   - This is SUPER versatile for demos

□ OpenAI Integration:
   - Action: "Send Prompt to ChatGPT"
   - Auth: API key
   - Input: { prompt, model }
   - Output: { response_text }
   - This is a WOW factor integration
```

**End of Day 7 Deliverable:** 5 integrations working (Webhook, Discord, Slack, HTTP, OpenAI). Connection management functional.

---

## DAY 8: Execution History + Logging UI

**Morning: Backend Logging**

```
□ Ensure WorkflowRun and StepRun records are being
  created properly during execution
□ GraphQL queries:
   - workflowRuns(workflowId) → [WorkflowRun with StepRuns]
   - Include input_data, output_data, status, timestamps
□ Add timing data (started_at, completed_at, duration)
```

**Afternoon: Frontend History View**

```
□ Workflow detail page → "History" tab
   - List of runs with status badges (green/red/yellow)
   - Timestamp, duration

□ Run detail view:
   - Step-by-step timeline visualization
   - Each step: expandable card showing
     - Status icon
     - Input data (formatted JSON)
     - Output data (formatted JSON)
     - Error message if failed
     - Duration

□ This is EXTREMELY impressive in demos.
  Interviewers love seeing observability built in.
```

**End of Day 8 Deliverable:** Full execution history with step-by-step drill-down.

---

## DAY 9: Polling Triggers + OAuth Integration

**Morning: Polling System**

```
□ Celery Beat scheduled task:
   - Every 2-5 minutes: find all active workflows with polling triggers
   - For each: call trigger's poll() method
   - Deduplication:
     - Redis SET per workflow: "processed:{workflow_id}"
     - Check if item ID already in set → skip
     - Add new items to set
   - For each new item → queue execute_workflow task

□ Build GitHub integration with polling trigger:
   - Trigger: "New Star on Repository"
   - Poll: GET /repos/{owner}/{repo}/stargazers
     (check for new ones since last poll)
   - Action: not needed (use existing Discord/Slack actions)
```

**Afternoon: OAuth2 Flow (Google)**

```
□ Set up Google Cloud Console:
   - Create project
   - Enable Gmail API + Sheets API
   - Create OAuth2 credentials
   - Add redirect URI: http://localhost:8000/auth/google/callback

□ Backend OAuth endpoints:
   - GET /auth/google/start → redirect to Google consent screen
   - GET /auth/google/callback → exchange code for tokens
   - Store encrypted tokens as a Connection

□ Gmail Integration:
   - Trigger: "New Email" (polling — check every 5 min)
   - Action: "Send Email"

□ Google Sheets Integration:
   - Action: "Add Row to Spreadsheet"
```

**End of Day 9 Deliverable:** Polling triggers working. Gmail and Google Sheets connected via OAuth.

---

## DAY 10: Field Mapper UI + Variable System

**Morning: Variable Insertion in Frontend**

```
□ When configuring a step, show available variables
  from ALL previous steps

□ UI component: "Variable Picker"
   - Input field with a "+" or "{x}" button
   - Clicking opens dropdown showing:
     ├── Trigger Output
     │   ├── trigger.email
     │   ├── trigger.subject
     │   └── trigger.body
     └── Step 2 Output
         ├── step_2.response
         └── step_2.status

   - Clicking a variable inserts {{trigger.email}}
     into the input field
   - Show inserted variables as colored chips/pills

□ This is the feature that makes it FEEL like Zapier.
```

**Afternoon: Filter/Conditional Steps**

```
□ New step type: "Filter"
   - Condition builder UI:
     Field: {{trigger.amount}}
     Operator: greater than / equals / contains
     Value: 100

   - Backend: evaluate condition
     If true → continue to next step
     If false → skip remaining steps, mark run as "filtered"

□ This adds significant depth to your project.
```

**End of Day 10 Deliverable:** Dynamic field mapping with variable insertion. Filter steps working.

---

## DAY 11: More Integrations + Error Handling

**Morning: Add Remaining Integrations**

```
□ Telegram Bot:
   - Action: Send Message
   - Auth: Bot token (simple API key)

□ Notion:
   - Action: Create Page / Add to Database
   - Auth: OAuth2 or API key (internal integration)

□ Airtable:
   - Action: Create Record
   - Auth: API key / PAT

□ Target: 8-10 total integrations
```

**Afternoon: Robust Error Handling**

```
□ Retry logic in Celery:
   - Auto-retry failed tasks (max 3 attempts)
   - Exponential backoff (wait 30s, 60s, 120s)

□ Token refresh middleware:
   - Before executing OAuth-based step
   - Check if access_token expired
   - Auto-refresh using refresh_token
   - Update stored credentials

□ User-facing error messages:
   - "Gmail: Authentication expired. Please reconnect."
   - "Discord: Rate limited. Will retry in 60 seconds."
   - "Slack: Channel not found. Check your configuration."

□ Workflow auto-disable:
   - After 5 consecutive failures → pause workflow
   - Notify user (in-app notification or email)
```

**End of Day 11 Deliverable:** 8-10 integrations. Solid error handling with retries.

---

## DAY 12: Polish, Testing, Demo Workflows

**Morning: UI Polish**

```
□ Landing page:
   - Hero section explaining the product
   - Feature highlights with icons
   - "Get Started" CTA
   - Tech stack section (impressive for portfolio)

□ Dashboard improvements:
   - Run count per workflow
   - Last run timestamp
   - Success rate indicator
   - Empty states with illustrations

□ Builder improvements:
   - Smooth animations
   - Integration logos on nodes (use official brand colors)
   - Connection lines with animated dots
   - Loading states everywhere
   - Toast notifications for save/errors
```

**Afternoon: Create Demo Workflows**

```
□ Pre-build 3-4 showcase workflows:

   1. "Webhook → OpenAI → Discord"
      When webhook received → Ask ChatGPT to summarize →
      Post summary to Discord

   2. "GitHub New Star → Slack Notification"
      Poll GitHub stars → Send Slack message with star count

   3. "Gmail → Google Sheets"
      New email arrives → Log sender + subject to spreadsheet

   4. "Webhook → Filter → Telegram"
      Receive order data → Only if amount > $50 →
      Send Telegram alert

□ Test every workflow end-to-end manually
□ Fix all bugs found during testing
```

**End of Day 12 Deliverable:** Polished UI. Demo workflows working perfectly.

---

## DAY 13: Dockerize + Deploy

**Morning: Docker Setup**

```
□ Dockerfile for backend (FastAPI + Celery)
□ Dockerfile for frontend (React build + nginx)
□ docker-compose.yml with ALL services:
   - frontend (nginx)
   - backend (FastAPI/Uvicorn)
   - celery-worker
   - celery-beat
   - postgresql
   - redis

□ Test: docker-compose up → everything works
□ Environment variables properly externalized
□ .env.example file with all required vars documented
```

**Afternoon: Deploy**

```
□ Option A — Railway.app (easiest):
   - Deploy each service separately
   - Free PostgreSQL + Redis add-ons
   - Connect custom domain if you have one

□ Option B — Render.com:
   - Similar to Railway
   - Background workers supported

□ Option C — AWS EC2 (most impressive):
   - Single t2.micro instance (free tier)
   - Run docker-compose on it
   - Point domain to it

□ Verify deployed app works end-to-end:
   - Sign up on deployed URL
   - Create workflow
   - Trigger it
   - See execution history
```

**End of Day 13 Deliverable:** App deployed and accessible via public URL.

---

## DAY 14: README, Documentation, Final Touches

**Full Day: Portfolio Presentation**

```
□ README.md (THIS MATTERS ENORMOUSLY):
   - Project title + one-line description
   - Screenshot / GIF of the workflow builder in action
   - Architecture diagram (use draw.io or excalidraw)
   - Tech stack with justifications
   - Features list with checkmarks
   - How to run locally (docker-compose up)
   - API documentation link
   - Demo video link (record 2-3 min Loom video)
   - What I learned section
   - Future improvements section

□ Record demo video:
   - Walk through creating a workflow from scratch
   - Show it executing
   - Show execution history
   - Show multiple integrations
   - 2-3 minutes max

□ Architecture diagram showing:
   - Frontend → GraphQL → FastAPI → Celery → Redis
   - PostgreSQL for persistence
   - Integration plugin system
   - Webhook receiver flow
   - Polling flow

□ Final testing:
   - Test every integration one more time
   - Test error scenarios
   - Test on mobile viewport (responsive)
   - Fix any remaining bugs

□ Push clean commit history:
   - Squash messy commits
   - Write clear commit messages
   - Make sure no secrets are in git history
   - Add .gitignore properly
```

---

## DAILY TIME ALLOCATION SUMMARY

```
Day  1: Skeleton + Database              ████████ Foundation
Day  2: Authentication                   ████████ Foundation
Day  3: Integration Plugin Architecture  ████████ Core Architecture
Day  4: Workflow CRUD + GraphQL          ████████ Core Architecture
Day  5: Execution Engine                 ████████ ⭐ CRITICAL DAY
Day  6: Frontend Workflow Builder        ████████ ⭐ CRITICAL DAY
Day  7: Connections + More Integrations  ████████ Feature Building
Day  8: Execution History UI             ████████ Feature Building
Day  9: Polling + OAuth/Google           ████████ Feature Building
Day 10: Field Mapper + Filters           ████████ Feature Building
Day 11: More Integrations + Errors       ████████ Hardening
Day 12: Polish + Demo Workflows          ████████ Polish
Day 13: Docker + Deploy                  ████████ DevOps
Day 14: README + Documentation           ████████ Presentation
```

---

## CRITICAL SURVIVAL RULES FOR 2 WEEKS

**1. Do NOT perfectionist on Day 1-4.** Get things working ugly first. Polish on Day 12.

**2. Day 5 is make-or-break.** If the execution engine doesn't work by end of Day 5, everything falls apart. Spend extra hours if needed.

**3. Cut scope ruthlessly.** If by Day 9 you don't have OAuth working, skip it. Use only API-key-based integrations. A working project with 6 integrations beats a broken project with 10.

**4. Test end-to-end constantly.** After each day, manually run through the full flow: create workflow → execute → see results.

**5. Git commit after every working milestone.** Never lose progress.

**6. The builder UI is your portfolio hero.** Spend real time making it look and feel good. This is what people screenshot and share.

Start with Day 1 right now. Open your terminal, create the folder, and set up that `docker-compose.yml`.
