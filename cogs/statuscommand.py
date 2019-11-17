import discord
import time
import sys
from discord.ext import commands


class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    async def status(self, ctx):
        # unix time the bot has been up, takes time the bot was started minus the current unix time to get the difference
        unix = int(time.time() - self.bot.startedAt)

        mins, secs = divmod(unix, 60)
        hours, mins = divmod(mins, 60)
        days, hours = divmod(hours, 60)

        # create a new embed
        embed = discord.Embed(title="Bot Status", description=None, color=discord.Color.red())
        if mins > 0:
            embed.add_field(name="Uptime:", value=f"{mins} minute(s) and {secs} seconds", inline=False)
        elif hours > 0:
            embed.add_field(name="Uptime:", value=f"{hours} hours, {mins} minutes and {secs} seconds", inline=False)
        elif days > 0:
            embed.add_field(name="Uptime:", value=f"{days} days, {hours} hours, {mins} minutes and {secs} second(s)",
                            inline=False)
        else:
            embed.add_field(name="Uptime:", value=f"{secs} seconds", inline=False)

        # add the discord.py version
        embed.add_field(name="Python Version:", value=f"{sys.version.split(' ')[0]}", inline=False)
        embed.add_field(name="Discord.py Version:", value=f"{discord.__version__}", inline=False)
        embed.add_field(name="Created by:", value="Riley and Skyler", inline=False)

        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(StatusCog(bot))
