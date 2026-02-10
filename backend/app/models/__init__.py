# models package (SQLAlchemy models go here)
from app.models.base import Base
from app.models.user import User
from app.models.connection import Connection, ConnectionStatus, AuthType
from app.models.workflow import Workflow, WorkflowStatus
from app.models.workflow_step import WorkflowStep, StepType
from app.models.workflow_run import WorkflowRun, RunStatus
from app.models.step_run import StepRun, StepRunStatus

# This __all__ is critical for Alembic to discover all models
__all__ = [
    "Base",
    "User",
    "Connection",
    "ConnectionStatus",
    "AuthType",
    "Workflow",
    "WorkflowStatus",
    "WorkflowStep",
    "StepType",
    "WorkflowRun",
    "RunStatus",
    "StepRun",
    "StepRunStatus",
]