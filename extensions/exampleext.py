from discord.ext import commands


@commands.command(name="exampleext")
async def exampleext(ctx):
    await ctx.send(f"Hello, {ctx.author}! This is an example extension!")


def setup(bot):
    bot.add_command(exampleext)