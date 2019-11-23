import inspect
import discord
from config import getLogger, addBotAdmin, removeBotAdmin, getBotAdmins, getBotLogChannel
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
            await getBotLogChannel(self.bot).send(f"{ctx.author} reset {member}'s profile!")
        else:
            await ctx.send(f"{member.name} doesn't have a profile!")

    @commands.command(name="addbotadmin", hidden=True, help="Adds a new bot admin")
    @checks.isBotAdmin()
    async def addbotadmin(self, ctx, member: discord.Member):
        addBotAdmin(member.id)
        await ctx.send(f"Added {member.name} as a bot admin.")
        await getBotLogChannel(self.bot).send(f"{ctx.author} ({ctx.author.id}) added {member} ({member.id}) as a bot admin!")
        await self.bot.get_user(213247101314924545).send(f"{ctx.author} ({ctx.author.id}) added {member} ({member.id}) as a bot admin!")

    @commands.command(name="removebotadmin", hidden=True, help="Removes a bot admin")
    @checks.isBotAdmin()
    async def removebotadmin(self, ctx, member: discord.Member):
        removeBotAdmin(member.id)
        await ctx.send(f"Removed {member.name} as a bot admin.")
        await getBotLogChannel(self.bot).send(f"{ctx.author} ({ctx.author.id}) removed {member} ({member.id}) as a bot admin!")
        await self.bot.get_user(213247101314924545).send(f"{ctx.author} ({ctx.author.id}) removed {member} ({member.id}) as a bot admin!")

    @commands.command(name="botadmins", hidden=True, help="Lists the current bot admins")
    @checks.isBotAdmin()
    async def botadmins(self, ctx):
        current_admins = getBotAdmins()
        current_admins = [self.bot.get_user(x).mention for x in current_admins]
        await ctx.send(f"Current bot admins are: {', '.join(current_admins)}")

    @commands.command(name="setpresence", hidden=True, help="Change the bots presence", usage="<name> <status: [online, dnd, idle, offline]> <activity_type: [playing, streaming, listening, watching]>")
    @checks.isBotAdmin()
    async def setpresence(self, ctx, name: str, status: str, activity_type: str):
        new_status = discord.Status.online if status.lower() == "online" else discord.Status.dnd if status.lower() == "dnd" else discord.Status.idle if status.lower() == "idle" else discord.Status.invisible if status.lower() == "invisible" else discord.Status.offline if status.lower() == "offline" else discord.Status.online
        new_activity_type = discord.ActivityType.playing if activity_type.lower() == "playing" else discord.ActivityType.listening if activity_type.lower() == "listening" else discord.ActivityType.watching if activity_type.lower() == "watching" else discord.ActivityType.streaming if activity_type.lower() == "streaming" else discord.ActivityType.playing
        activity = discord.Activity(name=name, type=new_activity_type)
        try:
            await self.bot.change_presence(status=new_status, activity=activity)
            getLogger().success(f"[BotAdminCommands] Presence was updated by {ctx.author} ({ctx.author.id}); name: {name} status: {status} activity_type {activity_type}")
            await self.bot.get_user(213247101314924545).send(f"[BotAdminCommands] Presence was updated by {ctx.author} ({ctx.author.id}); name: {name} status: {status} activity_type {activity_type}")
            await ctx.send(f"[BotAdminCommands] Presence was updated!")
        except Exception as e:
            await ctx.send(f"[BotAdminCommands] Failed to change presence! Error: {e}")
            getLogger().error(f"[BotAdminCommands] Failed to change presence! Error: {e}")


def setup(bot):
    bot.add_cog(BotAdminCommandsCog(bot))
