import discord
import utils
from .utils import checks
from discord.ext import commands


class CogManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reloadcog")
    @checks.isAdmin()
    async def reload(self, ctx, *, cog: str):
        # to reload we need to unload it first
        try:
            self.bot.unload_extension(f"commands.{cog}")
            self.bot.load_extension(f"commands.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to reload cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Reloaded!")

    @commands.command(name="loadcog")
    @checks.isAdmin()
    async def load(self, ctx, *, cog: str):
        # try to load cog
        try:
            self.bot.load_extension(f"commands.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to load cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Loaded!")

    @commands.command(name="unloadcog")
    @checks.isAdmin()
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(f"commands.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to unload cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Unloaded!")

    @commands.command(name="unloadallcogs")
    @checks.isAdmin()
    async def unloadAll(self, ctx):
        pass
        # try:
        #     utils.unloadallcogs(self.bot)
        # except Exception as e:
        #     await ctx.send(f"Caught Exception while unloading all cogs: {type(e).__name__}, See console for more info")
        #     print(f"Caught Exception while unloading all cogs: {type(e).__name__} - {e}")


def setup(bot):
    bot.add_cog(CogManagementCog(bot))
