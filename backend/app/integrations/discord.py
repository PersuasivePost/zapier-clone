"""
Discord Integration

A complete example integration showing how to implement the plugin architecture.

WHAT IS DISCORD?
- Discord is a messaging platform
- It has "webhooks" - special URLs you can POST to that send messages to a channel
- No OAuth needed - the webhook URL itself contains the auth token

WHAT CAN IT DO?
- Zero triggers (Discord doesn't push data to us)
- One action: "Send Message" (POST to webhook URL)

This serves as the blueprint for all future integrations.
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
# ACTIONS
# ============================================================================

class DiscordSendMessage(BaseAction):
    """
    Action: Send a message to a Discord channel via webhook.
    
    How it works:
    1. User provides webhook URL (contains auth) and message content
    2. We POST to the webhook URL with JSON body: {"content": "message"}
    3. Discord returns the message object if successful
    """
    
    id = "send_message"
    name = "Send Message"
    description = "Send a message to a Discord channel via webhook"
    
    def get_input_schema(self) -> List[FieldSchema]:
        """
        What does the user need to configure?
        - message_content: The actual message text to send
        """
        return [
            FieldSchema(
                key="message_content",
                label="Message Content",
                type="text",
                required=True,
                placeholder="Hello from Zapier Clone!",
                description="The message to send to the Discord channel. Supports Discord markdown."
            ),
            FieldSchema(
                key="username",
                label="Username Override",
                type="string",
                required=False,
                placeholder="My Bot",
                description="Optional: Override the webhook's default username"
            ),
            FieldSchema(
                key="avatar_url",
                label="Avatar URL",
                type="string",
                required=False,
                placeholder="https://...",
                description="Optional: Override the webhook's default avatar"
            )
        ]
    
    def get_output_schema(self) -> List[FieldSchema]:
        """
        What data does this action produce?
        - message_id: Discord's ID for the sent message
        - channel_id: The channel it was sent to
        - timestamp: When it was sent
        """
        return [
            FieldSchema(
                key="message_id",
                label="Message ID",
                type="string",
                description="Discord's unique ID for the message"
            ),
            FieldSchema(
                key="channel_id",
                label="Channel ID",
                type="string",
                description="The Discord channel ID where the message was sent"
            ),
            FieldSchema(
                key="timestamp",
                label="Timestamp",
                type="string",
                description="ISO 8601 timestamp of when the message was sent"
            ),
            FieldSchema(
                key="success",
                label="Success",
                type="boolean",
                description="Whether the message was sent successfully"
            )
        ]
    
    async def execute(
        self,
        credentials: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute: Send the message to Discord.
        
        Args:
            credentials: {"webhook_url": "https://discord.com/api/webhooks/..."}
            config: {"message_content": "...", "username": "...", "avatar_url": "..."}
        
        Returns:
            {"message_id": "...", "channel_id": "...", "timestamp": "...", "success": true}
        """
        # Extract webhook URL from credentials
        webhook_url = credentials.get("webhook_url")
        if not webhook_url:
            raise ValueError("webhook_url is required in credentials")
        
        # Extract message content from config
        message_content = config.get("message_content")
        if not message_content:
            raise ValueError("message_content is required in config")
        
        # Build Discord webhook payload
        payload = {
            "content": message_content
        }
        
        # Optional fields
        if config.get("username"):
            payload["username"] = config["username"]
        if config.get("avatar_url"):
            payload["avatar_url"] = config["avatar_url"]
        
        # Make the HTTP request to Discord
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    params={"wait": "true"}  # Tell Discord to return the message object
                )
                response.raise_for_status()
                
                # Parse response
                message_data = response.json()
                
                return {
                    "message_id": message_data.get("id", ""),
                    "channel_id": message_data.get("channel_id", ""),
                    "timestamp": message_data.get("timestamp", ""),
                    "success": True
                }
            
            except httpx.HTTPStatusError as e:
                # Discord returned an error
                error_data = {}
                try:
                    error_data = e.response.json()
                except:
                    pass
                
                raise Exception(
                    f"Discord API error: {e.response.status_code} - "
                    f"{error_data.get('message', e.response.text)}"
                )
            
            except Exception as e:
                raise Exception(f"Failed to send Discord message: {str(e)}")


# ============================================================================
# INTEGRATION DEFINITION
# ============================================================================

# This is what gets registered in the integration registry
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


# ============================================================================
# INTEGRATION METADATA
# ============================================================================

# This is used by the integration registry to provide helpful info
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
