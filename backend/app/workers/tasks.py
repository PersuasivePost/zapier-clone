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
# This will be implemented in the next step

# @celery_app.task(name="tasks.execute_workflow", bind=True)
# def execute_workflow(self, workflow_id: str, trigger_data: dict):
#     """
#     Execute a complete workflow step by step.
#     
#     Args:
#         workflow_id: String UUID of the workflow to execute
#         trigger_data: Dictionary containing the trigger data
#         
#     Returns:
#         Dictionary with execution results
#     """
#     pass


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
