import discord
import random
from discord.ext import commands
from datetime import datetime
from discord.errors import HTTPException, Forbidden, InvalidArgument
from discord.ext.commands.errors import BadArgument
from discord.errors import NotFound


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
            await ctx.send(f"{member.name} is an admin and cannot be banned!")
            return

        # TODO: log channel embed with reason (see: https://github.com/Puyodead1/Extron/blob/master/Discord/Commands/ban.js)
        embed = discord.Embed(title=None,
                              description=f"Bye Bye **{member.name}** 🔨",
                              color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.set_image(url="https://thumbs.gfycat.com/ElderlyViciousFeline-size_restricted.gif")
        embed.set_footer(text=f"Banned by {ctx.author.name}", icon_url=ctx.author.avatar_url)

        try:
            await member.ban(reason=reason, delete_message_days=dmd)
            await ctx.send(content=None, embed=embed)
        except Forbidden as e:
            embed = discord.Embed(title=f"Missing permission!", description=f"Error: {e.text}",
                                  color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        except HTTPException as e:
            embed = discord.Embed(title=f"Failed to ban {member.name}", description=f"Error: {e.text}",
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
                                      description=f"{member.name} has been unbanned!",
                                      color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
                embed.add_field(name=f"Unban Reason", value=reason)
                embed.set_thumbnail(
                    url="https://icon-library.net/images/green-checkmark-icon/green-checkmark-icon-11.jpg")
                embed.set_footer(text=f"Unbanned by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
            except Forbidden as e:
                embed = discord.Embed(title=f"Missing `ban_members` permission!", description=f"Error: {e.text}",
                                      color=discord.Color.red(),
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
            except HTTPException as e:
                embed = discord.Embed(title=f"User {member.name}#{member.discriminator} is not banned!",
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
            await ctx.send(f"{member.name} is a bot.")
            return

        try:
            muted_role = [x for x in ctx.guild.roles if x.name == "Muted"]
            muted_role = muted_role[0] if len(muted_role) == 1 else None
            # check length of the list, if 0 no muted role, if > 0 there is one or more
            if muted_role:
                try:
                    await member.add_roles(muted_role, reason=reason, atomic=False)
                    embed = discord.Embed(title=None, description=f"**{member.name}** was muted 🔇",
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
                        embed = discord.Embed(title=f"{member.name}#{member.discriminator} was muted!",
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
                            print(f"Set permissions on channel {channel.name}")
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
                        embed = discord.Embed(title=None, description=f"**{member.name}** was muted 🔇",
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
                            embed = discord.Embed(title=f"{member.name}#{member.discriminator} was muted!",
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
            await ctx.send(f"{member.name} is a bot.")
            return

        try:
            muted_role = [x for x in ctx.guild.roles if x.name == "Muted"]
            muted_role = muted_role[0] if len(muted_role) == 1 else None
            # check length of the list, if 0 no muted role, if == 0 there is one
            try:
                await member.remove_roles(muted_role, reason=reason)
                embed = discord.Embed(title=None, description=f"**{member.name}** was unmuted 🔊",
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
                    embed = discord.Embed(title=f"{member.name}#{member.discriminator} was unmuted!",
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
            embed = discord.Embed(title=None, description=f"**{member.name}** was kicked 👋",
                                  color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_image(url="https://media1.tenor.com/images/ca1bad80a757fa8b87dacd9c051f2670/tenor.gif")
            embed.set_footer(text=f"Kicked by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        except Forbidden as e:
            await ctx.send(f"[ModerationCommands] Missing permission! Error: {e.text}")
        except HTTPException as e:
            await ctx.send(f"[ModerationCommands] Failed to kick user {member.name}! Error: {e.text}")

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
    @commands.bot_has_permissions(manage_members=True)
    async def addrole(self, ctx, role: discord.Role, member: discord.Member):
        try:
            await member.add_roles(role, reason=f"Requested by {ctx.message.author.name}")
            await ctx.send(f"Added role {role.name} to {member.name}")
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
            await ctx.send(f"Removed role {role.name} from {member.name}")
        except Forbidden as e:
            await ctx.send(f"[ModerationCommands] Missing permission to remove role! Error: {e.text}")
        except HTTPException as e:
            await ctx.send(f"[ModerationCommands] Failed to remove role! Error: {e.text}")

    @commands.command(name="strike", help="Add a strike to a user", enabled=False, usage="<@user> [reason]")
    @commands.guild_only()
    async def strike(self, ctx, member: discord.Member, reason: str = None):
        pass

    @commands.command(name="createcc", help="Creates a new counting channel")
    @commands.guild_only()
    async def newcountingchannel(self, ctx):
        try:
            channel = await ctx.guild.create_text_channel(name="counting", topic="1")
            await ctx.send(f"Channel created! {channel.mention}")
        except Forbidden as e:
            return await ctx.send(f"[ModerationCommands] Missing permission to create channel! Error: {e.text}")
        except HTTPException as e:
            return await ctx.send(f"[ModerationCommands] Failed to create channel! Error: {e.text}")
        except InvalidArgument as e:
            return await ctx.send(f"[ModerationCommands] Permission override information is invalid! Error: {e} ")


def setup(bot):
    bot.add_cog(ModerationCommandsCog(bot))
