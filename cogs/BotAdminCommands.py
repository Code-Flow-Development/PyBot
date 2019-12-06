import ast
import inspect
from datetime import datetime

import discord
from discord.ext import commands

from utils import UserProfiles, getLogger, getSystemLogChannel, BotAdmins
from .utils import checks


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
        if len(self.bot.voice_clients) > 0:
            await ctx.send(f"There are {len(self.bot.voice_clients)} active voice clients")
        await ctx.send("Good Bye :(")
        try:
            await self.bot.close()
        except Exception as e:
            getLogger().critical(f"[Bot Management] Caught Exception during shutdown: {type(e).__name__} - {e}")
            await ctx.send(f"Caught Exception during shutdown: {type(e).__name__}, See console for more info.")

    @commands.command(name="eval", hidden=True, help="Evaluates code")
    @checks.isBotAdmin()
    async def eval(self, ctx, *, code: str):
        fn_name = "_eval_expr"

        cmd = code.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }

        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))
            if result is not None:
                return await ctx.send(f"```py\n{result}\n```")
            else:
                return await ctx.send(f"Empty Result")
        except Exception as e:
            await ctx.send(f"[Eval] Error running code: {type(e).__name__} - {e}")

    @commands.command(name="resetuser", hidden=True, help="Clears a users profile")
    @commands.guild_only()
    @checks.isBotAdmin()
    async def resetuser(self, ctx, member: discord.Member):
        result = UserProfiles(member).reset()
        if result.deleted_count == 1:
            await ctx.send(f"{member.name}'s profile was reset!")
            await getSystemLogChannel(self.bot).send(f"{ctx.author} reset {member}'s profile!")
        else:
            await ctx.send(f"{member.name} doesn't have a profile!")

    @commands.command(name="addbotadmin", hidden=True, help="Adds a new bot admin")
    @checks.isBotAdmin()
    async def addbotadmin(self, ctx, member: discord.Member):
        if not BotAdmins().add(member.id):
            embed = discord.Embed(title=None,
                                  description=f"{member.mention} is already a bot admin!",
                                  color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        else:
            embed = discord.Embed(title="New Bot Admin",
                                  description=f"{member.mention} was added as a bot admin by {ctx.author.mention}",
                                  color=discord.Color.green(),
                                  timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

            await ctx.send(content=None, embed=embed)
            await getSystemLogChannel(self.bot).send(content=None, embed=embed)
            await self.bot.get_user(213247101314924545).send(content=None, embed=embed)

    @commands.command(name="removebotadmin", hidden=True, help="Removes a bot admin")
    @checks.isBotAdmin()
    async def removebotadmin(self, ctx, member: discord.Member):
        if not BotAdmins().remove(member.id):
            embed = discord.Embed(title=None,
                                  description=f"{member.mention} is not a bot admin!",
                                  color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

            await ctx.send(content=None, embed=embed)
        else:
            embed = discord.Embed(title="Bot Admin Removed",
                                  description=f"{member.mention} was removed as a bot admin by {ctx.author.mention}",
                                  color=discord.Color.red(),
                                  timestamp=datetime.utcnow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

            await ctx.send(content=None, embed=embed)
            await getSystemLogChannel(self.bot).send(content=None, embed=embed)
            await self.bot.get_user(213247101314924545).send(content=None, embed=embed)

    @commands.command(name="botadmins", hidden=True, help="Lists the current bot admins")
    @checks.isBotAdmin()
    async def botadmins(self, ctx):
        current_admins = BotAdmins().get()
        current_admins = [self.bot.get_user(x).mention for x in current_admins]
        admins = "\n".join(current_admins)

        embed = discord.Embed(title="Current Bot Admins", description=admins, color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="setpresence", hidden=True, help="Change the bots presence",
                      usage="<name> <status: [online, dnd, idle, offline]> <activity_type: [playing, streaming, listening, watching]>")
    @checks.isBotAdmin()
    async def setpresence(self, ctx, name: str, status: str, activity_type: str):
        new_status = discord.Status.online if status.lower() == "online" else discord.Status.dnd if status.lower() == "dnd" else discord.Status.idle if status.lower() == "idle" else discord.Status.invisible if status.lower() == "invisible" else discord.Status.offline if status.lower() == "offline" else discord.Status.online
        new_activity_type = discord.ActivityType.playing if activity_type.lower() == "playing" else discord.ActivityType.listening if activity_type.lower() == "listening" else discord.ActivityType.watching if activity_type.lower() == "watching" else discord.ActivityType.streaming if activity_type.lower() == "streaming" else discord.ActivityType.playing
        activity = discord.Activity(name=name, type=new_activity_type)
        try:
            await self.bot.change_presence(status=new_status, activity=activity)
            getLogger().success(
                f"[BotAdminCommands] Presence was updated by {ctx.author} ({ctx.author.id}); name: {name} status: {status} activity_type {activity_type}")
            await self.bot.get_user(213247101314924545).send(
                f"[BotAdminCommands] Presence was updated by {ctx.author} ({ctx.author.id})! ```name: {name}\nstatus: {status}\nactivity_type: {activity_type}```")
            await ctx.send(f"[BotAdminCommands] Presence was updated!")
        except Exception as e:
            await ctx.send(f"[BotAdminCommands] Failed to change presence! Error: {e}")
            getLogger().error(f"[BotAdminCommands] Failed to change presence! Error: {e}")


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


def setup(bot):
    bot.add_cog(BotAdminCommandsCog(bot))
