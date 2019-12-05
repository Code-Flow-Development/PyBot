from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="examplecog")
    async def examplecog(self, ctx):
        await ctx.send(f"Hello, {ctx.author}! This is an example cog!")


def setup(bot):
    bot.add_cog(ExampleCog(bot))
