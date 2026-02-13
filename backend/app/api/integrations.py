from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.integrations import integration_registry
from app.schemas.integration import (
    IntegrationSummaryResponse,
    IntegrationDetailResponse,
    TriggerResponse,
    ActionResponse,
    TestActionRequest,
    TestActionResponse,
)

from app.api.auth import get_current_user  # reuse existing auth dependency

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/", response_model=List[IntegrationSummaryResponse])
def list_integrations():
    integrations = integration_registry.list_integrations()
    results = []
    for integ in integrations:
        results.append(
            IntegrationSummaryResponse(
                id=integ["id"],
                name=integ["name"],
                icon=integ.get("icon_url") or integ.get("icon") or "",
                auth_type=integ.get("auth_type", "none"),
                trigger_count=integ.get("trigger_count", 0),
                action_count=integ.get("action_count", 0),
            )
        )
    return results


@router.get("/{integration_id}", response_model=IntegrationDetailResponse)
def get_integration(integration_id: str):
    integ = integration_registry.get_integration_with_metadata(integration_id)
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not found")

    # Build trigger and action objects
    triggers = []
    for t in integ.get("triggers", []):
        triggers.append(
            TriggerResponse(
                id=t.get("id"),
                name=t.get("name"),
                description=t.get("description"),
                trigger_type=t.get("trigger_type"),
                input_schema=t.get("input_schema", []),
                output_schema=t.get("output_schema", []),
            )
        )

    actions = []
    for a in integ.get("actions", []):
        actions.append(
            ActionResponse(
                id=a.get("id"),
                name=a.get("name"),
                description=a.get("description"),
                input_schema=a.get("input_schema", []),
                output_schema=a.get("output_schema", []),
            )
        )

    return IntegrationDetailResponse(
        id=integ.get("id"),
        name=integ.get("name"),
        icon=integ.get("icon_url"),
        auth_type=integ.get("auth_type"),
        trigger_count=integ.get("trigger_count", 0),
        action_count=integ.get("action_count", 0),
        description=integ.get("description", ""),
        triggers=triggers,
        actions=actions,
    )


@router.get("/{integration_id}/triggers", response_model=List[TriggerResponse])
def get_triggers(integration_id: str):
    integ = integration_registry.get_integration(integration_id)
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not found")

    return [t.to_dict() for t in integ.triggers]


@router.get("/{integration_id}/actions", response_model=List[ActionResponse])
def get_actions(integration_id: str):
    integ = integration_registry.get_integration(integration_id)
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not found")

    return [a.to_dict() for a in integ.actions]


@router.post("/test-action", response_model=TestActionResponse)
async def test_action(request: TestActionRequest, user=Depends(get_current_user)):
    # For Day 3 we only support no-auth actions; credentials passed as empty dict
    action = integration_registry.get_action(request.integration_id, request.action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    try:
        result = await action.execute({}, request.input_data)
        return TestActionResponse(success=True, output=result)
    except Exception as e:
        return TestActionResponse(success=False, error=str(e))
