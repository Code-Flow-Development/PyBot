import discord
from discord.ext import commands
from datetime import datetime
from discord import errors
from config import getLogger
from .utils.checks import isGuildAdmin


class UnbanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="unban", pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True, ban_members=True)
    async def ban(self, ctx, user_id: str, reason="No reason specified!"):
        try:
            member = await self.bot.fetch_user(user_id=user_id)
            try:
                await ctx.guild.unban(user=member, reason=reason)
                embed = discord.Embed(title=f"{member.name} has been unbanned!",
                                      description=f"Unban Reason: {reason}",
                                      color=discord.Color.green(),
                                      timestamp=datetime.utcnow())
                embed.set_thumbnail(url="https://icon-library.net/images/green-checkmark-icon/green-checkmark-icon-11.jpg")
                embed.set_footer(text=f"Unbanned by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
            except errors.Forbidden as e:
                embed = discord.Embed(title=f"Missing `ban_members` permission!", description=f"Error: {e.text}", color=discord.Color.red(),
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
            except errors.HTTPException as e:
                embed = discord.Embed(title=f"User {member.name}#{member.discriminator} is not banned!", description=f"Error: {e.text}", color=discord.Color.red(),
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(content=None, embed=embed)
        except errors.NotFound as e:
            embed = discord.Embed(title=f"User with ID {user_id} not found!", description=f"Error: {e.text}", color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        except errors.HTTPException as e:
            embed = discord.Embed(title=f"Failed to fetch user with ID {user_id}", description=f"Error: {e.text}", color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(UnbanCog(bot))
