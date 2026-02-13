"""
Webhook Integration Package

Exports the webhook integration definition for the registry to find.
"""

from .definition import webhook_integration, INTEGRATION_METADATA
from .triggers import IncomingWebhookTrigger


__all__ = [
    "webhook_integration",
    "INTEGRATION_METADATA",
    "IncomingWebhookTrigger"
]
