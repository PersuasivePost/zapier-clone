"""
Webhook Integration - Definition

The "identity card" for the Webhook integration.

Answers the three questions:
1. What are you? → Webhook integration for receiving HTTP POST data
2. What can you do? → One trigger: Incoming Webhook (no actions)
3. How do you authenticate? → No auth needed (webhooks are public endpoints)
"""

from ..base import IntegrationDefinition, AuthConfig
from .triggers import IncomingWebhookTrigger


# Create the integration definition instance
webhook_integration = IntegrationDefinition(
    id="webhook",
    name="Webhooks",
    description="Receive data from external services via HTTP webhooks",
    icon_url="🔗",  # Using emoji for now, can be replaced with actual icon URL
    
    # No authentication required
    # Webhooks are public endpoints - the security comes from the URL being secret
    auth_type="none",
    auth_config=AuthConfig.none(),
    
    # One trigger: Incoming Webhook
    triggers=[
        IncomingWebhookTrigger()
    ],
    
    # No actions (webhook is for receiving, not sending)
    actions=[]
)


# Integration metadata for the registry
INTEGRATION_METADATA = {
    "category": "Developer Tools",
    "tags": ["webhook", "http", "api", "trigger"],
    "setup_instructions": """
        Setting up a webhook trigger is simple:
        
        1. Create a workflow
        2. Choose "Incoming Webhook" as the trigger
        3. Save the workflow
        4. Copy the generated webhook URL
        5. Configure your external service to POST to that URL
        
        When data arrives at the webhook URL, your workflow runs!
        
        The entire JSON payload becomes available in your workflow as:
        {{trigger.data}}
        
        Example: If someone POSTs {"user_id": 123, "action": "signup"},
        you can access those values as:
        - {{trigger.data.user_id}} → 123
        - {{trigger.data.action}} → "signup"
    """,
    "documentation_url": "https://docs.example.com/integrations/webhook",
    "support_email": "support@example.com",
    "examples": [
        {
            "title": "Stripe Payment Webhook",
            "description": "Trigger workflow when Stripe payment succeeds",
            "payload_example": {
                "event": "payment.succeeded",
                "amount": 2999,
                "currency": "usd",
                "customer_email": "customer@example.com"
            }
        },
        {
            "title": "GitHub Push Event",
            "description": "Trigger workflow on git push",
            "payload_example": {
                "repository": "my-repo",
                "branch": "main",
                "commits": 3,
                "pusher": "john-doe"
            }
        }
    ]
}
