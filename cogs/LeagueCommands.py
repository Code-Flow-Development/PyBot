import discord
import json
import random
import asyncio
from discord.ext import commands


class LeagueCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Main command for the league cog, might be the only one.
    @commands.command(name="league")
    async def league(self, ctx, decider: str, decider2: str = None):
        # Displays all the champions in the bot currently.
        if decider.lower() == "champlist":
            file = open("LolData\LoLChamps.json", 'r')
            contents = file.read()
            json_contents = json.loads(contents)
            embed = discord.Embed(title="Champions List",
                                  description=', '.join(json_contents),
                                  color=discord.Color.orange())
            await ctx.send(content=None, embed=embed)

        # Displays all the items in the bot currently.
        elif decider.lower() == "itemlist":
            file = open("LolData\LoLItems.json", 'r')
            contents = file.read()
            json_contents = json.loads(contents)
            embed = discord.Embed(title="Items List",
                                  description=', '.join(json_contents),
                                  color=discord.Color.orange())
            await ctx.send(content=None, embed=embed)

        # Displays all the runes in the bot currently.
        elif decider.lower() == "runes":
            file = open("LolData\LoLRunes.json", 'r')
            contents = file.read()
            json_contents = json.loads(contents)
            embed = discord.Embed(title="Runes List",
                                  description=', '.join(json_contents),
                                  color=discord.Color.orange())
            await ctx.send(content=None, embed=embed)

        # Displays a random set of 6 items.
        elif decider2 is not None:
            if decider.lower() == "random" and decider2.lower() == "champs":
                file = open("LolData\LoLChamps.json", 'r')
                contents = file.read()
                json_contents = json.loads(contents)
                randchamp = random.choice(json_contents)
                await ctx.send(randchamp)
            elif decider.lower() == "random" and decider2.lower() == "items":
                try:
                    await ctx.send("What lane are you playing?")
                    response = await self.bot.wait_for('message', timeout=20)
                    if response.content.lower() == "top" or response.content.lower() == "mid" or response.content.lower() == "bot":
                        await ctx.send("You have selected top mid or bot.")
                        file = open("LolData\LoLItems.json", 'r')
                        contents = file.read()
                        json_contents = json.loads(contents)
                        randitemone = random.choice(json_contents)
                        randitemtwo = None
                        randitemthree = None
                        randitemfour = None
                        randitemfive = None
                        while True:
                            desireditem = random.choice(json_contents)
                            if randitemtwo is None:
                                if not desireditem == randitemone:
                                    randitemtwo = desireditem
                            elif randitemthree is None:
                                if not desireditem == randitemone or randitemtwo:
                                    randitemthree = desireditem
                            elif randitemfour is None:
                                if not desireditem == randitemone or randitemtwo or randitemthree:
                                    randitemfour = desireditem
                            elif randitemfive is None:
                                if not desireditem == randitemone or randitemtwo or randitemthree or randitemfour:
                                    randitemfive = desireditem
                                    break

                        file.close()
                        file = open("LolData\LoLBoots.json", 'r')
                        contents = file.read()
                        json_contents = json.loads(contents)
                        randboots = random.choice(json_contents)

                        await ctx.send(f"first item : {randitemone}\nsecond item : {randitemtwo}\nthird item : {randitemthree}\nfourth item : {randitemfour}\nfifth item : {randitemfive}\nboots : {randboots}")
                    elif response.content.lower() == "jungle":
                        await ctx.send("You have selected jungle!")
                        file = open("LolData\LoLjgItems.json", 'r')
                        contents = file.read()
                        json_contents = json.loads(contents)
                        randitemone = random.choice(json_contents)
                        file.close()
                        file = open("LolData\LoLItems.json", 'r')
                        contents = file.read()
                        json_contents = json.loads(contents)
                        randitemtwo = None
                        randitemthree = None
                        randitemfour = None
                        randitemfive = None
                        while True:
                            desireditem = random.choice(json_contents)
                            if randitemtwo is None:
                                if not desireditem == randitemone:
                                    randitemtwo = desireditem
                            elif randitemthree is None:
                                if not desireditem == randitemone or randitemtwo:
                                    randitemthree = desireditem
                            elif randitemfour is None:
                                if not desireditem == randitemone or randitemtwo or randitemthree:
                                    randitemfour = desireditem
                            elif randitemfive is None:
                                if not desireditem == randitemone or randitemtwo or randitemthree or randitemfour:
                                    randitemfive = desireditem
                                    break

                        file.close()
                        file = open("LolData\LoLBoots.json", 'r')
                        contents = file.read()
                        json_contents = json.loads(contents)
                        randboots = random.choice(json_contents)

                        await ctx.send(f"first item : {randitemone}\nsecond item : {randitemtwo}\nthird item : {randitemthree}\nfourth item : {randitemfour}\nfifth item : {randitemfive}\nboots : {randboots}")
                    elif response.content.lower() == "support":
                        await ctx.send("You have selected support!")
                        file = open("LolData\LoLsuppItems.json", 'r')
                        contents = file.read()
                        json_contents = json.loads(contents)
                        randitemone = random.choice(json_contents)
                        file.close()
                        file = open("LolData\LoLItems.json", 'r')
                        contents = file.read()
                        json_contents = json.loads(contents)
                        randitemtwo = None
                        randitemthree = None
                        randitemfour = None
                        randitemfive = None
                        while True:
                            desireditem = random.choice(json_contents)
                            if randitemtwo is None:
                                if not desireditem == randitemone:
                                    randitemtwo = desireditem
                            elif randitemthree is None:
                                if not desireditem == randitemone or randitemtwo:
                                    randitemthree = desireditem
                            elif randitemfour is None:
                                if not desireditem == randitemone or randitemtwo or randitemthree:
                                    randitemfour = desireditem
                            elif randitemfive is None:
                                if not desireditem == randitemone or randitemtwo or randitemthree or randitemfour:
                                    randitemfive = desireditem
                                    break

                        file.close()
                        file = open("LolData\LoLBoots.json", 'r')
                        contents = file.read()
                        json_contents = json.loads(contents)
                        randboots = random.choice(json_contents)

                        await ctx.send(f"first item : {randitemone}\nsecond item : {randitemtwo}\nthird item : {randitemthree}\nfourth item : {randitemfour}\nfifth item : {randitemfive}\nboots : {randboots}")
                    else:
                        await ctx.send("[LeagueCommands] Lane was not recognized, please re-run the command.")
                except asyncio.TimeoutError:
                    await ctx.send("[LeagueCommands] Bot has timed out, please re-run the command.")
            elif decider.lower() == "random" and decider2.lower() == "runes":
                file = open("LolData\LoLRunes.json", 'r')
                contents = file.read()
                json_contents = json.loads(contents)
                randruneprimary = random.choice(json_contents)
                randrunesecondary = random.choice(json_contents)
                while randrunesecondary == randruneprimary:
                    randrunesecondary = random.choice(json_contents)
                await ctx.send(f"primary rune : {randruneprimary}\nsecondary rune : {randrunesecondary}")

        # Tells them how to use the command properly, because they didn't use arguments.
        elif decider.lower() == "help":
            embed = discord.Embed(title="League Command Help",
                                  description="This command needs parameters to run properly!",
                                  color=discord.Color.orange())
            embed.add_field(name="{league champlist",
                            value="Displays a list of all the champs in the bot.",
                            inline=True)
            embed.add_field(name="{league itemlist",
                            value="Displays a list of all the items in the bot.",
                            inline=True)
            embed.add_field(name="{league runes",
                            value="Displays a list of all the runes in the bot.",
                            inline=True)
            embed.add_field(name="{league [rand,random] items",
                            value="Displays a random sets of items for you to use!",
                            inline=True)
            embed.add_field(name="{league [rand,random] champs",
                            value="Displays a random champion for you to use!",
                            inline=True)
            embed.add_field(name="{league [rand,random] runes",
                            value="Displays a random set of runes for you to use!",
                            inline=True)
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(LeagueCommandsCog(bot))
