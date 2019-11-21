import inspect
import discord
from config import getLogger
from .utils import checks
from discord.ext import commands
from utils import UserProfiles


class BotAdminCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reloadcog", hidden=True, help="Reloads a cog")
    @checks.isBotAdmin()
    async def reloadcog(self, ctx, *, cog: str):
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

    @commands.command(name="loadcog", hidden=True, help="Loads a cog")
    @checks.isBotAdmin()
    async def loadcog(self, ctx, *, cog: str):
        # try to load cog
        try:
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to load cog: {type(e).__name__} - {e}")
            getLogger().error(f"[Cog Management] Failed to load cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Loaded!")
            getLogger().success(f"[Cog Management] {ctx.author.name} loaded cog: {cog}")

    @commands.command(name="unloadcog", hidden=True, help="Unloads a cog")
    @checks.isBotAdmin()
    async def unloadcog(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to unload cog: {type(e).__name__} - {e}")
            getLogger().error(f"[Cog Management] Failed to unload cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Unloaded!")
            getLogger().success(f"[Cog Management] {ctx.author.name} unloaded cog: {cog}")

    @commands.command(name="reloadext", hidden=True, help="Reloads an extension")
    @checks.isBotAdmin()
    async def reloadext(self, ctx, *, ext: str):
        # to reload we need to unload it first
        try:
            self.bot.unload_extension(f"extensions.{ext}")
            self.bot.load_extension(f"extensions.{ext}")
        except Exception as e:
            await ctx.send(f"Failed to reload extension: {type(e).__name__} - {e}")
            getLogger().error(f"[Extension Management] Failed to reload extension: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Extension Reloaded!")
            getLogger().success(f"[Extension Management] {ctx.author.name} reloaded extension: {ext}")

    @commands.command(name="loadext", hidden=True, help="Loads an extension")
    @checks.isBotAdmin()
    async def loadext(self, ctx, *, ext: str):
        # try to load cog
        try:
            self.bot.load_extension(f"extensions.{ext}")
        except Exception as e:
            await ctx.send(f"Failed to load extension: {type(e).__name__} - {e}")
            getLogger().error(f"[Extension Management] Failed to load extension: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Extension Loaded!")
            getLogger().success(f"[Extension Management] {ctx.author.name} loaded extension: {ext}")

    @commands.command(name="unloadext", hidden=True, help="Unloads an extension")
    @checks.isBotAdmin()
    async def unloadext(self, ctx, *, ext: str):
        try:
            self.bot.unload_extension(f"extensions.{ext}")
        except Exception as e:
            await ctx.send(f"Failed to unload extension: {type(e).__name__} - {e}")
            getLogger().error(f"[Extension Management] Failed to unload extension: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Extension Unloaded!")
            getLogger().success(f"[Extension Management] {ctx.author.name} unloaded extension: {ext}")

    @commands.command(name="stop", hidden=True, help="Stops the bot")
    @checks.isBotAdmin()
    async def stop(self, ctx):
        await ctx.send("Shutting down...")
        try:
            await self.bot.close()
        except Exception as e:
            getLogger().critical(f"[Bot Management] Caught Exception during shutdown: {type(e).__name__} - {e}")
            await ctx.send(f"Caught Exception during shutdown: {type(e).__name__}, See console for more info.")

    @commands.command(name="eval", hidden=True, help="Evaluates code")
    @checks.isBotAdmin()
    async def eval(self, ctx, *, code: str):
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        try:
            result = eval(code)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(f"[Eval] Error running code: {type(e).__name__} - {e}")
        else:
            if result:
                await ctx.send(result)
            else:
                await ctx.send("[Eval] Empty result")

    @commands.command(name="resetuser", hidden=True, help="Clears a users profile")
    @commands.guild_only()
    @checks.isBotAdmin()
    async def resetuser(self, ctx, member: discord.Member):
        result = UserProfiles(member).reset()
        if result.deleted_count == 1:
            await ctx.send(f"{member.name}'s profile was reset!")
        else:
            await ctx.send(f"{member.name} doesn't have a profile!")


def setup(bot):
    bot.add_cog(BotAdminCommandsCog(bot))
