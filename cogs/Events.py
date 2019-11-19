import traceback
import sys
from discord.ext import commands
from config import getLogger


class CommandEventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # This prevents any cogs with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = commands.CommandNotFound

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except:
                pass

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(error)

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Missing arguments!")

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send("You don't have permission to use that command!")

        # All other Errors not returned come here... And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        getLogger().info(
            f"[Commands] {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) ran command {ctx.command.name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if "xd" in message.content.lower():
            await message.channel.send("Ecks Dee")
            return

        if "meme" in message.content.lower():
            await message.channel.send("shit meme")
            return

        if "anime" in message.content.lower():
            await message.channel.send("fucking weeb")
            return


def setup(bot):
    bot.add_cog(CommandEventsCog(bot))
