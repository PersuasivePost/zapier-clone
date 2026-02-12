"""
Integration Registry

The central catalog of all available integrations.

THINK OF THIS AS:
- A library catalog that knows about every book (integration)
- A plugin loader that makes integrations discoverable
- The single source of truth for "what integrations exist"

RESPONSIBILITIES:
1. Register integrations (Discord, Webhook, Gmail, etc.)
2. List all available integrations
3. Get a specific integration by ID
4. Get a specific action or trigger from any integration

HOW TO USE:
    from app.integrations.registry import integration_registry
    
    # List all integrations
    all_integrations = integration_registry.list_integrations()
    
    # Get Discord integration
    discord = integration_registry.get_integration("discord")
    
    # Get Discord's "send_message" action
    action = integration_registry.get_action("discord", "send_message")
    
    # Execute an action
    result = await action.execute(credentials, config)
"""

from typing import Dict, List, Optional
from .base import IntegrationDefinition, BaseAction, BaseTrigger


class IntegrationRegistry:
    """
    The global registry of all integrations.
    
    This is a singleton - there's only one registry in the entire application.
    All integrations are registered here at startup.
    """
    
    def __init__(self):
        self._integrations: Dict[str, IntegrationDefinition] = {}
        self._metadata: Dict[str, Dict] = {}
    
    def register(
        self,
        integration: IntegrationDefinition,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Register an integration in the catalog.
        
        Args:
            integration: The IntegrationDefinition instance
            metadata: Optional metadata (category, tags, setup instructions, etc.)
        
        Example:
            registry.register(discord_integration, INTEGRATION_METADATA)
        """
        integration_id = integration.id
        
        # Check for duplicates
        if integration_id in self._integrations:
            raise ValueError(f"Integration '{integration_id}' is already registered")
        
        # Validate integration has at least one trigger or action
        if not integration.triggers and not integration.actions:
            raise ValueError(
                f"Integration '{integration_id}' must have at least one trigger or action"
            )
        
        # Register
        self._integrations[integration_id] = integration
        self._metadata[integration_id] = metadata or {}
        
        print(f"✓ Registered integration: {integration.name} "
              f"({len(integration.triggers)} triggers, {len(integration.actions)} actions)")
    
    def list_integrations(self, category: Optional[str] = None) -> List[Dict]:
        """
        Get all registered integrations.
        
        Args:
            category: Optional filter by category (e.g., "Communication", "Developer Tools")
        
        Returns:
            List of integration dictionaries with metadata
        """
        integrations = []
        
        for integration_id, integration in self._integrations.items():
            metadata = self._metadata.get(integration_id, {})
            
            # Apply category filter if specified
            if category and metadata.get("category") != category:
                continue
            
            # Build response
            integration_dict = integration.to_dict()
            integration_dict.update({
                "category": metadata.get("category", "Other"),
                "tags": metadata.get("tags", []),
                "setup_instructions": metadata.get("setup_instructions", ""),
                "documentation_url": metadata.get("documentation_url", ""),
                "support_email": metadata.get("support_email", "")
            })
            
            integrations.append(integration_dict)
        
        # Sort by name
        integrations.sort(key=lambda x: x["name"])
        
        return integrations
    
    def get_integration(self, integration_id: str) -> Optional[IntegrationDefinition]:
        """
        Get a specific integration by its ID.
        
        Args:
            integration_id: The integration ID (e.g., "discord", "webhook")
        
        Returns:
            IntegrationDefinition or None if not found
        """
        return self._integrations.get(integration_id)
    
    def get_integration_with_metadata(self, integration_id: str) -> Optional[Dict]:
        """
        Get an integration with its metadata as a dictionary.
        
        Args:
            integration_id: The integration ID
        
        Returns:
            Dictionary with integration data and metadata, or None if not found
        """
        integration = self.get_integration(integration_id)
        if not integration:
            return None
        
        metadata = self._metadata.get(integration_id, {})
        result = integration.to_dict()
        result.update({
            "category": metadata.get("category", "Other"),
            "tags": metadata.get("tags", []),
            "setup_instructions": metadata.get("setup_instructions", ""),
            "documentation_url": metadata.get("documentation_url", ""),
            "support_email": metadata.get("support_email", "")
        })
        
        return result
    
    def get_action(
        self,
        integration_id: str,
        action_id: str
    ) -> Optional[BaseAction]:
        """
        Get a specific action from an integration.
        
        Args:
            integration_id: The integration ID (e.g., "discord")
            action_id: The action ID (e.g., "send_message")
        
        Returns:
            BaseAction instance or None if not found
        
        Example:
            action = registry.get_action("discord", "send_message")
            result = await action.execute(credentials, config)
        """
        integration = self.get_integration(integration_id)
        if not integration:
            return None
        
        return integration.get_action(action_id)
    
    def get_trigger(
        self,
        integration_id: str,
        trigger_id: str
    ) -> Optional[BaseTrigger]:
        """
        Get a specific trigger from an integration.
        
        Args:
            integration_id: The integration ID (e.g., "webhook")
            trigger_id: The trigger ID (e.g., "webhook_received")
        
        Returns:
            BaseTrigger instance or None if not found
        
        Example:
            trigger = registry.get_trigger("webhook", "webhook_received")
            items = await trigger.poll(credentials, config, last_poll_time)
        """
        integration = self.get_integration(integration_id)
        if not integration:
            return None
        
        return integration.get_trigger(trigger_id)
    
    def list_categories(self) -> List[str]:
        """
        Get all unique categories from registered integrations.
        
        Returns:
            Sorted list of category names
        """
        categories = set()
        for metadata in self._metadata.values():
            category = metadata.get("category", "Other")
            categories.add(category)
        
        return sorted(list(categories))
    
    def search_integrations(self, query: str) -> List[Dict]:
        """
        Search integrations by name, description, or tags.
        
        Args:
            query: Search term
        
        Returns:
            List of matching integrations
        """
        query_lower = query.lower()
        results = []
        
        for integration in self.list_integrations():
            # Search in name
            if query_lower in integration["name"].lower():
                results.append(integration)
                continue
            
            # Search in description
            if query_lower in integration["description"].lower():
                results.append(integration)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in integration["tags"]):
                results.append(integration)
                continue
        
        return results
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the registry.
        
        Returns:
            Dictionary with counts and other stats
        """
        total_integrations = len(self._integrations)
        total_triggers = sum(
            len(integration.triggers)
            for integration in self._integrations.values()
        )
        total_actions = sum(
            len(integration.actions)
            for integration in self._integrations.values()
        )
        
        # Count by auth type
        auth_types = {}
        for integration in self._integrations.values():
            auth_type = integration.auth_type
            auth_types[auth_type] = auth_types.get(auth_type, 0) + 1
        
        # Count by category
        categories = {}
        for integration_id, metadata in self._metadata.items():
            category = metadata.get("category", "Other")
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_integrations": total_integrations,
            "total_triggers": total_triggers,
            "total_actions": total_actions,
            "auth_types": auth_types,
            "categories": categories
        }


# ============================================================================
# GLOBAL REGISTRY INSTANCE
# ============================================================================

# This is the ONE registry instance used throughout the application
integration_registry = IntegrationRegistry()


# ============================================================================
# AUTO-REGISTER INTEGRATIONS
# ============================================================================

def register_all_integrations():
    """
    Register all available integrations at application startup.
    
    This function is called once when the FastAPI app starts.
    Add new integrations here as you build them.
    """
    print("\n" + "="*70)
    print("REGISTERING INTEGRATIONS")
    print("="*70)
    
    # Import all integrations
    from .discord import discord_integration, INTEGRATION_METADATA as discord_metadata
    from .webhook import webhook_integration, INTEGRATION_METADATA as webhook_metadata
    
    # Register them
    integration_registry.register(discord_integration, discord_metadata)
    integration_registry.register(webhook_integration, webhook_metadata)
    
    # TODO: Add more integrations here as you build them
    # from .gmail import gmail_integration, INTEGRATION_METADATA as gmail_metadata
    # integration_registry.register(gmail_integration, gmail_metadata)
    
    # Print stats
    stats = integration_registry.get_stats()
    print("="*70)
    print(f"Registration complete!")
    print(f"  Total integrations: {stats['total_integrations']}")
    print(f"  Total triggers: {stats['total_triggers']}")
    print(f"  Total actions: {stats['total_actions']}")
    print(f"  Categories: {', '.join(stats['categories'].keys())}")
    print("="*70 + "\n")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_integration_by_id(integration_id: str) -> Optional[IntegrationDefinition]:
    """Convenience function to get an integration"""
    return integration_registry.get_integration(integration_id)


def get_action_by_id(integration_id: str, action_id: str) -> Optional[BaseAction]:
    """Convenience function to get an action"""
    return integration_registry.get_action(integration_id, action_id)


def get_trigger_by_id(integration_id: str, trigger_id: str) -> Optional[BaseTrigger]:
    """Convenience function to get a trigger"""
    return integration_registry.get_trigger(integration_id, trigger_id)
