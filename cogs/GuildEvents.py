import discord
import random
from datetime import datetime
from utils import utc_to_epoch
from discord.ext import commands
from config import getLogger


class GuildEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = [x for x in member.guild.channels if x.name == "logs"]
        log_channel = log_channel[0] if len(
            log_channel) == 1 else member.guild.system_channel if member.guild.system_channel else random.choice(
            await self.bot.fetch_channls())
        if log_channel:
            created_at_unix = utc_to_epoch(member.created_at)
            created_date = datetime.fromtimestamp(created_at_unix)
            embed = discord.Embed(title="User joined the server!", description=None, color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name=f"User ID", value=member.id, inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.add_field(name="Account created", value=f"{created_date}", inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(content=None, embed=embed)
        else:
            getLogger().error(f"[Guild Events] Could not find suitable channel to send a event for guild {member.guild.name}!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # get ban list
        banned_users = await member.guild.bans()
        # check if user is on the ban list
        is_banned = [x for x in banned_users if x.user.id == member.id]
        # if the user is banned, ignore this event because we will use the on_member_ban event
        if is_banned:
            return

        log_channel = [x for x in member.guild.channels if x.name == "logs"]
        log_channel = log_channel[0] if len(
            log_channel) == 1 else member.guild.system_channel if member.guild.system_channel else random.choice(
            await self.bot.fetch_channls())
        if log_channel:
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
        else:
            getLogger().error(f"[Guild Events] Could not find suitable channel to send a event for guild {member.guild.name}!")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        log_channel = [x for x in guild.channels if x.name == "logs"]
        log_channel = log_channel[0] if len(
            log_channel) == 1 else guild.system_channel if guild.system_channel else random.choice(
            await self.bot.fetch_channls())
        if log_channel:
            ban_reason = await guild.fetch_ban(user=member)
            embed = discord.Embed(title="User was banned from the server!", description=None, color=discord.Color.red(), timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="User ID", value=member.id, inline=False)
            embed.add_field(name=f"Ban Reason", value=ban_reason.reason)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=member.name, icon_url=member.avatar_url)
            await log_channel.send(content=None, embed=embed)
        else:
            getLogger().error(f"[Guild Events] Could not find suitable channel to send a event for guild {guild.name}!")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        log_channel = [x for x in guild.channels if x.name == "logs"]
        log_channel = log_channel[0] if len(log_channel) == 1 else guild.system_channel if guild.system_channel else random.choice(await self.bot.fetch_channls())
        if log_channel:
            embed = discord.Embed(title="User was unbanned from the server!", description=None, color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="User ID", value=member.id, inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=member.name, icon_url=member.avatar_url)
            await log_channel.send(content=None, embed=embed)
        else:
            getLogger().error(f"[Guild Events] Could not find suitable channel to send a event log for guild {guild.name}!")


def setup(bot):
    bot.add_cog(GuildEventsCog(bot))
