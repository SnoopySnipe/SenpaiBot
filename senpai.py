import sys
import signal
import asyncio

import discord
from discord.ext import commands
import random

from bot_answers import *

description = '''The senpai of the server.'''

# amount of arguments
argc = len(sys.argv)
# bot token
token = ""
# parse command line arguments
for i in range(argc):
    if (sys.argv[i] == "-t" and i < argc):
        token = sys.argv[i+1]

# initialize bot
bot = commands.Bot(command_prefix='!', description=description)
# song queue
queue = []
# players
player_list = []

# keep track of volume
#global_volume = 1

def signal_handler(signal, frame):
    '''(Signal, Frame) -> null
    Upon signal, stop the bot and exit the program
    '''
    
    print("\nLogging out bot...")
    queue.clear()
    player_skip()
    # log out bot and close connection
    bot.logout()
    bot.close()
    print("Bot has logged out.")
    # exit program
    sys.exit(0)

# map Ctrl+C to trigger signal_handler function
signal.signal(signal.SIGINT, signal_handler)


async def join_voice_channel_of_user(message):
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


async def play_video(bot_voice, message):
    '''(VoiceClient, Message) -> null
    Plays songs in the queue.
    '''    
    # play songs while there are songs in the queue
    while (queue):
        # pop the next song off the queue
        url = queue.pop(0)
        # play the song
        player = await bot_voice.create_ytdl_player(url)
        # adjust the volume
        #player.volume = global_volume
        player.start()
        player_list.append(player)
        # print a message showing what is currently playing
        reply = ("`Playing: \"" + player.title + "\"`")
        await bot.send_message(message.channel, reply)
        # if the bot is no longer playing anything, stop the player and leave
        while (not player.is_done()):
            await asyncio.sleep(3)
        player.stop()
        player_list.pop()
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


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_message(message):
    message_content = message.content

    # Answers question with a yes or no
    if (message_content.startswith("!8ball")):
        reply = ("`Kouhai, dou shita no?`")

        offset = len("!8ball")
        question = message_content[offset+1:]

        # check if user actually asked a question
        if len(question) > 0:
            reply = ("`Question: " + question + "\n" +
                     "Answer: " + answers[random.randint(0, num_answers)] + "`")

        await bot.send_message(message.channel, reply)
        
    # Coinflip
    elif (message_content == "!coin"):
        flip = random.randint(0,1)
        if flip == 0:
            reply = "`Tails.`"
        elif flip == 1:
            reply = "`Heads.`"
        await bot.send_message(message.channel, reply)
            


    # Help menu for commands
    elif (message_content == "!help"):
        reply = ("```" +
                 "!8ball <question> " + "\t" * 4 + "Senpai knows all...\n" +
                 "!coin " + "\t" * 7 + "Flips a coin\n" +
                 "!play " + "\t" * 7 + "Plays YouTube videos\n" +
                 "```")
        await bot.send_message(message.channel, reply)
      
    # display a help menu for the play command  
    elif (message_content == "!play"):
        reply = ("```" +
                 "!play <url> " + "\t" * 4 + "Play the YouTube URL\n" +
                 "!play skip  " + "\t" * 4 + "Skip to the next song in the queue\n" +
                 "!play stop  " + "\t" * 4 + "Empties the song queue\n" +
                 "!play queue " + "\t" * 4 + "Display the song queue\n" +
                 "!play pause " + "\t" * 4 + "Pause the music\n" +
                 "!play resume" + "\t" * 4 + "Resume the music\n" +
                 "!play volume <volume>" + "\t" + "   Adjust the volume from 0 to 100\n" +
                 "```") 
        await bot.send_message(message.channel, reply)        

    # start playing youtube
    elif (message_content.startswith("!play")):
        offset = len("!play")
        url = message_content[offset+1:]

        already_connected = False
        bot_voice = False
        # check if bot is already connected.
        for voice in bot.voice_clients:
            if (voice.is_connected()):
                already_connected = True
                bot_voice = voice
                break

        # if bot is not already connected,
        # then connect them to voice channel
        if (not bot_voice):
            bot_voice = await join_voice_channel_of_user(message)
        # if bot is connected
        if (bot_voice):
            # check if it is a valid url
            if (url.startswith("http")):
                # add the url to the queue
                queue.append(url)
                # if the bot wasn't already connected, join voice channel
                # and play the video
                if (not already_connected):
                    await play_video(bot_voice, message)
                # if the bot was already connected, just print a message saying
                # that the song was queued
                else:
                    reply = "`Enqueued.`"
                    await bot.send_message(message.channel, reply)
            
            # skip to the next song in queue
            elif (url == "skip"):
                await player_skip()
                
            # clear the queue and skip
            elif (url == "stop"):
                queue.clear()
                await player_skip()
                
            # display the song queue
            elif (url == "queue"):
                reply = "`"
                if len(queue) == 0:
                    reply = "`Queue is empty.`"
                else:
                    for i in range(len(queue)):
                        if i != 0:
                            reply += "\n"
                        reply += str(i) + "\t" * 4 + queue[i]
                    reply += "`"
                await bot.send_message(message.channel, reply)
                
            # pause the music
            elif (url == "pause"):
                for player in player_list:
                    player.pause()
                    
            # resume the music
            elif (url == "resume"):
                for player in player_list:
                    player.resume()
            
            # adjust the music volume
            elif (url.startswith("volume")):
                volume_offset = len("volume")
                volume = url[volume_offset+1 : ]
                # display current volume
                if volume == "":
                    for player in player_list:
                        vol = player.volume
                    reply = "`Volume is currently at " + str(vol * 50) + ".`"
                # if valid volume, adjust it right now and globally
                elif (float(volume) >= 0 and float(volume) <= 100):
                    for player in player_list:
                        player.volume = float(volume) / 50
                    # adjust the global volume
                    #global_volume = float(volume) / 50
                    reply = "`Volume has been adjusted to " + str(volume) + ".`"
                # prompt for a valid volume if invalid
                else:
                    reply = "`Please enter a volume between 0 and 100.`"
                await bot.send_message(message.channel, reply)                
            
            # search for a song
            #else:

        # if the user is not connected to a voice channel, print an error msg
        elif (not bot_voice):
            reply = ("\@" + str(author) +
                    ", please join a voice channel to play music")
            await bot.send_message(message.channel, reply)
        # if something horrible goes wrong
        else:
            reply = ("`Kouhai, dou shita no?`")
            await bot.send_message(message.channel, reply)

bot.run(token)
