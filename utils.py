import os
import discord
from discord.ext.commands import errors


def loadallcogs(bot):
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
