import disnake
from disnake.ext import commands
import json
import random
import sqlite3
import asyncio
from datetime import datetime
from config import LOG_CHANNEL_ID, ALLOWED_CHANNEL_IDS, AUTHORIZED_ROLES
from functools import lru_cache
from typing import Optional

class CommandsCog(commands.Cog):
    """Primary class for bot commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Set up database connection.
        self.conn = sqlite3.connect("punishments.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cache = {}

    @lru_cache(maxsize=128)
    async def get_channel(self, guild_id: int, channel_id: int) -> Optional[disnake.TextChannel]:
        """Cached channel retrieval."""
        return self.bot.get_guild(guild_id).get_channel(channel_id)

    @commands.slash_command(name="hello")
    async def hello(self, inter: disnake.ApplicationCommandInteraction):
        """Greeting command."""
        await inter.response.send_message(
            f"Hello, {inter.author.mention}!",
            ephemeral=True
        )

    @commands.slash_command(name="ping")
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """Bot latency check."""
        await inter.response.send_message(
            f"Pong! Latency: {round(self.bot.latency * 1000)}ms",
            ephemeral=True
        )

    @commands.slash_command(name="meme")
    async def meme(self, inter: disnake.ApplicationCommandInteraction):
        """Sends a random meme."""
        if inter.channel_id not in ALLOWED_CHANNEL_IDS:
            await inter.response.send_message(
                "This command is not available in this channel.",
                ephemeral=True
            )
            return

        # Cache meme data.
        cache_key = f'memes_{random.choice(["ru", "it"])}'
        if cache_key not in self.cache:
            try:
                with open(f'memes_{cache_key.split("_")[1]}.json', 'r') as file:
                    self.cache[cache_key] = json.load(file).get("urls", [])
            except Exception as e:
                await inter.response.send_message(f"Error: {e}")
                return

        if self.cache[cache_key]:
            await inter.response.send_message(
                random.choice(self.cache[cache_key]),
                ephemeral=True
            )
        else:
            await inter.response.send_message(
                "The meme list is empty.",
                ephemeral=True
            )

    @commands.slash_command(name="give_role", description="Assign a role to a user")
    @commands.has_role()  # Ensure the user has an authorized role (authorization is checked dynamically).
    async def give_role(self, inter: disnake.ApplicationCommandInteraction):
        """Command to assign roles to users."""
        if inter.channel_id not in ALLOWED_CHANNEL_IDS:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="Access Denied",
                    description="This command is only available in a designated channel.",
                    color=disnake.Color.red()
                ),
                ephemeral=True
            )
            return

        modal = RoleInputModal()
        await inter.response.send_modal(modal)

    @give_role.error
    async def give_role_error(self, inter: disnake.ApplicationCommandInteraction, error):
        """Error handler for the role assignment command."""
        if isinstance(error, commands.MissingRole):
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="Access Error",
                    description="You do not have the required role to use this command.",
                    color=disnake.Color.red()
                ),
                ephemeral=True
            )

    @commands.slash_command(name="create_role", description="Create a new role with a random color")
    @commands.has_permissions(administrator=True)
    async def create_role(self, inter: disnake.ApplicationCommandInteraction, name: str):
        """
        Create a new role with the specified name and a random color.
        
        Parameters
        ----------
        name: The name of the new role.
        """
        try:
            # Generate a random color.
            color = disnake.Color.from_rgb(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            role = await inter.guild.create_role(
                name=name,
                color=color,
                reason=f"Created by {inter.author}"
            )

            embed = disnake.Embed(
                title="✅ Role Created",
                description=f"The role {role.mention} was created\nColor: #{hex(color.value)[2:].zfill(6)}",
                color=color
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            asyncio.create_task(self._log_role_creation(inter, role, color))
        except Exception as e:
            await inter.response.send_message(
                f"Error: {str(e)}",
                ephemeral=True
            )

    async def _log_role_creation(self, inter, role, color):
        """Asynchronously log role creation."""
        channel = await self.get_channel(inter.guild.id, LOG_CHANNEL_ID)
        if channel:
            embed = disnake.Embed(
                title="📝 Role Creation",
                description=f"Administrator {inter.author.mention} created role {role.mention}",
                color=color,
                timestamp=datetime.now()
            )
            await channel.send(embed=embed)

    @create_role.error
    async def create_role_error(self, inter: disnake.ApplicationCommandInteraction, error):
        """General error handler for commands."""
        error_embed = disnake.Embed(
            title="❌ Error",
            description=str(error),
            color=disnake.Color.red()
        )
        await inter.response.send_message(embed=error_embed, ephemeral=True)

class RoleInputModal(disnake.ui.Modal):
    """Modal for inputting role assignment data."""
    def __init__(self):
        super().__init__(
            title="Assign Role",
            components=[
                disnake.ui.TextInput(
                    label="Role ID",
                    placeholder="Enter role ID",
                    custom_id="role_id",
                    required=True
                ),
                disnake.ui.TextInput(
                    label="User ID",
                    placeholder="Enter user ID", 
                    custom_id="user_id",
                    required=True
                )
            ]
        )

    async def on_submit(self, inter: disnake.ApplicationCommandInteraction):
        """Handle form submission."""
        try:
            role_id = int(self.children[0].value)
            user_id = int(self.children[1].value)
            
            log_channel = inter.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = disnake.Embed(
                    title="Logging Data",
                    description=f"Role ID: {role_id}, User ID: {user_id}",
                    color=disnake.Color.blue()
                )
                await log_channel.send(embed=embed)
                await inter.response.send_message("Role assigned successfully!", ephemeral=True)
        except ValueError as e:
            await inter.response.send_message(f"Invalid input: {e}", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"An error occurred: {e}", ephemeral=True)

def setup(bot):
    bot.add_cog(CommandsCog(bot))
