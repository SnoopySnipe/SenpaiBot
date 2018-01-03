import asyncio

import discord

class UserNotInVoiceChannelException(Exception):
    '''This exception is thrown when a user is not in a voice channel'''

class SenpaiPlayer:

    def __init__(self, delay=3):
        self._client = None
        # song queue, list of string
        self._queue = []
        # local song queue, list of SenpaiSong
        self._local_queue = []
        # list of players
        self._player_list = []
        self._player_volume = 50.0
        # sleep delay for bot reponse time
        self._roundtrip_delay = delay

    async def leave_all_voice_channels(self, bot):
        '''(SenpaiPlayer, Client) -> None
        makes the Client leave all connected voice channels
        '''

        connected_voices = []
        # get a list of all voice channels the bot is connected to
        for voice in bot.voice_clients:
            # if bot is connected to the channel, add it to the list
            if (voice.is_connected()):
                connected_voices.append(voice)
        # if bot is not connected to any voice channel, print error message
        if (connected_voices):
            # disconnect bot from all connected voice channels
            for voice in connected_voices:
                await voice.disconnect()

    async def join_voice_channel_of_user(self, message, bot):
        '''(SenpaiPlayer, Message, Client) -> VoiceClient
        given the message of a user, join their voice channel if they are in one
        '''

        bot_voice = None
        # get the sender of the message
        author = message.author
        # get their current voice channel
        cur_author_vchannel = author.voice.voice_channel
        # if they are in a voice channel, join it
        if (cur_author_vchannel):
            bot_voice = await bot.join_voice_channel(cur_author_vchannel)
        else:
            raise UserNotInVoiceChannelException(author +
                " is not in a voice channel")

        return bot_voice

    async def play_song(self, bot, bot_voice, message):
        '''(SenpaiPlayer, Client, VoiceClient, Message) -> None
        Plays songs in the queue.
        '''
        await asyncio.sleep(self._roundtrip_delay)
        # play songs while there are songs in the queue
        while (self._queue):
            # pop the next song off the queue
            song = self._queue.pop(0)
            # retrieve song
            player = await bot_voice.create_ytdl_player(song.path)
            song.title = player.title
            # play the song
            player.start()
            # set player volume
            self.player_set_volume(self._player_volume)
            self._player_list.append(player)

            # print a message showing what is currently playing
            reply = ("`Playing: \"" + song.title + "\"`")
            await bot.send_message(message.channel, reply)
            # if the bot is no longer playing anything, stop the player and leave
            while (not player.is_done()):
                await asyncio.sleep(self._roundtrip_delay)
            player.stop()
            self._player_list.pop()
        # output message saying bot has left and leave
        reply = "`Leaving voice channel.`"
        await bot.send_message(message.channel, reply)
        await self.leave_all_voice_channels(bot)

    async def play_song_local(self, bot, bot_voice, message):
        '''(SenpaiPlayer, Client, VoiceClient, Message) -> None
        Plays songs in the local queue.
        '''
        await asyncio.sleep(self._roundtrip_delay)
        # play songs while there are songs in the queue
        while (self._local_queue):
            # pop the next song off the queue
            song = self._local_queue[0]

            # retrieve song
            player = bot_voice.create_ffmpeg_player(song.path)
            # set player volume
            self.player_set_volume(self._player_volume)
            # play the song
            player.start()
            # add player to list of playing players
            self._player_list.append(player)
            # print a message showing what is currently playing
            reply = ("`Playing: \"" + song.title + "\"`")
            await bot.send_message(message.channel, reply)
            # if the bot is no longer playing anything, stop the player and leave
            while (not player.is_done()):
                await asyncio.sleep(self._roundtrip_delay)
            player.stop()
            song.delete_local()
            self._player_list.pop()
            self._local_queue.pop(0)
        # output message saying bot has left and leave
        reply = "`Leaving voice channel.`"
        await bot.send_message(message.channel, reply)
        await self.leave_all_voice_channels(bot)

    async def player_skip(self):
        '''(SenpaiPlayer) -> None
        Skip the current song in all queues
        '''
        for player in self._player_list:
            player.stop()

    async def player_pause(self):
        '''(SenpaiPlayer) -> None
        Pauses all songs in all queues
        '''
        for player in self._player_list:
            player.pause()

    async def player_resume(self):
        '''(SenpaiPlayer) -> null
        Resumes all songs in all queues
        '''
        for player in self._player_list:
            player.resume()

    def player_get_volume(self):
        '''(SenpaiPlayer) -> float
        Returns the volume for this player
        '''
        return self._player_volume

    def player_clear(self):
        '''(SenpaiPlayer) -> float
        Clears the queue and local queue of this player
        '''
        self._queue.clear()
        self._local_queue.clear()

    def player_set_volume(self, volume):
        '''(SenpaiPlayer, float) -> None
        Sets the volume for this player in all queues
        '''
        for player in self._player_list:
            player.volume = volume / 50

    def add_song(self, song):
        '''(SenpaiPlayer, String) -> None
        Add a song to the queue
        '''
        self._queue.append(song)

    def add_song_local(self, song):
        self._local_queue.append(song)

    def get_queue(self):
        return self._queue

    def get_localqueue(self):
        return self._local_queue

