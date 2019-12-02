import discord
import json
import random
import asyncio
from datetime import datetime
from discord.ext import commands
from datetime import datetime
from utils import getLoLBootsJson, getLoLChampsJson, getLoLItemsJson, getLoLjgItemsJson, getLoLRunesJson, getLoLSuppItemsJson, getLoLChampsKeyList


class LeagueCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Main command for the league cog, might be the only one.
    @commands.command(name="league")
    async def league(self, ctx, decider: str, decider2: str = None):
        # Displays all the champions in the bot currently.
        if decider.lower() == "champlist":
            champ_key_list = getLoLChampsKeyList()
            embed = discord.Embed(title="Champions List",
                                  description=', '.join(champ_key_list),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)

        # Displays all the items in the bot currently.
        elif decider.lower() == "itemlist":
            items_list = getLoLItemsJson()
            embed = discord.Embed(title="Items List",
                                  description=', '.join(items_list),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.now())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)

        # Displays all the runes in the bot currently.
        elif decider.lower() == "runes":
            runes_list = getLoLRunesJson()
            embed = discord.Embed(title="Runes List",
                                  description=', '.join(runes_list),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)

        # Displays a random set of 6 items.
        elif decider2 is not None:
            if decider.lower() == "random" and decider2.lower() == "champs":
                champs_list = getLoLChampsJson()
                randchamp = random.choice(champs_list)
                displayname = randchamp[list(randchamp.keys())[0]]["display_name"]
                titlename = randchamp[list(randchamp.keys())[0]]['title']
                loresnippet = randchamp[list(randchamp.keys())[0]]['lore_snippet']
                embed = discord.Embed(title=f"{displayname} {titlename}",
                                      description=f"{loresnippet} \n **Goodluck with the random champion!**",
                                      color=discord.Color.orange(),
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await ctx.send(content=None, embed=embed)
            elif decider.lower() == "random" and decider2.lower() == "items":
                try:
                    await ctx.send("What lane are you playing?")
                    response = await self.bot.wait_for('message', timeout=20)
                    if response.content.lower() == "top" or response.content.lower() == "mid" or response.content.lower() == "bot":
                        items_list = getLoLItemsJson()
                        randitemone = random.choice(items_list)
                        randitemtwo = None
                        randitemthree = None
                        randitemfour = None
                        randitemfive = None
                        while True:
                            desireditem = random.choice(items_list)
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

                        items_list = getLoLBootsJson()
                        randboots = random.choice(items_list)

                        embed = discord.Embed(title=f"You have selected top mid or bot!",
                                              description=None,
                                              color=discord.Color.orange(),
                                              timestamp=datetime.utcnow())
                        embed.add_field(name="First Item", value=f"{randitemone}", inline=False)
                        embed.add_field(name="Second Item", value=f"{randitemtwo}", inline=False)
                        embed.add_field(name="Third Item", value=f"{randitemthree}", inline=False)
                        embed.add_field(name="Fourth Item", value=f"{randitemfour}", inline=False)
                        embed.add_field(name="Fifth Item", value=f"{randitemfive}", inline=False)
                        embed.add_field(name="Boots", value=f"{randboots}", inline=False)
                        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        await ctx.send(content=None, embed=embed)
                    elif response.content.lower() == "jungle":
                        jgitems_list = getLoLjgItemsJson()
                        randitemone = random.choice(jgitems_list)
                        items_list = getLoLItemsJson()
                        randitemtwo = None
                        randitemthree = None
                        randitemfour = None
                        randitemfive = None
                        while True:
                            desireditem = random.choice(items_list)
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

                        boots_list = getLoLBootsJson()
                        randboots = random.choice(boots_list)

                        embed = discord.Embed(title=f"You have selected jungle!",
                                              description=None,
                                              color=discord.Color.orange(),
                                              timestamp=datetime.utcnow())
                        embed.add_field(name="Jungle Item", value=f"{randitemone}", inline=False)
                        embed.add_field(name="Second Item", value=f"{randitemtwo}", inline=False)
                        embed.add_field(name="Third Item", value=f"{randitemthree}", inline=False)
                        embed.add_field(name="Fourth Item", value=f"{randitemfour}", inline=False)
                        embed.add_field(name="Fifth Item", value=f"{randitemfive}", inline=False)
                        embed.add_field(name="Boots", value=f"{randboots}", inline=False)
                        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        await ctx.send(content=None, embed=embed)
                    elif response.content.lower() == "support":
                        suppitems_list = getLoLSuppItemsJson()
                        randitemone = random.choice(suppitems_list)
                        items_list = getLoLItemsJson()
                        randitemtwo = None
                        randitemthree = None
                        randitemfour = None
                        randitemfive = None
                        while True:
                            desireditem = random.choice(items_list)
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

                        boots_list = getLoLBootsJson()
                        randboots = random.choice(boots_list)

                        embed = discord.Embed(title="You have selected support!",
                                              description=None,
                                              color=discord.Color.orange(),
                                              timestamp=datetime.utcnow())
                        embed.add_field(name="Support Item", value=f"{randitemone}", inline=False)
                        embed.add_field(name="Second Item", value=f"{randitemtwo}", inline=False)
                        embed.add_field(name="Third Item", value=f"{randitemthree}", inline=False)
                        embed.add_field(name="Fourth Item", value=f"{randitemfour}", inline=False)
                        embed.add_field(name="Fifth Item", value=f"{randitemfive}", inline=False)
                        embed.add_field(name="Boots", value=f"{randboots}", inline=False)
                        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        await ctx.send(content=None, embed=embed)
                    else:
                        await ctx.send("[LeagueCommands] Lane was not recognized, please re-run the command.")
                except asyncio.TimeoutError:
                    await ctx.send("[LeagueCommands] Bot has timed out, please re-run the command.")
            elif decider.lower() == "random" and decider2.lower() == "runes":
                runes_list = getLoLRunesJson()
                randruneprimary = random.choice(runes_list)
                randrunesecondary = random.choice(runes_list)
                while randrunesecondary == randruneprimary:
                    randrunesecondary = random.choice(runes_list)
                embed = discord.Embed(title=None,
                                      description=None,
                                      color=discord.Color.orange(),
                                      timestamp=datetime.utcnow())
                embed.add_field(name="Primary Runes", value=f"{randruneprimary}", inline=False)
                embed.add_field(name="Secondary Runes", value=f"{randrunesecondary}", inline=False)
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await ctx.send(content=None, embed=embed)

        # Tells them how to use the command properly, because they didn't use arguments.
        elif decider.lower() == "help":
            embed = discord.Embed(title="League Command Help",
                                  description="This command needs parameters to run properly!",
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name="{league champlist",
                            value="Displays a list of all the champs in the bot.",
                            inline=True)
            embed.add_field(name="{league itemlist",
                            value="Displays a list of all the items in the bot.",
                            inline=True)
            embed.add_field(name="{league runes",
                            value="Displays a list of all the runes in the bot.",
                            inline=True)
            embed.add_field(name="{league random items",
                            value="Displays a random sets of items for you to use!",
                            inline=True)
            embed.add_field(name="{league random champs",
                            value="Displays a random champion for you to use!",
                            inline=True)
            embed.add_field(name="{league random runes",
                            value="Displays a random set of runes for you to use!",
                            inline=True)
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(LeagueCommandsCog(bot))
