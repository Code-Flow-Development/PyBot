from config import getLogger
from discord.ext import commands
from .utils import checks


class BotManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stop")
    @checks.isAdmin()
    async def stop(self, ctx):
        await ctx.send("Shutting down...")
        try:
            await self.bot.close()
        except Exception as e:
            getLogger().critical(f"[Bot Management] Caught Exception during shutdown: {type(e).__name__} - {e}")
            await ctx.send(f"Caught Exception during shutdown: {type(e).__name__}, See console for more info.")

    @commands.command(name="eval")
    @checks.isAdmin()
    async def eval(self, ctx, *, code: str):
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        try:
            result = eval(code)
        except Exception as e:
            await ctx.send(f"Error running code: {type(e).__name__} - {e}")
        else:
            await ctx.send(result)


def setup(bot):
    bot.add_cog(BotManagementCog(bot))
