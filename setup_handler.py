import discord
import yaml
import asyncio
from pathlib import Path

class ServerSetupHandler:
    def __init__(self, bot):
        self.bot = bot
        self.templates_dir = Path("templates")
        self.available_templates = {
            "default": "default_template.yaml",
            "minimal": "minimal_template.yaml",
            "gaming": "gaming_template.yaml",
            "professional": "professional_template.yaml",
            "educational": "educational_template.yaml"
        }
    
    async def load_template(self, template_name="default"):
        """Load server setup template from YAML file"""
        try:
            if template_name not in self.available_templates:
                print(f"Template '{template_name}' not found. Available templates: {list(self.available_templates.keys())}")
                template_name = "default"
            
            template_file = self.templates_dir / self.available_templates[template_name]
            with open(template_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Template file not found: {template_file}")
            return None
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return None
    
    async def get_available_templates(self):
        """Get list of available templates with descriptions"""
        template_descriptions = {
            "default": "🏠 Standard server setup with basic categories and roles",
            "minimal": "⚡ Minimal setup with essential channels only",
            "gaming": "🎮 Gaming-focused server with LFG and tournament channels",
            "professional": "💼 Professional/business server with department channels",
            "educational": "📚 Educational server with study rooms and course channels"
        }
        return template_descriptions
    
    async def setup_server(self, guild, template=None):
        """Main setup function that orchestrates the entire server setup"""
        if template is None:
            template = await self.load_template()
        
        if not template:
            return False, "Failed to load template"
        
        try:
            # Create setup log channel first
            setup_log = await self.create_setup_log_channel(guild)
            
            # Create roles
            roles_created = await self.create_roles(guild, template.get('roles', []))
            await self.log_action(setup_log, f"Created {len(roles_created)} roles")
            
            # Create categories and channels
            categories_created = await self.create_categories_and_channels(guild, template.get('categories', []))
            await self.log_action(setup_log, f"Created {len(categories_created)} categories with channels")
            
            # Set up permissions
            await self.setup_permissions(guild, template, roles_created)
            await self.log_action(setup_log, "Configured channel permissions")
            
            # Send utility bot information
            await self.send_utility_bot_info(guild, template.get('utility_bots', []))
            await self.log_action(setup_log, "Sent utility bot information")
            
            return True, "Server setup completed successfully!"
            
        except Exception as e:
            print(f"Error during setup: {e}")
            return False, f"Setup failed: {str(e)}"
    
    async def create_setup_log_channel(self, guild):
        """Create or find the setup log channel"""
        existing_channel = discord.utils.get(guild.channels, name="setup-log")
        if existing_channel:
            return existing_channel
        
        # Create staff category if it doesn't exist
        staff_category = discord.utils.get(guild.categories, name="👨‍💼 Staff")
        if not staff_category:
            staff_category = await guild.create_category("👨‍💼 Staff")
        
        # Create setup log channel
        setup_log = await guild.create_text_channel(
            "setup-log",
            category=staff_category,
            topic="Bot setup logs"
        )
        return setup_log
    
    async def create_roles(self, guild, roles_config):
        """Create roles based on template configuration"""
        created_roles = {}
        
        for role_config in roles_config:
            try:
                # Check if role already exists
                existing_role = discord.utils.get(guild.roles, name=role_config['name'])
                if existing_role:
                    created_roles[role_config['name']] = existing_role
                    continue
                
                # Create permissions
                permissions = discord.Permissions()
                for perm in role_config.get('permissions', []):
                    setattr(permissions, perm, True)
                
                # Create role
                role = await guild.create_role(
                    name=role_config['name'],
                    color=discord.Color(role_config.get('color', 0x000000)),
                    permissions=permissions,
                    hoist=role_config.get('hoist', False)
                )
                created_roles[role_config['name']] = role
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error creating role {role_config['name']}: {e}")
        
        return created_roles
    
    async def create_categories_and_channels(self, guild, categories_config):
        """Create categories and their channels"""
        created_categories = {}
        
        for category_config in categories_config:
            try:
                # Check if category already exists
                existing_category = discord.utils.get(guild.categories, name=category_config['name'])
                if existing_category:
                    category = existing_category
                else:
                    # Create category
                    category = await guild.create_category(category_config['name'])
                    await asyncio.sleep(0.5)
                
                created_categories[category_config['name']] = category
                
                # Create channels in category
                for channel_config in category_config.get('channels', []):
                    try:
                        # Check if channel already exists
                        existing_channel = discord.utils.get(guild.channels, name=channel_config['name'])
                        if existing_channel:
                            continue
                        
                        if channel_config['type'] == 'text':
                            await guild.create_text_channel(
                                channel_config['name'],
                                category=category,
                                topic=channel_config.get('topic', '')
                            )
                        elif channel_config['type'] == 'voice':
                            await guild.create_voice_channel(
                                channel_config['name'],
                                category=category
                            )
                        
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        print(f"Error creating channel {channel_config['name']}: {e}")
                        
            except Exception as e:
                print(f"Error creating category {category_config['name']}: {e}")
        
        return created_categories
    
    async def setup_permissions(self, guild, template, roles_created):
        """Set up channel permissions for roles"""
        try:
            # Get important roles
            admin_role = roles_created.get('Admin')
            mod_role = roles_created.get('Moderator')
            member_role = roles_created.get('Member')
            muted_role = roles_created.get('Muted')
            
            # Set permissions for staff channels
            staff_category = discord.utils.get(guild.categories, name="👨‍💼 Staff")
            if staff_category:
                # Only admins and mods can see staff channels
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                }
                if admin_role:
                    overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True)
                if mod_role:
                    overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True)
                
                await staff_category.edit(overwrites=overwrites)
            
            # Set muted role permissions
            if muted_role:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(muted_role, send_messages=False)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(muted_role, speak=False)
                    await asyncio.sleep(0.2)  # Small delay to avoid rate limits
                        
        except Exception as e:
            print(f"Error setting up permissions: {e}")
    
    async def send_utility_bot_info(self, guild, utility_bots):
        """Send information about utility bots to a channel"""
        try:
            # Find bot-commands channel or general channel
            bot_commands_channel = discord.utils.get(guild.channels, name="bot-commands")
            if not bot_commands_channel:
                bot_commands_channel = discord.utils.get(guild.channels, name="general")
            
            if bot_commands_channel and utility_bots:
                embed = discord.Embed(
                    title="🤖 Recommended Utility Bots",
                    description="Here are some useful bots you can add to your server:",
                    color=0x00ff00
                )
                
                for bot in utility_bots:
                    embed.add_field(
                        name=bot['name'],
                        value=f"{bot['description']}\\n[Invite Link]({bot['invite_url']})",
                        inline=False
                    )
                
                await bot_commands_channel.send(embed=embed)
                
        except Exception as e:
            print(f"Error sending utility bot info: {e}")
    
    async def log_action(self, channel, message):
        """Log an action to the setup log channel"""
        try:
            if channel:
                embed = discord.Embed(
                    title="Setup Action",
                    description=message,
                    color=0x0099ff,
                    timestamp=discord.utils.utcnow()
                )
                await channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging action: {e}")
