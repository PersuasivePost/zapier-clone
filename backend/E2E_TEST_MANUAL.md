# Manual E2E Test Instructions

## Prerequisites

Make sure you have 3 terminals open:

**Terminal 1** - FastAPI Server:

```bash
cd backend
source ../.venv/Scripts/activate  # or .venv/Scripts/activate on Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2** - Celery Worker:

```bash
cd backend
source ../.venv/Scripts/activate
celery -A app.workers.celery_app worker --loglevel=info
```

**Terminal 3** - For running tests (this terminal)

---

## Step 1: Create Workflow

In Terminal 3, run:

```bash
curl -X POST http://localhost:8000/api/workflows \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMDgxN2UxNi0wNTg3LTRjYWUtOWQwYy1jNTNmMGE3NDIzNDEiLCJlbWFpbCI6ImFzaHZhdHRoMjcwNjIwMDZAZ21haWwuY29tIiwiZXhwIjoxNzcxMjU2NjMwfQ.HYNqfOoy_izIIg6XN3cGxmMQ2C-zSNs9KW2Pnf1h5yY" \
  -d '{
    "name": "E2E Test: Webhook to Discord",
    "status": "active",
    "steps": [
      {
        "step_order": 1,
        "step_type": "trigger",
        "integration_id": "webhook",
        "operation_id": "incoming_webhook",
        "config": {}
      },
      {
        "step_order": 2,
        "step_type": "action",
        "integration_id": "discord",
        "operation_id": "send_message",
        "config": {
          "webhook_url": "https://discord.com/api/webhooks/1472616900612587693/Sfe9g2z2xg6Z4L3jVD_DjzlPy5b5xHalpmsYbMDou5_679gD1gO64zwQ0qagxH4-XxH6",
          "content": "🔥 Webhook received!\n\nMessage: {{trigger.message}}\nUser: {{trigger.user}}"
        }
      }
    ]
  }'
```

**Copy the `webhook_token` from the response!**

Example response:

```json
{
  "id": "abc-123-...",
  "webhook_token": "XYZ789...",
  "name": "E2E Test: Webhook to Discord",
  "status": "active"
}
```

---

## Step 2: Fire the Webhook

Replace `YOUR_WEBHOOK_TOKEN` with the token from Step 1:

```bash
curl -X POST http://localhost:8000/api/webhooks/YOUR_WEBHOOK_TOKEN \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from test!",
    "user": "Test User",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

Expected response:

```json
{
  "status": "accepted",
  "message": "Workflow execution queued"
}
```

---

## Step 3: Verify Results

### Terminal 1 (FastAPI) should show:

```
INFO:     127.0.0.1 - "POST /api/webhooks/YOUR_TOKEN HTTP/1.1" 200 OK
```

### Terminal 2 (Celery Worker) should show:

```
[2024-01-15 10:30:00] Task tasks.execute_workflow[abc-123] received
[2024-01-15 10:30:00] 🚀 Starting workflow execution
[2024-01-15 10:30:00]    Workflow ID: abc-123
[2024-01-15 10:30:00] ✅ Loaded workflow: E2E Test: Webhook to Discord
[2024-01-15 10:30:00] ✅ Created WorkflowRun: xyz-789
[2024-01-15 10:30:00]
[2024-01-15 10:30:00] 📍 Executing step 1: webhook.incoming_webhook
[2024-01-15 10:30:00]    ⚡ Trigger step - recording trigger data
[2024-01-15 10:30:00]    ✅ Trigger step completed
[2024-01-15 10:30:00]
[2024-01-15 10:30:00] 📍 Executing step 2: discord.send_message
[2024-01-15 10:30:00]    ⚡ Action step - executing discord.send_message
[2024-01-15 10:30:00]    Resolved config: {...}
[2024-01-15 10:30:01]    ✅ Action executed successfully
[2024-01-15 10:30:01]
[2024-01-15 10:30:01] 🎉 Workflow execution completed successfully!
[2024-01-15 10:30:01] Task tasks.execute_workflow[abc-123] succeeded in 1.5s
```

### Discord Channel should show:

```
🔥 Webhook received!

Message: Hello from test!
User: Test User
```

---

## Troubleshooting

### If workflow creation fails:

- Check Terminal 1 for errors
- Verify your auth token is valid
- Make sure database is accessible

### If webhook returns 404:

- Check you copied the correct `webhook_token`
- Verify workflow was created with `status: "active"`

### If Celery doesn't process the task:

- Check Terminal 2 is running
- Verify Redis is running: `docker ps`
- Check Celery can see the task: Look for `tasks.execute_workflow` in startup logs

### If Discord message doesn't appear:

- Check Terminal 2 for error messages
- Verify Discord webhook URL is correct
- Check Discord channel permissions

---

## Success Criteria

✅ All three terminals show activity  
✅ FastAPI returns 200 OK  
✅ Celery worker processes the task  
✅ Message appears in Discord  
✅ No error messages in any terminal

If all checks pass: **YOUR AUTOMATION PLATFORM IS WORKING! 🎉**
