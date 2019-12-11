import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands

from utils import LeagueAPI, getLogger
from .utils.checks import isLoLEnabled


class LeagueCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boots_list = [
            "Boots of Swiftness",
            "Boots of Mobility",
            "Ionian Boots of Lucidity",
            "Berserker's Greaves",
            "Sorcerer's Shoes",
            "Ninja Tabi",
            "Mercury's Treads"
        ]
        self.supp_items = [
            "Spelltheif's Edge",
            "Steel Shoulderguards",
            "Relic Shield",
            "Spectral Sickle"
        ]
        self.jungle_items = [
            "Blue Smite: Warrior",
            "Blue Smite: Cinderhulk",
            "Blue Smite: Runic Echoes",
            "Blue Smite: Bloodrazor",
            "Red Smite: Warrior",
            "Red Smite: Cinderhulk",
            "Red Smite: Runic Echoes",
            "Red Smite: Bloodrazor"
        ]

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
            champions = LeagueAPI().getChampions()
            champion_names = [champions["keys"][key] for key in champions["keys"]]
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
            items = LeagueAPI().getItems()
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
            runes = LeagueAPI().getRunes()
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

        # # Displays a random set of 6 items.
        elif decider2 is not None:
            if decider.lower() == "random" and decider2.lower() == "champs":
                champions = LeagueAPI().getChampions()
                champion_names = [champions["keys"][key] for key in champions["keys"]]
                random_champion = champions["data"][random.choice(champion_names)]
                name = random_champion["name"]
                title = random_champion["title"]
                lore = random_champion["lore"]

                embed = discord.Embed(title=f"{name} - {title}",
                                      description=f"{lore}",
                                      color=discord.Color.orange(),
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                embed.set_thumbnail(url=LeagueAPI().getChampionAvatarURL(name))
                await ctx.send(content=None, embed=embed)

            elif decider.lower() == "random" and decider2.lower() == "items":
                await ctx.send("What lane are you playing?")
                try:
                    response = await self.bot.wait_for('message', timeout=20)
                except asyncio.TimeoutError:
                    await ctx.send("[LeagueCommands] Timed out, please re-run the command.")
                else:
                    content = response.content.lower()
                    if content == "top" or content == "mid" or content == "bot":
                        items = LeagueAPI().getItems()["data"]
                        item_names = [items[key]["name"] for key in items]
                        random_items = [random.choice(item_names)]

                        # there are only five random items so we loop 5 times
                        for x in range(0, 5):
                            getLogger().debug(
                                f"Length of random_items is: {len(random_items)}; We are on iteration number: {x}")
                            desired_item = random.choice(item_names)
                            if not len(random_items) == 5 and desired_item not in random_items:
                                random_items.append(desired_item)
                                print(random_items)

                        random_boots = random.choice(self.boots_list)

                        embed = discord.Embed(title=f"You have selected top, mid, or bot!",
                                              description=None,
                                              color=discord.Color.orange(),
                                              timestamp=datetime.utcnow())
                        embed.add_field(name="First Item", value=f"{random_items[0]}", inline=False)
                        embed.add_field(name="Second Item", value=f"{random_items[1]}", inline=False)
                        embed.add_field(name="Third Item", value=f"{random_items[2]}", inline=False)
                        embed.add_field(name="Fourth Item", value=f"{random_items[3]}", inline=False)
                        embed.add_field(name="Fifth Item", value=f"{random_items[4]}", inline=False)
                        embed.add_field(name="Boots", value=f"{random_boots}", inline=False)
                        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        await ctx.send(content=None, embed=embed)

                    elif content == "jungle":
                        items = LeagueAPI().getItems()["data"]
                        item_names = [items[key]["name"] for key in items]

                        random_items = [random.choice(self.jungle_items)]

                        # there are only five random items so we loop 5 times
                        for x in range(0, 5):
                            desired_item = random.choice(item_names)
                            if not len(random_items) == x and desired_item not in random_items:
                                random_items.append(desired_item)

                        random_boots = random.choice(self.boots_list)

                        embed = discord.Embed(title=f"You have selected jungle!",
                                              description=None,
                                              color=discord.Color.orange(),
                                              timestamp=datetime.utcnow())
                        embed.add_field(name="Jungle Item", value=f"{random_items[0]}", inline=False)
                        embed.add_field(name="Second Item", value=f"{random_items[1]}", inline=False)
                        embed.add_field(name="Third Item", value=f"{random_items[2]}", inline=False)
                        embed.add_field(name="Fourth Item", value=f"{random_items[3]}", inline=False)
                        embed.add_field(name="Fifth Item", value=f"{random_items[4]}", inline=False)
                        embed.add_field(name="Boots", value=f"{random_boots}", inline=False)
                        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        await ctx.send(content=None, embed=embed)
                    elif response.content.lower() == "support":
                        items = LeagueAPI().getItems()["data"]
                        item_names = [items[key]["name"] for key in items]

                        random_items = [random.choice(self.supp_items)]

                        # there are only five random items so we loop 5 times
                        for x in range(0, 5):
                            desired_item = random.choice(item_names)
                            if not len(random_items) == x and desired_item not in random_items:
                                random_items.append(desired_item)

                        random_boots = random.choice(self.boots_list)

                        embed = discord.Embed(title="You have selected support!",
                                              description=None,
                                              color=discord.Color.orange(),
                                              timestamp=datetime.utcnow())
                        embed.add_field(name="Support Item", value=f"{random_items[0]}", inline=False)
                        embed.add_field(name="Second Item", value=f"{random_items[1]}", inline=False)
                        embed.add_field(name="Third Item", value=f"{random_items[2]}", inline=False)
                        embed.add_field(name="Fourth Item", value=f"{random_items[3]}", inline=False)
                        embed.add_field(name="Fifth Item", value=f"{random_items[4]}", inline=False)
                        embed.add_field(name="Boots", value=f"{random_boots}", inline=False)
                        embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        await ctx.send(content=None, embed=embed)
                    else:
                        await ctx.send("[LeagueCommands] Lane was not recognized, please re-run the command.")

            elif decider.lower() == "random" and decider2.lower() == "runes":
                runes = LeagueAPI().getRunes()
                rune_tier_names = [rune_tier["name"] for rune_tier in runes]
                random_runes = [random.choice(rune_tier_names), random.choice(rune_tier_names)]
                while random_runes[0] == random_runes[1]:
                    random_runes[1] = random.choice(rune_tier_names)

                embed = discord.Embed(title=None,
                                      description=None,
                                      color=discord.Color.orange(),
                                      timestamp=datetime.utcnow())
                embed.add_field(name="Primary Runes", value=f"{random_runes[0]}", inline=False)
                embed.add_field(name="Secondary Runes", value=f"{random_runes[1]}", inline=False)
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                await ctx.send(content=None, embed=embed)

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
