import traceback
import sys
import discord
from datetime import datetime
from discord.ext import commands
from utils import ServerSettings, getLogger, getSystemLogChannel


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        # This prevents any cogs with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = commands.CommandNotFound

        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        # handle disabled commands
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        # handle commands that cant be used in DMS
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except:
                pass

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(error)

        # handle missing arguments
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Missing arguments! Usage: {ctx.command.usage}")

        # handle too many arguments
        elif isinstance(error, commands.TooManyArguments):
            return await ctx.send(f"Too many arguments! Usage: {ctx.command.usage}")

        # handle incorrect channel
        elif isinstance(error, commands.NSFWChannelRequired):
            return await ctx.send(f"That command is NSFW and requires an NSFW channel!")

        # intended to ignore blocked users or servers
        elif isinstance(error, commands.CommandError):
            return

        # handle invalid permissions (mainly bot admin only commands)
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send("You don't have permission to use that command!")

        # All other Errors not returned come here... And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # on command listener
    @commands.Cog.listener()
    async def on_command(self, ctx):
        getLogger().info(
            f"[Commands] {ctx.author} ({ctx.author.id}) ran command {ctx.command.name}")

    # on guild join listener
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        # socketio.emit("server count", {"servers": len(self.bot.guilds)})
        ServerSettings(guild)
        embed = discord.Embed(title=f"New Guild", description=None, color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.add_field(name="Guild Name", value=f"{guild.name}")
        embed.add_field(name="Guild ID", value=f"{guild.id}")
        embed.add_field(name="Guild Members", value=f"{guild.member_count}")
        embed.add_field(name="Guild Owner", value=f"{guild.owner} ({guild.owner.id})")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await getSystemLogChannel(self.bot).send(content=None, embed=embed)

    # on guild leave event
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        # socketio.emit("server count", {"servers": len(self.bot.guilds)})
        ServerSettings(guild).reset()
        embed = discord.Embed(title=f"Guild Left", description=None, color=discord.Color.red(),
                              timestamp=datetime.utcnow())
        embed.add_field(name="Guild Name", value=f"{guild.name}")
        embed.add_field(name="Guild ID", value=f"{guild.id}")
        embed.add_field(name="Guild Owner", value=f"{guild.owner} ({guild.owner.id})")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await getSystemLogChannel(self.bot).send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(EventsCog(bot))
