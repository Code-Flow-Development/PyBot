import discord
import time
import sys
from discord.ext import commands
from datetime import datetime


class MiscCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    @commands.guild_only()
    async def ping(self, ctx):
        # gets the time (as of the message being sent)
        before = time.monotonic()
        # sends a message to the channel
        message = await ctx.send("Pong!")
        # calculates the ping using the current time and the time the message was sent
        ping = (time.monotonic() - before) * 1000
        # creates a new embed, sets title to blank with a description and color (color int generator: https://www.shodor.org/stella2java/rgbint.html)
        embed = discord.Embed(title="Bot Response Time", description=None, color=discord.Colour.red(), timestamp=datetime.utcnow())
        # adds a new field to the embed
        embed.add_field(name="🤖 Bot Latency:", value=f"{int(ping)}ms", inline=False)
        # adds a footer to the embed with the bot name and avatar
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        # edits the previous message sent with the new embed
        await message.edit(content=None, embed=embed)

    @commands.command(name="status")
    async def status(self, ctx):
        # unix time the bot has been up, takes time the bot was started minus the current unix time to get the difference
        unix = int(time.time() - self.bot.startedAt)

        mins, secs = divmod(unix, 60)
        hours, mins = divmod(mins, 60)
        days, hours = divmod(hours, 60)

        # create a new embed
        embed = discord.Embed(title="Bot Status", description=None, color=discord.Color.red(),
                              timestamp=datetime.utcnow())
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
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="avatar")
    @commands.guild_only()
    async def avatar(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        embed = discord.Embed(title=f"Avatar for {member.display_name}", description=None, color=discord.Colour.red(),
                              timestamp=datetime.utcnow())
        embed.set_image(url=member.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="ddos")
    @commands.guild_only()
    async def ddos(self, ctx, member: discord.Member):
        await ctx.send(f"Initiating DDoS attack on {member.name}, please wait...")
        time.sleep(1000)
        await ctx.send("Malicious UDP packets were sent to their IP address, they should be offline now. :)")

    @commands.command(name="swat")
    @commands.guild_only()
    async def swat(self, ctx, member: discord.Member):
        await ctx.send(f"Initiating SWAT procedures on {member.name}, please wait...")
        time.sleep(1000)
        await ctx.send("Your local police department has been notified that you have shot your Dad & now have your mother hostage in your home, along with a can of gas with you to burn your house down. Enjoy the shitshow, motherfucker.")


def setup(bot):
    bot.add_cog(MiscCommandsCog(bot))
