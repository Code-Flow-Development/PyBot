import discord
from datetime import datetime
from discord.ext import commands


class XCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="xban")
    @commands.guild_only()
    async def xban(self, ctx, member: discord.Member, reason: str = None):
        embed = discord.Embed(title=f"{member.name} has been banned!",
                              description=f"Banned for: {reason}" if reason else None,
                              color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.set_image(url="https://thumbs.gfycat.com/ElderlyViciousFeline-size_restricted.gif")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=f"Banned by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="xmute")
    @commands.guild_only()
    async def xmute(self, ctx, member: discord.Member, reason: str = None):
        if reason:
            await ctx.send(content=f"{member.name} was muted by {ctx.author.name} for {reason}")
        else:
            await ctx.send(content=f"{member.name} was muted by {ctx.author.name}")


def setup(bot):
    bot.add_cog(XCommandsCog(bot))
