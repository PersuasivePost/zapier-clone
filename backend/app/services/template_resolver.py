"""
Template Variable Resolver

Resolves template variables like {{trigger.data.field}} in workflow step configurations.

This is the magic that enables users to reference data from:
- Trigger outputs: {{trigger.field}}
- Previous step outputs: {{step_2.field}}
- Nested data: {{trigger.data.nested.value}}

Example:
    config = {
        "message": "Hello {{trigger.username}}!",
        "count": "{{trigger.data.items.length}}"
    }
    context = {
        "trigger": {
            "username": "John",
            "data": {"items": {"length": 5}}
        }
    }
    result = resolve_config(config, context)
    # {"message": "Hello John!", "count": "5"}
"""

import re
from typing import Any, Dict, List, Optional, Union


def deep_get(data: Dict[str, Any], path: str, default: str = "") -> str:
    """
    Get a value from a nested dictionary using a dot-separated path.
    
    Args:
        data: The dictionary to search
        path: Dot-separated path like "trigger.data.message"
        default: Value to return if path not found (default: empty string)
    
    Returns:
        The value at the path, converted to string, or default if not found
    
    Examples:
        >>> data = {"trigger": {"data": {"message": "Hello"}}}
        >>> deep_get(data, "trigger.data.message")
        'Hello'
        >>> deep_get(data, "trigger.nonexistent")
        ''
        >>> deep_get(data, "trigger.data.count", "0")
        '0'
    """
    # Handle empty path
    if not path or not path.strip():
        return default
    
    # Split the path and walk through the dictionary
    keys = path.strip().split(".")
    current = data
    
    try:
        for key in keys:
            if not isinstance(current, dict):
                # Intermediate value is not a dict, can't continue
                return default
            
            if key not in current:
                # Key doesn't exist
                return default
            
            current = current[key]
        
        # Successfully reached the end of the path
        # Convert the value to string
        if current is None:
            return default
        
        # Handle different types
        if isinstance(current, bool):
            return str(current).lower()  # true/false instead of True/False
        elif isinstance(current, (dict, list)):
            # Don't convert complex structures to string
            # This usually means the path is incomplete
            return default
        else:
            return str(current)
    
    except (KeyError, TypeError, AttributeError):
        return default


def resolve_template_string(template: str, context: Dict[str, Any]) -> str:
    """
    Resolve template variables in a single string.
    
    Finds all {{variable.path}} patterns and replaces them with actual values
    from the context dictionary.
    
    Args:
        template: String containing template variables like "Hello {{trigger.name}}"
        context: Dictionary with variable values
    
    Returns:
        String with all template variables replaced
    
    Examples:
        >>> resolve_template_string("Hello {{trigger.name}}", {"trigger": {"name": "John"}})
        'Hello John'
        >>> resolve_template_string("{{user}} sent {{count}} items", {"user": "Jane", "count": 5})
        'Jane sent 5 items'
    """
    if not isinstance(template, str):
        return template
    
    # Regex pattern to find {{...}} 
    # Non-greedy match (.*?) to handle multiple variables in one string
    pattern = r'\{\{(.*?)\}\}'
    
    def replacer(match):
        """Replacement function called for each match"""
        # Extract the path from inside {{ }}
        path = match.group(1).strip()
        
        # Get the value from context using deep_get
        value = deep_get(context, path, default="")
        
        return value
    
    # Replace all matches
    result = re.sub(pattern, replacer, template)
    
    return result


def resolve_config(
    config: Union[Dict, List, str, Any], 
    context: Dict[str, Any]
) -> Union[Dict, List, str, Any]:
    """
    Recursively resolve template variables in a configuration dictionary.
    
    Handles nested dictionaries, lists, and string values. Non-string values
    (numbers, booleans, None) are left unchanged.
    
    Args:
        config: Configuration dict/list/string with potential template variables
        context: Dictionary with variable values
    
    Returns:
        New config with all template variables resolved (original not mutated)
    
    Examples:
        >>> config = {
        ...     "url": "https://api.com",
        ...     "message": "Hello {{trigger.name}}",
        ...     "metadata": {
        ...         "source": "{{trigger.source}}"
        ...     }
        ... }
        >>> context = {"trigger": {"name": "John", "source": "webhook"}}
        >>> resolve_config(config, context)
        {'url': 'https://api.com', 'message': 'Hello John', 'metadata': {'source': 'webhook'}}
    """
    # Handle different types
    if isinstance(config, dict):
        # Recursively resolve all values in the dictionary
        resolved = {}
        for key, value in config.items():
            resolved[key] = resolve_config(value, context)
        return resolved
    
    elif isinstance(config, list):
        # Recursively resolve all items in the list
        return [resolve_config(item, context) for item in config]
    
    elif isinstance(config, str):
        # Resolve template variables in the string
        return resolve_template_string(config, context)
    
    else:
        # Leave other types (int, float, bool, None) unchanged
        return config


# Convenience function for the most common use case
def resolve_step_config(
    step_config: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolve template variables in a workflow step configuration.
    
    This is the main function that will be called from the execution engine.
    
    Args:
        step_config: The step's config dict from the database
        context: Execution context with trigger data and previous step outputs
    
    Returns:
        Resolved config ready to be passed to an action's execute() method
    
    Examples:
        >>> step_config = {
        ...     "webhook_url": "https://discord.com/api/webhooks/...",
        ...     "content": "New message: {{trigger.message}}"
        ... }
        >>> context = {"trigger": {"message": "Hello World"}}
        >>> resolve_step_config(step_config, context)
        {'webhook_url': 'https://discord.com/api/webhooks/...', 'content': 'New message: Hello World'}
    """
    return resolve_config(step_config, context)
