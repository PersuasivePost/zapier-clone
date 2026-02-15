"""
Celery Tasks

This module contains all Celery tasks for workflow execution.

TASK NAMING CONVENTION:
- execute_workflow: Main task that runs a complete workflow
- poll_workflows: Scheduled task that checks for new data (polling triggers)
- retry_failed_workflow: Retry a failed workflow run

IMPORTANT: 
- Tasks use SYNCHRONOUS database access (app.core.database.get_sync_db)
- Integration actions are async and need asyncio.run() to execute
- All task arguments must be JSON-serializable (use string IDs, not UUIDs)
"""

from celery import Task
from app.workers.celery_app import celery_app

# ============================================================================
# UTILITY: Test Task
# ============================================================================

@celery_app.task(name="tasks.ping")
def ping():
    """Simple test task to verify Celery is working."""
    print("🏓 Pong!")
    return {"status": "success", "message": "pong"}


# ============================================================================
# MAIN WORKFLOW EXECUTION TASK
# ============================================================================

from typing import Dict, Any, Union
from uuid import UUID
from app.workers.executor import execute_workflow as run_workflow


@celery_app.task(
    name="tasks.execute_workflow",
    bind=True,                      # Allows access to self for retry functionality
    max_retries=3,                  # Retry up to 3 times on failure
    default_retry_delay=60,         # Wait 60 seconds before retrying
    acks_late=True,                 # Don't acknowledge until task completes (crash-safe)
    reject_on_worker_lost=True,     # Requeue task if worker crashes
    serializer='json',              # Use JSON serialization for arguments
    autoretry_for=(Exception,),     # Auto-retry on any exception
    retry_backoff=True,             # Exponential backoff: 60s, 120s, 240s
    retry_backoff_max=600,          # Max backoff delay: 10 minutes
    retry_jitter=True,              # Add random jitter to avoid thundering herd
)
def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a workflow from start to finish.
    
    This is the main task that gets called when a webhook arrives or
    a polling trigger finds new data.
    
    IMPORTANT: All arguments must be JSON-serializable!
    - workflow_id: Pass as string, NOT UUID object
    - trigger_data: Must be plain JSON (strings, numbers, dicts, lists)
    
    Args:
        workflow_id: UUID of the workflow to execute (as string, e.g., "abc-123-...")
        trigger_data: Data that triggered this workflow run (must be JSON-serializable)
    
    Returns:
        Dictionary with execution result:
        {
            "success": bool,
            "workflow_run_id": str,
            "status": str,
            "error": str (if failed)
        }
    
    Retry behavior:
        - Attempt 1: Immediate
        - Attempt 2: After 60 seconds
        - Attempt 3: After 120 seconds (exponential backoff)
        - Attempt 4: After 240 seconds
        - Then gives up and returns error
    
    Example:
        # Queue the task (non-blocking)
        result = execute_workflow.delay(
            workflow_id="abc-123-def-456",
            trigger_data={"message": "Hello", "user": "John"}
        )
        
        # Or with apply_async for more control
        result = execute_workflow.apply_async(
            args=[workflow_id, trigger_data],
            queue='high_priority',  # Use high-priority queue
            countdown=5             # Delay execution by 5 seconds
        )
    """
    try:
        print(f"\n{'='*70}")
        print(f"🚀 Starting workflow execution [Attempt {self.request.retries + 1}]")
        print(f"   Task ID: {self.request.id}")
        print(f"   Workflow ID: {workflow_id}")
        print(f"   Trigger data keys: {list(trigger_data.keys())}")
        print(f"{'='*70}\n")
        
        # Validate inputs
        if not workflow_id:
            raise ValueError("workflow_id cannot be empty")
        
        if not isinstance(trigger_data, dict):
            raise ValueError("trigger_data must be a dictionary")
        
        # Execute the workflow using the executor
        result = run_workflow(workflow_id, trigger_data)
        
        print(f"\n{'='*70}")
        print(f"✅ Workflow execution completed successfully")
        print(f"   Task ID: {self.request.id}")
        print(f"   Workflow Run ID: {result.get('workflow_run_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"{'='*70}\n")
        
        return result
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ Workflow execution failed [Attempt {self.request.retries + 1}]")
        print(f"   Task ID: {self.request.id}")
        print(f"   Workflow ID: {workflow_id}")
        print(f"   Error: {str(e)}")
        print(f"{'='*70}\n")
        
        # Import traceback for detailed error logging
        import traceback
        traceback.print_exc()
        
        # Celery will automatically retry based on autoretry_for configuration
        # The retry_backoff=True setting means delays will be exponential:
        # Attempt 2: 60s, Attempt 3: 120s, Attempt 4: 240s
        # retry_jitter adds randomness to prevent thundering herd
        
        if self.request.retries < self.max_retries:
            print(f"⏳ Will retry after backoff delay (attempt {self.request.retries + 2}/{self.max_retries + 1})...")
            # Re-raise to trigger auto-retry (Celery handles the backoff)
            raise
        else:
            print(f"⛔ Max retries ({self.max_retries}) exceeded - giving up")
            # Return error result instead of raising on final attempt
            # This ensures the task completes and doesn't stay in retry loop forever
            return {
                "success": False,
                "error": f"Max retries exceeded after {self.max_retries + 1} attempts: {str(e)}",
                "workflow_id": workflow_id,
                "attempts": self.request.retries + 1
            }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def queue_workflow_execution(
    workflow_id: Union[str, UUID],
    trigger_data: Dict[str, Any],
    priority: str = "default",
    delay: int = 0
) -> Any:
    """
    Helper function to queue a workflow execution task with proper UUID handling.
    
    This is a convenience wrapper that handles UUID conversion and provides
    a clean interface for queueing workflows from REST endpoints or webhooks.
    
    Args:
        workflow_id: UUID of the workflow (can be UUID object or string)
        trigger_data: Dictionary of trigger data (must be JSON-serializable)
        priority: Queue priority - "default", "high_priority", or "polling"
        delay: Optional delay in seconds before executing (countdown)
    
    Returns:
        AsyncResult object that can be used to check task status
    
    Example:
        # From a webhook endpoint
        result = queue_workflow_execution(
            workflow_id=workflow.id,  # UUID object is fine
            trigger_data=request.json(),
            priority="high_priority"
        )
        
        # Check status later
        if result.ready():
            print(result.get())
    """
    # Convert UUID to string if needed
    workflow_id_str = str(workflow_id)
    
    # Validate trigger_data is JSON-serializable
    import json
    try:
        json.dumps(trigger_data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"trigger_data must be JSON-serializable: {e}")
    
    # Queue the task
    if delay > 0:
        # Delayed execution
        return execute_workflow.apply_async(
            args=[workflow_id_str, trigger_data],
            queue=priority,
            countdown=delay
        )
    else:
        # Immediate execution
        return execute_workflow.apply_async(
            args=[workflow_id_str, trigger_data],
            queue=priority
        )


# ============================================================================
# POLLING TASK (for Day 9)
# ============================================================================

# @celery_app.task(name="tasks.poll_workflows")
# def poll_workflows(integration_id: str):
#     """
#     Poll for new data from integrations with polling triggers.
#     
#     Args:
#         integration_id: Which integration to poll (e.g., "gmail", "github")
#     """
#     pass


print("✅ Celery tasks module loaded")
