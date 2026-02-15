"""
End-to-end test for the workflow execution engine.

Prerequisites:
1. Terminal 1: uvicorn app.main:app --reload --port 8000
2. Terminal 2: celery -A app.workers.celery_app worker --loglevel=info
3. Terminal 3: python test_e2e.py
"""

import httpx
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMDgxN2UxNi0wNTg3LTRjYWUtOWQwYy1jNTNmMGE3NDIzNDEiLCJlbWFpbCI6ImFzaHZhdHRoMjcwNjIwMDZAZ21haWwuY29tIiwiZXhwIjoxNzcxMjU2NjMwfQ.HYNqfOoy_izIIg6XN3cGxmMQ2C-zSNs9KW2Pnf1h5yY"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1472616900612587693/Sfe9g2z2xg6Z4L3jVD_DjzlPy5b5xHalpmsYbMDou5_679gD1gO64zwQ0qagxH4-XxH6"

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def create_workflow():
    """Step 1: Create an active workflow with Discord integration."""
    print_section("🔧 STEP 1: Creating Workflow")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    payload = {
        "name": "E2E Test: Webhook → Discord",
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
                    "webhook_url": DISCORD_WEBHOOK,
                    "content": "🔥 Webhook received!\n\nMessage: {{trigger.message}}\nUser: {{trigger.user}}\nTimestamp: {{trigger.timestamp}}"
                }
            }
        ]
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_URL}/api/workflows/",
                headers=headers,
                json=payload,
                timeout=10.0
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Workflow created successfully!")
            print(f"   ID: {data['id']}")
            print(f"   Name: {data['name']}")
            print(f"   Status: {data['status']}")
            print(f"   Webhook Token: {data['webhook_token']}")
            print(f"   Steps: {len(data['steps'])}")
            return data['id'], data['webhook_token']
        else:
            print(f"❌ Failed to create workflow")
            print(f"Response: {response.text}")
            return None, None
            
    except httpx.ConnectError:
        print("❌ Connection Error: Is FastAPI running on port 8000?")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def fire_webhook(webhook_token):
    """Step 2: Fire the webhook with test data."""
    print_section("🚀 STEP 2: Firing Webhook")
    
    webhook_url = f"{BASE_URL}/api/webhooks/{webhook_token}"
    print(f"URL: {webhook_url}")
    
    payload = {
        "message": "Hello from E2E test! 🎉",
        "user": "Test User",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "e2e_test_script",
        "test_data": {
            "nested": "value",
            "count": 42,
            "active": True
        }
    }
    
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    try:
        with httpx.Client() as client:
            response = client.post(
                webhook_url,
                json=payload,
                timeout=10.0
            )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ Webhook accepted! Workflow execution queued.")
            return True
        else:
            print(f"\n❌ Webhook was not accepted")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_results():
    """Step 3: Tell user what to check."""
    print_section("📊 STEP 3: Verify Results")
    
    print("\n✅ What you should see now:\n")
    
    print("1️⃣  Terminal 1 (FastAPI) should show:")
    print("   - POST /api/workflows HTTP/1.1\" 200 OK")
    print("   - POST /api/webhooks/... HTTP/1.1\" 200 OK")
    
    print("\n2️⃣  Terminal 2 (Celery Worker) should show:")
    print("   - Task tasks.execute_workflow received")
    print("   - 🚀 Starting workflow execution")
    print("   - ✅ Loaded workflow: E2E Test: Webhook → Discord")
    print("   - ✅ Created WorkflowRun")
    print("   - 📍 Executing step 1: webhook.incoming_webhook")
    print("   - 📍 Executing step 2: discord.send_message")
    print("   - ✅ Action executed successfully")
    print("   - 🎉 Workflow execution completed successfully!")
    print("   - Task succeeded in X.Xs")
    
    print("\n3️⃣  Discord Channel should show:")
    print("   🔥 Webhook received!")
    print("   ")
    print("   Message: Hello from E2E test! 🎉")
    print("   User: Test User")
    print("   Timestamp: [current time]")
    
    print("\n" + "=" * 70)

def main():
    """Run the complete end-to-end test."""
    print("\n" + "=" * 70)
    print("🧪 END-TO-END TEST: Webhook → Celery → Discord")
    print("=" * 70)
    
    print("\nPrerequisites:")
    print("  ✓ Terminal 1: FastAPI running (uvicorn app.main:app --reload --port 8000)")
    print("  ✓ Terminal 2: Celery worker running (celery -A app.workers.celery_app worker --loglevel=info)")
    print("  ✓ Terminal 3: This test script")
    print("  ✓ Redis running (docker ps)")
    
    input("\nPress Enter when all prerequisites are ready...")
    
    # Step 1: Create workflow
    workflow_id, webhook_token = create_workflow()
    
    if not workflow_id or not webhook_token:
        print("\n❌ Test failed: Could not create workflow")
        return
    
    # Wait a moment for database sync
    print("\n⏳ Waiting 2 seconds for database sync...")
    time.sleep(2)
    
    # Step 2: Fire webhook
    success = fire_webhook(webhook_token)
    
    if not success:
        print("\n❌ Test failed: Webhook was not accepted")
        return
    
    # Wait for processing
    print("\n⏳ Waiting 3 seconds for Celery to process...")
    time.sleep(3)
    
    # Step 3: Verify
    verify_results()
    
    print("\n🎉 Test completed!")
    print("Check the terminals and Discord channel to verify everything worked.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
