import discord
import json
import asyncio
from utils import getUserConfig
from discord.ext import commands


class GameCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rpgstart")
    @commands.guild_only()
    async def rpgstart(self, ctx):
        content = getUserConfig(ctx.author.id)
        json_content = json.loads(content)
        charactercreated = json_content["RPGData"]["CreatedCharacter"]
        if not charactercreated:
            await ctx.send("You have not created a character. Let's create one.")
            await ctx.send("What is the first name of your character?")

            try:
                firstname = await self.bot.wait_for('message', timeout=10)
                await ctx.send(firstname.content)
            except asyncio.TimeoutError:
                return await ctx.send("The bot has timed out!")
        else:
            await ctx.send("You already have a character, please use a different command!")

    @commands.command(name="rpgprofile")
    @commands.guild_only()
    async def rpgprofile(self, ctx, member=discord.Member):
        pass


def setup(bot):
    bot.add_cog(GameCommandsCog(bot))
