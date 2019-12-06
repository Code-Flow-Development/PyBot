import discord
from discord.ext import commands
from utils import YTDLSource
from .utils.checks import isMusicEnabled


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player = None

    @commands.command(name="music_join")
    @commands.guild_only()
    @isMusicEnabled()
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        if channel is None and ctx.author.voice is not None:
            channel = ctx.author.voice.channel

        if channel is None:
            return await ctx.send(f"You are not in a voice channel and you didn't specify a channel to join!")

        await channel.connect()
        await ctx.send(f"Bot has joined the channel!")

    @commands.command(name="music_play")
    @commands.guild_only()
    @isMusicEnabled()
    async def play(self, ctx, *, url):
        try:
            warn_msg = await ctx.send(f"The file must download first, please wait...")
            async with ctx.typing():
                self.player = await YTDLSource.from_url_play(url, loop=self.bot.loop)
                if self.player is not None:
                    ctx.voice_client.play(self.player, after=lambda e: print(f'Player error: {e}') if e else None)
                    await warn_msg.delete()
                else:
                    await warn_msg.delete()
                    return await ctx.send(f"File is too large to play! Use stream instead!")
            await ctx.send(f"Now playing: ``{self.player.title}``")
        except Exception as e:
            await ctx.send(f"An error occurred! Error: ```{e}```")

    @commands.command(name="tacticalnuke")
    @commands.guild_only()
    @isMusicEnabled()
    async def tactical_nuke(self, ctx):
        try:
            async with ctx.typing():
                player = await YTDLSource.from_url_stream("https://cdn.discordapp.com/attachments/645773103296675880/652321635512352768/Modern_Warfare_2_-_Tactical_Nuke_Sound.weba", loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e1: print(f"Player error: {e1}") if e1 else None)
            await ctx.send(f"Now streaming: ``{player.title}``")
        except Exception as e:
            await ctx.send(f"An error occurred! Error: ```{e}```")

    @commands.command(name="music_stream")
    @commands.guild_only()
    @isMusicEnabled()
    async def stream(self, ctx, *, url):
        try:
            async with ctx.typing():
                player = await YTDLSource.from_url_stream(url, loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print(f"Player error: {e}") if e else None)
            await ctx.send(f"Now streaming: ``{player.title}``")
        except Exception as e:
            await ctx.send(f"An error occurred! Error: ```{e}```")

    @commands.command(name="music_volume")
    @commands.guild_only()
    @isMusicEnabled()
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}")

    @commands.command(name="music_stop")
    @commands.guild_only()
    @isMusicEnabled()
    async def stop(self, ctx: discord.ext.commands.Context):
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        if self.player and self.player.filename:
            YTDLSource.cleanup_file(self.player.filename)
        await ctx.send("Music stopped!")

    @commands.command(name="music_pause")
    @commands.guild_only()
    @isMusicEnabled()
    async def pause(self, ctx: discord.ext.commands.Context):
        ctx.voice_client.pause()
        await ctx.send("Music paused! Use ``{music_resume`` to resume it!")

    @commands.command(name="music_resume")
    @commands.guild_only()
    @isMusicEnabled()
    async def resume(self, ctx: discord.ext.commands.Context):
        ctx.voice_client.resume()
        await ctx.send(f"Music resumed!")

    @play.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


def setup(bot):
    bot.add_cog(MusicCog(bot))
