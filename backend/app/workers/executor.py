"""
Workflow Executor

This is the core execution engine that runs workflows step by step.

EXECUTION FLOW:
1. Load workflow and steps from database
2. Create WorkflowRun record (status: RUNNING)
3. Initialize context with trigger data
4. For each step in order:
   - Create StepRun record
   - Resolve template variables in config
   - Execute the step (trigger/action/filter)
   - Store output and update context
   - Handle errors
5. Mark workflow as SUCCESS or FAILED

CONTEXT STRUCTURE:
{
    "trigger": { ...trigger data... },
    "step_2": { ...step 2 output... },
    "step_3": { ...step 3 output... },
    ...
}

Each step can reference previous steps via templates:
- {{trigger.field}}
- {{step_2.output_field}}
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_sync_db
from app.models.workflow import Workflow, WorkflowStatus
from app.models.workflow_step import WorkflowStep, StepType
from app.models.workflow_run import WorkflowRun, RunStatus
from app.models.step_run import StepRun, StepRunStatus
from app.models.connection import Connection
from app.services.template_resolver import resolve_step_config
from app.integrations import integration_registry


class WorkflowExecutor:
    """
    Executes a workflow step by step.
    
    This class maintains execution state (context, database session, current run)
    and orchestrates the entire workflow execution process.
    """
    
    def __init__(self, workflow_id: str, trigger_data: Dict[str, Any]):
        """
        Initialize the executor.
        
        Args:
            workflow_id: UUID of the workflow to execute (as string)
            trigger_data: Data that triggered this workflow run
        """
        self.workflow_id = UUID(workflow_id)
        self.trigger_data = trigger_data
        self.db: Optional[Session] = None
        self.workflow: Optional[Workflow] = None
        self.workflow_run: Optional[WorkflowRun] = None
        self.context: Dict[str, Any] = {}
        
    def execute(self) -> Dict[str, Any]:
        """
        Main entry point - execute the entire workflow.
        
        Returns:
            Dictionary with execution result:
            {
                "success": bool,
                "workflow_run_id": str,
                "status": str,
                "error": str (if failed)
            }
        """
        try:
            # Get database session
            from app.core.database import SyncSessionLocal
            self.db = SyncSessionLocal()
            
            # Load workflow
            if not self._load_workflow():
                return {
                    "success": False,
                    "error": "Workflow not found or not active"
                }
            
            # Create workflow run record
            self._create_workflow_run()
            
            # Initialize context with trigger data
            self.context["trigger"] = self.trigger_data
            
            # Execute all steps in order
            self._execute_steps()
            
            # If we got here, all steps succeeded
            self._mark_success()
            
            return {
                "success": True,
                "workflow_run_id": str(self.workflow_run.id),
                "status": "success"
            }
            
        except Exception as e:
            # Top-level error handler (shouldn't normally reach here)
            print(f"❌ FATAL ERROR in workflow executor: {e}")
            import traceback
            traceback.print_exc()
            
            if self.workflow_run:
                self._mark_failure(str(e), error_step_order=None)
            
            return {
                "success": False,
                "workflow_run_id": str(self.workflow_run.id) if self.workflow_run else None,
                "status": "failed",
                "error": str(e)
            }
            
        finally:
            # Always close database session
            if self.db:
                self.db.close()
    
    def _load_workflow(self) -> bool:
        """
        Load workflow from database with all steps.
        
        Returns:
            True if workflow found and active, False otherwise
        """
        # Load workflow with steps eagerly loaded
        stmt = (
            select(Workflow)
            .where(Workflow.id == self.workflow_id)
            .options(selectinload(Workflow.steps))
        )
        result = self.db.execute(stmt)
        self.workflow = result.scalar_one_or_none()
        
        if not self.workflow:
            print(f"❌ Workflow {self.workflow_id} not found")
            return False
        
        if self.workflow.status != WorkflowStatus.ACTIVE:
            print(f"❌ Workflow {self.workflow_id} is not active (status: {self.workflow.status})")
            return False
        
        if not self.workflow.steps:
            print(f"❌ Workflow {self.workflow_id} has no steps")
            return False
        
        print(f"✅ Loaded workflow: {self.workflow.name} ({len(self.workflow.steps)} steps)")
        return True
    
    def _create_workflow_run(self):
        """Create WorkflowRun record to track this execution."""
        self.workflow_run = WorkflowRun(
            workflow_id=self.workflow.id,
            status=RunStatus.RUNNING,
            trigger_data=self.trigger_data,
            started_at=datetime.utcnow(),
            attempt_number=1,
        )
        self.db.add(self.workflow_run)
        self.db.commit()
        self.db.refresh(self.workflow_run)
        
        print(f"✅ Created WorkflowRun: {self.workflow_run.id}")
    
    def _execute_steps(self):
        """
        Execute all workflow steps in order.
        
        Handles trigger steps, action steps, and filter steps.
        Stops on first error or filter that blocks execution.
        """
        steps = sorted(self.workflow.steps, key=lambda s: s.step_order)
        
        for step in steps:
            print(f"\n📍 Executing step {step.step_order}: {step.integration_id}.{step.operation_id}")
            
            try:
                # Create step run record
                step_run = self._create_step_run(step)
                
                # Handle different step types
                if step.step_order == 1:
                    # Trigger step - already fired, just record the data
                    self._execute_trigger_step(step, step_run)
                
                elif step.step_type == StepType.FILTER:
                    # Filter step - evaluate condition
                    should_continue = self._execute_filter_step(step, step_run)
                    if not should_continue:
                        # Filter blocked execution - mark remaining steps as skipped
                        self._skip_remaining_steps(steps, step.step_order)
                        return  # Stop execution
                
                elif step.step_type == StepType.ACTION:
                    # Action step - execute the action
                    self._execute_action_step(step, step_run)
                
                else:
                    # Other step types (delay, transform) - not implemented yet
                    print(f"⚠️  Step type {step.step_type} not yet implemented, skipping")
                    step_run.status = StepRunStatus.SKIPPED
                    step_run.completed_at = datetime.utcnow()
                    self.db.commit()
                
            except Exception as e:
                # Step execution failed
                print(f"❌ Step {step.step_order} failed: {e}")
                import traceback
                traceback.print_exc()
                
                self._handle_step_failure(step, step_run, str(e))
                self._skip_remaining_steps(steps, step.step_order)
                
                # Raise to stop execution
                raise
    
    def _create_step_run(self, step: WorkflowStep) -> StepRun:
        """
        Create StepRun record to track this step's execution.
        
        Args:
            step: The workflow step being executed
        
        Returns:
            The created StepRun record
        """
        step_run = StepRun(
            workflow_run_id=self.workflow_run.id,
            workflow_step_id=step.id,
            step_order=step.step_order,
            integration_id=step.integration_id,
            operation_id=step.operation_id,
            status=StepRunStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self.db.add(step_run)
        self.db.commit()
        self.db.refresh(step_run)
        
        return step_run
    
    def _execute_trigger_step(self, step: WorkflowStep, step_run: StepRun):
        """
        Handle trigger step execution.
        
        The trigger already fired (that's why we're here), so we just
        record the trigger data as this step's output.
        
        Args:
            step: The trigger step
            step_run: The step run record
        """
        print(f"   ⚡ Trigger step - recording trigger data")
        
        # Store trigger data as output
        step_run.input_data = {}
        step_run.output_data = self.trigger_data
        step_run.status = StepRunStatus.SUCCESS
        step_run.completed_at = datetime.utcnow()
        
        # Calculate duration
        if step_run.started_at and step_run.completed_at:
            duration = (step_run.completed_at - step_run.started_at).total_seconds() * 1000
            step_run.duration_ms = int(duration)
        
        self.db.commit()
        
        # Trigger data is already in context (added in execute())
        print(f"   ✅ Trigger step completed")
    
    def _execute_filter_step(self, step: WorkflowStep, step_run: StepRun) -> bool:
        """
        Handle filter step execution.
        
        Evaluates a condition and decides whether to continue or stop.
        
        Args:
            step: The filter step
            step_run: The step run record
        
        Returns:
            True if workflow should continue, False if filtered (stopped)
        """
        print(f"   🔍 Filter step - evaluating condition")
        
        # Resolve template variables in config
        resolved_config = resolve_step_config(step.config, self.context)
        step_run.input_data = resolved_config
        
        # TODO: Implement actual filter logic
        # For now, just pass through (always continue)
        # Real implementation would evaluate:
        #   field_value = resolved_config.get("field")
        #   operator = resolved_config.get("operator")
        #   compare_value = resolved_config.get("value")
        #   result = evaluate_condition(field_value, operator, compare_value)
        
        should_continue = True  # Placeholder
        
        if should_continue:
            step_run.status = StepRunStatus.SUCCESS
            step_run.output_data = {"passed": True}
            print(f"   ✅ Filter passed - continuing")
        else:
            step_run.status = StepRunStatus.FILTERED
            step_run.output_data = {"passed": False}
            self.workflow_run.status = RunStatus.FILTERED
            print(f"   ⛔ Filter blocked - stopping workflow")
        
        step_run.completed_at = datetime.utcnow()
        
        # Calculate duration
        if step_run.started_at and step_run.completed_at:
            duration = (step_run.completed_at - step_run.started_at).total_seconds() * 1000
            step_run.duration_ms = int(duration)
        
        self.db.commit()
        
        return should_continue
    
    def _execute_action_step(self, step: WorkflowStep, step_run: StepRun):
        """
        Handle action step execution.
        
        This is the main execution path:
        1. Resolve template variables in config
        2. Get integration and action from registry
        3. Get credentials if needed
        4. Execute the action
        5. Store result and update context
        
        Args:
            step: The action step
            step_run: The step run record
        """
        print(f"   🚀 Action step - executing {step.integration_id}.{step.operation_id}")
        
        # 1. Resolve template variables in config
        resolved_config = resolve_step_config(step.config, self.context)
        step_run.input_data = resolved_config
        self.db.commit()  # Save input_data immediately
        
        print(f"   📝 Resolved config: {resolved_config}")
        
        # 2. Get integration and action from registry
        integration = integration_registry.get_integration(step.integration_id)
        if not integration:
            raise Exception(f"Integration '{step.integration_id}' not found in registry")
        
        action = integration.get_action(step.operation_id)
        if not action:
            raise Exception(f"Action '{step.operation_id}' not found in integration '{step.integration_id}'")
        
        # 3. Get credentials if needed
        credentials = self._get_credentials_for_step(step)
        
        # 4. Execute the action
        # Actions are async, but Celery tasks are sync, so we use asyncio.run()
        print(f"   ⏳ Calling action.execute()...")
        result = asyncio.run(action.execute(credentials, resolved_config))
        
        print(f"   📦 Action result: {result}")
        
        # 5. Store result
        step_run.output_data = result
        step_run.status = StepRunStatus.SUCCESS
        step_run.completed_at = datetime.utcnow()
        
        # Calculate duration
        if step_run.started_at and step_run.completed_at:
            duration = (step_run.completed_at - step_run.started_at).total_seconds() * 1000
            step_run.duration_ms = int(duration)
        
        self.db.commit()
        
        # 6. Add to context for next steps
        self.context[f"step_{step.step_order}"] = result
        
        print(f"   ✅ Action step completed")
    
    def _get_credentials_for_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Get decrypted credentials for a step.
        
        Args:
            step: The workflow step
        
        Returns:
            Dictionary of credentials (empty dict if no connection needed)
        """
        if step.connection_id is None:
            # No connection needed (e.g., webhook actions where URL is in config)
            return {}
        
        # Load connection
        connection = self.db.get(Connection, step.connection_id)
        if not connection:
            raise Exception(f"Connection {step.connection_id} not found")
        
        # TODO: Implement actual decryption on Day 7
        # For now, return empty dict
        # Real implementation:
        #   from app.core.security import decrypt_credentials
        #   return decrypt_credentials(connection.credentials_encrypted)
        
        print(f"   🔑 Using connection: {connection.display_name}")
        return {}
    
    def _handle_step_failure(self, step: WorkflowStep, step_run: StepRun, error_message: str):
        """
        Handle step execution failure.
        
        Updates the step run and workflow run with error information.
        
        Args:
            step: The step that failed
            step_run: The step run record
            error_message: Error message
        """
        # Update step run
        step_run.status = StepRunStatus.FAILED
        step_run.error_message = error_message
        step_run.completed_at = datetime.utcnow()
        
        # Calculate duration
        if step_run.started_at and step_run.completed_at:
            duration = (step_run.completed_at - step_run.started_at).total_seconds() * 1000
            step_run.duration_ms = int(duration)
        
        self.db.commit()
        
        # Update workflow run
        self._mark_failure(error_message, step.step_order)
    
    def _skip_remaining_steps(self, all_steps, failed_step_order: int):
        """
        Mark all remaining steps as SKIPPED.
        
        Called when a step fails or a filter blocks execution.
        
        Args:
            all_steps: List of all workflow steps
            failed_step_order: The step order that failed or filtered
        """
        remaining_steps = [s for s in all_steps if s.step_order > failed_step_order]
        
        print(f"   ⏭️  Skipping {len(remaining_steps)} remaining steps")
        
        for step in remaining_steps:
            step_run = StepRun(
                workflow_run_id=self.workflow_run.id,
                workflow_step_id=step.id,
                step_order=step.step_order,
                integration_id=step.integration_id,
                operation_id=step.operation_id,
                status=StepRunStatus.SKIPPED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            self.db.add(step_run)
        
        self.db.commit()
    
    def _mark_success(self):
        """Mark workflow run and workflow as successful."""
        # Update workflow run
        self.workflow_run.status = RunStatus.SUCCESS
        self.workflow_run.completed_at = datetime.utcnow()
        
        # Update workflow
        self.workflow.last_run_at = datetime.utcnow()
        self.workflow.consecutive_failures = 0
        
        self.db.commit()
        
        print(f"\n🎉 Workflow execution completed successfully!")
    
    def _mark_failure(self, error_message: str, error_step_order: Optional[int]):
        """
        Mark workflow run and workflow as failed.
        
        Args:
            error_message: Error message
            error_step_order: Step order where error occurred (None for top-level errors)
        """
        # Update workflow run
        self.workflow_run.status = RunStatus.FAILED
        self.workflow_run.error_message = error_message
        self.workflow_run.error_step_order = error_step_order
        self.workflow_run.completed_at = datetime.utcnow()
        
        # Update workflow
        self.workflow.consecutive_failures += 1
        
        # Auto-disable after 5 consecutive failures
        if self.workflow.consecutive_failures >= 5:
            self.workflow.status = WorkflowStatus.ERROR
            print(f"⚠️  Workflow auto-disabled after 5 consecutive failures")
        
        self.db.commit()
        
        print(f"\n❌ Workflow execution failed: {error_message}")


def execute_workflow(workflow_id: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a workflow (convenience function).
    
    This is the function that will be called from the Celery task.
    
    Args:
        workflow_id: UUID of the workflow to execute (as string)
        trigger_data: Data that triggered this workflow run
    
    Returns:
        Dictionary with execution result
    """
    executor = WorkflowExecutor(workflow_id, trigger_data)
    return executor.execute()
