import discord
from config import ADMINS
from discord.ext import commands


def isAdmin(ctx):
    if str(ctx.message.author.id) in ADMINS:
        return True
    else:
        return False


class CogManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reloadcog")
    @commands.guild_only()
    @commands.check(isAdmin)
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
    @commands.guild_only()
    @commands.check(isAdmin)
    async def load(self, ctx, *, cog: str):
        # try to load cog
        try:
            self.bot.load_extension(f"commands.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to load cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Loaded!")

    @commands.command(name="unloadcog")
    @commands.guild_only()
    @commands.check(isAdmin)
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(f"commands.{cog}")
        except Exception as e:
            await ctx.send(f"Failed to unload cog: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"Cog Unloaded!")


def setup(bot):
    bot.add_cog(CogManagementCog(bot))
