import traceback
import sys
import discord
from datetime import datetime
from discord.ext import commands
from config import getLogger, getBotLogChannel
from utils import ServerSettings


class EventsCog(commands.Cog):
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
            return await ctx.send(f"Missing arguments! Usage: {ctx.command.usage}")

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send("You don't have permission to use that command!")

        elif isinstance(error, commands.TooManyArguments):
            return await ctx.send(f"Too many arguments! Usage: {ctx.command.usage}")

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

        server_settings = ServerSettings(message.guild)
        server_document = server_settings.getServerDocument()
        message_responses_enabled = server_document["message_responses_enabled"]
        counting_channel_enabled = server_document["counting_channels_enabled"]

        if counting_channel_enabled:
            if message.channel.type == discord.ChannelType.text and message.channel.name.lower().startswith("count-to-"):
                try:
                    # try to convert the string to a number
                    number = int(message.content)
                    next_number = int(message.channel.name.split("-")[-1])
                    if number == next_number and next_number >= 0:
                        # user gave the correct next number
                        await message.channel.edit(name=f"count-to-{number + 1}")
                    elif int(next_number - 2) == number and next_number >= 0:
                        await message.channel.edit(name=f"count-to-{next_number - 1}")
                    else:
                        # not the next number so delete the message
                        await message.delete()
                except ValueError:
                    # not a valid number so delete the message
                    await message.delete()

        if message_responses_enabled:
            custom_message_responses = server_document["custom_message_responses"]
            for custom_response in custom_message_responses:
                trigger = custom_response["trigger"]
                response = custom_response["response"]
                if trigger in message.content.lower():
                    await message.channel.send(response)
                    return

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        embed = discord.Embed(title=f"New Guild", description=None, color=discord.Color.green(),
                              timestamp=datetime.utcnow())
        embed.add_field(name="Guild Name", value=f"{guild.name}")
        embed.add_field(name="Guild ID", value=f"{guild.id}")
        embed.add_field(name="Guild Members", value=f"{guild.member_count}")
        embed.add_field(name="Guild Owner", value=f"{guild.owner} ({guild.owner.id})")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await getBotLogChannel(self.bot).send(content=None, embed=embed)
        ServerSettings(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        embed = discord.Embed(title=f"Guild Left", description=None, color=discord.Color.red(),
                              timestamp=datetime.utcnow())
        embed.add_field(name="Guild Name", value=f"{guild.name}")
        embed.add_field(name="Guild ID", value=f"{guild.id}")
        embed.add_field(name="Guild Owner", value=f"{guild.owner} ({guild.owner.id})")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await getBotLogChannel(self.bot).send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(EventsCog(bot))
