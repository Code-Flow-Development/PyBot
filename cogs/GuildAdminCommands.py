import discord
import random
from discord.ext import commands
from datetime import datetime
from discord.errors import HTTPException, Forbidden, InvalidArgument
from discord.ext.commands.errors import BadArgument
from discord.errors import NotFound


class GuildAdminCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, reason: str = "No reason specified", dmd=0):
        if member is None or member == ctx.message.author:
            await ctx.send(f"You cannot ban yourself!")
            return
        # dont ban members that have administrator permission
        if member.guild_permissions.administrator:
            await ctx.send(f"{member.name} is an admin and cannot be banned!")
            return

        # TODO.md: log channel embed with reason (see: https://github.com/Puyodead1/Extron/blob/master/Discord/Commands/ban.js)
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

    @commands.command(name="unban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user_id: str, reason="No reason specified"):
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

    # TODO.md: maybe use roles for permissions instead (ex: Moderator)
    @commands.command(name="mute")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
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
                    await ctx.send(f"[GuildAdminCommands] Missing permission! Error: {e.text}")
                except HTTPException as e:
                    await ctx.send(f"[GuildAdminCommands] Failed to add role! Error: {e.text}")
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
                            await ctx.send(f"[GuildAdminCommands] Missing permission! Error: {e.text}")
                        except NotFound as e:
                            await ctx.send(
                                f"[GuildAdminCommands] The role or member being edited is not part of the guild! Error: {e.text}")
                        except HTTPException as e:
                            await ctx.send(
                                f"[GuildAdminCommands] Editing channel specific permissions failed for channel `{channel.name}`! Error: {e.text}")
                        except InvalidArgument as e:
                            await ctx.send(
                                f"[GuildAdminCommands] The overwrite parameter is invalid or the target type was not role or member! Error: {e}")

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
                        await ctx.send(f"[GuildAdminCommands] Missing permission! Error: {e.text}")
                    except HTTPException as e:
                        await ctx.send(f"[GuildAdminCommands] Failed to add role! Error: {e.text}")
                except Forbidden as e:
                    # no permission to create the role
                    await ctx.send(f"[GuildAdminCommands] Cannot create muted role, Missing "
                                   f"permission! Error: {e.text}")
                except HTTPException as e:
                    # Creating role failed
                    await ctx.send(f"[GuildAdminCommands] Failed to create muted role! Error: {e.text}")
                except InvalidArgument as e:
                    # Invalid keyword was given
                    await ctx.send(f"[GuildAdminCommands] Invalid keyword given! Error: {e}")
        except HTTPException as e:
            # Retrieving roles failed
            await ctx.send(f"[GuildAdminCommands] Retrieving roles failed! Error: {e.text}")

    @commands.command(name="unmute")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
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
                await ctx.send(f"[GuildAdminCommands] Missing permission! Error: {e.text}")
            except HTTPException as e:
                await ctx.send(f"[GuildAdminCommands] Failed to remove roles! Error: {e.text}")
        except HTTPException as e:
            # Retrieving roles failed
            await ctx.send(f"[GuildAdminCommands] Retrieving roles failed! Error: {e.text}")


    @commands.command(name="kick")
    @commands.guild_only()
    # TODO.md: reason?
    async def kick(self, ctx, member: discord.Member):
        try:
            await member.kick()
            embed = discord.Embed(title=None, description=f"**{member.name}** was kicked 👋", color=discord.Color.green(), timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=f"Kicked by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        except Forbidden as e:
            await ctx.send(f"[GuildAdminCommands] Missing permission! Error: {e.text}")
        except HTTPException as e:
            await ctx.send(f"[GuildAdminCommands] Failed to kick user {member.name}! Error: {e.text}")

    # @commands.command(name="strike")
    # @commands.guild_only()
    # async def strike(self, ctx, member: discord.Member, reason: str = "No reason specified"):
    #     # TODO: define strikes
    #     if len(strikes) == 1:
    #         embed = discord.Embed(title=None, description=f"Ok, **{member.name}** now has 1 strike 🚦 I warned them via PM ⚠", color=discord.Color.green(), timestamp=datetime.utcnow())
    #         embed.set_footer(text=f"Striked by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    #         try:
    #             dm_embed = discord.Embed(title=f"You just got a warning / strike from {ctx.author.name} on {ctx.guild.name}: ```{reason}```", color=discord.Color.red(), timestamp=datetime.utcnow())
    #             embed.set_footer(text=f"Striked by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    #         except:
    #             # TODO: catch the correct catch
    #             pass


def setup(bot):
    bot.add_cog(GuildAdminCommandsCog(bot))
