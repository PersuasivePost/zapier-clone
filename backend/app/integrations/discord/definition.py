"""
Discord Integration Definition

The "identity card" for the Discord integration.
"""

from ..base import IntegrationDefinition, AuthConfig
from .actions import DiscordSendMessage


# Create the integration definition
discord_integration = IntegrationDefinition(
    id="discord",
    name="Discord",
    description="Send messages to Discord channels via webhooks",
    icon_url="https://cdn.prod.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
    
    # Authentication: Discord webhooks are self-contained (URL has the token)
    auth_type="webhook_url",
    auth_config=AuthConfig.webhook_url(),
    
    # No triggers - Discord doesn't push events to us
    triggers=[],
    
    # One action: Send Message
    actions=[
        DiscordSendMessage()
    ]
)


# Integration metadata for the registry
INTEGRATION_METADATA = {
    "category": "Communication",
    "tags": ["messaging", "chat", "notifications"],
    "setup_instructions": """
        To set up Discord integration:
        
        1. Go to your Discord server
        2. Click Server Settings → Integrations
        3. Click "Create Webhook" or "View Webhooks"
        4. Click "New Webhook"
        5. Choose a channel for the webhook
        6. Click "Copy Webhook URL"
        7. Paste that URL into the connection settings
        
        That's it! No OAuth, no API keys, just the webhook URL.
    """,
    "documentation_url": "https://discord.com/developers/docs/resources/webhook",
    "support_email": "support@example.com"
}
