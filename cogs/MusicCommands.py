import asyncio
import itertools

import discord
from discord.ext import commands

from utils import YTDLSource, MusicPlayer, getLogger
from .utils.checks import isMusicEnabled


class MusicCog(commands.Cog):
    """Commands for Music Module"""
    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            for entry in self.players[guild.id].queue._queue:
                if isinstance(entry, YTDLSource):
                    entry.cleanup()
            self.players[guild.id].queue._queue.clear()
        except KeyError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name="music_connect", aliases=["music_join"])
    @commands.guild_only()
    @isMusicEnabled()
    async def connect(self, ctx, *, channel: discord.VoiceChannel = None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send("Invalid voice channel!")
        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                return await ctx.send(f"Connecting to channel <{channel}> timed out.")
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                return await ctx.send(f"Connecting to channel <{channel}> timed out.")
        await ctx.send(f"Connected to: **{channel}**", delete_after=20)

    @commands.command(name="music_play")
    @commands.guild_only()
    @isMusicEnabled()
    async def play(self, ctx, *, search: str):
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        async with ctx.typing():
            source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        if isinstance(source, list):
            # list of entryies (aka playlist)
            for entry in source:
                await player.queue.put(entry)

        await player.queue.put(source)

    @commands.command(name="music_pause")
    @commands.guild_only()
    @isMusicEnabled()
    async def pause(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send(f"Nothing is playing!", delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f"Paused")

    @commands.command(name="music_resume")
    @commands.guild_only()
    @isMusicEnabled()
    async def resume(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f"Nothing is playing!", delete_after=20)
        elif vc.is_paused():
            return

        vc.resume()
        await ctx.send(f"Resumed")

    @commands.command(name="music_skip")
    @commands.guild_only()
    @isMusicEnabled()
    async def skip(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send(f"Nothing is playing!", delete_after=20)
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f"Skipped")

    @commands.command(name="music_queue", aliases=["music_playlist", "music_q"])
    @commands.guild_only()
    @isMusicEnabled()
    async def queue_info(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            await ctx.send(f"Not connect to a voice channel!", delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send(f"Queue is empty")

        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = "\n".join(f"**`{_['title']}`**" for _ in upcoming)
        embed = discord.Embed(title=f"Upcoming - Next {len(upcoming)}", description=fmt)
        await ctx.send(embed=embed)

    @commands.command(name="music_nowplaying", aliases=["music_np", "music_playing"])
    @commands.guild_only()
    @isMusicEnabled()
    async def now_playing(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f"Not connected to voice channel!", delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send("Nothing is playing")

        try:
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(f"**Now Playing:** `{vc.source.title}`\nRequested by: `{vc.source.requester}`")

    @commands.command(name="music_volume", aliases=["music_v"])
    @commands.guild_only()
    @isMusicEnabled()
    async def volume(self, ctx, *, vol: float):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f"Not connected to voice channel!", delete_after=20)

        if not 0 < vol < 101:
            return await ctx.send(f"Please enter a value between 1 and 100")

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f"Set volume to **{vol}%**")

    @commands.command(name="music_stop", aliases=["music_s"])
    @commands.guild_only()
    @isMusicEnabled()
    async def stop(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f"Not connected to voice channel!", delete_after=20)

        await self.cleanup(ctx.guild)

    @commands.command(name="tacticalnuke")
    @commands.guild_only()
    @isMusicEnabled()
    async def tactical_nuke(self, ctx):
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect)
        player = self.get_player(ctx)
        source = await YTDLSource.create_source(ctx,
                                                "https://cdn.discordapp.com/attachments/645773103296675880/652321635512352768/Modern_Warfare_2_-_Tactical_Nuke_Sound.weba",
                                                loop=self.bot.loop, download=False)
        await player.queue.put(source)


def setup(bot):
    bot.add_cog(MusicCog(bot))
