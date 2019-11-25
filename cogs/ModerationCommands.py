import discord
import random
import time
import timeago
from discord.ext import commands
from datetime import datetime
from discord.errors import HTTPException, Forbidden, InvalidArgument
from discord.ext.commands.errors import BadArgument
from discord.errors import NotFound
from utils import UserProfiles, ServerSettings
from config import getLogger


class ModerationCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban", help="Ban a user from the server", usage="<@user or user id> [reason]",
                      description="Requires ban_members permission")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, reason: str = "No reason specified", dmd=0):
        if member is None or member == ctx.message.author:
            await ctx.send(f"You cannot ban yourself!")
            return

        # dont ban members that have administrator permission
        if member.guild_permissions.administrator:
            await ctx.send(f"{member} is an admin and cannot be banned!")
            return

        embed = discord.Embed(title=None,
                              description=f"Bye Bye **{member}** 🔨",
                              color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.set_image(url="https://thumbs.gfycat.com/ElderlyViciousFeline-size_restricted.gif")
        embed.set_footer(text=f"Banned by {ctx.author.name}", icon_url=ctx.author.avatar_url)

        try:
            await member.ban(reason=reason, delete_message_days=dmd)
            await ctx.send(content=None, embed=embed)
            log_channel = ServerSettings(ctx.guild).getLogChannel(self.bot)
            embed2 = discord.Embed(title=None, description=f"**{member}** was banned!", color=discord.Color.red(), timestamp=datetime.utcnow())
            embed2.add_field(name="Banned by", value=f"{ctx.author.mention} ({ctx.author.id})")
            embed2.add_field(name="Banned for", value=f"{reason}")
            embed2.add_field(name="User ID", value=member.id)
            embed2.set_thumbnail(url=member.avatar_url)
            await log_channel.send(content=None, embed=embed2)
        except Forbidden as e:
            embed = discord.Embed(title=f"Missing permission!", description=f"Error: {e.text}",
                                  color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        except HTTPException as e:
            embed = discord.Embed(title=f"Failed to ban {member}", description=f"Error: {e.text}",
                                  color=discord.Color.red(), timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        except BadArgument as e:
            embed = discord.Embed(title=f"User not found!", description=f"Error: {e}",
                                  color=discord.Color.red(), timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)

    @commands.command(name="unban", help="Unbans a user from the server", usage="<user id> [reason]",
                      description="Requires ban_members permission")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str, reason="No reason specified"):
        try:
            member = await self.bot.fetch_user(user_id=user_id)
            try:
                await ctx.guild.unban(user=member, reason=reason)
                embed = discord.Embed(title=None,
                                      description=f"{member} has been unbanned!",
                                      color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
                embed.add_field(name=f"Unban Reason", value=reason)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/emojis/646882488353947709.gif?v=1")
                embed.set_footer(text=f"Unbanned by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
            except Forbidden as e:
                embed = discord.Embed(title=f"Missing `ban_members` permission!", description=f"Error: {e.text}",
                                      color=discord.Color.red(),
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
            except HTTPException as e:
                embed = discord.Embed(title=f"User {member} is not banned!",
                                      description=f"Error: {e.text}", color=discord.Color.red(),
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
        except NotFound as e:
            embed = discord.Embed(title=f"User with ID {user_id} not found!", description=f"Error: {e.text}",
                                  color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        except HTTPException as e:
            embed = discord.Embed(title=f"Failed to fetch user with ID {user_id}", description=f"Error: {e.text}",
                                  color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)

    # TODO: maybe use roles for permissions instead (ex: Moderator)
    @commands.command(name="mute", help="Mutes a user", usage="<@user or user id> [reason]",
                      description="Requires kick_members and manage_roles permission")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, reason: str = "No reason specified"):
        if member.bot:
            await ctx.send(f"{member} is a bot.")
            return

        try:
            muted_role = [x for x in ctx.guild.roles if x.name == "Muted"]
            muted_role = muted_role[0] if len(muted_role) == 1 else None
            # check length of the list, if 0 no muted role, if > 0 there is one or more
            if muted_role:
                try:
                    await member.add_roles(muted_role, reason=reason, atomic=False)
                    embed = discord.Embed(title=None, description=f"**{member}** was muted 🔇",
                                          color=discord.Color.green(), timestamp=datetime.utcnow())
                    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    embed.set_footer(text=f"Muted by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                    await ctx.send(content=None, embed=embed)
                    await member.send(
                        f"You were muted by {ctx.message.author.name} in {ctx.guild.name} for {reason}")
                    log_channel = [x for x in member.guild.channels if x.name == "logs"]
                    log_channel = log_channel[0] if len(
                        log_channel) == 1 else member.guild.system_channel if member.guild.system_channel else random.choice(
                        await self.bot.fetch_channls())
                    if log_channel:
                        embed = discord.Embed(title=f"{member} was muted!",
                                              description=None, color=discord.Color.red(),
                                              timestamp=datetime.utcnow())
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        embed.add_field(name=f"Mute Reason", value=reason)
                        embed.set_thumbnail(url=member.avatar_url)
                        embed.set_footer(text=f"Muted by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                        await log_channel.send(content=None, embed=embed)
                except Forbidden as e:
                    await ctx.send(f"[ModerationCommands] Missing permission! Error: {e.text}")
                except HTTPException as e:
                    await ctx.send(f"[ModerationCommands] Failed to add role! Error: {e.text}")
            else:
                # create the role
                try:
                    muted_role = await ctx.guild.create_role(name="Muted", reason="No muted role existed",
                                                             permissions=discord.Permissions.none())
                    # loop channels and add muted role permissions
                    for channel in [x for x in ctx.guild.channels]:
                        try:
                            await channel.set_permissions(muted_role, send_messages=False, add_reactions=False,
                                                          manage_messages=False, embed_links=False,
                                                          attach_files=False,
                                                          external_emojis=False)
                            getLogger().info(f"Set permissions on channel {channel.name}")
                        except Forbidden as e:
                            # no permission to edit channel specific permissions
                            await ctx.send(f"[ModerationCommands] Missing permission! Error: {e.text}")
                        except NotFound as e:
                            await ctx.send(
                                f"[ModerationCommands] The role or member being edited is not part of the guild! Error: {e.text}")
                        except HTTPException as e:
                            await ctx.send(
                                f"[ModerationCommands] Editing channel specific permissions failed for channel `{channel.name}`! Error: {e.text}")
                        except InvalidArgument as e:
                            await ctx.send(
                                f"[ModerationCommands] The overwrite parameter is invalid or the target type was not role or member! Error: {e}")

                    try:
                        await member.add_roles(muted_role, reason=reason, atomic=False)
                        embed = discord.Embed(title=None, description=f"**{member}** was muted 🔇",
                                              color=discord.Color.green(), timestamp=datetime.utcnow())
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        embed.set_footer(text=f"Muted by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                        await ctx.send(content=None, embed=embed)
                        await member.send(
                            f"You were muted by {ctx.message.author.name} in {ctx.guild.name} for {reason}")
                        log_channel = [x for x in member.guild.channels if x.name == "logs"]
                        log_channel = log_channel[0] if len(
                            log_channel) == 1 else member.guild.system_channel if member.guild.system_channel else random.choice(
                            await self.bot.fetch_channls())
                        if log_channel:
                            embed = discord.Embed(title=f"{member} was muted!",
                                                  description=None, color=discord.Color.red(),
                                                  timestamp=datetime.utcnow())
                            embed.add_field(name=f"Mute Reason", value=reason)
                            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                            embed.set_thumbnail(url=member.avatar_url)
                            embed.set_footer(text=f"Muted by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                            await log_channel.send(content=None, embed=embed)
                    except Forbidden as e:
                        await ctx.send(f"[ModerationCommands] Missing permission! Error: {e.text}")
                    except HTTPException as e:
                        await ctx.send(f"[ModerationCommands] Failed to add role! Error: {e.text}")
                except Forbidden as e:
                    # no permission to create the role
                    await ctx.send(f"[ModerationCommands] Cannot create muted role, Missing "
                                   f"permission! Error: {e.text}")
                except HTTPException as e:
                    # Creating role failed
                    await ctx.send(f"[ModerationCommands] Failed to create muted role! Error: {e.text}")
                except InvalidArgument as e:
                    # Invalid keyword was given
                    await ctx.send(f"[ModerationCommands] Invalid keyword given! Error: {e}")
        except HTTPException as e:
            # Retrieving roles failed
            await ctx.send(f"[ModerationCommands] Retrieving roles failed! Error: {e.text}")

    @commands.command(name="unmute", help="Unmutes a user", usage="<@user or user id> [reason]",
                      descrition="Requires ban_members and manage_roles permission")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, reason: str = "No reason specified"):
        if member.bot:
            await ctx.send(f"{member} is a bot.")
            return

        try:
            muted_role = [x for x in ctx.guild.roles if x.name == "Muted"]
            muted_role = muted_role[0] if len(muted_role) == 1 else None
            # check length of the list, if 0 no muted role, if == 0 there is one
            try:
                await member.remove_roles(muted_role, reason=reason)
                embed = discord.Embed(title=None, description=f"**{member}** was unmuted 🔊",
                                      color=discord.Color.green(), timestamp=datetime.utcnow())
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                embed.set_footer(text=f"Unmuted by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
                await member.send(f"You were unmuted by {ctx.message.author.name} in {ctx.guild.name}")
                log_channel = [x for x in member.guild.channels if x.name == "logs"]
                log_channel = log_channel[0] if len(
                    log_channel) == 1 else member.guild.system_channel if member.guild.system_channel else random.choice(
                    await self.bot.fetch_channls())
                if log_channel:
                    embed = discord.Embed(title=f"{member} was unmuted!",
                                          description=None, color=discord.Color.green(),
                                          timestamp=datetime.utcnow())
                    embed.add_field(name=f"Unmute Reason", value=reason)
                    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    embed.set_thumbnail(url=member.avatar_url)
                    embed.set_footer(text=f"Unmuted by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                    await log_channel.send(content=None, embed=embed)
            except Forbidden as e:
                # missing permission to remove roles
                await ctx.send(f"[ModerationCommands] Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(f"[ModerationCommands] Failed to remove roles! Error: {e.text}")
        except HTTPException as e:
            # Retrieving roles failed
            await ctx.send(f"[ModerationCommands] Retrieving roles failed! Error: {e.text}")

    @commands.command(name="kick", help="Kicks a user from the server", usage="<@user or user id> [reason]",
                      description="Requires kick_members permission")
    @commands.guild_only()
    # TODO: reason?
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):
        try:
            await member.kick()
            embed = discord.Embed(title=None, description=f"**{member}** was kicked 👋",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_image(url="https://media1.tenor.com/images/ca1bad80a757fa8b87dacd9c051f2670/tenor.gif")
            embed.set_footer(text=f"Kicked by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        except Forbidden as e:
            await ctx.send(f"[ModerationCommands] Missing permission! Error: {e.text}")
        except HTTPException as e:
            await ctx.send(f"[ModerationCommands] Failed to kick user {member}! Error: {e.text}")

    @commands.command(name="createrole", help="Creates a new role",
                      usage="<role name> [hoist: true/false] [mentionable: true/false]",
                      description="Requires manage_roles permission")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def createrole(self, ctx, rolename: str, hoist: bool = False, mentionable: bool = False):
        try:
            await ctx.guild.create_role(name=rolename, hoist=hoist, mentionable=mentionable,
                                        reason=f"Requested by {ctx.author.name}")
            await ctx.send(f"Role Created!")
        except Forbidden as e:
            await ctx.send(f"[ModerationCommands] Missing permissions to create role! Error: {e.text}")
        except HTTPException as e:
            await ctx.send(f"[ModerationCommands] Failed to create role! Error: {e.text}")
        except InvalidArgument as e:
            await ctx.send(f"[ModerationCommands] Invalid Argument Error! Error: {e}")
        pass

    @commands.command(name="deleterole", help="Deletes a role", usage="<@role or role id>",
                      description="Requires manage_roles permission")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def deleterole(self, ctx, role: discord.Role):
        try:
            await role.delete(reason=f"Requested by f{ctx.author.name}")
            await ctx.send(f"Role deleted!")
        except Forbidden as e:
            await ctx.send(f"[ModerationCommands] Missing permissions to delete role! Error: {e.text}")
        except HTTPException as e:
            await ctx.send(f"[ModerationCommands] Failed to delete role! Error: {e.text}")

    @commands.command(name="addrole", help="Add role to user", usage="<@role or role id> <@user or userid>",
                      description="Requires manage_members permission")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def addrole(self, ctx, role: discord.Role, member: discord.Member):
        try:
            await member.add_roles(role, reason=f"Requested by {ctx.message.author.name}")
            await ctx.send(f"Added role {role.name} to {member}")
        except Forbidden as e:
            await ctx.send(f"[ModerationCommands] Missing permission to add role! Error: {e.text}")
        except HTTPException as e:
            await ctx.send(f"[ModerationCommands] Failed to add roles! Error: {e.text}")

    @commands.command(name="removerole", help="Remove a role from a user",
                      usage="<@role or role id> <@user or user id>", description="Requires manage_members permission")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_members=True)
    async def removerole(self, ctx, role: discord.Role, member: discord.Member):
        try:
            await member.remove_roles(role, reason=f"Requested by {ctx.message.author.name}")
            await ctx.send(f"Removed role {role.name} from {member}")
        except Forbidden as e:
            await ctx.send(f"[ModerationCommands] Missing permission to remove role! Error: {e.text}")
        except HTTPException as e:
            await ctx.send(f"[ModerationCommands] Failed to remove role! Error: {e.text}")

    @commands.command(name="strike", help="Add a strike to a user", usage="<@user> [reason]")
    @commands.guild_only()
    async def strike(self, ctx, member: discord.Member, reason: str = "No reason"):
        profile = UserProfiles(member)
        profile_content = profile.getUserProfile()
        strikes = profile_content["MiscData"]["strikes"]
        strike_payload = {
            "strike_id": (len(strikes) + 1),
            "reason": reason,
            "striked_by": ctx.author.name,
            "timestamp": time.time()
        }
        strikes.append(strike_payload)
        profile.update("MiscData", profile_content["MiscData"])
        embed = discord.Embed(title=None, description=f"**{member}** now has {len(strikes)} strikes 🚦",
                              color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=f"Kicked by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="removestrike", help="Removes a strike from a user", usage="<strike id>")
    @commands.guild_only()
    # TODO: use role based permissions
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def removestrike(self, ctx, member: discord.Member, strike_id: str):
        profile = UserProfiles(member)
        profile_content = profile.getUserProfile()
        old_strikes = profile_content["MiscData"]["strikes"]
        profile_content["MiscData"]["strikes"] = [x for x in old_strikes if x["strike_id"] != int(strike_id)]
        profile.update("MiscData", profile_content["MiscData"])
        await ctx.send(f"Strike removed")

    @commands.command(name="strikes", help="Lists a users strikes", usage="<@user>")
    @commands.guild_only()
    async def strikes(self, ctx, member: discord.Member):
        profile = UserProfiles(member)
        profile_content = profile.getUserProfile()
        strikes = profile_content["MiscData"]["strikes"]

        if len(strikes) > 0:
            embed = discord.Embed(title=f"Here are the strikes for {member}", description=None,
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            for strike in strikes:
                strike_id = str(strike["strike_id"])
                reason = strike["reason"]
                striked_by = strike["striked_by"]
                strike_timestamp = strike["timestamp"]
                striked_date = datetime.fromtimestamp(strike_timestamp)
                now = datetime.now()
                embed.add_field(name=f"[{strike_id}] Warning from @{striked_by}",
                                value=f"{reason} - {timeago.format(striked_date, now)}", inline=True)
        else:
            embed = discord.Embed(title=f"{member} does not have any strikes!", description=None,
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="createcountingchannel", help="Creates a new counting channel", aliases=["createcc", "newcountingchannel", "createcounting"])
    @commands.guild_only()
    async def newcountingchannel(self, ctx):
        try:
            channel = await ctx.guild.create_text_channel(name="count-to-1")
            await ctx.send(f"Channel created! {channel.mention}")
        except Forbidden as e:
            return await ctx.send(f"[ModerationCommands] Missing permission to create channel! Error: {e.text}")
        except HTTPException as e:
            return await ctx.send(f"[ModerationCommands] Failed to create channel! Error: {e.text}")
        except InvalidArgument as e:
            return await ctx.send(f"[ModerationCommands] Permission override information is invalid! Error: {e} ")

    @commands.command(name="setlogchannel", help="Set the log channel for the server")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setlogchannel(self, ctx, log_channel: discord.TextChannel):
        server_settings = ServerSettings(ctx.guild)
        server_document = server_settings.getServerDocument()
        server_document["log_channel"] = log_channel.id
        server_settings.update("settings", server_document)
        await ctx.send(f"Updated log channel to {log_channel.mention}")

    @commands.command(name="eventsettings", help="Enable/Disable event logging")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def eventsettings(self, ctx, event: str, setting: bool):
        server_settings = ServerSettings(ctx.guild)
        server_document = server_settings.getServerDocument()
        current_event_settings = server_document["events"]
        try:
            theSetting = current_event_settings[event]
            current_event_settings[event] = setting
            server_settings.update("settings", server_document)
            await ctx.send(f"Setting updated!")
        except KeyError:
            await ctx.send(f"{event} is not a valid event!")

    @commands.command(name="config", help="Shows the current config for the server")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx, setting: str = None, value: bool = None):
        server_settings = ServerSettings(ctx.guild)
        server_document = server_settings.getServerDocument()
        if not setting:
            settings = server_document
            log_channel = self.bot.get_channel(settings["log_channel"])

            embed = discord.Embed(title=f"Current settings for '{ctx.guild.name}'", description=None,
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.add_field(name="Log Channel",
                            value=log_channel.mention if log_channel is not None else "No log channel set")
            embed.add_field(name="Message Responses",
                            value=server_document["message_responses_enabled"])
            embed.add_field(name="Counting Channels",
                            value=server_document["counting_channels_enabled"])
            embed.add_field(name="Events", value='\n'.join(
                ['**' + x + ':** ' + str(y) for x, y in server_document['events'].items()]))
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        else:
            try:
                theSetting = server_document[setting]
                server_document[setting] = value
                server_settings.update("settings", server_document)
                await ctx.send(f"Setting updated!")
            except KeyError:
                await ctx.send(f"{setting} is not a valid setting!")


def setup(bot):
    bot.add_cog(ModerationCommandsCog(bot))
