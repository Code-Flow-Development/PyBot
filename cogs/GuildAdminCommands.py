import discord
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
    async def ban(self, ctx, member: discord.Member = None, reason: str = "No reason specified!", dmd=0):
        if member is None or member == ctx.message.author:
            await ctx.send(f"You cannot ban yourself!")
            return
        # dont ban members that have administrator permission
        if member.guild_permissions.administrator:
            await ctx.send(f"{member.name} is an admin and cannot be banned!")
            return

        # TODO: log channel embed with reason (see: https://github.com/Puyodead1/Extron/blob/master/Discord/Commands/ban.js)
        embed = discord.Embed(title=f"Bye Bye **{member.name}** 🔨",
                              color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.set_image(url="https://thumbs.gfycat.com/ElderlyViciousFeline-size_restricted.gif")
        embed.set_footer(text=f"Banned by {ctx.author.name}", icon_url=ctx.author.avatar_url)

        try:
            await member.ban(reason=reason, delete_message_days=dmd)
            await ctx.send(content=None, embed=embed)
        except Forbidden as e:
            embed = discord.Embed(title=f"Missing `ban_members` permission!", description=f"Error: {e.text}",
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
    async def ban(self, ctx, user_id: str, reason="No reason specified!"):
        try:
            member = await self.bot.fetch_user(user_id=user_id)
            try:
                await ctx.guild.unban(user=member, reason=reason)
                embed = discord.Embed(title=f"{member.name} has been unbanned!",
                                      description=f"Unban Reason: {reason}",
                                      color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
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
    @commands.command(name="mute")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member, reason: str = None):
        try:
            muted_role = [x for x in ctx.guild.roles if x.name == "Muted"]
            muted_role = muted_role[0] if len(muted_role) == 1 else None
            # check length of the list, if 0 no muted role, if > 0 there is one or more
            if muted_role:
                try:
                    await member.add_roles(muted_role, reason=reason, atomic=False)
                    await ctx.send(f"{member.name} was muted!")
                except Forbidden as e:
                    await ctx.send(f"[GuildAdminCommands] Missing `manage_roles` permission! Error: {e.text}")
                except HTTPException as e:
                    await ctx.send(f"[GuildAdminCommands] Failed to add role! Error: {e.text}")
            else:
                # create the role
                try:
                    muted_role = await ctx.guild.create_role(name="Muted", reason="No muted role existed", permissions=discord.Permissions.none())
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
                            await ctx.send(f"[GuildAdminCommands] Missing `administrator` permission! Error: {e.text}")
                        except NotFound as e:
                            await ctx.send(f"[GuildAdminCommands] The role or member being edited is not part of the guild! Error: {e.text}")
                        except HTTPException as e:
                            await ctx.send(f"[GuildAdminCommands] Editing channel specific permissions failed for channel `{channel.name}`! Error: {e.text}")
                        except InvalidArgument as e:
                            await ctx.send(f"[GuildAdminCommands] The overwrite parameter is invalid or the target type was not role or member! Error: {e}")

                    try:
                        await member.add_roles(muted_role, reason=reason, atomic=False)
                        await ctx.send(f"{member.name} was muted!")
                    except Forbidden as e:
                        await ctx.send(f"[GuildAdminCommands] Missing `manage_roles` permission! Error: {e.text}")
                    except HTTPException as e:
                        await ctx.send(f"[GuildAdminCommands] Failed to add role! Error: {e.text}")
                except Forbidden as e:
                    # no permission to create the role
                    await ctx.send(f"[GuildAdminCommands] Cannot create muted role, Missing `manage_roles` "
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


def setup(bot):
    bot.add_cog(GuildAdminCommandsCog(bot))
