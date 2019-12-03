from discord.ext import commands
from config import getBotAdmins
from utils import ServerSettings


def isBotAdminCheck(ctx):
    if ctx.message.author.id in getBotAdmins():
        return True
    else:
        return False


def isBotAdmin():
    return commands.check(lambda ctx: isBotAdminCheck(ctx))


def isMusicEnabledCheck(ctx):
    server_document = ServerSettings(ctx.guild).getServerDocument()

    if server_document["modules"]["music"]:
        return True
    else:
        commands.CommandError(f"music commands are not enabled")


def isMusicEnabled():
    return commands.check(lambda ctx: isMusicEnabledCheck(ctx))


def isLoLEnabledCheck(ctx):
    server_document = ServerSettings(ctx.guild).getServerDocument()

    if server_document["modules"]["lol"]:
        return True
    else:
        commands.CommandError(f"lol commands are not enabled")


def isLoLEnabled():
    return commands.check(lambda ctx: isLoLEnabledCheck(ctx))


def isNSFWEnabledCheck(ctx):
    server_document = ServerSettings(ctx.guild).getServerDocument()

    if server_document["modules"]["nsfw_commands"]:
        return True
    else:
        commands.CommandError(f"nsfw commands are not enabled")


def isNSFWEnabled():
    return commands.check(lambda ctx: isNSFWEnabledCheck(ctx))

