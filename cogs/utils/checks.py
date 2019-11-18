import discord
from discord.ext import commands
from config import ADMINS


def isBotAdminCheck(ctx):
    if str(ctx.message.author.id) in ADMINS:
        return True
    else:
        return False


def isBotAdmin():
    return commands.check(lambda ctx: isBotAdminCheck(ctx))