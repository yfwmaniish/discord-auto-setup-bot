# Quick Setup Guide

## 🚀 Getting Your Bot Running

### Step 1: Create Discord Application
1. Go to https://discord.com/developers/applications
2. Click "New Application" and name it (e.g., "Auto Setup Bot")
3. Go to "Bot" tab and click "Add Bot"
4. Copy the bot token (keep it secret!)

### Step 2: Configure Environment
1. Open the `.env` file in this folder
2. Replace `your_bot_token_here` with your actual bot token:
   ```
   DISCORD_TOKEN=your_actual_bot_token_here
   ```

### Step 3: Get Bot Invite Link
1. In Discord Developer Portal, go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`
3. Select permissions:
   - Manage Channels
   - Manage Roles
   - Send Messages
   - Manage Webhooks
4. Copy the generated URL and use it to invite your bot to a server

### Step 4: Run the Bot
Double-click `run_bot.bat` or run in terminal:
```bash
python bot.py
```

## 🎯 Testing the Bot

1. In your Discord server, type `!info` to test if the bot responds
2. Type `!setup` to run the full server setup (Admin only)
3. Check the `#setup-log` channel for detailed logs

## 🔧 Troubleshooting

**Bot doesn't respond?**
- Check if the bot token is correct in `.env`
- Make sure the bot is online (green status)
- Verify the bot has Send Messages permission

**Setup fails?**
- Ensure bot has required permissions
- Check if roles/channels already exist
- Look at console output for error messages

**Permission errors?**
- Make sure you have Administrator permissions
- Bot needs Manage Channels and Manage Roles permissions

## 📝 Bot Commands

- `!setup` - Auto-setup server (Admin only)
- `!info` - Show bot information
- `!help` - Show all commands

## 🎨 Customization

Edit `templates/default_template.yaml` to customize:
- Channel names and structure
- Role permissions
- Utility bot recommendations

## 🆘 Need Help?

If you encounter issues:
1. Check the console output for error messages
2. Verify all permissions are granted
3. Make sure the bot token is valid
4. Try the minimal template first
