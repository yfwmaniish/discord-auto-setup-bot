#!/usr/bin/env python3
"""
Quick test script to verify bot configuration
"""
import os
import sys
from dotenv import load_dotenv

def test_configuration():
    """Test if bot configuration is valid"""
    print("🔍 Testing Discord Bot Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    
    # Check token
    if not token or token == 'your_bot_token_here':
        print("❌ Bot token not configured!")
        print("   Please add your bot token to the .env file")
        return False
    
    print("✅ Bot token found")
    
    # Check if token looks valid
    if not token.startswith(('MTA', 'MTI', 'MTE')) or len(token) < 50:
        print("⚠️  Bot token might be invalid")
        print("   Make sure you copied the full token from Discord Developer Portal")
    else:
        print("✅ Bot token format looks correct")
    
    # Test imports
    try:
        import discord
        print("✅ discord.py imported successfully")
    except ImportError:
        print("❌ discord.py not installed")
        print("   Run: pip install --user -r requirements.txt")
        return False
    
    try:
        import yaml
        print("✅ PyYAML imported successfully")
    except ImportError:
        print("❌ PyYAML not installed")
        return False
    
    try:
        from setup_handler import ServerSetupHandler
        print("✅ Setup handler imported successfully")
    except Exception as e:
        print(f"❌ Setup handler import failed: {e}")
        return False
    
    # Test template loading
    try:
        handler = ServerSetupHandler(None)
        template = handler.load_template()
        if template:
            print("✅ Template loaded successfully")
            print(f"   Found {len(template.get('categories', []))} categories")
            print(f"   Found {len(template.get('roles', []))} roles")
        else:
            print("❌ Template loading failed")
            return False
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Your bot is ready to run.")
    print("\nNext steps:")
    print("1. Run the bot: python bot.py")
    print("2. Invite it to your server")
    print("3. Type !setup in your server")
    
    return True

if __name__ == "__main__":
    success = test_configuration()
    if not success:
        sys.exit(1)
