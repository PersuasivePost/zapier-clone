"""
Webhook Integration

The most fundamental integration - receiving and sending webhooks.

WHAT IS IT?
- RECEIVE webhooks: External services POST data to us (triggers workflows)
- SEND webhooks: We POST data to external URLs (action)

WHAT CAN IT DO?
- One trigger: "Webhook Received" (instant trigger when data arrives)
- One action: "Send Webhook" (POST JSON to any URL)

This is the universal integration - it works with anything that speaks HTTP.
"""

import httpx
from typing import Any, Dict, List

from .base import (
    BaseAction,
    BaseTrigger,
    IntegrationDefinition,
    FieldSchema,
    AuthConfig
)


# ============================================================================
# TRIGGERS
# ============================================================================

class WebhookReceived(BaseTrigger):
    """
    Trigger: Webhook Received
    
    How it works:
    1. User creates a workflow with this trigger
    2. We generate a unique webhook URL for them (e.g., /webhooks/abc123)
    3. External service POSTs to that URL
    4. We receive the payload and trigger the workflow
    5. The entire payload is passed to the workflow
    """
    
    id = "webhook_received"
    name = "Webhook Received"
    description = "Trigger when a webhook is received at your unique webhook URL"
    trigger_type = "webhook"
    
    def get_input_schema(self) -> List[FieldSchema]:
        """
        Webhook triggers don't need configuration - the URL is auto-generated.
        But we might want optional validation settings.
        """
        return [
            FieldSchema(
                key="validate_signature",
                label="Validate Signature",
                type="boolean",
                required=False,
                description="Require HMAC signature validation (advanced)"
            ),
            FieldSchema(
                key="secret_key",
                label="Secret Key",
                type="string",
                required=False,
                placeholder="your-secret-key",
                description="Secret key for HMAC validation (if enabled)"
            )
        ]
    
    def get_output_schema(self) -> List[FieldSchema]:
        """
        The output is the entire webhook payload - we don't know its structure ahead of time.
        We'll return a generic schema.
        """
        return [
            FieldSchema(
                key="payload",
                label="Webhook Payload",
                type="text",
                description="The full JSON payload received from the webhook"
            ),
            FieldSchema(
                key="headers",
                label="Request Headers",
                type="text",
                description="HTTP headers from the webhook request"
            ),
            FieldSchema(
                key="timestamp",
                label="Received At",
                type="string",
                description="ISO 8601 timestamp of when the webhook was received"
            )
        ]
    
    async def handle_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Process incoming webhook.
        
        Args:
            payload: The JSON body of the POST request
            headers: HTTP headers
        
        Returns:
            Normalized data to pass to the workflow
        """
        from datetime import datetime
        
        # TODO: Add signature validation if configured
        
        return {
            "payload": payload,
            "headers": dict(headers),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# ACTIONS
# ============================================================================

class SendWebhook(BaseAction):
    """
    Action: Send Webhook
    
    POST JSON data to any URL. The universal action for integrating with anything.
    """
    
    id = "send_webhook"
    name = "Send Webhook"
    description = "Send a POST request with JSON data to any URL"
    
    def get_input_schema(self) -> List[FieldSchema]:
        """
        Configuration needed:
        - URL to POST to
        - JSON payload (as text that will be parsed)
        - Optional headers
        - Optional HTTP method
        """
        return [
            FieldSchema(
                key="url",
                label="Webhook URL",
                type="string",
                required=True,
                placeholder="https://example.com/webhook",
                description="The URL to send the webhook to"
            ),
            FieldSchema(
                key="method",
                label="HTTP Method",
                type="select",
                required=True,
                description="HTTP method to use",
                options=[
                    {"label": "POST", "value": "POST"},
                    {"label": "PUT", "value": "PUT"},
                    {"label": "PATCH", "value": "PATCH"}
                ]
            ),
            FieldSchema(
                key="payload",
                label="JSON Payload",
                type="text",
                required=True,
                placeholder='{"key": "value"}',
                description="JSON data to send (can use variables from previous steps)"
            ),
            FieldSchema(
                key="headers",
                label="Custom Headers",
                type="text",
                required=False,
                placeholder='{"Authorization": "Bearer token"}',
                description="Optional: Custom HTTP headers as JSON"
            )
        ]
    
    def get_output_schema(self) -> List[FieldSchema]:
        """
        Output from sending the webhook:
        - Response status code
        - Response body
        - Success indicator
        """
        return [
            FieldSchema(
                key="status_code",
                label="Status Code",
                type="number",
                description="HTTP status code of the response"
            ),
            FieldSchema(
                key="response_body",
                label="Response Body",
                type="text",
                description="Body of the HTTP response"
            ),
            FieldSchema(
                key="success",
                label="Success",
                type="boolean",
                description="Whether the request was successful (2xx status)"
            ),
            FieldSchema(
                key="timestamp",
                label="Sent At",
                type="string",
                description="When the webhook was sent"
            )
        ]
    
    async def execute(
        self,
        credentials: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute: Send the webhook.
        
        Args:
            credentials: Not used for webhooks (no auth needed)
            config: {
                "url": "...",
                "method": "POST",
                "payload": "...",
                "headers": "..."
            }
        """
        import json
        from datetime import datetime
        
        # Extract config
        url = config.get("url")
        method = config.get("method", "POST").upper()
        payload_str = config.get("payload", "{}")
        headers_str = config.get("headers", "{}")
        
        if not url:
            raise ValueError("url is required")
        
        # Parse JSON strings
        try:
            payload = json.loads(payload_str) if isinstance(payload_str, str) else payload_str
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in payload: {str(e)}")
        
        try:
            headers = json.loads(headers_str) if isinstance(headers_str, str) else headers_str
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in headers: {str(e)}")
        
        # Default headers
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        
        # Make the request
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                # Try to get response body
                try:
                    response_body = response.json()
                except:
                    response_body = response.text
                
                return {
                    "status_code": response.status_code,
                    "response_body": response_body,
                    "success": 200 <= response.status_code < 300,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            except httpx.RequestError as e:
                raise Exception(f"Failed to send webhook: {str(e)}")
            
            except Exception as e:
                raise Exception(f"Error sending webhook: {str(e)}")


# ============================================================================
# INTEGRATION DEFINITION
# ============================================================================

webhook_integration = IntegrationDefinition(
    id="webhook",
    name="Webhook",
    description="Send and receive webhooks - the universal HTTP integration",
    icon_url="https://cdn-icons-png.flaticon.com/512/2165/2165004.png",
    
    # No authentication needed - webhooks are public endpoints
    auth_type="none",
    auth_config=AuthConfig.none(),
    
    # One trigger: Webhook Received
    triggers=[
        WebhookReceived()
    ],
    
    # One action: Send Webhook
    actions=[
        SendWebhook()
    ]
)


# ============================================================================
# INTEGRATION METADATA
# ============================================================================

INTEGRATION_METADATA = {
    "category": "Developer Tools",
    "tags": ["webhook", "http", "api", "universal"],
    "setup_instructions": """
        Webhooks are the most flexible integration:
        
        AS A TRIGGER (Receive):
        1. Add "Webhook Received" as your workflow trigger
        2. We'll generate a unique webhook URL for you
        3. Copy that URL
        4. Configure your external service to POST to that URL
        5. When data arrives, your workflow runs!
        
        AS AN ACTION (Send):
        1. Add "Send Webhook" as a workflow action
        2. Enter the target URL
        3. Configure the JSON payload to send
        4. That's it - we'll POST to that URL when the workflow runs
        
        Works with any service that speaks HTTP!
    """,
    "documentation_url": "https://docs.example.com/integrations/webhook",
    "support_email": "support@example.com"
}
