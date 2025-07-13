import os
import discord
from discord.ext import commands
from discord.ui import Button, View, Select, Modal, InputText
from dotenv import load_dotenv
from setup_handler import ServerSetupHandler
import asyncio
import json
import datetime
from typing import Optional, List, Dict
import re
from googletrans import Translator
import random
import sqlite3
from contextlib import asynccontextmanager

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Bot setup with slash commands
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = discord.Bot(
    description="Advanced Discord Auto Setup Bot with Slash Commands",
    intents=intents
)

setup_handler = ServerSetupHandler(bot)
translator = Translator()

# Database setup
class DatabaseManager:
    def __init__(self):
        self.db_path = "bot_data.db"
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                channel_id TEXT,
                user_id TEXT,
                username TEXT,
                message_content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                role_name TEXT,
                permissions TEXT,
                color TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_pending (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                user_id TEXT,
                verification_code TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_message(self, guild_id, channel_id, user_id, username, message_content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO message_history (guild_id, channel_id, user_id, username, message_content)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(guild_id), str(channel_id), str(user_id), username, message_content))
        conn.commit()
        conn.close()
    
    def search_messages(self, guild_id, query, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username, message_content, timestamp 
            FROM message_history 
            WHERE guild_id = ? AND message_content LIKE ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (str(guild_id), f'%{query}%', limit))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def add_custom_role(self, guild_id, role_name, permissions, color):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO custom_roles (guild_id, role_name, permissions, color)
            VALUES (?, ?, ?, ?)
        ''', (str(guild_id), role_name, permissions, color))
        conn.commit()
        conn.close()
    
    def get_custom_roles(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role_name, permissions, color 
            FROM custom_roles 
            WHERE guild_id = ?
        ''', (str(guild_id),))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def add_verification_code(self, guild_id, user_id, code):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO verification_pending (guild_id, user_id, verification_code)
            VALUES (?, ?, ?)
        ''', (str(guild_id), str(user_id), code))
        conn.commit()
        conn.close()
    
    def verify_user(self, guild_id, user_id, code):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM verification_pending 
            WHERE guild_id = ? AND user_id = ? AND verification_code = ?
        ''', (str(guild_id), str(user_id), code))
        result = cursor.fetchone()
        
        if result:
            cursor.execute('''
                DELETE FROM verification_pending 
                WHERE guild_id = ? AND user_id = ?
            ''', (str(guild_id), str(user_id)))
            conn.commit()
        
        conn.close()
        return result is not None

db_manager = DatabaseManager()

# Chatbot responses
CHATBOT_RESPONSES = {
    "greeting": [
        "Hey there! 👋 How can I help you today?",
        "Hello! 😊 What's up?",
        "Hi! 🌟 Ready to make your server awesome?",
        "Greetings! 🎉 How can I assist you?"
    ],
    "how_are_you": [
        "I'm doing great! Thanks for asking! 😄",
        "I'm fantastic! Ready to help setup some servers! 🚀",
        "I'm wonderful! How about you? 😊",
        "I'm doing amazing! What can I do for you? ✨"
    ],
    "thanks": [
        "You're very welcome! 😊",
        "No problem at all! Happy to help! 🎉",
        "Anytime! That's what I'm here for! 💫",
        "Glad I could help! 🌟"
    ],
    "goodbye": [
        "See you later! 👋",
        "Goodbye! Feel free to call me anytime! 😊",
        "Until next time! 🌟",
        "Bye! Take care! 🎉"
    ],
    "confused": [
        "I'm not sure I understand. Could you try asking differently? 🤔",
        "Hmm, I didn't quite get that. Can you rephrase? 😅",
        "I'm a bit confused. Could you clarify? 🤷‍♂️",
        "Sorry, I didn't catch that. Try again? 😊"
    ]
}

def get_chatbot_response(message_content):
    content = message_content.lower()
    
    if any(word in content for word in ['hello', 'hi', 'hey', 'sup', 'yo']):
        return random.choice(CHATBOT_RESPONSES["greeting"])
    elif any(word in content for word in ['how are you', 'how you doing', 'how are u']):
        return random.choice(CHATBOT_RESPONSES["how_are_you"])
    elif any(word in content for word in ['thanks', 'thank you', 'thx', 'ty']):
        return random.choice(CHATBOT_RESPONSES["thanks"])
    elif any(word in content for word in ['bye', 'goodbye', 'see you', 'cya']):
        return random.choice(CHATBOT_RESPONSES["goodbye"])
    else:
        return random.choice(CHATBOT_RESPONSES["confused"])

@bot.event
async def on_ready():
    print(f'🚀 {bot.user.name} is online!')
    print(f'📊 Connected to {len(bot.guilds)} servers')
    print(f'⚡ Slash commands enabled!')

@bot.event
async def on_guild_join(guild):
    """Enhanced welcome message when bot joins a server"""
    channel = None
    for ch in guild.text_channels:
        if ch.permissions_for(guild.me).send_messages:
            channel = ch
            break
    
    if channel:
        embed = discord.Embed(
            title="🎉 Welcome to the Future of Discord Setup!",
            description="Thanks for adding me! I'm now **slash command enabled** for a better experience.",
            color=0x00ff00
        )
        embed.add_field(
            name="🔥 Quick Start",
            value="Use `/setup` to see all available templates and get started!",
            inline=False
        )
        embed.add_field(
            name="⚡ New Features",
            value="• Modern slash commands\n• Interactive buttons\n• Template selection menus\n• Enhanced UI experience",
            inline=False
        )
        
        view = QuickStartView()
        await channel.send(embed=embed, view=view)

class TemplateSelectView(View):
    def __init__(self, ctx):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.add_item(TemplateSelect())

class TemplateSelect(Select):
    def __init__(self):
        # Define template options
        options = [
            discord.SelectOption(
                label="Default",
                description="🏠 Standard server setup with basic categories",
                emoji="🏠",
                value="default"
            ),
            discord.SelectOption(
                label="Gaming",
                description="🎮 Gaming-focused with LFG and tournaments",
                emoji="🎮",
                value="gaming"
            ),
            discord.SelectOption(
                label="Professional",
                description="💼 Business server with departments",
                emoji="💼",
                value="professional"
            ),
            discord.SelectOption(
                label="Educational",
                description="📚 Study server with courses and tutoring",
                emoji="📚",
                value="educational"
            ),
            discord.SelectOption(
                label="Minimal",
                description="⚡ Basic setup with essential channels",
                emoji="⚡",
                value="minimal"
            )
        ]
        
        super().__init__(
            placeholder="Choose a server template...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        template_name = self.values[0]
        
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permissions to use this command.",
                ephemeral=True
            )
            return
        
        # Check bot permissions
        required_perms = ['manage_channels', 'manage_roles', 'manage_webhooks', 'send_messages']
        missing_perms = []
        
        for perm in required_perms:
            if not getattr(interaction.guild.me.guild_permissions, perm):
                missing_perms.append(perm.replace('_', ' ').title())
        
        if missing_perms:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description=f"I need these permissions:\\n\\n• {chr(10).join(missing_perms)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Start setup process
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🔧 Setting up your server...",
            description=f"Using **{template_name}** template\\n\\nThis may take a few moments...",
            color=0xffff00
        )
        await interaction.followup.send(embed=embed)
        
        # Load template and setup
        template = await setup_handler.load_template(template_name)
        success, result_message = await setup_handler.setup_server(interaction.guild, template)
        
        if success:
            embed = discord.Embed(
                title="✅ Server Setup Complete!",
                description=result_message,
                color=0x00ff00
            )
            embed.add_field(
                name="Template Used:",
                value=f"**{template_name.title()}**",
                inline=False
            )
            view = PostSetupView()
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            embed = discord.Embed(
                title="❌ Setup Failed",
                description=result_message,
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)

class PreviewView(View):
    def __init__(self, template_name, template_data):
        super().__init__(timeout=300)
        self.template_name = template_name
        self.template_data = template_data
        
    @discord.ui.button(label="Apply This Template", style=discord.ButtonStyle.green, emoji="✅")
    async def apply_template(self, button: Button, interaction: discord.Interaction):
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permissions to use this command.",
                ephemeral=True
            )
            return
        
        # Start setup
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🔧 Applying template...",
            description=f"Setting up **{self.template_name}** template",
            color=0xffff00
        )
        await interaction.followup.send(embed=embed)
        
        success, result_message = await setup_handler.setup_server(interaction.guild, self.template_data)
        
        if success:
            embed = discord.Embed(
                title="✅ Template Applied Successfully!",
                description=result_message,
                color=0x00ff00
            )
            view = PostSetupView()
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            embed = discord.Embed(
                title="❌ Setup Failed",
                description=result_message,
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)

class PostSetupView(View):
    def __init__(self):
        super().__init__(timeout=300)
        
    @discord.ui.button(label="View Setup Logs", style=discord.ButtonStyle.secondary, emoji="📋")
    async def view_logs(self, button: Button, interaction: discord.Interaction):
        # Find setup-log channel
        log_channel = discord.utils.get(interaction.guild.channels, name="setup-log")
        if log_channel:
            await interaction.response.send_message(
                f"📋 Setup logs can be found in {log_channel.mention}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "📋 Setup logs channel not found.",
                ephemeral=True
            )
    
    @discord.ui.button(label="Setup Another Server", style=discord.ButtonStyle.blurple, emoji="🔄")
    async def setup_another(self, button: Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎨 Choose Another Template",
            description="Select a template to setup another server configuration:",
            color=0x9932cc
        )
        view = TemplateSelectView(interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class QuickStartView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Get Started", style=discord.ButtonStyle.green, emoji="🚀")
    async def get_started(self, button: Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎨 Choose Your Server Template",
            description="Select a template to automatically setup your server:",
            color=0x9932cc
        )
        view = TemplateSelectView(interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Custom Role Management UI
class RoleConfigModal(Modal):
    def __init__(self, guild_id):
        super().__init__(title="🎭 Custom Role Configuration")
        self.guild_id = guild_id
        
        self.role_name = InputText(
            label="Role Name",
            placeholder="e.g., VIP, Rookie, Member",
            required=True
        )
        
        self.permissions = InputText(
            label="Permissions (comma-separated)",
            placeholder="e.g., send_messages, manage_messages, kick_members",
            style=discord.InputTextStyle.paragraph,
            required=True
        )
        
        self.color = InputText(
            label="Role Color (hex)",
            placeholder="e.g., #FF0000, #00FF00, #0000FF",
            required=False
        )
        
        self.add_item(self.role_name)
        self.add_item(self.permissions)
        self.add_item(self.color)
    
    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permissions to configure roles.",
                ephemeral=True
            )
            return
        
        # Save role configuration
        color_hex = self.color.value if self.color.value else "#7289da"
        db_manager.add_custom_role(
            self.guild_id,
            self.role_name.value,
            self.permissions.value,
            color_hex
        )
        
        # Create the role
        try:
            color_int = int(color_hex.replace('#', ''), 16)
            role = await interaction.guild.create_role(
                name=self.role_name.value,
                color=discord.Color(color_int),
                mentionable=True
            )
            
            # Set permissions
            perms_list = [p.strip() for p in self.permissions.value.split(',')]
            permissions = discord.Permissions()
            
            for perm in perms_list:
                if hasattr(permissions, perm):
                    setattr(permissions, perm, True)
            
            await role.edit(permissions=permissions)
            
            embed = discord.Embed(
                title="✅ Role Created Successfully!",
                description=f"**{self.role_name.value}** has been created with custom permissions.",
                color=color_int
            )
            embed.add_field(
                name="Permissions",
                value=self.permissions.value,
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error creating role: {str(e)}",
                ephemeral=True
            )

class VerificationView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Verify Account", style=discord.ButtonStyle.green, emoji="✅")
    async def verify_button(self, button: Button, interaction: discord.Interaction):
        # Generate verification code
        verification_code = ''.join(random.choices('0123456789', k=6))
        
        # Save to database
        db_manager.add_verification_code(
            interaction.guild.id,
            interaction.user.id,
            verification_code
        )
        
        # Send DM with verification code
        try:
            embed = discord.Embed(
                title="🔐 Account Verification",
                description=f"Your verification code for **{interaction.guild.name}** is: `{verification_code}`",
                color=0x00ff00
            )
            embed.add_field(
                name="Next Steps:",
                value="Use `/verify` command with this code in the server.",
                inline=False
            )
            
            await interaction.user.send(embed=embed)
            
            await interaction.response.send_message(
                "📧 Verification code sent to your DMs! Check your messages.",
                ephemeral=True
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ Couldn't send DM. Your verification code is: `{verification_code}`\nUse `/verify {verification_code}` to verify.",
                ephemeral=True
            )

# Auto-Moderation Setup
@bot.event
async def on_message(message):
    # Prevent bot from responding to its own messages
    if message.author.bot:
        return
    
    # Store message in database for history
    db_manager.add_message(
        message.guild.id,
        message.channel.id,
        message.author.id,
        message.author.display_name,
        message.content
    )
    
    # Simple auto-moderation filter
    bad_words = ["spam", "offensive"]
    if any(word in message.content.lower() for word in bad_words):
        await message.delete()
        await message.channel.send(f"{message.author.mention}, please avoid using inappropriate language.", delete_after=10)
        return
    
    # Chatbot interaction
    if bot.user.mentioned_in(message) or message.content.lower().startswith(f'{bot.user.name.lower()}'):
        response = get_chatbot_response(message.content)
        await message.reply(response)
    
    # Process commands
    await bot.process_commands(message)

# Welcome Message Setup
@bot.event
async def on_member_join(member):
    guild = member.guild
    # Find a channel to send welcome message
    welcome_channel = discord.utils.get(guild.text_channels, name="welcome")
    
    if welcome_channel:
        embed = discord.Embed(
            title="🎉 Welcome!",
            description=(
                f"Hello {member.mention}, welcome to **{guild.name}**! 🎉"
                "\nFeel free to explore and engage with our awesome community!"
                "\nMake sure to check out #rules and say hello!"
            ),
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else guild.icon.url)
        await welcome_channel.send(embed=embed)

# Reaction Roles Setup
@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id != 987654321098765432:
        return
    
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    
    # Define reaction-role mapping
    role_map = {
        "🔴": "Role 1",
        "🔵": "Role 2",
        "🟢": "Role 3"
    }
    
    role_name = role_map.get(payload.emoji.name)
    if role_name:
        role = discord.utils.get(guild.roles, name=role_name)
        member = guild.get_member(payload.user_id)
        
        if role and member:
            await member.add_roles(role)
            try:
                await member.send(f"You've been given the '{role.name}' role in {guild.name}!")
            except discord.HTTPException:
                pass

# Slash Commands
@bot.slash_command(name="setup", description="Setup your server with automated categories, channels, and roles")
async def setup(
    ctx: discord.ApplicationContext,
    template: discord.Option(
        str,
        description="Choose a server template",
        choices=["default", "gaming", "professional", "educational", "minimal"],
        required=False
    )
):
    if template:
        # Direct setup with specified template
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return
        
        # Check bot permissions
        required_perms = ['manage_channels', 'manage_roles', 'manage_webhooks', 'send_messages']
        missing_perms = []
        
        for perm in required_perms:
            if not getattr(ctx.guild.me.guild_permissions, perm):
                missing_perms.append(perm.replace('_', ' ').title())
        
        if missing_perms:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description=f"I need these permissions:\\n\\n• {chr(10).join(missing_perms)}",
                color=0xff0000
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        # Start setup
        await ctx.defer()
        
        embed = discord.Embed(
            title="🔧 Setting up your server...",
            description=f"Using **{template}** template\\n\\nThis may take a few moments...",
            color=0xffff00
        )
        await ctx.followup.send(embed=embed)
        
        # Load template and setup
        template_data = await setup_handler.load_template(template)
        success, result_message = await setup_handler.setup_server(ctx.guild, template_data)
        
        if success:
            embed = discord.Embed(
                title="✅ Server Setup Complete!",
                description=result_message,
                color=0x00ff00
            )
            embed.add_field(
                name="Template Used:",
                value=f"**{template.title()}**",
                inline=False
            )
            view = PostSetupView()
            await ctx.edit_original_response(embed=embed, view=view)
        else:
            embed = discord.Embed(
                title="❌ Setup Failed",
                description=result_message,
                color=0xff0000
            )
            await ctx.edit_original_response(embed=embed)
    else:
        # Show template selection
        embed = discord.Embed(
            title="🎨 Choose Your Server Template",
            description="Select a template to automatically setup your server:",
            color=0x9932cc
        )
        view = TemplateSelectView(ctx)
        await ctx.respond(embed=embed, view=view, ephemeral=True)

@bot.slash_command(name="templates", description="Show all available server templates")
async def templates(ctx: discord.ApplicationContext):
    available_templates = await setup_handler.get_available_templates()
    
    embed = discord.Embed(
        title="🎨 Available Server Templates",
        description="Choose from these professionally designed templates:",
        color=0x9932cc
    )
    
    for name, description in available_templates.items():
        embed.add_field(
            name=f"**{name.title()}**",
            value=description,
            inline=False
        )
    
    embed.set_footer(text="Use /setup to choose a template or /preview to see details")
    await ctx.respond(embed=embed)

@bot.slash_command(name="preview", description="Preview what a template will create")
async def preview(
    ctx: discord.ApplicationContext,
    template: discord.Option(
        str,
        description="Template to preview",
        choices=["default", "gaming", "professional", "educational", "minimal"],
        required=True
    )
):
    template_data = await setup_handler.load_template(template)
    
    if not template_data:
        await ctx.respond("❌ Template not found.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🔍 Template Preview: {template.title()}",
        description=f"Here's what the **{template}** template will create:",
        color=0x00bfff
    )
    
    # Categories and channels
    categories_text = ""
    for category in template_data.get('categories', []):
        categories_text += f"**{category['name']}**\\n"
        for channel in category.get('channels', []):
            emoji = "💬" if channel['type'] == 'text' else "🔊"
            categories_text += f"  {emoji} {channel['name']}\\n"
        categories_text += "\\n"
    
    embed.add_field(
        name="📁 Categories & Channels",
        value=categories_text[:1024] if categories_text else "None",
        inline=False
    )
    
    # Roles
    roles_text = ""
    for role in template_data.get('roles', []):
        roles_text += f"• {role['name']}\\n"
    
    embed.add_field(
        name="👥 Roles",
        value=roles_text[:1024] if roles_text else "None",
        inline=True
    )
    
    # Utility bots
    bots_text = ""
    for bot_info in template_data.get('utility_bots', []):
        bots_text += f"• {bot_info['name']}\\n"
    
    embed.add_field(
        name="🤖 Recommended Bots",
        value=bots_text[:1024] if bots_text else "None",
        inline=True
    )
    
    view = PreviewView(template, template_data)
    await ctx.respond(embed=embed, view=view)

# New Advanced Commands
@bot.slash_command(name="roleconfig", description="Configure custom roles with permissions")
async def roleconfig(ctx: discord.ApplicationContext):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("❌ You need Administrator permissions to configure roles.", ephemeral=True)
        return
    
    modal = RoleConfigModal(ctx.guild.id)
    await ctx.response.send_modal(modal)

@bot.slash_command(name="verify", description="Verify your account with the code sent to your DM")
async def verify(
    ctx: discord.ApplicationContext,
    code: discord.Option(str, description="6-digit verification code", required=True)
):
    success = db_manager.verify_user(ctx.guild.id, ctx.author.id, code)
    
    if success:
        # Give verified role
        verified_role = discord.utils.get(ctx.guild.roles, name="Verified")
        if not verified_role:
            # Create verified role if it doesn't exist
            verified_role = await ctx.guild.create_role(
                name="Verified",
                color=discord.Color.green(),
                mentionable=True
            )
        
        await ctx.author.add_roles(verified_role)
        
        embed = discord.Embed(
            title="✅ Verification Successful!",
            description=f"Welcome to **{ctx.guild.name}**! You now have access to all channels.",
            color=0x00ff00
        )
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="❌ Verification Failed",
            description="Invalid verification code. Please try again or request a new code.",
            color=0xff0000
        )
        await ctx.respond(embed=embed, ephemeral=True)

@bot.slash_command(name="search_history", description="Search chat history for specific messages")
async def search_history(
    ctx: discord.ApplicationContext,
    query: discord.Option(str, description="Search term", required=True),
    limit: discord.Option(int, description="Number of results (default: 10)", required=False, default=10)
):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.respond("❌ You need Manage Messages permissions to search history.", ephemeral=True)
        return
    
    results = db_manager.search_messages(ctx.guild.id, query, limit)
    
    if not results:
        embed = discord.Embed(
            title="🔍 No Results Found",
            description=f"No messages found containing '{query}'",
            color=0xffff00
        )
        await ctx.respond(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🔍 Search Results for '{query}'",
        description=f"Found {len(results)} message(s):",
        color=0x00bfff
    )
    
    for i, (username, message_content, timestamp) in enumerate(results[:5]):
        embed.add_field(
            name=f"**{username}** - {timestamp}",
            value=message_content[:100] + "..." if len(message_content) > 100 else message_content,
            inline=False
        )
    
    if len(results) > 5:
        embed.set_footer(text=f"Showing 5 of {len(results)} results. Use a more specific query for better results.")
    
    await ctx.respond(embed=embed, ephemeral=True)

@bot.slash_command(name="translate", description="Translate a message to another language")
async def translate_message(
    ctx: discord.ApplicationContext,
    text: discord.Option(str, description="Text to translate", required=True),
    target_language: discord.Option(str, description="Target language code (e.g., es, fr, de)", required=True)
):
    try:
        translation = translator.translate(text, dest=target_language)
        
        embed = discord.Embed(
            title="🌐 Translation Result",
            color=0x00ff00
        )
        embed.add_field(
            name=f"Original ({translation.src}):",
            value=text,
            inline=False
        )
        embed.add_field(
            name=f"Translated ({target_language}):",
            value=translation.text,
            inline=False
        )
        
        await ctx.respond(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Translation Failed",
            description=f"Error: {str(e)}\n\nMake sure you're using a valid language code (e.g., es, fr, de, ja, ko)",
            color=0xff0000
        )
        await ctx.respond(embed=embed, ephemeral=True)

@bot.slash_command(name="setup_verification", description="Setup verification system for new members")
async def setup_verification(ctx: discord.ApplicationContext):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("❌ You need Administrator permissions to setup verification.", ephemeral=True)
        return
    
    # Create verification channel if it doesn't exist
    verification_channel = discord.utils.get(ctx.guild.channels, name="verification")
    if not verification_channel:
        verification_channel = await ctx.guild.create_text_channel("verification")
    
    # Create verification embed and view
    embed = discord.Embed(
        title="🔐 Account Verification",
        description="Welcome to the server! Please verify your account to gain access to all channels.",
        color=0x00ff00
    )
    embed.add_field(
        name="How to verify:",
        value="1. Click the 'Verify Account' button below\n2. Check your DMs for a verification code\n3. Use `/verify <code>` to complete verification",
        inline=False
    )
    
    view = VerificationView()
    await verification_channel.send(embed=embed, view=view)
    
    await ctx.respond(f"✅ Verification system set up in {verification_channel.mention}!", ephemeral=True)

@bot.slash_command(name="info", description="Show information about the bot")
async def info(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="🤖 Discord Auto Setup Bot - Advanced Edition",
        description="Professional Discord server automation with modern slash commands!",
        color=0x0099ff
    )
    
    embed.add_field(
        name="⚡ Main Commands:",
        value="• `/setup` - Setup your server with templates\n• `/templates` - Show all available templates\n• `/preview` - Preview template details\n• `/info` - Show this information",
        inline=False
    )
    
    embed.add_field(
        name="🎭 Advanced Features:",
        value="• `/roleconfig` - Configure custom roles\n• `/verify` - Verify your account\n• `/search_history` - Search chat history\n• `/translate` - Translate messages\n• `/setup_verification` - Setup verification system",
        inline=False
    )
    
    embed.add_field(
        name="🎨 Available Templates:",
        value="• **Default** - Standard setup\n• **Gaming** - Gaming community\n• **Professional** - Business server\n• **Educational** - Study server\n• **Minimal** - Basic setup",
        inline=False
    )
    
    embed.add_field(
        name="✨ Modern Features:",
        value="• Interactive slash commands\n• Custom role management\n• Verification system\n• Chat history search\n• Translation support\n• Chatbot interactions",
        inline=False
    )
    
    embed.set_footer(text="Made with ❤️ using py-cord | Use /setup to get started!")
    await ctx.respond(embed=embed)

if __name__ == '__main__':
    if not token:
        print("Error: DISCORD_TOKEN not found!")
        print("Please add your bot token to the .env file.")
    else:
        bot.run(token)
