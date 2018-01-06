import asyncio
import os

import discord

import download_youtube

from helpers import *

class UserNotInVoiceChannelException(Exception):
    '''This exception is thrown when a user is not in a voice channel'''

class SenpaiPlayerLocal:

    def __init__(self, delay=3):
        '''
        _client : Client
        _queue : list
        _refcount_dict : dict
        _player_list :
        _player_volume :
        _roundtrip_delay : int
        '''
        self._client = None
        self._queue = []
        self._refcount_dict = {}
        self._current_player = None
        self._player_volume = 50.0
        # sleep delay for bot reponse time
        self._roundtrip_delay = delay

    def get_queue(self):
        return self._queue

    async def play(self, bot, bot_voice, message):
        '''(SenpaiPlayer, Client, VoiceClient, Message) -> None
        Plays songs in the local queue.
        '''
        await asyncio.sleep(self._roundtrip_delay)
        # play songs while there are songs in the queue
        while (self._queue):
            # pop the next song off the queue
            song = self.get_song(0)

            # retrieve song
            player = bot_voice.create_ffmpeg_player(song.path)

            # print a message showing what is currently playing
            bot_reply = ("`Playing: \"" + song.title + "\"`")
            await bot.say(bot_reply)

            self._current_player = player
            # set player volume
            self.set_volume(self._player_volume)
            # play the song
            player.start()
            # if the bot is no longer playing anything, stop the player and leave
            while (not player.is_done()):
                await asyncio.sleep(self._roundtrip_delay)
            player.stop()
            self.pop_song(0)

        # output message saying bot has left and leave
        bot_reply = "`Leaving voice channel`"
        await bot.say(bot_reply)
        await bot_voice.disconnect()

    async def skip(self):
        '''(SenpaiPlayer) -> None
        Skip the current song in all queues
        '''
        if (self._current_player):
            self._current_player.stop()

    async def pause(self):
        '''(SenpaiPlayer) -> None
        Pauses all songs in all queues
        '''
        if (self._current_player):
            self._current_player.pause()

    async def resume(self):
        '''(SenpaiPlayer) -> null
        Resumes all songs in all queues
        '''
        if (self._current_player):
            self._current_player.resume()

    def get_volume(self):
        '''(SenpaiPlayer) -> float
        Returns the volume for this player
        '''
        return self._player_volume

    def set_volume(self, volume):
        '''(SenpaiPlayer, float) -> None
        Sets the volume for this player in all queues
        '''
        self._player_volume = volume
        if (self._current_player):
            self._current_player.volume = self._player_volume / 50

    def clear_queue(self):
        '''(SenpaiPlayer) -> float
        Clears the queue and local queue of this player
        '''
        self._queue.clear()
        self._refcount_dict.clear()

    def add_song(self, url):
        song = None
        if (url in self._refcount_dict):
            song = self._refcount_dict[url][0]
            ref = self._refcount_dict[url][1]
            self._refcount_dict[url] = (song, ref+1)
        else:
            song = download_youtube.download_song(url)
            if (not os.path.isfile(song.path)):
                download_youtube.download_song(url)
            self._refcount_dict[url] = (song, 1)
        self._queue.append(song)
        return song

    def get_song(self, queue_num):
        return self._queue[queue_num]

    def pop_song(self, queue_num):
        song = None
        if (not self._queue):
            return song

        song = self._queue.pop(queue_num)
        ref = self._refcount_dict[song.url][1] - 1
        if (ref <= 0):
            self._refcount_dict.pop(song.url, None)
            if (os.path.isfile(song.path)):
                print("removing file: " + song.path)
                os.remove(song.path)
        else:
            self._refcount_dict[song.url] = (song, ref)
        return song


class SenpaiPlayer:

    def __init__(self, delay=3):
        self._client = None
        # song queue, list of string
        self._queue = []

        # reference counter dictionary
        self._refcount_dict = {}

        self._current_player = None

        self._player_volume = 50.0
        # sleep delay for bot reponse time
        self._roundtrip_delay = delay

    def get_queue(self):
        return self._queue

    async def play(self, bot, bot_voice, message):
        '''(SenpaiPlayer, Client, VoiceClient, Message) -> None
        Plays songs in the queue.
        '''
        await asyncio.sleep(self._roundtrip_delay)
        # play songs while there are songs in the queue
        while (self._queue):
            # pop the next song off the queue
            song = self.get_song(0)
            # retrieve song
            player = await bot_voice.create_ytdl_player(song.path)

            # print a message showing what is currently playing
            bot_reply = ("`Playing: \"" + song.title + "\"`")
            await bot.say(bot_reply)

            self._current_player = player
            # play the song
            player.start()
            # set player volume
            self.set_volume(self._player_volume)

            # if the bot is no longer playing anything, stop the player and leave
            while (not player.is_done()):
                await asyncio.sleep(self._roundtrip_delay)
            player.stop()
            self.pop_song(0)

        # output message saying bot has left and leave
        bot_reply = "`Leaving voice channel`"
        await bot.say(bot_reply)
        await bot_voice.disconnect()

    async def skip(self):
        '''(SenpaiPlayer) -> None
        Skip the current song in all queues
        '''
        if (self._current_player):
            self._current_player.stop()

    async def pause(self):
        '''(SenpaiPlayer) -> None
        Pauses all songs in all queues
        '''
        if (self._current_player):
            self._current_player.pause()

    async def resume(self):
        '''(SenpaiPlayer) -> null
        Resumes all songs in all queues
        '''
        if (self._current_player):
            self._current_player.resume()

    def get_volume(self):
        '''(SenpaiPlayer) -> float
        Returns the volume for this player
        '''
        return self._player_volume

    def set_volume(self, volume):
        '''(SenpaiPlayer, float) -> None
        Sets the volume for this player in all queues
        '''
        self._player_volume = volume
        if (self._current_player):
            self._current_player.volume = self._player_volume / 50

    def clear_queue(self):
        '''(SenpaiPlayer) -> float
        Clears the queue and local queue of this player
        '''
        self._queue.clear()
        self._refcount_dict.clear()

    def add_song(self, url):
        '''(SenpaiPlayer, String) -> None
        Add a song to the queue
        '''
        song = None
        if (url in self._refcount_dict):
            song = self._refcount_dict[url][0]
            ref = self._refcount_dict[url][1]
            self._refcount_dict[url] = (song, ref+1)
        else:
            song = download_youtube.get_song_info(url)
            self._refcount_dict[url] = (song, 1)
        self._queue.append(song)

        return song

    def get_song(self, queue_num):
        return self._queue[queue_num]

    def pop_song(self, queue_num):
        song = None
        if (not self._queue):
            return song

        song = self._queue.pop(queue_num)
        ref = self._refcount_dict[song.url][1] - 1
        if (ref <= 0):
            self._refcount_dict.pop(song.url, None)
        else:
            self._refcount_dict[song.url] = (song, ref)

        return song

