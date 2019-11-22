import discord
import random
from datetime import datetime
from utils import utc_to_epoch, ServerSettings
from discord.ext import commands
from config import getLogger


class GuildEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        server_settings = ServerSettings(member.guild).getServerDocument()
        log_channel = self.bot.get_channel(server_settings["settings"]["log_channel"]) if server_settings["settings"]["log_channel"] else None
        enabled = server_settings["settings"]["events"]["member_join"]
        if log_channel and enabled:
            created_at_unix = utc_to_epoch(member.created_at)
            created_date = datetime.fromtimestamp(created_at_unix)
            embed = discord.Embed(title="User joined the server!", description=None, color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name=f"User ID", value=member.id, inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.add_field(name="Account created", value=f"{created_date}", inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(content=None, embed=embed)
        else:
            getLogger().debug(f"on_member_join log_channel is null or not enabled for guild {member.guild.name}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member == self.bot.user:
            return
        banned_users = await member.guild.bans()
        is_banned = [x for x in banned_users if x.user.id == member.id]
        if is_banned:
            return

        server_settings = ServerSettings(member.guild).getServerDocument()
        log_channel = self.bot.get_channel(server_settings["settings"]["log_channel"]) if server_settings["settings"][
            "log_channel"] else None
        enabled = server_settings["settings"]["events"]["member_leave"]
        if log_channel and enabled:
            created_at_unix = utc_to_epoch(member.created_at)
            created_date = datetime.fromtimestamp(created_at_unix)
            joined_at_unix = utc_to_epoch(member.joined_at)
            joined_date = datetime.fromtimestamp(joined_at_unix)
            embed = discord.Embed(title="User left the server!", description=None, color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name=f"User ID", value=member.id, inline=False)
            embed.add_field(name="Account created", value=f"{created_date}", inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.add_field(name="Joined", value=f"{joined_date}", inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(content=None, embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        server_settings = ServerSettings(member.guild).getServerDocument()
        log_channel = self.bot.get_channel(server_settings["settings"]["log_channel"]) if server_settings["settings"][
            "log_channel"] else None
        enabled = server_settings["settings"]["events"]["member_ban"]
        if log_channel and enabled:
            ban_reason = await guild.fetch_ban(user=member)
            embed = discord.Embed(title="User was banned from the server!", description=None, color=discord.Color.red(), timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="User ID", value=member.id, inline=False)
            embed.add_field(name=f"Ban Reason", value=ban_reason.reason)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=member.name, icon_url=member.avatar_url)
            await log_channel.send(content=None, embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        server_settings = ServerSettings(member.guild).getServerDocument()
        log_channel = self.bot.get_channel(server_settings["settings"]["log_channel"]) if server_settings["settings"][
            "log_channel"] else None
        enabled = server_settings["settings"]["events"]["member_unban"]
        if log_channel and enabled:
            embed = discord.Embed(title="User was unbanned from the server!", description=None, color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="User ID", value=member.id, inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=member.name, icon_url=member.avatar_url)
            await log_channel.send(content=None, embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        server_settings = ServerSettings(before.guild).getServerDocument()
        log_channel = self.bot.get_channel(server_settings["settings"]["log_channel"]) if server_settings["settings"]["log_channel"] else None
        enabled = server_settings["settings"]["events"]["member_update"]
        if log_channel and enabled:
            print(before, after)


def setup(bot):
    bot.add_cog(GuildEventsCog(bot))
