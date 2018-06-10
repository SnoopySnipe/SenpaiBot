import asyncio
import os

import discord

import download_youtube

from discord.ext import commands
from helpers import *

class SenpaiSong:

    def __init__(self, title, url, path):
        self.title = title
        self.url = url
        self.path = path

    def __str__(self):
        return self.title

class SenpaiSongLocal(SenpaiSong):

    def __init__(self, title, url, path, voice_channel):
        SenpaiSong.__init__(self, title, url, path)
        self.voice_channel = voice_channel

class SenpaiSongYoutube(SenpaiSong):

    def __init__(self, title, url, voice_channel):
        SenpaiSong.__init__(self, title, url, url)
        self.voice_channel = voice_channel


class SenpaiPlayer:

    def __init__(self, bot):
        self.bot = bot
        self.delay = 3
        self.client = None
        self.player_queue = []
        self.refcount_dict = {}
        self.current_player = None
        self.player_volume = 50.0
        self.voice_channel = None
        self.voice = None

    def _set_volume(self, volume):
        '''(SenpaiPlayer, float) -> None
        Sets the volume for this player in all queues
        '''
        self.player_volume = volume
        if (self.current_player):
            self.current_player.volume = self.player_volume / 50

    def _clear_queue(self):
        '''(SenpaiPlayer) -> float
        Clears the queue and local queue of this player
        '''
        self.player_queue.clear()
        self.refcount_dict.clear()

    def _add_song(self, url, voice_channel):
        song = None
        if (url in self.refcount_dict):
            song = self.refcount_dict[url][0]
            ref = self.refcount_dict[url][1]
            self.refcount_dict[url] = (song, ref+1)
        else:
            song = download_youtube.create_youtube_song(url, voice_channel)
            self.refcount_dict[url] = (song, 1)
        self.player_queue.append(song)

    def _add_song_local(self, url, voice_channel):
        song = None
        if (url in self.refcount_dict):
            song = self.refcount_dict[url][0]
            ref = self.refcount_dict[url][1]
            if (song.path == song.url):
                song = download_youtube.create_local_song(url, voice_channel)
            self.refcount_dict[url] = (song, ref+1)
        else:
            song = download_youtube.create_local_song(url, voice_channel)
            self.refcount_dict[url] = (song, 1)
        self.player_queue.append(song)
        return song

    def _deref_song(self, queue_num):
        song = None
        if (not self.player_queue):
            return

        song = self.player_queue.pop(queue_num)

        if (song.url not in self.refcount_dict):
            return

        ref = self.refcount_dict[song.url][1] - 1
        if (ref <= 0):
            self.refcount_dict.pop(song.url, None)
            if (os.path.isfile(song.path)):
                print("removing file: " + song.path)
                os.remove(song.path)
        else:
            self.refcount_dict[song.url] = (song, ref)

    async def _play(self):
        '''(SenpaiPlayer, Client, VoiceClient, Message) -> None
        Plays songs in the local queue.
        '''
        await asyncio.sleep(self.delay)
        # play songs while there are songs in the queue
        while (self.player_queue):
            # pop the next song off the queue
            song = self.player_queue[0]

            if (song.voice_channel != self.voice_channel):
                self.voice_channel = song.voice_channel
                self.voice.move_to(self.voice_channel)

            # retrieve song
            if (isinstance(song, SenpaiSongLocal)):
                player = self.voice.create_ffmpeg_player(song.path)
            elif (isinstance(song, SenpaiSongYoutube)):
                player = await self.voice.create_ytdl_player(song.path)

            # print a message showing what is currently playing
            bot_reply = ("`Playing: \"" + song.title + "\"\nPath: " + song.path + "`")
            await self.bot.say(bot_reply)

            self.current_player = player
            # set player volume
            self._set_volume(self.player_volume)
            # play the song
            player.start()
            # if the bot is no longer playing anything, stop the player and leave
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
    async def volume(self, new_volume=None):
        if (new_volume is None):
            self.bot.say("`Volume is currently at " +
                         str(self.player_volume) + "`")
            return

        try:
            # if valid volume, adjust it
            volume = float(new_volume)

            self._set_volume(volume)
            reply = ("`Volume has been adjusted to " + str(self.player_volume) + "`")

        # prompt for a valid volume if invalid
        except ValueError:
            reply = "`Please enter a volume between 0 and 100`"
        await self.bot.say(reply)

    @commands.command()
    async def skip(self):
        if (self.current_player):
            self.current_player.stop()

    @commands.command()
    async def pause(self):
        if (self.current_player):
            self.current_player.pause()

    @commands.command()
    async def resume(self):
        if (self.current_player):
            self.current_player.resume()

    @commands.command(pass_context=True)
    async def stop(self, context):
        self._clear_queue()
        await self.skip.invoke(context)

    @commands.command()
    async def queue(self):
        await self.bot.say(_queue_to_string(self.player_queue))

    @commands.command(pass_context=True)
    async def play(self, context, url):

        # bot_voice = await bot.join_voice_channel(user_voice_channel)
        # async def _join_voice_channel(bot, voice_channel
        # bot_voice = await bot.join_voice_channel(author_voice_channel)

        user_voice_channel = context.message.author.voice_channel
        if (user_voice_channel is None):
            bot_reply = ("\@" + str(message.author) +
                         ", please join a voice channel")
            self.bot.say(bot_reply)
            return

        # await self.bot.delete_message(context.message)
        download_msg = await self.bot.say("`Downloading video...`")

        song = self._add_song(url, user_voice_channel)

        await self.bot.delete_message(download_msg)

        if (self.voice_channel is None):
            self.voice_channel = user_voice_channel
            self.voice = await self.bot.join_voice_channel(self.voice_channel)
            await self._play()
        else:
            bot_reply = "`Enqueued: " + str(song) + "`"
            await self.bot.say(bot_reply)

    @commands.command(pass_context=True)
    async def playlocal(self, context, url):
        user_voice_channel = context.message.author.voice_channel
        if (user_voice_channel is None):
            bot_reply = ("\@" + str(message.author) +
                         ", please join a voice channel")
            self.bot.say(bot_reply)
            return

        # await self.bot.delete_message(context.message)
        download_msg = await self.bot.say("`Downloading video...`")

        song = self._add_song_local(url, user_voice_channel)

        await self.bot.delete_message(download_msg)

        if (self.voice_channel is None):
            self.voice_channel = user_voice_channel
            self.voice = await self.bot.join_voice_channel(self.voice_channel)
            await self._play()
        else:
            bot_reply = "`Enqueued: " + str(song) + "`"
            await self.bot.say(bot_reply)


def setup(bot):
    bot.add_cog(SenpaiPlayer(bot))


def _queue_to_string(queue : list):
    reply = "`"
    queue_size = len(queue)
    if (queue_size == 0):
        reply += "Queue is empty."
    else:
        for i in range(queue_size):
            reply += (str(i) + "." + "\t" * 4 +
                str(queue[i]) + "\n")
    reply += "`"
    return reply
