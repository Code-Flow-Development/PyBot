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
                                    await ctx.send(f"[GameCommands] Character saved!\nNow you need to select a race:\n**Orc**\n**Elf** \n**Dark Elf**\n**Human** \n**Dwarf** \n**Goblin**\n**Kobold**")

                                    def check(message):
                                        return True if message.content else False

                                    try:
                                        response = await self.bot.wait_for('message', check=check, timeout=20)
                                        await ctx.message.channel.purge(limit=4)
                                        if response.content.lower() == "orc":
                                            profile_data["RPGData"]["Race"] = "orc"
                                            profile.update("RPGData", profile_data["RPGData"])
                                            await ctx.message.channel.purge(limit=8)
                                            await ctx.send("[GameManager] Your race has been selected as orc.")
                                        elif response.content.lower() == "elf":
                                            profile_data["RPGData"]["Race"] = "elf"
                                            profile.update("RPGData", profile_data["RPGData"])
                                            await ctx.message.channel.purge(limit=8)
                                            await ctx.send("[GameManager] Your race has been selected as elf.")
                                        elif response.content.lower() == "dark elf":
                                            profile_data["RPGData"]["Race"] = "dark elf"
                                            profile.update("RPGData", profile_data["RPGData"])
                                            await ctx.message.channel.purge(limit=8)
                                            await ctx.send("[GameManager] Your race has been selected as dark elf.")
                                        elif response.content.lower() == "human":
                                            profile_data["RPGData"]["Race"] = "human"
                                            profile.update("RPGData", profile_data["RPGData"])
                                            await ctx.message.channel.purge(limit=8)
                                            await ctx.send("[GameManager] Your race has been selected as human.")
                                        elif response.content.lower() == "dwarf":
                                            profile_data["RPGData"]["Race"] = "dwarf"
                                            profile.update("RPGData", profile_data["RPGData"])
                                            await ctx.message.channel.purge(limit=8)
                                            await ctx.send("[GameManager] Your race has been selected as dwarf.")
                                        elif response.content.lower() == "goblin":
                                            profile_data["RPGData"]["Race"] = "goblin"
                                            profile.update("RPGData", profile_data["RPGData"])
                                            await ctx.message.channel.purge(limit=8)
                                            await ctx.send("[GameManager] Your race has been selected as goblin.")
                                        elif response.content.lower() == "kobold":
                                            profile_data["RPGData"]["Race"] = "kobold"
                                            profile.update("RPGData", profile_data["RPGData"])
                                            await ctx.message.channel.purge(limit=8)
                                            await ctx.send("[GameManager] Your race has been selected as kobold.")
                                    except asyncio.TimeoutError:
                                        await ctx.send("[GameManager] The bot has timed out.")
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
        profile = UserProfiles(ctx.author)
        profile_data = profile.getUserProfile()
        a = profile_data['RPGData']['Name']
        isCreated = profile_data["RPGData"]["CreatedCharacter"]
        if isCreated:
            embed = discord.Embed(title=f"Rpg Profile",
                                  description=f"[Title] : {a['FirstName']} {a['MiddleName']} {a['LastName']}",
                                  color=discord.Color.gold())
            embed.add_field(name="Stats",
                            value=f"[Level] : {profile_data['RPGData']['Stats']['Level']}"
                                  f"\n- [Current EXP] : {profile_data['RPGData']['Stats']['CurrentExp']}"
                                  f"\n- [Needed EXP] : {profile_data['RPGData']['Stats']['MaxExp']}\n"
                                  f"\n[Race] : {profile_data['RPGData']['Race']}\n"
                                  f"\n[Sheckels] : {profile_data['RPGData']['Stats']['Sheckels']}",
                            inline=False)
            embed.add_field(name="Inventory",
                            value=f"I'm an inventory!",
                            inline=False)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            await ctx.send(content=None, embed=embed)
        else:
            await ctx.send("You must created a character before you use this command. \n Do '{rpgstart'!")


def setup(bot):
    bot.add_cog(GameCommandsCog(bot))
