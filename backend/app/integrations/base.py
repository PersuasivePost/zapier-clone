"""
Integration Plugin Architecture - Base Classes

This module defines the core abstractions that every integration must implement.
Think of these as the "electrical outlet" - they define the shape that all integrations
must conform to, making them uniformly pluggable into the execution engine.

THREE LAYERS:
1. DEFINITION (What are you? What can you do?) → IntegrationDefinition
2. SCHEMA (What inputs/outputs?) → input_schema, output_schema
3. EXECUTION (How do you do it?) → execute(), poll(), handle_webhook()
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Literal
from datetime import datetime


# ============================================================================
# SCHEMA TYPES
# ============================================================================

class FieldSchema:
    """
    Defines a single field in a form or data structure.
    Used to dynamically generate forms on the frontend and validate input.
    
    Example:
        FieldSchema(
            key="webhook_url",
            label="Discord Webhook URL",
            type="string",
            required=True,
            placeholder="https://discord.com/api/webhooks/...",
            description="Get this from Server Settings → Integrations"
        )
    """
    
    def __init__(
        self,
        key: str,
        label: str,
        type: Literal["string", "text", "number", "boolean", "select"],
        required: bool = False,
        placeholder: str = "",
        description: str = "",
        options: Optional[List[Dict[str, str]]] = None  # For select type: [{"label": "...", "value": "..."}]
    ):
        self.key = key
        self.label = label
        self.type = type
        self.required = required
        self.placeholder = placeholder
        self.description = description
        self.options = options or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "key": self.key,
            "label": self.label,
            "type": self.type,
            "required": self.required,
            "placeholder": self.placeholder,
            "description": self.description,
            "options": self.options
        }


# ============================================================================
# LAYER 2 + 3: BASE ACTION (Schema + Execution)
# ============================================================================

class BaseAction(ABC):
    """
    Abstract base class for all integration actions.
    
    An action is something the integration DOES (e.g., "Send Message", "Create Task").
    Every action answers:
    1. What is your ID, name, description?
    2. What inputs do you need? (input_schema)
    3. What outputs do you produce? (output_schema)
    4. How do you execute? (execute method)
    
    Example subclass:
        class DiscordSendMessage(BaseAction):
            id = "send_message"
            name = "Send Message"
            description = "Send a message to a Discord channel via webhook"
            
            def get_input_schema(self):
                return [
                    FieldSchema("message_content", "Message", "text", required=True)
                ]
            
            def execute(self, credentials, config):
                # POST to Discord API...
                return {"message_id": "12345"}
    """
    
    # These must be set by subclasses
    id: str
    name: str
    description: str
    
    @abstractmethod
    def get_input_schema(self) -> List[FieldSchema]:
        """
        Define what fields the user needs to fill in to configure this action.
        Returns a list of FieldSchema objects.
        """
        pass
    
    @abstractmethod
    def get_output_schema(self) -> List[FieldSchema]:
        """
        Define what data this action produces after execution.
        Returns a list of FieldSchema objects.
        """
        pass
    
    @abstractmethod
    async def execute(
        self,
        credentials: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the action.
        
        Args:
            credentials: Decrypted authentication credentials (API keys, tokens, etc.)
            config: User's configuration for this specific action instance
            
        Returns:
            Dictionary containing the output data (must match output_schema)
            
        Raises:
            Exception: If execution fails
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize action metadata for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "input_schema": [field.to_dict() for field in self.get_input_schema()],
            "output_schema": [field.to_dict() for field in self.get_output_schema()]
        }


# ============================================================================
# LAYER 2 + 3: BASE TRIGGER (Schema + Execution)
# ============================================================================

class BaseTrigger(ABC):
    """
    Abstract base class for all integration triggers.
    
    A trigger is something that STARTS a workflow (e.g., "New Email", "Webhook Received").
    
    Two types of triggers:
    1. WEBHOOK: External service pushes data to us (instant)
    2. POLLING: We periodically check for new items (delayed)
    
    Every trigger answers:
    1. What is your ID, name, description?
    2. What type are you? (webhook or polling)
    3. What configuration do you need? (input_schema)
    4. What data do you produce? (output_schema)
    5. How do you work? (poll method for polling, handle_webhook for webhooks)
    """
    
    # These must be set by subclasses
    id: str
    name: str
    description: str
    trigger_type: Literal["webhook", "polling"]
    
    @abstractmethod
    def get_input_schema(self) -> List[FieldSchema]:
        """
        Define what configuration the user needs to provide for this trigger.
        For webhook triggers, this might be empty.
        For polling triggers, this might include filters, time windows, etc.
        """
        pass
    
    @abstractmethod
    def get_output_schema(self) -> List[FieldSchema]:
        """
        Define what data this trigger produces when it fires.
        This is the data that flows into the workflow.
        """
        pass
    
    async def poll(
        self,
        credentials: Dict[str, Any],
        config: Dict[str, Any],
        last_poll_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for new items since last poll (only for polling triggers).
        
        Args:
            credentials: Decrypted authentication credentials
            config: User's trigger configuration
            last_poll_time: When we last checked (None on first run)
            
        Returns:
            List of new items found. Each item is a dict matching output_schema.
            Empty list if no new items.
        """
        if self.trigger_type != "polling":
            raise NotImplementedError(f"{self.__class__.__name__} is not a polling trigger")
        return []
    
    async def handle_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Process incoming webhook data (only for webhook triggers).
        
        Args:
            payload: The raw JSON payload from the webhook
            headers: HTTP headers from the webhook request
            
        Returns:
            Normalized/parsed data matching output_schema
        """
        if self.trigger_type != "webhook":
            raise NotImplementedError(f"{self.__class__.__name__} is not a webhook trigger")
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize trigger metadata for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_type": self.trigger_type,
            "input_schema": [field.to_dict() for field in self.get_input_schema()],
            "output_schema": [field.to_dict() for field in self.get_output_schema()]
        }


# ============================================================================
# LAYER 1: INTEGRATION DEFINITION (What are you? What can you do?)
# ============================================================================

class IntegrationDefinition:
    """
    The "identity card" of an integration.
    
    This is the top-level object that represents an entire integration service
    (Discord, Gmail, Slack, etc.). It contains:
    1. Metadata (ID, name, icon, description)
    2. Authentication requirements (OAuth, API key, webhook, none)
    3. List of triggers this integration provides
    4. List of actions this integration provides
    
    Think of this as the "catalog entry" - when a user browses available
    integrations, they're looking at IntegrationDefinition objects.
    
    Example:
        discord = IntegrationDefinition(
            id="discord",
            name="Discord",
            description="Send messages to Discord channels",
            icon_url="https://...",
            auth_type="webhook_url",
            triggers=[],
            actions=[DiscordSendMessage()]
        )
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        icon_url: str = "",
        auth_type: Literal["oauth2", "api_key", "webhook_url", "none"] = "none",
        auth_config: Optional[Dict[str, Any]] = None,
        triggers: Optional[List[BaseTrigger]] = None,
        actions: Optional[List[BaseAction]] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.icon_url = icon_url
        self.auth_type = auth_type
        self.auth_config = auth_config or {}
        self.triggers = triggers or []
        self.actions = actions or []
        
        # Build lookup maps for quick access
        self._triggers_map = {trigger.id: trigger for trigger in self.triggers}
        self._actions_map = {action.id: action for action in self.actions}
    
    def get_trigger(self, trigger_id: str) -> Optional[BaseTrigger]:
        """Get a specific trigger by its ID"""
        return self._triggers_map.get(trigger_id)
    
    def get_action(self, action_id: str) -> Optional[BaseAction]:
        """Get a specific action by its ID"""
        return self._actions_map.get(action_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize integration definition for API responses.
        This is what the frontend sees when browsing integrations.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "auth_type": self.auth_type,
            "auth_config": self.auth_config,
            "triggers": [trigger.to_dict() for trigger in self.triggers],
            "actions": [action.to_dict() for action in self.actions],
            "trigger_count": len(self.triggers),
            "action_count": len(self.actions)
        }


# ============================================================================
# AUTH CONFIG HELPERS
# ============================================================================

class AuthConfig:
    """
    Helper class to build auth_config dictionaries for common auth types.
    
    Usage:
        # For OAuth2
        auth_config = AuthConfig.oauth2(
            auth_url="https://discord.com/api/oauth2/authorize",
            token_url="https://discord.com/api/oauth2/token",
            scopes=["webhook.incoming"]
        )
        
        # For API Key
        auth_config = AuthConfig.api_key(
            header_name="Authorization",
            header_prefix="Bearer"
        )
    """
    
    @staticmethod
    def oauth2(
        auth_url: str,
        token_url: str,
        scopes: List[str],
        client_id_required: bool = True
    ) -> Dict[str, Any]:
        """OAuth2 authentication configuration"""
        return {
            "type": "oauth2",
            "auth_url": auth_url,
            "token_url": token_url,
            "scopes": scopes,
            "client_id_required": client_id_required
        }
    
    @staticmethod
    def api_key(
        header_name: str = "Authorization",
        header_prefix: str = "Bearer",
        param_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """API Key authentication configuration"""
        config = {
            "type": "api_key",
            "header_name": header_name,
            "header_prefix": header_prefix
        }
        if param_name:
            config["param_name"] = param_name
        return config
    
    @staticmethod
    def webhook_url() -> Dict[str, Any]:
        """Webhook URL authentication (Discord-style)"""
        return {
            "type": "webhook_url",
            "description": "Uses a webhook URL that contains the authentication token"
        }
    
    @staticmethod
    def none() -> Dict[str, Any]:
        """No authentication required"""
        return {
            "type": "none"
        }
