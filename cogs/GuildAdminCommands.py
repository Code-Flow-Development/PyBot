import discord
from discord.ext import commands
from datetime import datetime
from discord.errors import HTTPException, Forbidden
from discord.ext.commands.errors import BadArgument
from discord.errors import NotFound
from config import getLogger
from .utils.checks import isGuildAdmin


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


def setup(bot):
    bot.add_cog(GuildAdminCommandsCog(bot))
