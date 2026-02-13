"""
Webhook Integration - Triggers

The simplest possible trigger: receive data via HTTP POST.
No authentication, no external API calls, just pure data passthrough.
"""

from typing import Any, Dict, List
from datetime import datetime

from ..base import BaseTrigger, FieldSchema


class IncomingWebhookTrigger(BaseTrigger):
    """
    Trigger: Incoming Webhook
    
    The "hello world" of triggers. When someone POSTs JSON to the webhook URL,
    this trigger fires and passes the data to the workflow.
    
    How it works:
    1. User creates workflow with this trigger
    2. System generates unique webhook URL (based on workflow's webhook_token)
    3. External service POSTs data to that URL
    4. This trigger receives the payload and fires the workflow
    5. The entire payload becomes available to subsequent workflow steps
    
    No configuration needed - the webhook URL is auto-generated.
    """
    
    id = "incoming_webhook"
    name = "Incoming Webhook"
    description = "Triggers when data is received via webhook URL"
    trigger_type = "webhook"
    
    def get_input_schema(self) -> List[FieldSchema]:
        """
        No configuration needed from the user.
        The webhook URL is automatically generated from the workflow's webhook_token.
        
        We could add optional validation settings later like:
        - HMAC signature verification
        - IP whitelist
        - Request method filtering
        
        But for MVP, keep it simple: zero configuration.
        """
        return []
    
    def get_output_schema(self) -> List[FieldSchema]:
        """
        What data does this trigger produce?
        
        Since we don't know what JSON structure will be POSTed, we return
        a generic "data" field that contains the entire payload.
        
        The user can then access fields like {{trigger.data.user_id}} in
        subsequent steps.
        """
        return [
            FieldSchema(
                key="data",
                label="Webhook Payload",
                type="text",
                description="The complete JSON payload received from the webhook"
            ),
            FieldSchema(
                key="headers",
                label="Request Headers",
                type="text",
                description="HTTP headers from the webhook request (useful for debugging)"
            ),
            FieldSchema(
                key="received_at",
                label="Received At",
                type="string",
                description="ISO 8601 timestamp of when the webhook was received"
            ),
            FieldSchema(
                key="method",
                label="HTTP Method",
                type="string",
                description="HTTP method used (GET, POST, PUT, etc.)"
            )
        ]
    
    async def handle_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Process incoming webhook data.
        
        This is called by the webhook endpoint when data arrives.
        
        Args:
            payload: The parsed JSON body of the request
            headers: HTTP headers from the request
            
        Returns:
            Normalized data in the format expected by workflow engine
            
        Design decision: Return the payload as-is under "data" key.
        This keeps the trigger simple and flexible - works with any JSON structure.
        """
        
        # Get HTTP method from headers if available (FastAPI typically provides this)
        method = headers.get("x-http-method", "POST")
        
        # Build the output
        return {
            "data": payload,
            "headers": dict(headers),  # Convert to plain dict
            "received_at": datetime.utcnow().isoformat() + "Z",
            "method": method
        }
    
    async def validate_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        config: Dict[str, Any]
    ) -> bool:
        """
        Optional: Validate webhook authenticity.
        
        For MVP, we accept all webhooks. In production, you might:
        - Verify HMAC signatures
        - Check IP whitelist
        - Validate required headers
        
        Args:
            payload: The webhook payload
            headers: Request headers
            config: Trigger configuration (empty for MVP)
            
        Returns:
            True if valid, False to reject
        """
        # TODO: Implement validation if config specifies it
        # For now, accept everything
        return True
