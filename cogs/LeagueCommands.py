import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from utils import LeagueofLegends
from .utils.checks import isLoLEnabled


class LeagueCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_reactions(self, ctx, message, page, pagination, list_type):
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=90.0,
                                                     check=lambda r, u: u == ctx.message.author)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            return await ctx.send(f"Timed out", delete_after=10)
        else:
            if reaction.emoji == "➡":
                page += 1
                new_embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - {list_type} List",
                                          description="\n".join(pagination[page]),
                                          color=discord.Color.orange(),
                                          timestamp=datetime.utcnow())
                new_embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                new_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await message.clear_reactions()
                if page + 2 >= 1 or page + 2 == len(pagination):
                    await message.add_reaction("⬅")
                if page + 2 <= 1 or page + 2 < len(pagination):
                    await message.add_reaction("➡")
                await message.add_reaction("❌")

                await message.edit(content=None, embed=new_embed)
                await self.process_reactions(ctx, message, page, pagination, list_type)
            elif reaction.emoji == "⬅":
                page -= 1
                new_embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - Champions List",
                                          description="\n".join(pagination[page]),
                                          color=discord.Color.orange(),
                                          timestamp=datetime.utcnow())
                new_embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                new_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await message.clear_reactions()
                if page - 1 >= 1 or page - 1 == len(pagination):
                    await message.add_reaction("⬅")
                if page - 1 <= 1 or page + 1 < len(pagination):
                    await message.add_reaction("➡")
                await message.add_reaction("❌")

                await message.edit(content=None, embed=new_embed)
                await self.process_reactions(ctx, message, page, pagination, list_type)
            elif reaction.emoji == "❌":
                await message.delete()

    # Main command for the league cog, might be the only one.
    @commands.command(name="league", usage="<decider> [decider2]")
    @isLoLEnabled()
    async def league(self, ctx, decider: str, decider2: str = None):
        # Displays all the champions in the bot currently.
        if decider.lower() == "champs":
            champions = LeagueofLegends().getChampions()
            champion_names = [key for key in champions]
            pagination = [champion_names[i:i + 15] for i in range(0, len(champion_names), 15)]
            page = 0

            embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - Champion List",
                                  description="\n".join(pagination[page]),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            champion_list_message = await ctx.send(content=None, embed=embed)
            if page + 2 <= 1 or page + 2 < len(pagination):
                await champion_list_message.add_reaction("➡")
            await champion_list_message.add_reaction("❌")

            await self.process_reactions(ctx, champion_list_message, page, pagination, list_type="Champion")


        # Displays all the items in the bot currently.
        elif decider.lower() == "items":
            items = LeagueofLegends().getItems()
            item_names = [items[key]["name"] for key in items]
            pagination = [item_names[i:i + 15] for i in range(0, len(item_names), 15)]
            page = 0

            embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - Item List",
                                  description="\n".join(pagination[page]),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            item_list_message = await ctx.send(content=None, embed=embed)
            if page + 2 <= 1 or page + 2 < len(pagination):
                await item_list_message.add_reaction("➡")
            await item_list_message.add_reaction("❌")

            await self.process_reactions(ctx, item_list_message, page, pagination, list_type="Item")
        #
        # # Displays all the runes in the bot currently.
        elif decider.lower() == "runes":
            runes = LeagueofLegends().getRunes()
            rune_tier_names = [rune_tier["name"] for rune_tier in runes]
            pagination = [rune_tier_names[i:i + 15] for i in range(0, len(rune_tier_names), 15)]
            page = 0

            embed = discord.Embed(title=f"Page {page + 1} of {len(pagination)} - Rune List",
                                  description="\n".join(pagination[page]),
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            rune_list_message = await ctx.send(content=None, embed=embed)
            if page + 2 <= 1 or page + 2 < len(pagination):
                await rune_list_message.add_reaction("➡")
            await rune_list_message.add_reaction("❌")

            await self.process_reactions(ctx, rune_list_message, page, pagination, list_type="Rune")
        #
        # # Displays a random set of 6 items.
        # elif decider2 is not None:
        #     if decider.lower() == "random" and decider2.lower() == "champs":
        #         champs_list = getLoLChampsJson()
        #         randchamp = random.choice(champs_list)
        #         displayname = randchamp[list(randchamp.keys())[0]]["display_name"]
        #         titlename = randchamp[list(randchamp.keys())[0]]['title']
        #         loresnippet = randchamp[list(randchamp.keys())[0]]['lore_snippet']
        #         embed = discord.Embed(title=f"{displayname} {titlename}",
        #                               description=f"{loresnippet} \n **Goodluck with the random champion!**",
        #                               color=discord.Color.orange(),
        #                               timestamp=datetime.utcnow())
        #         embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        #         embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        #         await ctx.send(content=None, embed=embed)
        #     elif decider.lower() == "random" and decider2.lower() == "items":
        #         try:
        #             await ctx.send("What lane are you playing?")
        #             response = await self.bot.wait_for('message', timeout=20)
        #             if response.content.lower() == "top" or response.content.lower() == "mid" or response.content.lower() == "bot":
        #                 items_list = getLoLItemsJson()
        #                 randitemone = random.choice(items_list)
        #                 randitemtwo = None
        #                 randitemthree = None
        #                 randitemfour = None
        #                 randitemfive = None
        #                 while True:
        #                     desireditem = random.choice(items_list)
        #                     if randitemtwo is None:
        #                         if not desireditem == randitemone:
        #                             randitemtwo = desireditem
        #                     elif randitemthree is None:
        #                         if not desireditem == randitemone or randitemtwo:
        #                             randitemthree = desireditem
        #                     elif randitemfour is None:
        #                         if not desireditem == randitemone or randitemtwo or randitemthree:
        #                             randitemfour = desireditem
        #                     elif randitemfive is None:
        #                         if not desireditem == randitemone or randitemtwo or randitemthree or randitemfour:
        #                             randitemfive = desireditem
        #                             break
        #
        #                 items_list = getLoLBootsJson()
        #                 randboots = random.choice(items_list)
        #
        #                 embed = discord.Embed(title=f"You have selected top mid or bot!",
        #                                       description=None,
        #                                       color=discord.Color.orange(),
        #                                       timestamp=datetime.utcnow())
        #                 embed.add_field(name="First Item", value=f"{randitemone}", inline=False)
        #                 embed.add_field(name="Second Item", value=f"{randitemtwo}", inline=False)
        #                 embed.add_field(name="Third Item", value=f"{randitemthree}", inline=False)
        #                 embed.add_field(name="Fourth Item", value=f"{randitemfour}", inline=False)
        #                 embed.add_field(name="Fifth Item", value=f"{randitemfive}", inline=False)
        #                 embed.add_field(name="Boots", value=f"{randboots}", inline=False)
        #                 embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        #                 embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        #                 await ctx.send(content=None, embed=embed)
        #             elif response.content.lower() == "jungle":
        #                 jgitems_list = getLoLjgItemsJson()
        #                 randitemone = random.choice(jgitems_list)
        #                 items_list = getLoLItemsJson()
        #                 randitemtwo = None
        #                 randitemthree = None
        #                 randitemfour = None
        #                 randitemfive = None
        #                 while True:
        #                     desireditem = random.choice(items_list)
        #                     if randitemtwo is None:
        #                         if not desireditem == randitemone:
        #                             randitemtwo = desireditem
        #                     elif randitemthree is None:
        #                         if not desireditem == randitemone or randitemtwo:
        #                             randitemthree = desireditem
        #                     elif randitemfour is None:
        #                         if not desireditem == randitemone or randitemtwo or randitemthree:
        #                             randitemfour = desireditem
        #                     elif randitemfive is None:
        #                         if not desireditem == randitemone or randitemtwo or randitemthree or randitemfour:
        #                             randitemfive = desireditem
        #                             break
        #
        #                 boots_list = getLoLBootsJson()
        #                 randboots = random.choice(boots_list)
        #
        #                 embed = discord.Embed(title=f"You have selected jungle!",
        #                                       description=None,
        #                                       color=discord.Color.orange(),
        #                                       timestamp=datetime.utcnow())
        #                 embed.add_field(name="Jungle Item", value=f"{randitemone}", inline=False)
        #                 embed.add_field(name="Second Item", value=f"{randitemtwo}", inline=False)
        #                 embed.add_field(name="Third Item", value=f"{randitemthree}", inline=False)
        #                 embed.add_field(name="Fourth Item", value=f"{randitemfour}", inline=False)
        #                 embed.add_field(name="Fifth Item", value=f"{randitemfive}", inline=False)
        #                 embed.add_field(name="Boots", value=f"{randboots}", inline=False)
        #                 embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        #                 embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        #                 await ctx.send(content=None, embed=embed)
        #             elif response.content.lower() == "support":
        #                 suppitems_list = getLoLSuppItemsJson()
        #                 randitemone = random.choice(suppitems_list)
        #                 items_list = getLoLItemsJson()
        #                 randitemtwo = None
        #                 randitemthree = None
        #                 randitemfour = None
        #                 randitemfive = None
        #                 while True:
        #                     desireditem = random.choice(items_list)
        #                     if randitemtwo is None:
        #                         if not desireditem == randitemone:
        #                             randitemtwo = desireditem
        #                     elif randitemthree is None:
        #                         if not desireditem == randitemone or randitemtwo:
        #                             randitemthree = desireditem
        #                     elif randitemfour is None:
        #                         if not desireditem == randitemone or randitemtwo or randitemthree:
        #                             randitemfour = desireditem
        #                     elif randitemfive is None:
        #                         if not desireditem == randitemone or randitemtwo or randitemthree or randitemfour:
        #                             randitemfive = desireditem
        #                             break
        #
        #                 boots_list = getLoLBootsJson()
        #                 randboots = random.choice(boots_list)
        #
        #                 embed = discord.Embed(title="You have selected support!",
        #                                       description=None,
        #                                       color=discord.Color.orange(),
        #                                       timestamp=datetime.utcnow())
        #                 embed.add_field(name="Support Item", value=f"{randitemone}", inline=False)
        #                 embed.add_field(name="Second Item", value=f"{randitemtwo}", inline=False)
        #                 embed.add_field(name="Third Item", value=f"{randitemthree}", inline=False)
        #                 embed.add_field(name="Fourth Item", value=f"{randitemfour}", inline=False)
        #                 embed.add_field(name="Fifth Item", value=f"{randitemfive}", inline=False)
        #                 embed.add_field(name="Boots", value=f"{randboots}", inline=False)
        #                 embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        #                 embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        #                 await ctx.send(content=None, embed=embed)
        #             else:
        #                 await ctx.send("[LeagueCommands] Lane was not recognized, please re-run the command.")
        #         except asyncio.TimeoutError:
        #             await ctx.send("[LeagueCommands] Bot has timed out, please re-run the command.")
        #     elif decider.lower() == "random" and decider2.lower() == "runes":
        #         runes_list = getLoLRunesJson()
        #         randruneprimary = random.choice(runes_list)
        #         randrunesecondary = random.choice(runes_list)
        #         while randrunesecondary == randruneprimary:
        #             randrunesecondary = random.choice(runes_list)
        #         embed = discord.Embed(title=None,
        #                               description=None,
        #                               color=discord.Color.orange(),
        #                               timestamp=datetime.utcnow())
        #         embed.add_field(name="Primary Runes", value=f"{randruneprimary}", inline=False)
        #         embed.add_field(name="Secondary Runes", value=f"{randrunesecondary}", inline=False)
        #         embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        #         embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        #         await ctx.send(content=None, embed=embed)

        # Tells them how to use the command properly, because they didn't use arguments.
        elif decider.lower() == "help":
            embed = discord.Embed(title="League Command Help",
                                  description="This command needs parameters to run properly!",
                                  color=discord.Color.orange(),
                                  timestamp=datetime.utcnow())
            embed.add_field(name="{league champs",
                            value="Displays a list of all the champs in the bot.",
                            inline=True)
            embed.add_field(name="{league items",
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
