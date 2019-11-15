import discord
import time
from discord.ext import commands


class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    async def status(self, ctx):
        embed = discord.Embed(title="Bot Status", description=None, color=discord.Color.red())
        embed.add_field(name="Uptime:", value=f"{self.bot.startedAt}")
        await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(StatusCog(bot))
