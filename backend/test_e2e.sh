#!/bin/bash
# End-to-End Test Script
# Run this in a separate terminal while FastAPI and Celery worker are running

set -e

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMDgxN2UxNi0wNTg3LTRjYWUtOWQwYy1jNTNmMGE3NDIzNDEiLCJlbWFpbCI6ImFzaHZhdHRoMjcwNjIwMDZAZ21haWwuY29tIiwiZXhwIjoxNzcxMjU2NjMwfQ.HYNqfOoy_izIIg6XN3cGxmMQ2C-zSNs9KW2Pnf1h5yY"
DISCORD_WEBHOOK="https://discord.com/api/webhooks/1472616900612587693/Sfe9g2z2xg6Z4L3jVD_DjzlPy5b5xHalpmsYbMDou5_679gD1gO64zwQ0qagxH4-XxH6"

echo "======================================================================"
echo "🧪 END-TO-END TEST: Webhook → Celery → Discord"
echo "======================================================================"
echo ""
echo "Prerequisites:"
echo "  ✓ Terminal 1: FastAPI running (uvicorn app.main:app --reload --port 8000)"
echo "  ✓ Terminal 2: Celery worker running (celery -A app.workers.celery_app worker --loglevel=info)"
echo "  ✓ Terminal 3: This script"
echo ""
echo "======================================================================"

# Step 1: Create workflow
echo ""
echo "STEP 1: Creating workflow..."
echo "======================================================================"

WORKFLOW_RESPONSE=$(curl -s -X POST http://localhost:8000/api/workflows \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
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
          "webhook_url": "'"$DISCORD_WEBHOOK"'",
          "content": "🔥 Webhook received!\n\nMessage: {{trigger.message}}\nUser: {{trigger.user}}\nTimestamp: {{trigger.timestamp}}"
        }
      }
    ]
  }')

echo "Response: $WORKFLOW_RESPONSE"
echo ""

# Extract workflow_id and webhook_token
WORKFLOW_ID=$(echo $WORKFLOW_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"\([^"]*\)"/\1/')
WEBHOOK_TOKEN=$(echo $WORKFLOW_RESPONSE | grep -o '"webhook_token":"[^"]*"' | sed 's/"webhook_token":"\([^"]*\)"/\1/')

if [ -z "$WORKFLOW_ID" ]; then
    echo "❌ Failed to create workflow or extract workflow_id"
    echo "Response: $WORKFLOW_RESPONSE"
    exit 1
fi

echo "✅ Workflow created!"
echo "   ID: $WORKFLOW_ID"
echo "   Webhook Token: $WEBHOOK_TOKEN"
echo ""

# Step 2: Wait a moment for database to sync
echo "⏳ Waiting 2 seconds for database sync..."
sleep 2

# Step 3: Fire the webhook
echo ""
echo "STEP 2: Firing webhook..."
echo "======================================================================"
echo "URL: http://localhost:8000/api/webhooks/$WEBHOOK_TOKEN"
echo ""

WEBHOOK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/webhooks/$WEBHOOK_TOKEN \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from end-to-end test!",
    "user": "Test User",
    "timestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
    "source": "test_script",
    "test_data": {
      "nested": "value",
      "count": 42
    }
  }')

echo "Response: $WEBHOOK_RESPONSE"
echo ""

# Check if webhook was accepted
if echo "$WEBHOOK_RESPONSE" | grep -q "accepted"; then
    echo "✅ Webhook accepted! Workflow execution queued."
    echo ""
    echo "======================================================================"
    echo "📊 WHAT TO CHECK NOW:"
    echo "======================================================================"
    echo ""
    echo "1. Terminal 1 (FastAPI) should show:"
    echo "   - POST /api/webhooks/$WEBHOOK_TOKEN"
    echo "   - 200 OK response"
    echo ""
    echo "2. Terminal 2 (Celery Worker) should show:"
    echo "   - Task received: tasks.execute_workflow"
    echo "   - Loading workflow: E2E Test: Webhook to Discord"
    echo "   - Executing step 1: webhook.incoming_webhook"
    echo "   - Executing step 2: discord.send_message"
    echo "   - Task succeeded"
    echo ""
    echo "3. Check your Discord channel for the message:"
    echo "   🔥 Webhook received!"
    echo "   Message: Hello from end-to-end test!"
    echo "   User: Test User"
    echo "   Timestamp: [current time]"
    echo ""
    echo "======================================================================"
else
    echo "❌ Webhook was not accepted!"
    echo "Response: $WEBHOOK_RESPONSE"
    exit 1
fi

echo ""
echo "🎉 Test completed! Check the outputs above and your Discord channel."
echo ""
