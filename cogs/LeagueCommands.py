import discord
import json
from discord.ext import commands


class LeagueCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Main command for the league cog, might be the only one.
    @commands.command(name="league")
    async def league(self, ctx, decider: str, decider2: str = None):
        # Displays all the champions in the bot currently.
        if decider.lower() == "champlist":
            file = open("LoLChamps.json", 'r')
            contents = file.read()
            json_contents = json.loads(contents)
            embed = discord.Embed(title="Champions List",
                                  description=', '.join(json_contents),
                                  color=discord.Color.orange())
            await ctx.send(content=None, embed=embed)

        # Displays all the items in the bot currently.
        elif decider.lower() == "itemlist":
            file = open("LoLItems.json", 'r')
            contents = file.read()
            json_contents = json.loads(contents)
            embed = discord.Embed(title="Items List",
                                  description=', '.join(json_contents),
                                  color=discord.Color.orange())
            await ctx.send(content=None, embed=embed)

        # Displays all the runes in the bot currently.
        elif decider.lower() == "runes":
            file = open("LoLRunes.json", 'r')
            contents = file.read()
            json_contents = json.loads(contents)
            embed = discord.Embed(title="Runes List",
                                  description=', '.join(json_contents),
                                  color=discord.Color.orange())
            await ctx.send(content=None, embed=embed)

        # Displays a random set of 6 items.
        elif decider.lower() == "rand" or decider.lower() == "random" and decider2.lower() == "items":
            await ctx.send("random items!")

        # Displays a random champion for them to play.
        elif decider.lower() == "rand" or decider.lower() == "random" and decider2.lower() == "champs":
            await ctx.send("random champ!")

        # Displays a random set of runes for them to use.
        elif decider.lower() == "rand" or decider.lower() == "random" and decider2.lower() == "runes":
            await ctx.send("random runes")

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
