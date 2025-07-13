# Discord Auto Server Setup Bot - Advanced Edition

A comprehensive Discord bot that automatically sets up your server with organized categories, channels, roles, and advanced features including verification, translation, and chat history.

## 🚀 Enhanced Features

### 🏗️ **Core Server Setup**
- **Automatic Server Structure**: Creates organized categories and channels
- **Dynamic Role Management**: Custom roles with specific permissions
- **Permission Configuration**: Advanced channel permissions for different roles
- **Template System**: 5 professional server templates
- **Setup Logging**: Comprehensive action logging

### 🎭 **Advanced Role Management**
- **Custom Role Creation**: Dynamic role creation with custom permissions
- **Permission Hierarchy**: VIP, Rookie, and custom role configurations
- **Color-coded Roles**: Hex color support for role customization
- **Interactive UI**: Modal-based role configuration

### 🔐 **Verification System**
- **Automatic Verification**: DM-based verification codes
- **Security Features**: 6-digit verification codes
- **Role Assignment**: Automatic verified role assignment
- **User Management**: Comprehensive verification tracking

### 🤖 **Interactive Chatbot**
- **Natural Language Processing**: Human-like conversations
- **Context-aware Responses**: Intelligent response system
- **Greeting System**: Welcome and farewell interactions
- **Help Integration**: Contextual assistance

### 📜 **Chat History & Search**
- **Message Storage**: SQLite database for message history
- **Advanced Search**: Search past conversations by keywords
- **Moderation Tools**: History-based moderation features
- **Data Analytics**: User activity tracking

### 🌐 **Translation System**
- **Multi-language Support**: 100+ languages supported
- **Real-time Translation**: Instant message translation
- **Google Translate API**: Professional translation service
- **Language Detection**: Automatic source language detection

## Quick Start

### 1. Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token

### 2. Setup Environment

1. Copy `.env.example` to `.env`
2. Edit `.env` and add your bot token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
python modern_bot.py
```

## Bot Invite

Use this URL to invite your bot to a server (replace CLIENT_ID with your bot's client ID):

```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=268446720&scope=bot+applications.commands
```

Required permissions:
- Manage Channels
- Manage Roles
- Send Messages
- Manage Webhooks
- Read Message History
- Add Reactions
- Use Slash Commands

## ⚡ Slash Commands

### **Main Commands:**
- `/setup` - Setup your server with templates
- `/templates` - Show all available server templates  
- `/preview <template>` - Preview what a template will create
- `/info` - Show bot information and all commands

### **🎭 Advanced Features:**
- `/roleconfig` - Configure custom roles with permissions
- `/verify <code>` - Verify your account with DM code
- `/search_history <query>` - Search chat history for specific messages
- `/translate <text> <language>` - Translate messages to different languages
- `/setup_verification` - Setup verification system for new members

### **🎨 Available Templates:**
- **Default** - Standard server setup with basic categories
- **Gaming** - Gaming-focused with LFG and tournaments
- **Professional** - Business server with departments  
- **Educational** - Study server with courses and tutoring
- **Minimal** - Basic setup with essential channels

## What Gets Created

### Categories & Channels
- 📋 **Information**: rules, announcements, welcome
- 💬 **General**: general, memes, bot-commands
- 🔊 **Voice Channels**: General, Music, Gaming
- 👨‍💼 **Staff**: staff-chat, mod-logs, setup-log

### Roles
- **Admin**: Full administrator permissions
- **Moderator**: Channel and member management
- **Member**: Basic chat and voice permissions
- **Muted**: Restricted permissions

### Utility Bots
- **Dyno**: Moderation bot
- **MEE6**: Leveling and moderation
- **Hydra**: Music bot

## Customization

You can modify the server template by editing `templates/default_template.yaml`. The template includes:
- Categories and channels structure
- Role permissions
- Utility bot recommendations

## Project Structure

```
discord-auto-setup-bot/
├── modern_bot.py          # Enhanced main bot file with all features
├── setup_handler.py       # Core setup logic
├── bot_data.db           # SQLite database for message history
├── templates/
│   ├── default_template.yaml    # Standard server template
│   ├── gaming_template.yaml     # Gaming server template
│   ├── professional_template.yaml # Business server template
│   ├── educational_template.yaml  # Study server template
│   └── minimal_template.yaml     # Basic server template
├── requirements.txt       # All dependencies
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Environment variables template
├── README.md            # This file
├── DEPLOYMENT_GUIDE.md   # Comprehensive deployment guide
└── .gitignore           # Git ignore file
```

## 🛠️ Development

The bot is built with:
- **py-cord**: Modern Discord API wrapper with slash commands
- **PyYAML**: YAML configuration parsing
- **python-dotenv**: Environment variable management
- **aiofiles**: Async file operations
- **sqlite3**: Database for message history and user data
- **googletrans**: Translation API integration
- **asyncio**: Asynchronous programming support

## 🚀 Advanced Features Implementation

### Database Schema:
- **message_history**: Stores all server messages for search
- **custom_roles**: Stores custom role configurations
- **verification_pending**: Manages verification codes

### UI Components:
- **Interactive Modals**: For role configuration
- **Selection Menus**: For template selection
- **Button Views**: For verification and setup actions
- **Dynamic Embeds**: For rich information display

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.
