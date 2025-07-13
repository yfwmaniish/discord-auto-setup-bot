import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from setup_handler import ServerSetupHandler

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
command_prefix = os.getenv('COMMAND_PREFIX', '!')

description = "A bot to automate Discord server setup."
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True  # Required for message content

bot = commands.Bot(command_prefix=command_prefix, description=description, intents=intents)
setup_handler = ServerSetupHandler(bot)

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name} (ID: {bot.user.id})')
    print('Ready to automate setups!')
    print(f'Bot is in {len(bot.guilds)} servers')

@bot.event
async def on_guild_join(guild):
    """Welcome message when bot joins a server"""
    # Find a channel to send welcome message
    channel = None
    for ch in guild.text_channels:
        if ch.permissions_for(guild.me).send_messages:
            channel = ch
            break
    
    if channel:
        embed = discord.Embed(
            title="👋 Hello! I'm your Discord Auto Setup Bot",
            description="Thanks for adding me to your server!\n\nUse `!setup` to automatically configure your server with:\n• Categories and channels\n• Roles with permissions\n• Utility bot recommendations\n\nType `!help` for more commands.",
            color=0x00ff00
        )
        await channel.send(embed=embed)

# Auto-Setup Command with Template Selection
@bot.command(name='setup')
@commands.has_permissions(administrator=True)
async def setup(ctx, template_type=None):
    """Set up the server with channels, roles, and permissions"""
    # Check if bot has required permissions
    required_perms = [
        'manage_channels', 'manage_roles', 'manage_webhooks', 'send_messages'
    ]
    
    missing_perms = []
    for perm in required_perms:
        if not getattr(ctx.guild.me.guild_permissions, perm):
            missing_perms.append(perm.replace('_', ' ').title())
    
    if missing_perms:
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description=f"I need the following permissions to set up your server:\n\n• {chr(10).join(missing_perms)}\n\nPlease grant these permissions and try again.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # If no template specified, use default
    if not template_type:
        template_type = "default"
    
    # Validate template
    available_templates = await setup_handler.get_available_templates()
    if template_type not in available_templates:
        embed = discord.Embed(
            title="❌ Invalid Template",
            description=f"Template '{template_type}' not found.\n\nAvailable templates:\n" + 
                       "\n".join([f"• `{name}` - {desc}" for name, desc in available_templates.items()]),
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Send initial message
    setup_embed = discord.Embed(
        title="🔧 Setting up your server...",
        description=f"Using template: **{template_type}**\n{available_templates[template_type]}\n\nThis may take a few moments. Please wait...",
        color=0xffff00
    )
    message = await ctx.send(embed=setup_embed)
    
    # Load template and perform setup
    template = await setup_handler.load_template(template_type)
    success, result_message = await setup_handler.setup_server(ctx.guild, template)
    
    if success:
        final_embed = discord.Embed(
            title="✅ Server Setup Complete!",
            description=result_message,
            color=0x00ff00
        )
        final_embed.add_field(
            name="Template Used:",
            value=f"**{template_type}** - {available_templates[template_type]}",
            inline=False
        )
        final_embed.add_field(
            name="What was created:",
            value="• Categories and channels\n• Roles with permissions\n• Staff-only areas\n• Utility bot recommendations",
            inline=False
        )
    else:
        final_embed = discord.Embed(
            title="❌ Setup Failed",
            description=result_message,
            color=0xff0000
        )
    
    await message.edit(embed=final_embed)

@bot.command(name='templates')
async def templates(ctx):
    """Show available server templates"""
    available_templates = await setup_handler.get_available_templates()
    
    embed = discord.Embed(
        title="🎨 Available Server Templates",
        description="Choose from these pre-made templates for your server setup:",
        color=0x9932cc
    )
    
    for name, description in available_templates.items():
        embed.add_field(
            name=f"`{name}`",
            value=description,
            inline=False
        )
    
    embed.add_field(
        name="Usage:",
        value="Use `!setup <template_name>` to set up your server\nExample: `!setup gaming`",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='preview')
async def preview(ctx, template_name="default"):
    """Preview what a template will create"""
    template = await setup_handler.load_template(template_name)
    
    if not template:
        embed = discord.Embed(
            title="❌ Template Not Found",
            description=f"Template '{template_name}' not found. Use `!templates` to see available templates.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"🔍 Template Preview: {template_name}",
        description=f"Here's what the **{template_name}** template will create:",
        color=0x00bfff
    )
    
    # Show categories and channels
    categories_text = ""
    for category in template.get('categories', []):
        categories_text += f"**{category['name']}**\n"
        for channel in category.get('channels', []):
            channel_emoji = "💬" if channel['type'] == 'text' else "🔊"
            categories_text += f"  {channel_emoji} {channel['name']}\n"
        categories_text += "\n"
    
    embed.add_field(
        name="📁 Categories & Channels",
        value=categories_text[:1024] if categories_text else "None",
        inline=False
    )
    
    # Show roles
    roles_text = ""
    for role in template.get('roles', []):
        roles_text += f"• {role['name']}\n"
    
    embed.add_field(
        name="👥 Roles",
        value=roles_text[:1024] if roles_text else "None",
        inline=True
    )
    
    # Show utility bots
    bots_text = ""
    for bot in template.get('utility_bots', []):
        bots_text += f"• {bot['name']}\n"
    
    embed.add_field(
        name="🤖 Recommended Bots",
        value=bots_text[:1024] if bots_text else "None",
        inline=True
    )
    
    embed.set_footer(text=f"Use !setup {template_name} to apply this template")
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx):
    """Show information about the bot"""
    embed = discord.Embed(
        title="🤖 Discord Auto Setup Bot - Advanced Edition",
        description="I help automate Discord server setup with multiple templates!",
        color=0x0099ff
    )
    embed.add_field(
        name="🎯 Main Commands:",
        value="• `!setup [template]` - Set up your server\n• `!templates` - Show available templates\n• `!preview <template>` - Preview a template\n• `!info` - Show this information",
        inline=False
    )
    embed.add_field(
        name="🎨 Available Templates:",
        value="• `default` - Standard setup\n• `gaming` - Gaming community\n• `professional` - Business/work\n• `educational` - Study/learning\n• `minimal` - Basic setup",
        inline=False
    )
    embed.add_field(
        name="✨ Features:",
        value="• Multiple server templates\n• Smart permission management\n• Automated role creation\n• Utility bot recommendations\n• Detailed setup logging",
        inline=False
    )
    embed.set_footer(text="Created with ❤️ for Discord communities")
    await ctx.send(embed=embed)

@setup.error
async def setup_error(ctx, error):
    """Handle setup command errors"""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You need Administrator permissions to use this command.",
            color=0xff0000
        )
        await ctx.send(embed=embed)

if __name__ == '__main__':
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
    else:
        bot.run(token)
