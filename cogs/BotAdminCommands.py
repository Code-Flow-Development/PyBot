from config import getLogger
from .utils import checks
from discord.ext import commands


class BotAdminCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reloadcog")
    @checks.isBotAdmin()
    async def reload(self, ctx, *, cog: str):
        # to reload we need to unload it first
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to reload cog: {type(e).__name__} - {e}")
            getLogger().error(f"[Cog Management] Failed to reload cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Reloaded!")
            getLogger().success(f"[Cog Management] {ctx.author.name} reloaded cog: {cog}")

    @commands.command(name="loadcog")
    @checks.isBotAdmin()
    async def load(self, ctx, *, cog: str):
        # try to load cog
        try:
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to load cog: {type(e).__name__} - {e}")
            getLogger().error(f"[Cog Management] Failed to load cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Loaded!")
            getLogger().success(f"[Cog Management] {ctx.author.name} loaded cog: {cog}")

    @commands.command(name="unloadcog")
    @checks.isBotAdmin()
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to unload cog: {type(e).__name__} - {e}")
            getLogger().error(f"[Cog Management] Failed to unload cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Unloaded!")
            getLogger().success(f"[Cog Management] {ctx.author.name} unloaded cog: {cog}")

    @commands.command(name="unloadallcogs")
    @checks.isBotAdmin()
    async def unloadAll(self, ctx):
        pass
        # try:
        #     utils.unloadallcogs(self.bot)
        # except Exception as e:
        #     await ctx.send(f"Caught Exception while unloading all cogs: {type(e).__name__}, See console for more info")
        #     print(f"Caught Exception while unloading all cogs: {type(e).__name__} - {e}")

    @commands.command(name="stop")
    @checks.isBotAdmin()
    async def stop(self, ctx):
        await ctx.send("Shutting down...")
        try:
            await self.bot.close()
        except Exception as e:
            getLogger().critical(f"[Bot Management] Caught Exception during shutdown: {type(e).__name__} - {e}")
            await ctx.send(f"Caught Exception during shutdown: {type(e).__name__}, See console for more info.")

    @commands.command(name="eval")
    @checks.isBotAdmin()
    async def eval(self, ctx, *, code: str):
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        try:
            result = exec(code)
        except Exception as e:
            await ctx.send(f"[Eval] Error running code: {type(e).__name__} - {e}")
        else:
            await ctx.send(result)


def setup(bot):
    bot.add_cog(BotAdminCommandsCog(bot))
