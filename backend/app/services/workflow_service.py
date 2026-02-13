from typing import List, Optional
import uuid
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow, WorkflowStatus
from app.models.workflow_step import WorkflowStep
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate
from app.schemas.workflow_step import WorkflowStepCreate
from app.integrations import integration_registry


async def create_workflow(db: AsyncSession, user_id: uuid.UUID, data: WorkflowCreate) -> Workflow:
    # 1. Create workflow instance
    workflow = Workflow(
        user_id=user_id,
        name=data.name,
        description=data.description,
        polling_interval=data.polling_interval,
        status=WorkflowStatus.DRAFT,
    )

    db.add(workflow)
    await db.flush()

    # 3. If steps provided, validate and create
    if data.steps:
        await _validate_and_create_steps(db, workflow.id, data.steps)

    await db.commit()
    await db.refresh(workflow)
    return workflow


async def get_workflows(db: AsyncSession, user_id: uuid.UUID) -> List[Workflow]:
    stmt = (
        select(Workflow)
        .where(Workflow.user_id == user_id)
        .options(selectinload(Workflow.steps))
        .order_by(Workflow.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_workflow(db: AsyncSession, user_id: uuid.UUID, workflow_id: uuid.UUID) -> Workflow:
    stmt = (
        select(Workflow)
        .where(Workflow.id == workflow_id)
        .options(selectinload(Workflow.steps))
    )
    result = await db.execute(stmt)
    workflow = result.scalar_one_or_none()
    if not workflow or workflow.user_id != user_id:
        raise ValueError("Workflow not found")
    return workflow


async def update_workflow(db: AsyncSession, user_id: uuid.UUID, workflow_id: uuid.UUID, data: WorkflowUpdate) -> Workflow:
    # Fetch and validate ownership
    workflow = await get_workflow(db, user_id, workflow_id)

    # Update fields
    if data.name is not None:
        workflow.name = data.name
    if data.description is not None:
        workflow.description = data.description
    if data.polling_interval is not None:
        workflow.polling_interval = data.polling_interval

    # Handle status change
    if data.status is not None:
        # Validate activating only if steps exist and first step is a trigger
        if data.status == WorkflowStatus.ACTIVE:
            if not workflow.steps:
                raise ValueError("Cannot activate workflow with no steps")
            if workflow.steps[0].step_type.name.lower() != "trigger":
                raise ValueError("First step must be a trigger")
        workflow.status = data.status

    # Replace steps if provided
    if data.steps is not None:
        # Delete existing steps
        await db.execute(delete(WorkflowStep).where(WorkflowStep.workflow_id == workflow.id))
        await db.flush()
        await _validate_and_create_steps(db, workflow.id, data.steps)

    await db.commit()
    await db.refresh(workflow)
    return workflow


async def delete_workflow(db: AsyncSession, user_id: uuid.UUID, workflow_id: uuid.UUID) -> bool:
    workflow = await get_workflow(db, user_id, workflow_id)
    await db.delete(workflow)
    await db.commit()
    return True


async def toggle_workflow(db: AsyncSession, user_id: uuid.UUID, workflow_id: uuid.UUID) -> Workflow:
    workflow = await get_workflow(db, user_id, workflow_id)

    if workflow.status == WorkflowStatus.ACTIVE:
        workflow.status = WorkflowStatus.PAUSED
    else:
        # Activating from DRAFT or PAUSED
        if not workflow.steps:
            raise ValueError("Cannot activate workflow with no steps")
        if workflow.steps[0].step_type.name.lower() != "trigger":
            raise ValueError("First step must be a trigger")
        workflow.status = WorkflowStatus.ACTIVE
        workflow.consecutive_failures = 0

    await db.commit()
    await db.refresh(workflow)
    return workflow


async def _validate_and_create_steps(db: AsyncSession, workflow_id: uuid.UUID, steps: List[WorkflowStepCreate]):
    # Validate sequential order and single trigger at position 1
    orders = [s.step_order for s in steps]
    if sorted(orders) != list(range(1, len(orders) + 1)):
        raise ValueError("step_order values must be sequential starting at 1")

    # Validate first step is a trigger
    first = steps[0]
    if first.step_type.name.lower() != "trigger":
        raise ValueError("First step must be a trigger")

    # Validate integrations and operations
    for s in steps:
        integ = integration_registry.get_integration(s.integration_id)
        if not integ:
            raise ValueError(f"Integration '{s.integration_id}' does not exist")
        # Check operation exists as either trigger or action
        op = integ.get_action(s.operation_id) or integ.get_trigger(s.operation_id)
        if not op:
            raise ValueError(f"Operation '{s.operation_id}' not found in integration '{s.integration_id}'")

        step = WorkflowStep(
            workflow_id=workflow_id,
            step_order=s.step_order,
            step_type=s.step_type,
            integration_id=s.integration_id,
            operation_id=s.operation_id,
            connection_id=s.connection_id,
            config=s.config,
            ui_metadata=s.ui_metadata or {},
        )
        db.add(step)

    await db.flush()
