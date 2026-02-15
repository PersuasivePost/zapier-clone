"""
Test script to verify Celery tasks work correctly.
Run this while the Celery worker is running in another terminal.
"""
import time
from app.workers.tasks import ping

print("🧪 Testing Celery Task Execution")
print("=" * 60)

# Send task to queue
print("\n📤 Sending 'ping' task to Celery worker...")
result = ping.delay()

print(f"✅ Task sent! Task ID: {result.id}")
print(f"📊 Task state: {result.state}")

# Wait a bit for task to complete
print("\n⏳ Waiting for task to complete...")
time.sleep(2)

# Get result
try:
    output = result.get(timeout=5)
    print(f"\n✅ Task completed successfully!")
    print(f"📦 Result: {output}")
    print("\n🎉 Celery is working correctly!")
except Exception as e:
    print(f"\n❌ Error getting result: {e}")

print("=" * 60)
