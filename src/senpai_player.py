import asyncio
import os

import discord

import senpai_song

from discord.ext import commands

class SenpaiPlayer:

    def __init__(self):
        self.delay = 3
        self.song_queue = []
        self.refcount_dict = {}
        self.player_volume = 0.12
        self.voice_channel = None
        self.voice_client = None

    def _clear_queue(self):
        '''(SenpaiPlayer) -> None
        Clears the queue and local queue of this player
        '''
        self.song_queue.clear()
        self.refcount_dict.clear()

    def _set_volume(self, volume):
        '''(SenpaiPlayer, float) -> None
        Sets the volume for this player in all queues
        '''
        self.player_volume = volume / 100

        # TODO
        return
        if (self.voice_client and self.voice_client.source):
            self.voice_client.source.volume = self.player_volume

    def _add_song(self, url, voice_channel : discord.VoiceChannel):
        song = None
        if (url in self.refcount_dict):
            song = self.refcount_dict[url][0]
            ref = self.refcount_dict[url][1]
            self.refcount_dict[url] = (song, ref+1)
        else:
            song = senpai_song.create_youtube_song(url, voice_channel)
            self.refcount_dict[url] = (song, 1)
        self.song_queue.append(song)
        return song

    def _add_song_local(self, url, voice_channel : discord.VoiceChannel):
        song = None
        # song is already queued
        if (url in self.refcount_dict):
            song = self.refcount_dict[url][0]
            ref = self.refcount_dict[url][1]
            # queued song is online, not local, so we localize it
            if (isinstance(song, senpai_song.SenpaiSongYoutube)):
                song = senpai_song.create_local_song(url, voice_channel)
            self.refcount_dict[url] = (song, ref+1)
        else:
            song = senpai_song.create_local_song(url, voice_channel)
            self.refcount_dict[url] = (song, 1)
        self.song_queue.append(song)
        return song

    def _deref_song(self, queue_num):
        if (not self.song_queue):
            return

        song = self.song_queue.pop(queue_num)

        if (song.url not in self.refcount_dict):
            return

        ref = self.refcount_dict[song.url][1] - 1
        if (ref <= 0):
            self.refcount_dict.pop(song.url, None)
            if (os.path.isfile(song.path)):
                print("removing file: {}".format(song.path))
                os.remove(song.path)
        else:
            self.refcount_dict[song.url] = (song, ref)

    def after_func(self):
        self._deref_song(0)

    async def _play(self, context):
        # play songs while there are songs in the queue
        while (self.song_queue):
            # pop the next song off the queue
            song = self.song_queue[0]

            if (not self.voice_channel):
                self.voice_channel = song.voice_channel
                self.voice_client = await self.voice_channel.connect()
            elif (self.voice_channel != song.voice_channel):
                await self.voice_client.disconnect()
                self.voice_channel = song.voice_channel
                self.voice_client = await self.voice_channel.connect()

            # TODO: bad way of handling local songs and online songs
            if (isinstance(song, senpai_song.SenpaiSongLocal)):
                audio_src = discord.FFmpegPCMAudio(song.path)
            elif (isinstance(song, senpai_song.SenpaiSongYoutube)):
                audio_src = discord.FFmpegPCMAudio(song.path)

            # print a message showing what is currently playing
            embed_msg = discord.Embed(title="SenpaiPlayer", color=0xff93ac)
            embed_msg.add_field(name="`Playing:`", value=song.title, inline=False)
            embed_msg.add_field(name="`Path:`", value=song.path, inline=False)
            await context.send(embed=embed_msg)

            self.voice_client.play(audio_src)

            # TODO: volume does not work for testing environment
            # self.voice_client.source = discord.PCMVolumeTransformer(
            #                     self.voice_client.source, self.player_volume)

            # TODO: Fix busy waiting by making use of
            # create_ffmpeg_player(after=) and create_ytdl_player(after=)
            # or yield from (?)
            while (self.voice_client.is_playing()):
                await asyncio.sleep(self.delay)
            self.voice_client.stop()
            self._deref_song(0)

        # output message saying bot has left and leave
        await context.send("`Leaving voice channel`")
        await self.voice_client.disconnect()
        self.voice_channel = None
        self.voice_client = None

    @commands.command()
    async def skip(self, context):
        if (self.voice_client):
            self.voice_client.stop()

    @commands.command()
    async def stop(self, context):
        self._clear_queue()
        await self.skip.reinvoke(context)

    @commands.command()
    async def pause(self):
        if (self.voice_client):
            self.voice_client.pause()

    @commands.command()
    async def resume(self):
        if (self.voice_client):
            self.voice_client.resume()

    @commands.command()
    async def queue(self):
        await context.send(_queue_to_string(self.song_queue))

    @commands.command()
    async def dequeue(self, context, index=None):
        if (not self.song_queue):
            await context.send("`queue is empty`")
            return

        try:
            index = int(index)
            queue_size = len(self.song_queue)
            if (index >= queue_size or index < 0):
                raise ValueError

            song = self.song_queue[index]
            self._deref_song(index)
            await context.send("`removed: [{}] {}".format(index, song.title))

        except ValueError:
            reply = "`Please give an integer between 0 and {}`"
            await context.send(reply.format(queue_size))

    async def _vol_command(self, new_volume):
        if (new_volume is None):
            await context.send("`Volume is currently at {}%`".format(
                               str(self.player_volume)))
            return

        try:
            # if valid volume, adjust it
            volume = float(new_volume)
            if (volume < 0 or volume > 100):
                raise ValueError

            self._set_volume(volume)
            reply = "`Volume has been adjusted to {}%`".format(
                     str(self.player_volume))
        # prompt for a valid volume if invalid
        except ValueError:
            reply = "`Please enter a volume between 0 and 100`"
        await context.send(reply)

    @commands.command()
    async def volume(self, context, new_volume=None):
        await self._vol_command(new_volume)

    @commands.command()
    async def vol(self, context, new_volume=None):
        await self._vol_command(new_volume)

    @commands.command()
    async def playstream(self, context, url=None):
        if (not url):
            await context.send("`usage: !senpai playstream youtube-link`")
            return

        if (not context.message.author.voice):
            await context.send("{}, please join a voice channel".format(
                               context.message.author.mention))
            return

        download_msg = await context.send("`Adding song...`")

        user_voice_channel = context.message.author.voice.channel

        try:
            song = self._add_song(url, context.message.author.voice.channel)
        except:
            await download_msg.delete()
            await context.send("`Please provide a valid link`")
            return

        await download_msg.delete()

        if (self.voice_client):
            await context.send("`Enqueued: {}`".format(song.title))
        else:
            await self._play(context)


    @commands.command(name="play")
    async def playlocal(self, context, url=None):
        if (not url):
            await context.send("`usage: !senpai play youtube-link`")
            return

        if (not context.message.author.voice):
            await context.send("{}, please join a voice channel".format(
                               context.message.author.mention))
            return

        download_msg = await context.send("`Downloading song...`")

        try:
            song = self._add_song_local(url, context.message.author.voice.channel)
        except:
            await download_msg.delete()
            await context.send("`Please provide a valid link`")
            return

        await download_msg.delete()

        if (self.voice_client):
            await context.send("`Enqueued: {}`".format(song.title))
        else:
            await self._play(context)



def setup(bot):
    bot.add_cog(SenpaiPlayer())


def _queue_to_string(queue : list):
    reply = "`"
    queue_size = len(queue)
    if (queue_size == 0):
        reply += "Queue is empty."
    else:
        for i in range(queue_size):
            reply += "{}.\t{}\n".format(str(i), str(queue[i]))

    reply += "`"
    return reply
