"""
Celery Application Configuration

This is the Celery equivalent of FastAPI's app = FastAPI().
It configures the task queue system that executes workflows asynchronously.

ARCHITECTURE:
- Celery workers run in SEPARATE processes from FastAPI
- They use synchronous database connections (not async)
- They communicate via Redis message broker
- They can call async integration actions using asyncio.run()

PROCESS SEPARATION:
Terminal 1: uvicorn app.main:app --reload  (FastAPI server)
Terminal 2: celery -A app.workers.celery_app worker --loglevel=info  (Celery worker)
Terminal 3: celery -A app.workers.celery_app beat --loglevel=info  (Celery Beat scheduler)
"""

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

from app.core.config import get_settings

settings = get_settings()

# ============================================================================
# CELERY APPLICATION INSTANCE
# ============================================================================

celery_app = Celery(
    "flowforge_workers",
    broker=settings.CELERY_BROKER_URL or settings.REDIS_URL,
    backend=settings.REDIS_URL.replace("/0", "/1"),  # Use different Redis DB for results
)

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_acks_late=True,  # Acknowledge task after execution, not before
    task_reject_on_worker_lost=True,  # Reject task if worker crashes
    
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Task routing
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # Process one task at a time (prevents task hogging)
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (prevents memory leaks)
    
    # Task result configuration
    task_track_started=True,  # Track when tasks start (useful for monitoring)
    task_time_limit=300,  # Hard time limit: 5 minutes
    task_soft_time_limit=240,  # Soft time limit: 4 minutes (raises exception)
    
    # Beat scheduler configuration (for polling triggers)
    beat_schedule={
        # Polling tasks will be added here in Day 9
        # Example:
        # "poll-gmail-every-5-minutes": {
        #     "task": "app.workers.tasks.poll_workflows",
        #     "schedule": 300.0,  # Every 5 minutes
        #     "args": ("gmail",),
        # },
    },
    
    # Task discovery - tell Celery where to find task modules
    imports=[
        "app.workers.tasks",  # Main task module (we'll create this next)
    ],
)

# ============================================================================
# TASK QUEUES (for prioritization)
# ============================================================================

celery_app.conf.task_queues = (
    # Default queue for workflow execution
    Queue("default", Exchange("default"), routing_key="default"),
    
    # High priority queue for urgent workflows
    Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
    
    # Low priority queue for polling/scheduled tasks
    Queue("polling", Exchange("polling"), routing_key="polling"),
)

# ============================================================================
# CELERY EVENTS (optional monitoring hooks)
# ============================================================================

@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery is working."""
    print(f"Request: {self.request!r}")
    return "pong"


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

print("=" * 70)
print("🔧 Celery Configuration Loaded")
print("=" * 70)
print(f"Broker: {celery_app.conf.broker_url}")
print(f"Backend: {celery_app.conf.result_backend}")
print(f"Task Serializer: {celery_app.conf.task_serializer}")
print(f"Timezone: {celery_app.conf.timezone}")
print(f"Worker Prefetch: {celery_app.conf.worker_prefetch_multiplier}")
print("=" * 70)
print("\n💡 To start worker: celery -A app.workers.celery_app worker --loglevel=info")
print("💡 To start beat: celery -A app.workers.celery_app beat --loglevel=info")
print("=" * 70)
