"""
Integrations Package

This package contains the plugin architecture for integrations.

STRUCTURE:
    base.py       → Abstract base classes (BaseAction, BaseTrigger, IntegrationDefinition)
    registry.py   → Central registry that manages all integrations
    discord.py    → Discord integration implementation
    webhook.py    → Webhook integration implementation
    ...more integrations...

USAGE:
    # In your application code:
    from app.integrations import integration_registry
    
    # List all integrations
    integrations = integration_registry.list_integrations()
    
    # Get and execute an action
    action = integration_registry.get_action("discord", "send_message")
    result = await action.execute(credentials, config)
"""

# Export base classes for building new integrations
from .base import (
    BaseAction,
    BaseTrigger,
    IntegrationDefinition,
    FieldSchema,
    AuthConfig
)

# Export the registry and helper functions
from .registry import (
    integration_registry,
    register_all_integrations,
    get_integration_by_id,
    get_action_by_id,
    get_trigger_by_id
)

# Export individual integrations (optional, for direct access)
from .discord import discord_integration
from .webhook import webhook_integration


__all__ = [
    # Base classes
    "BaseAction",
    "BaseTrigger",
    "IntegrationDefinition",
    "FieldSchema",
    "AuthConfig",
    
    # Registry
    "integration_registry",
    "register_all_integrations",
    "get_integration_by_id",
    "get_action_by_id",
    "get_trigger_by_id",
    
    # Integrations
    "discord_integration",
    "webhook_integration"
]
