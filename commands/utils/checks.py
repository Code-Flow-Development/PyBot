import discord
from discord.ext import commands
from config import ADMINS


def isAdminCheck(ctx):
    if str(ctx.message.author.id) in ADMINS:
        return True
    else:
        return False


def isAdmin():
    return commands.check(lambda ctx: isAdminCheck(ctx))
