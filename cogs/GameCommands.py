import discord
import json
import asyncio
from utils import getUserConfig
from utils import saveUserConfig
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
                firstname = await self.bot.wait_for('message', timeout=20)
                await ctx.send("Please say your middle name now.")
            except asyncio.TimeoutError:
                return await ctx.send("The bot has timed out, please re-run the command.")
                
            try:
                middlename = await self.bot.wait_for('message', timeout=20)
                await ctx.send("Please say your last name.")
            except asyncio.TimeoutError:
                return await ctx.send("The bot has timed out, please re-run the command.")
                
            try:
                lastname = await self.bot.wait_for('message', timeout=20)
            except asyncio.TimeoutError:
                return await ctx.send("The bot has timed out, please re-run the command.")

            await ctx.send(f"So your full name is {firstname.content} {middlename.content} {lastname.content}?")
            await ctx.send(f"If this is correct, then please respond with **yes**, if not, respond with **no**.")
            await ctx.send(f"You must send either **yes** or **no**!")

            try:
                response = await self.bot.wait_for('message', timeout=20)
                if response.content.lower() == "yes":
                    json_content["RPGData"]["CreatedCharacter"] = True
                    json_content["RPGData"]["Name"]["FirstName"] = firstname.content
                    json_content["RPGData"]["Name"]["MiddleName"] = middlename.content
                    json_content["RPGData"]["Name"]["LastName"] = lastname.content
                    saveUserConfig(ctx.author.id, json_content)
                    await ctx.send(f"File saved")
                elif response.content.lower() == "no":
                    await ctx.send("Please run the command again to re-do the character creation process.")
                else:
                    await ctx.send(f"Since you didn't send a proper input, you get to do this all over again. **Dumbass!**")
            except asyncio.TimeoutError:
                return await ctx.send("The bot has timed out, please re-run the command.")
        else:
            await ctx.send("You already have a character, please use a different command!")

    @commands.command(name="rpgprofile")
    @commands.guild_only()
    async def rpgprofile(self, ctx, member=discord.Member):
        pass


def setup(bot):
    bot.add_cog(GameCommandsCog(bot))
