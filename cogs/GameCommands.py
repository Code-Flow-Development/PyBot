import discord
import asyncio
from utils import UserProfiles
from discord.ext import commands
from discord.errors import HTTPException, Forbidden


class GameCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rpgstart")
    @commands.guild_only()
    async def rpgstart(self, ctx):
        profile = UserProfiles(ctx.author)
        profile_data = profile.getUserProfile()
        isCreated = profile_data["RPGData"]["CreatedCharacter"]
        if not isCreated:
            await ctx.send("You have not created a character. Let's create one.\nWhat is the first name of your character?")
            try:
                firstname = await self.bot.wait_for('message', timeout=20)
                await ctx.send("Please say your middle name now.")
                try:
                    middlename = await self.bot.wait_for('message', timeout=20)
                    await ctx.send("Please say your last name.")
                    try:
                        lastname = await self.bot.wait_for('message', timeout=20)
                        await ctx.send(
                            f"So your full name is {firstname.content} {middlename.content} {lastname.content}?\nIf this is correct, then please respond with **yes**, if not, respond with **no**.")

                        try:
                            def check(message):
                                return True if message.content else False

                            response = await self.bot.wait_for('message', check=check, timeout=20)
                            if response.content.lower() == "yes":
                                profile_data["RPGData"]["CreatedCharacter"] = True
                                profile_data["RPGData"]["Name"]["FirstName"] = firstname.content
                                profile_data["RPGData"]["Name"]["MiddleName"] = middlename.content
                                profile_data["RPGData"]["Name"]["LastName"] = lastname.content
                                profile.update("RPGData", profile_data["RPGData"])
                                try:
                                    # delete all the questions and answers
                                    await ctx.message.channel.purge(limit=8)
                                    await ctx.send(f"[GameCommands] Character saved!")
                                except Forbidden as e:
                                    await ctx.send(f"[GameCommands] Missing permissions to delete messages! Error: {e.text}")
                                except HTTPException as e:
                                    await ctx.send(f"[GameCommands] Failed to delete messages! Error: {e.text}")
                            elif response.content.lower() == "no":
                                await ctx.send("[GameCommands] Please run the command again to re-do the character creation process.")
                            else:
                                await ctx.send(
                                    f"[GameCommands] Since you didn't send a proper input, you get to do this all over again. **Dumbass!**")
                        except asyncio.TimeoutError:
                            return await ctx.send("[GameCommands] The bot has timed out, please re-run the command.")
                    except asyncio.TimeoutError:
                        return await ctx.send("[GameCommands] The bot has timed out, please re-run the command.")
                except asyncio.TimeoutError:
                    return await ctx.send("[GameCommands] The bot has timed out, please re-run the command.")
            except asyncio.TimeoutError:
                return await ctx.send("[GameCommands] The bot has timed out, please re-run the command.")
        else:
            await ctx.send("You already have a character, please use a different command!")

    @commands.command(name="rpgprofile")
    @commands.guild_only()
    async def rpgprofile(self, ctx, member=discord.Member):
        pass


def setup(bot):
    bot.add_cog(GameCommandsCog(bot))
