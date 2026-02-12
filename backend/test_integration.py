"""
Quick test script to verify the integration system works.

Run this after starting the server to test the Discord integration.
Usage: python test_integration.py
"""

import asyncio
import sys
from app.integrations import integration_registry, register_all_integrations


async def test_integration_system():
    """Test the integration registry and Discord integration"""
    
    print("=" * 70)
    print("INTEGRATION SYSTEM TEST")
    print("=" * 70)
    
    # Initialize: Register all integrations first
    print("\n0. Registering integrations...")
    register_all_integrations()
    
    # Test 1: List all integrations
    print("\n1. Testing integration registry...")
    integrations = integration_registry.list_integrations()
    print(f"   ✓ Found {len(integrations)} integrations")
    for integration in integrations:
        print(f"     - {integration['name']} ({integration['id']})")
    
    # Test 2: Get Discord integration
    print("\n2. Testing Discord integration...")
    discord = integration_registry.get_integration("discord")
    if discord:
        print(f"   ✓ Discord integration loaded")
        print(f"     - Name: {discord.name}")
        print(f"     - Auth Type: {discord.auth_type}")
        print(f"     - Actions: {len(discord.actions)}")
        print(f"     - Triggers: {len(discord.triggers)}")
    else:
        print("   ✗ Discord integration not found!")
        return False
    
    # Test 3: Get send_message action
    print("\n3. Testing Discord send_message action...")
    action = integration_registry.get_action("discord", "send_message")
    if action:
        print(f"   ✓ Action found: {action.name}")
        print(f"     - Input schema fields: {len(action.get_input_schema())}")
        print(f"     - Output schema fields: {len(action.get_output_schema())}")
        
        # Show input schema
        print("\n     Input fields:")
        for field in action.get_input_schema():
            required = "required" if field.required else "optional"
            print(f"       - {field.key} ({field.type}, {required})")
    else:
        print("   ✗ send_message action not found!")
        return False
    
    # Test 4: Test webhook integration
    print("\n4. Testing Webhook integration...")
    webhook = integration_registry.get_integration("webhook")
    if webhook:
        print(f"   ✓ Webhook integration loaded")
        print(f"     - Triggers: {len(webhook.triggers)}")
        print(f"     - Actions: {len(webhook.actions)}")
    else:
        print("   ✗ Webhook integration not found!")
        return False
    
    # Test 5: Get stats
    print("\n5. Testing registry stats...")
    stats = integration_registry.get_stats()
    print(f"   ✓ Stats retrieved")
    print(f"     - Total integrations: {stats['total_integrations']}")
    print(f"     - Total triggers: {stats['total_triggers']}")
    print(f"     - Total actions: {stats['total_actions']}")
    print(f"     - Auth types: {', '.join(stats['auth_types'].keys())}")
    print(f"     - Categories: {', '.join(stats['categories'].keys())}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("=" * 70)
    
    # Test 6: Optional - Test actual Discord execution
    print("\n6. Discord Execution Test (optional)")
    print("   To test actual Discord message sending:")
    print("   - Get a Discord webhook URL from your server")
    print("   - Run: python test_integration.py <webhook_url>")
    
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]
        print(f"\n   Testing with webhook URL: {webhook_url[:50]}...")
        
        try:
            result = await action.execute(
                credentials={"webhook_url": webhook_url},
                config={"message_content": "🎉 Integration system test successful!"}
            )
            
            if result.get("success"):
                print(f"   ✓ Message sent successfully!")
                print(f"     - Message ID: {result.get('message_id')}")
                print(f"     - Channel ID: {result.get('channel_id')}")
            else:
                print(f"   ✗ Message failed to send")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    
    return True


if __name__ == "__main__":
    asyncio.run(test_integration_system())
