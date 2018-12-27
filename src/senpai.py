import sys
import signal
import discord
import asyncio
import time
from discord.ext import commands

import logging
client = discord.Client()
start = time.time()
voice_list = []
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

COMMANDS_CHANNEL_ID = 282336977418715146
DESCRIPTION = '''The senpai of the server.'''

# initialize bot
bot = commands.Bot(command_prefix="!senpai ", description=DESCRIPTION)

def signal_handler(signal, frame):
    '''(Signal, Frame) -> null
    Upon signal, stop the bot and exit the program
    '''

    print("\nLogging out bot...")
    leave_all_voice_channels(bot)
    # log out bot and close connection
    bot.logout()
    bot.close()
    print("Bot has logged out.")
    # exit program
    sys.exit(0)

def leave_all_voice_channels(bot):
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
            voice.disconnect()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def leave():
    leave_all_voice_channels(bot)
    print("Left all voice channels")

@bot.event
async def on_voice_state_update(member, before, after):
    if(after.channel != None and member.name not in voice_list):
        voice_list.append(member.name)
    elif(after.channel == None and member.name in voice_list):
        voice_list.remove(member.name)
        channel = client.get_channel(COMMANDS_CHANNEL_ID)
        if(channel is not None):
            print("Channel found")
            await channel.send('Someone left a voice channel')
        else:
            print("Channel not found")
        


@bot.event
async def on_message(message : str):
    try:
        await bot.process_commands(message)
    except commands.errors.CommandNotFound:
        await bot.say("command not supported")

modules = ["senpai_fortnite", "senpai_fortune",
           "senpai_imageboards", "senpai_player", "senpai_warframe",
           "senpai_8ball", "senpai_events", "senpai_yugioh"]

if (__name__ == "__main__"):

    # amount of arguments
    argc = len(sys.argv)
    # bot token
    token = None

    # map Ctrl+C to trigger signal_handler function
    signal.signal(signal.SIGINT, signal_handler)

    print("Logging in...")

    # parse command line arguments
    for i in range(argc):
        if (sys.argv[i] == "-t" and i < argc):
            token = sys.argv[i+1]
    if (token is None):
        print("Error: no token given")
        sys.exit(1)

    for module in modules:
        bot.load_extension(module)
    bot.run(token)


