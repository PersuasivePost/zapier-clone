from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class FieldDict(BaseModel):
    key: str
    label: Optional[str] = None
    type: Optional[str] = None
    required: Optional[bool] = False
    placeholder: Optional[str] = None
    description: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None


class IntegrationSummaryResponse(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None
    auth_type: Optional[str] = None
    trigger_count: int
    action_count: int


class TriggerResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    input_schema: List[Dict[str, Any]]
    output_schema: List[Dict[str, Any]]


class ActionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    input_schema: List[Dict[str, Any]]
    output_schema: List[Dict[str, Any]]


class IntegrationDetailResponse(IntegrationSummaryResponse):
    description: Optional[str] = None
    triggers: List[TriggerResponse]
    actions: List[ActionResponse]


class TestActionRequest(BaseModel):
    integration_id: str
    action_id: str
    input_data: Dict[str, Any]


class TestActionResponse(BaseModel):
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
