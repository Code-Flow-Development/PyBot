import discord
import os
import time
from discord.ext import commands
from discord.ext.commands import errors
from dotenv import load_dotenv

# Create a new 'bot' with prefix
bot = commands.Bot(command_prefix="{", description="PyBot")

# Loads commands from commands folder, no need to touch this when adding new commands, it loads them automagically!
if __name__ == '__main__':
    # loads commands
    for command in os.listdir("commands"):
        if command.endswith("py"):
            filename = command.split(".")[0]
            try:
                bot.load_extension(f"commands.{filename}")
                print(f"Command Loaded: {filename}")
            except (errors.ExtensionNotFound, errors.ExtensionAlreadyLoaded, errors.NoEntryPointError,
                    errors.ExtensionFailed) as e:
                print(f"Error loading command: {filename}, Error: {e}")

    # loads events
    for event in os.listdir("events"):
        if event.endswith("py"):
            filename = event.split(".")[0]
            try:
                bot.load_extension(f"events.{filename}")
                print(f"Event Loaded: {filename}")
            except (errors.ExtensionNotFound, errors.ExtensionAlreadyLoaded, errors.NoEntryPointError,
                    errors.ExtensionFailed) as e:
                print(f"Error loading event: {filename}, Error: {e}")


# Ready event
@bot.event
async def on_ready():
    bot.startedAt = time.time()
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator}')
    await bot.change_presence(
        activity=discord.Activity(name='in ' + str(len(bot.guilds)) + " server!", type=discord.ActivityType.playing))


# load the .env file with token
load_dotenv()
# login to discord
bot.run(os.getenv("TOKEN"))
