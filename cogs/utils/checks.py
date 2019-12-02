from discord.ext import commands
from config import getBotAdmins


def isBotAdminCheck(ctx):
    if ctx.message.author.id in getBotAdmins():
        return True
    else:
        return False


def isBotAdmin():
    return commands.check(lambda ctx: isBotAdminCheck(ctx))
