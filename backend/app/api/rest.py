from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.integrations import integration_registry

router = APIRouter()


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health():
    return {"status": "healthy"}


# ============================================================================
# INTEGRATION ENDPOINTS
# ============================================================================

@router.get("/integrations")
async def list_integrations(category: Optional[str] = None):
    """
    List all available integrations.
    
    Query params:
        category: Optional filter by category (e.g., "Communication")
    
    Returns:
        List of integration definitions with metadata
    """
    integrations = integration_registry.list_integrations(category=category)
    return {
        "integrations": integrations,
        "total": len(integrations)
    }


@router.get("/integrations/categories")
async def list_categories():
    """
    Get all available integration categories.
    
    Returns:
        List of category names
    """
    categories = integration_registry.list_categories()
    return {
        "categories": categories,
        "total": len(categories)
    }


@router.get("/integrations/stats")
async def integration_stats():
    """
    Get statistics about available integrations.
    
    Returns:
        Stats including counts, auth types, categories
    """
    stats = integration_registry.get_stats()
    return stats


@router.get("/integrations/search")
async def search_integrations(q: str):
    """
    Search integrations by name, description, or tags.
    
    Query params:
        q: Search query
    
    Returns:
        List of matching integrations
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters"
        )
    
    results = integration_registry.search_integrations(q)
    return {
        "results": results,
        "total": len(results),
        "query": q
    }


@router.get("/integrations/{integration_id}")
async def get_integration_detail(integration_id: str):
    """
    Get detailed information about a specific integration.
    
    Path params:
        integration_id: The integration ID (e.g., "discord", "webhook")
    
    Returns:
        Full integration definition with metadata
    """
    integration = integration_registry.get_integration_with_metadata(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=404,
            detail=f"Integration '{integration_id}' not found"
        )
    
    return integration


@router.get("/integrations/{integration_id}/actions/{action_id}")
async def get_action_detail(integration_id: str, action_id: str):
    """
    Get detailed schema for a specific action.
    
    Path params:
        integration_id: The integration ID
        action_id: The action ID
    
    Returns:
        Action definition with input/output schemas
    """
    action = integration_registry.get_action(integration_id, action_id)
    
    if not action:
        raise HTTPException(
            status_code=404,
            detail=f"Action '{action_id}' not found in integration '{integration_id}'"
        )
    
    return action.to_dict()


@router.get("/integrations/{integration_id}/triggers/{trigger_id}")
async def get_trigger_detail(integration_id: str, trigger_id: str):
    """
    Get detailed schema for a specific trigger.
    
    Path params:
        integration_id: The integration ID
        trigger_id: The trigger ID
    
    Returns:
        Trigger definition with input/output schemas
    """
    trigger = integration_registry.get_trigger(integration_id, trigger_id)
    
    if not trigger:
        raise HTTPException(
            status_code=404,
            detail=f"Trigger '{trigger_id}' not found in integration '{integration_id}'"
        )
    
    return trigger.to_dict()


# ============================================================================
# ACTION TESTING (for development/debugging)
# ============================================================================

class ActionTestRequest(BaseModel):
    """Request model for testing an action"""
    credentials: Dict[str, Any]
    config: Dict[str, Any]


@router.post("/integrations/{integration_id}/actions/{action_id}/test")
async def test_action(
    integration_id: str,
    action_id: str,
    request: ActionTestRequest
):
    """
    Test an action with provided credentials and config.
    
    THIS IS FOR DEVELOPMENT/DEBUGGING ONLY.
    In production, actions are executed through the workflow engine.
    
    Path params:
        integration_id: The integration ID
        action_id: The action ID
    
    Body:
        credentials: Authentication credentials
        config: Action configuration
    
    Returns:
        The action's output or error details
    """
    action = integration_registry.get_action(integration_id, action_id)
    
    if not action:
        raise HTTPException(
            status_code=404,
            detail=f"Action '{action_id}' not found in integration '{integration_id}'"
        )
    
    try:
        result = await action.execute(
            credentials=request.credentials,
            config=request.config
        )
        
        return {
            "success": True,
            "result": result
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# WEBHOOK HANDLING
# ============================================================================
# Note: Webhook handling has been moved to app/api/webhooks.py
# This endpoint is deprecated and should not be used
