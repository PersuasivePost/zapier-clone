"""
Day 3 Integration Plugin Architecture - Comprehensive Audit

This script tests all aspects of the Day 3 implementation to verify
that the plugin architecture is complete and working correctly.
"""

import asyncio
import json
from typing import Dict, Any


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


async def test_base_classes():
    """Test 1: Verify base classes exist and have correct structure"""
    print_section("TEST 1: Base Classes")
    
    from app.integrations.base import (
        BaseAction,
        BaseTrigger,
        IntegrationDefinition,
        FieldSchema,
        AuthConfig
    )
    
    # Check BaseAction
    print("✓ BaseAction imported")
    assert hasattr(BaseAction, 'get_input_schema'), "BaseAction missing get_input_schema"
    assert hasattr(BaseAction, 'get_output_schema'), "BaseAction missing get_output_schema"
    assert hasattr(BaseAction, 'execute'), "BaseAction missing execute"
    print("  - Has get_input_schema() method")
    print("  - Has get_output_schema() method")
    print("  - Has execute() method")
    
    # Check BaseTrigger
    print("\n✓ BaseTrigger imported")
    assert hasattr(BaseTrigger, 'get_input_schema'), "BaseTrigger missing get_input_schema"
    assert hasattr(BaseTrigger, 'get_output_schema'), "BaseTrigger missing get_output_schema"
    assert hasattr(BaseTrigger, 'poll'), "BaseTrigger missing poll"
    assert hasattr(BaseTrigger, 'handle_webhook'), "BaseTrigger missing handle_webhook"
    print("  - Has get_input_schema() method")
    print("  - Has get_output_schema() method")
    print("  - Has poll() method")
    print("  - Has handle_webhook() method")
    
    # Check IntegrationDefinition
    print("\n✓ IntegrationDefinition imported")
    assert hasattr(IntegrationDefinition, 'get_trigger'), "IntegrationDefinition missing get_trigger"
    assert hasattr(IntegrationDefinition, 'get_action'), "IntegrationDefinition missing get_action"
    print("  - Has get_trigger() method")
    print("  - Has get_action() method")
    
    # Check FieldSchema
    print("\n✓ FieldSchema imported")
    test_field = FieldSchema(
        key="test",
        label="Test Field",
        type="string",
        required=True
    )
    field_dict = test_field.to_dict()
    assert "key" in field_dict, "FieldSchema.to_dict() missing 'key'"
    assert "type" in field_dict, "FieldSchema.to_dict() missing 'type'"
    print("  - Can create FieldSchema instance")
    print("  - Has to_dict() method")
    
    # Check AuthConfig
    print("\n✓ AuthConfig imported")
    assert hasattr(AuthConfig, 'oauth2'), "AuthConfig missing oauth2"
    assert hasattr(AuthConfig, 'api_key'), "AuthConfig missing api_key"
    assert hasattr(AuthConfig, 'webhook_url'), "AuthConfig missing webhook_url"
    assert hasattr(AuthConfig, 'none'), "AuthConfig missing none"
    print("  - Has oauth2() helper")
    print("  - Has api_key() helper")
    print("  - Has webhook_url() helper")
    print("  - Has none() helper")


async def test_webhook_integration():
    """Test 2: Verify webhook integration is complete"""
    print_section("TEST 2: Webhook Integration")
    
    from app.integrations.webhook import webhook_integration, INTEGRATION_METADATA
    
    print(f"✓ Integration loaded: {webhook_integration.name}")
    print(f"  ID: {webhook_integration.id}")
    print(f"  Description: {webhook_integration.description}")
    print(f"  Auth type: {webhook_integration.auth_type}")
    print(f"  Triggers: {len(webhook_integration.triggers)}")
    print(f"  Actions: {len(webhook_integration.actions)}")
    
    # Check trigger
    assert len(webhook_integration.triggers) == 1, "Webhook should have 1 trigger"
    trigger = webhook_integration.triggers[0]
    print(f"\n✓ Trigger: {trigger.name}")
    print(f"  ID: {trigger.id}")
    print(f"  Type: {trigger.trigger_type}")
    assert trigger.trigger_type == "webhook", "Should be webhook type"
    
    # Check schemas
    input_schema = trigger.get_input_schema()
    output_schema = trigger.get_output_schema()
    print(f"  Input schema fields: {len(input_schema)}")
    print(f"  Output schema fields: {len(output_schema)}")
    assert len(output_schema) > 0, "Should have output schema"
    
    # Test webhook handling
    print("\n✓ Testing webhook handling...")
    test_payload = {"test": "data", "user_id": 123}
    test_headers = {"content-type": "application/json"}
    result = await trigger.handle_webhook(test_payload, test_headers)
    
    assert "data" in result, "Result should contain 'data'"
    assert result["data"] == test_payload, "Data should be preserved"
    print(f"  Webhook processed successfully")
    print(f"  Output keys: {list(result.keys())}")


async def test_discord_integration():
    """Test 3: Verify Discord integration is complete"""
    print_section("TEST 3: Discord Integration")
    
    from app.integrations.discord import discord_integration, INTEGRATION_METADATA
    
    print(f"✓ Integration loaded: {discord_integration.name}")
    print(f"  ID: {discord_integration.id}")
    print(f"  Description: {discord_integration.description}")
    print(f"  Auth type: {discord_integration.auth_type}")
    print(f"  Triggers: {len(discord_integration.triggers)}")
    print(f"  Actions: {len(discord_integration.actions)}")
    
    # Check action
    assert len(discord_integration.actions) == 1, "Discord should have 1 action"
    action = discord_integration.actions[0]
    print(f"\n✓ Action: {action.name}")
    print(f"  ID: {action.id}")
    
    # Check schemas
    input_schema = action.get_input_schema()
    output_schema = action.get_output_schema()
    print(f"  Input schema fields: {len(input_schema)}")
    for field in input_schema:
        print(f"    - {field.key} ({field.type}): {field.label}")
    print(f"  Output schema fields: {len(output_schema)}")
    for field in output_schema:
        print(f"    - {field.key} ({field.type}): {field.label}")
    
    assert any(f.key == "message_content" for f in input_schema), "Should have message_content field"
    assert any(f.key == "message_id" for f in output_schema), "Should have message_id in output"


async def test_registry():
    """Test 4: Verify registry functionality"""
    print_section("TEST 4: Integration Registry")
    
    from app.integrations.registry import (
        integration_registry,
        register_all_integrations
    )
    
    # Register all
    print("Registering integrations...")
    register_all_integrations()
    
    # Test list_integrations
    print("\n✓ Testing list_integrations()...")
    integrations = integration_registry.list_integrations()
    print(f"  Found {len(integrations)} integrations")
    assert len(integrations) >= 2, "Should have at least 2 integrations"
    
    for integ in integrations:
        print(f"  - {integ['name']} ({integ['id']})")
        print(f"    Triggers: {integ['trigger_count']}, Actions: {integ['action_count']}")
    
    # Test get_integration
    print("\n✓ Testing get_integration()...")
    discord = integration_registry.get_integration("discord")
    assert discord is not None, "Should find Discord integration"
    print(f"  Retrieved: {discord.name}")
    
    webhook = integration_registry.get_integration("webhook")
    assert webhook is not None, "Should find Webhook integration"
    print(f"  Retrieved: {webhook.name}")
    
    # Test get_action
    print("\n✓ Testing get_action()...")
    action = integration_registry.get_action("discord", "send_message")
    assert action is not None, "Should find Discord send_message action"
    print(f"  Retrieved: {action.name}")
    
    # Test get_trigger
    print("\n✓ Testing get_trigger()...")
    trigger = integration_registry.get_trigger("webhook", "incoming_webhook")
    assert trigger is not None, "Should find webhook incoming_webhook trigger"
    print(f"  Retrieved: {trigger.name}")
    
    # Test stats
    print("\n✓ Testing get_stats()...")
    stats = integration_registry.get_stats()
    print(f"  Total integrations: {stats['total_integrations']}")
    print(f"  Total triggers: {stats['total_triggers']}")
    print(f"  Total actions: {stats['total_actions']}")
    print(f"  Categories: {list(stats['categories'].keys())}")


async def test_serialization():
    """Test 5: Verify to_dict() methods work correctly"""
    print_section("TEST 5: Serialization (to_dict)")
    
    from app.integrations import integration_registry
    
    # Don't re-register, use existing registry
    
    # Test integration to_dict
    print("✓ Testing IntegrationDefinition.to_dict()...")
    discord = integration_registry.get_integration("discord")
    discord_dict = discord.to_dict()
    
    required_keys = ["id", "name", "description", "icon_url", "auth_type", 
                     "triggers", "actions", "trigger_count", "action_count"]
    for key in required_keys:
        assert key in discord_dict, f"Missing key: {key}"
    print(f"  All required keys present: {', '.join(required_keys)}")
    
    # Test action to_dict
    print("\n✓ Testing BaseAction.to_dict()...")
    action = integration_registry.get_action("discord", "send_message")
    action_dict = action.to_dict()
    
    required_keys = ["id", "name", "description", "input_schema", "output_schema"]
    for key in required_keys:
        assert key in action_dict, f"Missing key: {key}"
    print(f"  All required keys present: {', '.join(required_keys)}")
    
    # Verify schemas are properly serialized
    assert isinstance(action_dict["input_schema"], list), "input_schema should be a list"
    assert len(action_dict["input_schema"]) > 0, "input_schema should have fields"
    
    first_field = action_dict["input_schema"][0]
    assert "key" in first_field, "Field missing 'key'"
    assert "type" in first_field, "Field missing 'type'"
    assert "label" in first_field, "Field missing 'label'"
    print(f"  Schema fields properly formatted")
    
    # Test trigger to_dict
    print("\n✓ Testing BaseTrigger.to_dict()...")
    trigger = integration_registry.get_trigger("webhook", "incoming_webhook")
    trigger_dict = trigger.to_dict()
    
    required_keys = ["id", "name", "description", "trigger_type", "input_schema", "output_schema"]
    for key in required_keys:
        assert key in trigger_dict, f"Missing key: {key}"
    print(f"  All required keys present: {', '.join(required_keys)}")


async def test_api_compatibility():
    """Test 6: Verify data structures are API-ready"""
    print_section("TEST 6: API Compatibility")
    
    from app.integrations import integration_registry
    
    # Don't re-register, use existing registry
    
    print("✓ Testing JSON serialization...")
    integrations = integration_registry.list_integrations()
    
    # Try to serialize to JSON
    try:
        json_str = json.dumps(integrations, indent=2)
        print("  Successfully serialized to JSON")
        print(f"  JSON size: {len(json_str)} bytes")
        
        # Parse it back
        parsed = json.loads(json_str)
        assert len(parsed) == len(integrations), "Deserialization mismatch"
        print("  Successfully deserialized from JSON")
    except Exception as e:
        raise AssertionError(f"JSON serialization failed: {e}")
    
    print("\n✓ Testing integration detail serialization...")
    discord = integration_registry.get_integration("discord")
    discord_dict = discord.to_dict()
    
    try:
        json_str = json.dumps(discord_dict, indent=2)
        print("  Successfully serialized integration to JSON")
        
        # Verify structure
        parsed = json.loads(json_str)
        assert "actions" in parsed, "Missing actions"
        assert isinstance(parsed["actions"], list), "Actions should be a list"
        assert len(parsed["actions"]) > 0, "Should have actions"
        
        action = parsed["actions"][0]
        assert "input_schema" in action, "Action missing input_schema"
        assert "output_schema" in action, "Action missing output_schema"
        print("  Integration structure is API-ready")
    except Exception as e:
        raise AssertionError(f"Integration serialization failed: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  DAY 3 INTEGRATION PLUGIN ARCHITECTURE - AUDIT")
    print("=" * 70)
    
    tests = [
        ("Base Classes", test_base_classes),
        ("Webhook Integration", test_webhook_integration),
        ("Discord Integration", test_discord_integration),
        ("Integration Registry", test_registry),
        ("Serialization", test_serialization),
        ("API Compatibility", test_api_compatibility),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Final summary
    print("\n" + "=" * 70)
    print("  AUDIT SUMMARY")
    print("=" * 70)
    print(f"  Total tests: {len(tests)}")
    print(f"  Passed: {passed} ✓")
    print(f"  Failed: {failed} {'❌' if failed > 0 else ''}")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Day 3 implementation is complete.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
