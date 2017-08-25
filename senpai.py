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
# 
player_list = []

def signal_handler(signal, frame):
    '''(Signal, Frame) -> null
    Upon signal, stop the bot and exit the program
    '''

    print("\nLogging out bot...")
    while (queue):
        queue.pop()
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
    while (queue):
        url = queue.pop(0)
        player = await bot_voice.create_ytdl_player(url)
        player.start()
        player_list.append(player)
        reply = ("`Playing: \"" + player.title + "\"`")
        await bot.send_message(message.channel, reply)
        while (player.is_playing()):
            await asyncio.sleep(3)
        player.stop()
        player_list.pop()
    await leave_all_voice_channels(bot)

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


    # make bot join the voice channel the user is currently in
    elif (message_content == "!join"):
        await join_voice_channel_of_user(message)


    # disconnect bot from all connected voice channels
    elif (message_content == "!leave"):
        await leave_all_voice_channels(bot)


    # Help menu for commands
    elif (message_content == "!help"):
        reply = ("```" +
                 "!8ball <question> " + "\t" * 4 + "Senpai knows all...\n" +
                 "!join " + "\t" * 7 + "Joins the voice channel of sender\n" +
                 "!leave" + "\t" * 7 + "Leaves the voice channel\n" +
                 "!play <youtube url>" + "\t" * 4 + 
                 "Plays a video on YouTube\n" +
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
        if (bot_voice):
            # check if it is a valid url
            if (url.startswith("http")):
                queue.append(url)
                if (not already_connected):
                    await play_video(bot_voice, message)
                else:
                    reply = "enqueued."
                    await bot.send_message(message.channel, reply)

            elif (url == "skip"):
                for player in player_list:
                    player.stop()

        elif (not bot_voice):
            reply = ("\@" + str(author) +
                    ", please join a voice channel to play music")
            await bot.send_message(message.channel, reply)
        else:
            reply = ("`Kouhai, dou shita no?`")
            await bot.send_message(message.channel, reply)


# @bot.command()
# async def fortune(question : str):
    # reply = "`" + answers[random.randint(0, num_answers)] + "`"
    # await bot.say(reply)

bot.run(token)
