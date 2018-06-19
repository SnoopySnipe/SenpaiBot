import asyncio
import os

import senpai_song

from discord.ext import commands

class SenpaiPlayer:

    def __init__(self, bot):
        self.bot = bot
        self.delay = 3
        self.song_queue = []
        self.refcount_dict = {}
        self.current_player = None
        self.player_volume = 25.0
        self.voice_channel = None
        self.voice = None

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
        self.player_volume = volume
        if (self.current_player):
            self.current_player.volume = self.player_volume / 50

    def _add_song(self, url, voice_channel):
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

    def _add_song_local(self, url, voice_channel):
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
        player.stop()
        self._deref_song(0)

    async def _play2(self):
        if (self.song_queue):
            song = self.song_queue[0]

            # TODO: currently bot is not moving to another channel
            if (song.voice_channel != self.voice_channel):
                self.voice_channel = song.voice_channel
                self.voice.move_to(self.voice_channel)

            # TODO: bad way of handling local songs and online songs
            if (isinstance(song, senpai_song.SenpaiSongLocal)):
                player = self.voice.create_ffmpeg_player(song.path,
                                after=self.after_func)
            elif (isinstance(song, senpai_song.SenpaiSongYoutube)):
                player = await self.voice.create_ytdl_player(song.path,
                                after=self.after_func)

            self.current_player = player
            self._set_volume(self.player_volume)

            # print a message showing what is currently playing
            await self.bot.say("`Playing: \"{}\nPath: {}`".format(song.title,
                               song.path))
            player.start()

        else:
            # output message saying bot has left and leave
            await self.bot.say("`Leaving voice channel`")
            self.voice_channel = None
            await self.voice.disconnect()
            self.voice = None


    async def _play(self):
        # play songs while there are songs in the queue
        while (self.song_queue):
            # pop the next song off the queue
            song = self.song_queue[0]

            # TODO: currently bot is not moving to another channel
            if (song.voice_channel != self.voice_channel):
                self.voice_channel = song.voice_channel
                self.voice.move_to(self.voice_channel)

            # TODO: bad way of handling local songs and online songs
            if (isinstance(song, senpai_song.SenpaiSongLocal)):
                player = self.voice.create_ffmpeg_player(song.path)
            elif (isinstance(song, senpai_song.SenpaiSongYoutube)):
                player = await self.voice.create_ytdl_player(song.path)

            self.current_player = player
            self._set_volume(self.player_volume)

            # print a message showing what is currently playing
            await self.bot.say("`Playing: \"{}\nPath: {}`".format(song.title,
                               song.path))

            await player.start()

            # TODO: Fix busy waiting by making use of
            # create_ffmpeg_player(after=) and create_ytdl_player(after=)
            # or yield from (?)
            while (not player.is_done()):
                await asyncio.sleep(self.delay)
            player.stop()
            self._deref_song(0)

        # output message saying bot has left and leave
        await self.bot.say("`Leaving voice channel`")
        self.voice_channel = None
        await self.voice.disconnect()
        self.voice = None

    @commands.command()
    async def skip(self):
        if (self.current_player):
            self.current_player.stop()

    @commands.command(pass_context=True)
    async def stop(self, context):
        self._clear_queue()
        await self.skip.invoke(context)

    @commands.command()
    async def pause(self):
        if (self.current_player):
            self.current_player.pause()

    @commands.command()
    async def resume(self):
        if (self.current_player):
            self.current_player.resume()

    @commands.command()
    async def queue(self):
        await self.bot.say(_queue_to_string(self.song_queue))

    @commands.command(pass_context=True)
    async def dequeue(self, context, index=None):
        if (not self.song_queue):
            await self.bot.say("`queue is empty`")
            return

        try:
            index = int(index)
            queue_size = len(self.song_queue)
            if (index >= queue_size or index < 0):
                raise ValueError

            song = self.song_queue[index]
            self._deref_song(index)
            await self.bot.say("`removed: [{}] {}".format(index, song.title))

        except ValueError:
            reply = "`Please give an integer between 0 and {}`"
            await self.bot.say(reply.format(queue_size))

    async def _vol_command(self, new_volume):
        if (new_volume is None):
            await self.bot.say("`Volume is currently at {}%`".format(
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
        await self.bot.say(reply)

    @commands.command()
    async def volume(self, new_volume=None):
        await self._vol_command(new_volume)

    @commands.command()
    async def vol(self, new_volume=None):
        await self._vol_command(new_volume)

    @commands.command(pass_context=True)
    async def play(self, context, url=None):
        if (not url):
            await self.bot.say("usage: !senpai play youtube-link")
            return

        # bot_voice = await bot.join_voice_channel(user_voice_channel)
        # async def _join_voice_channel(bot, voice_channel
        # bot_voice = await bot.join_voice_channel(author_voice_channel)

        user_voice_channel = context.message.author.voice_channel
        if (user_voice_channel is None):
            await self.bot.say("{}, please join a voice channel".format(
                               context.message.author.mention))
            return

        # await self.bot.delete_message(context.message)
        download_msg = await self.bot.say("`Adding song...`")

        try:
            song = self._add_song(url, user_voice_channel)
        except:
            await self.bot.delete_message(download_msg)
            await self.bot.say("`Please provide a valid link`")
            return

        await self.bot.delete_message(download_msg)

        # TODO
        if (self.voice_channel is None):
            self.voice_channel = user_voice_channel
            self.voice = await self.bot.join_voice_channel(self.voice_channel)
            await self._play()
        else:
            await self.bot.say("`Enqueued: {}`".format(song.title))

    @commands.command(pass_context=True)
    async def playlocal(self, context, url=None):
        if (not url):
            await self.bot.say("usage: !senpai playlocal youtube-link")
            return

        user_voice_channel = context.message.author.voice_channel
        if (user_voice_channel is None):
            await self.bot.say("{}, please join a voice channel".format(
                               context.message.author.mention))
            return

        # await self.bot.delete_message(context.message)
        download_msg = await self.bot.say("`Downloading video...`")

        try:
            song = self._add_song_local(url, user_voice_channel)
        except:
            await self.bot.delete_message(download_msg)
            await self.bot.say("`Please provide a valid link`")
            return

        await self.bot.delete_message(download_msg)

        if (self.voice_channel is None):
            self.voice_channel = user_voice_channel
            self.voice = await self.bot.join_voice_channel(self.voice_channel)
            await self._play()
        else:
            await self.bot.say("`Enqueued: {}`".format(song.title))


def setup(bot):
    bot.add_cog(SenpaiPlayer(bot))


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
