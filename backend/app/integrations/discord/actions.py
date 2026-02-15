"""
Discord Actions

All action implementations for Discord integration.
"""

import httpx
from typing import Any, Dict, List

from ..base import BaseAction, FieldSchema


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
        # Extract webhook URL from credentials OR config
        # Priority: credentials > config (for flexibility)
        webhook_url = credentials.get("webhook_url") or config.get("webhook_url")
        if not webhook_url:
            raise ValueError("webhook_url is required in credentials or config")
        
        # Extract message content from config
        # Support both "message_content" (standard) and "content" (shorthand)
        message_content = config.get("message_content") or config.get("content")
        if not message_content:
            raise ValueError("message_content or content is required in config")
        
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
