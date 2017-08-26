import asyncio

import discord

# song queue
queue = []
# players
player_list = []

local_queue = []

player_volume = 50.0

roundtrip_delay = 4

async def join_voice_channel_of_user(message, bot):
    '''(Message) -> VoiceClient
    given the message of a user, join their voice channel if they are in one
    '''

    bot_voice = False
    # get the sender of the messge
    author = message.author
    # get their current voice channel
    cur_author_vchannel = author.voice.voice_channel
    # if they are in a voice channel, join it
    if (cur_author_vchannel):
        bot_voice = await bot.join_voice_channel(cur_author_vchannel)
    return bot_voice


async def leave_all_voice_channels(bot):
    '''(Client) -> null
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

async def play_song(bot, bot_voice, message):
    '''(VoiceClient, Message) -> null
    Plays songs in the queue.
    '''
    await asyncio.sleep(roundtrip_delay)
    # play songs while there are songs in the queue
    while (queue):
        # pop the next song off the queue
        url = queue.pop(0)
        # retrieve song
        player = await bot_voice.create_ytdl_player(url)
        # play the song
        player.start()
        player_list.append(player)
        await player_set_volume(player_volume)
        # print a message showing what is currently playing
        reply = ("`Playing: \"" + player.title + "\"`")
        await bot.send_message(message.channel, reply)
        # if the bot is no longer playing anything, stop the player and leave
        while (not player.is_done()):
            await asyncio.sleep(roundtrip_delay)
        player.stop()
        player_list.pop()
    # output message saying bot has left and leave
    reply = "`Leaving voice channel.`"
    await bot.send_message(message.channel, reply)
    await leave_all_voice_channels(bot)

async def play_local_song(bot, bot_voice, message):
    '''(VoiceClient, Message) -> null
    Plays songs in the queue.
    '''
    await asyncio.sleep(roundtrip_delay)
    # play songs while there are songs in the queue
    while (local_queue):
        # pop the next song off the queue
        song = local_queue[0]

        # retrieve song
        player = bot_voice.create_ffmpeg_player(song.file_path)
        # set volume
        await player_set_volume(player_volume)
        # play the song
        player.start()
        # add player to list of playing players
        player_list.append(player)
        # print a message showing what is currently playing
        reply = ("`Playing: \"" + song.title + "\"`")
        await bot.send_message(message.channel, reply)
        # if the bot is no longer playing anything, stop the player and leave
        while (not player.is_done()):
            await asyncio.sleep(roundtrip_delay)
        player.stop()
        song.delete_local()
        player_list.pop()
        local_queue.pop(0)
    # output message saying bot has left and leave
    reply = "`Leaving voice channel.`"
    await bot.send_message(message.channel, reply)
    await leave_all_voice_channels(bot)


async def player_skip():
    '''(null) -> null
    Skips the next song in queue.
    '''
    for player in player_list:
        player.stop()

async def player_pause():
    for player in player_list:
        player.pause()

async def player_resume():
    for player in player_list:
        player.resume()

def player_get_volume():
    return player_volume

async def player_set_volume(volume):
    for player in player_list:
        player.volume = volume / 50

