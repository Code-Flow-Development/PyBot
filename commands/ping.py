import discord, time
from discord.ext import commands


class PingCog(commands.Cog):
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
        embed = discord.Embed(title="Bot Response Time", description=None, color=discord.Colour(value=16711680))
        # adds a new field to the embed
        embed.add_field(name="🤖 Bot Latency:", value=f"{int(ping)}ms", inline=False)
        # adds a footer to the embed with the bot name and avatar
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        # edits the previous message sent with the new embed
        await message.edit(content=None, embed=embed)


def setup(bot):
    bot.add_cog(PingCog(bot))
