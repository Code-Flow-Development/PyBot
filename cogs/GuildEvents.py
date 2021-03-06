import discord
from datetime import datetime
import utils
from utils import utc_to_epoch, ServerSettings, ServerStats
from discord.ext import commands
from utils import UserProfiles


class GuildEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            UserProfiles(member)

        server_settings = ServerSettings(member.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings["log_channel"] else None
        enabled = server_settings["events"]["guild_member_join"]
        if log_channel is not None and enabled:
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

        stats = ServerStats(self.bot, member.guild)
        if stats.isEnabled():
            await stats.update()

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        if not member.bot:
            UserProfiles(member).reset()
        try:
            banned_users = await member.guild.bans()
        except:
            # TODO: add exceptions here and handle them
            return

        is_banned = [x for x in banned_users if x.user.id == member.id]
        if is_banned:
            return

        server_settings = ServerSettings(member.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_member_leave"]
        if log_channel is not None and enabled:
            created_at_unix = utc_to_epoch(member.created_at)
            created_date = datetime.fromtimestamp(created_at_unix)
            joined_at_unix = utc_to_epoch(member.joined_at)
            joined_date = datetime.fromtimestamp(joined_at_unix)
            embed = discord.Embed(title="User left the server!", description=None, color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.mention} ({member.id})", inline=False)
            embed.add_field(name="Account created", value=f"{created_date}", inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.add_field(name="Joined", value=f"{joined_date}", inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(content=None, embed=embed)

        stats = ServerStats(self.bot, member.guild)
        if stats.isEnabled():
            await stats.update()

    # commented out in favor of the message sent from the ban command
    # @commands.Cog.listener()
    # async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
    #     if member == self.bot.user:
    #         return
    #     server_settings = ServerSettings(member.guild).getServerDocument()
    #     log_channel = self.bot.get_channel(server_settings["settings"]["log_channel"]) if server_settings["settings"][
    #         "log_channel"] else None
    #     enabled = server_settings["settings"]["events"]["guild_member_ban"]
    #     if log_channel is not None and enabled:
    #         ban_reason = await guild.fetch_ban(user=member)
    #         embed = discord.Embed(title="User was banned from the server!", description=None, color=discord.Color.red(), timestamp=datetime.utcnow())
    #         embed.add_field(name=f"Username", value=f"{member.mention} ({member.id})", inline=False)
    #         embed.add_field(name="User ID", value=member.id, inline=False)
    #         embed.add_field(name=f"Ban Reason", value=ban_reason.reason)
    #         embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
    #         embed.set_thumbnail(url=member.avatar_url)
    #         embed.set_footer(text=member.name, icon_url=member.avatar_url)
    #         await log_channel.send(content=None, embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, member: discord.Member):
        if member == self.bot.user:
            return
        server_settings = ServerSettings(guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_member_unban"]
        if log_channel is not None and enabled:
            embed = discord.Embed(title="User was unbanned from the server!", description=None,
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name=f"Username", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="User ID", value=member.id, inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=member.name, icon_url=member.avatar_url)
            await log_channel.send(content=None, embed=embed)

    # @commands.Cog.listener()
    # async def on_member_update(self, before: discord.Member, after: discord.Member):
    #     server_settings = ServerSettings(before.guild).getServerDocument()
    #     log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings["log_channel"] else None
    #     enabled = server_settings["events"]["guild_member_update"]
    #     if log_channel is not None and enabled:
    #         pass

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        server_settings = ServerSettings(message.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_message_delete"]
        if log_channel is not None and enabled:
            embed = discord.Embed(title=f"Message deleted", description=None,
                                  color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name=f"Author", value=f"{message.author.mention} ({message.author.id})", inline=False)
            embed.add_field(name=f"Content", value=f"{message.content}", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(content=None, embed=embed)
        else:
            print("no log channel or not enabled")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return
        server_settings = ServerSettings(before.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_message_edit"]
        if log_channel is not None and enabled:
            embed = discord.Embed(title=f"Message edited", description=None,
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name=f"Author", value=f"{before.author.mention} ({before.author.id})", inline=False)
            embed.add_field(name=f"Old Content", value=f"{before.content}", inline=False)
            embed.add_field(name=f"New Content", value=f"{after.content}", inline=False)
            embed.add_field(name="Channel", value=before.channel.mention)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(content=None, embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        server_settings = ServerSettings(channel.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_channel_create"]
        if log_channel is not None and enabled:
            await log_channel.send(f"Channel created: {channel.mention} [{channel.name}] ({channel.id})")

        stats = ServerStats(self.bot, channel.guild)
        if stats.isEnabled():
            await stats.update()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        server_settings = ServerSettings(channel.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_channel_delete"]
        if log_channel is not None and enabled:
            await log_channel.send(f"Channel deleted: {channel.name} ({channel.id})")

        stats = ServerStats(self.bot, channel.guild)
        if stats.isEnabled():
            await stats.update()

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        # TODO: Make this an embed
        server_settings = ServerSettings(before).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_update"]
        if log_channel is not None and enabled:
            embed = discord.Embed(title=f"Guild Updated", description=None, color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(f"Guild was updated!")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        server_settings = ServerSettings(role.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_role_create"]
        embed = discord.Embed(title=f"Role Created", description=None, color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.add_field(name="Role Name", value=f"{role.name}")
        embed.add_field(name="Role ID", value=f"{role.id}")
        embed.add_field(name="Hoisted", value=f"{role.hoist}")
        embed.add_field(name="Mentionable", value=f"{role.mentionable}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        if log_channel is not None and enabled:
            await log_channel.send(content=None, embed=embed)

        stats = ServerStats(self.bot, role.guild)
        if stats.isEnabled():
            await stats.update()

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        server_settings = ServerSettings(role.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_role_delete"]
        embed = discord.Embed(title=f"Role Deleted", description=None, color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.add_field(name="Role Name", value=f"{role.name}")
        embed.add_field(name="Role ID", value=f"{role.id}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        if log_channel is not None and enabled:
            await log_channel.send(content=None, embed=embed)

        stats = ServerStats(self.bot, role.guild)
        if stats.isEnabled():
            await stats.update()

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        # TODO: Make this an embed
        server_settings = ServerSettings(before.guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_role_update"]
        if log_channel is not None and enabled:
            embed = discord.Embed(title=f"Role Updated", description=None, color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(f"Role updated: {before.name}")

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: discord.Guild, before: discord.Emoji, after: discord.Emoji):
        # TODO: Make this an embed and correctly log this change
        server_settings = ServerSettings(guild).getServerSettings()
        log_channel = self.bot.get_channel(server_settings["log_channel"]) if server_settings[
            "log_channel"] else None
        enabled = server_settings["events"]["guild_role_update"]
        if log_channel is not None and enabled:
            # embed = discord.Embed(title=f"Emoji Updated", description=None, color=discord.Color.green(),
            #                       timestamp=datetime.utcnow())
            # embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await log_channel.send(f"Emoji Updated")
            utils.getLogger().debug(before)
            utils.getLogger().debug(after)


def setup(bot):
    bot.add_cog(GuildEventsCog(bot))
