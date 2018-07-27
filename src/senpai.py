import sys
import signal
import asyncio

from discord.ext import commands

from helpers import *

import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

DESCRIPTION = '''The senpai of the server.'''

# initialize bot
bot = commands.Bot(command_prefix="!senpai ", description=DESCRIPTION)

# keep track of volume
#global_volume = 1

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

@bot.command(pass_context=True)
async def clean_yourself(context, lim):

    def is_bot(message):
        return message.author == bot.user

    channel = context.message.channel
    lim = int(lim)

    deleted = await bot.purge_from(channel, limit=lim, check=is_bot)
    await bot.say("Deleted {} message(s)".format(len(deleted)))

@bot.command()
async def leave():
    leave_all_voice_channels(bot)
    print("Left all voice channels")


@bot.event
async def on_message(message : str):
    try:
        await bot.process_commands(message)
    except commands.errors.CommandNotFound:
        await bot.say("command not supported")

modules = ["senpai_fortnite", "senpai_fortune",
           "senpai_imageboards", "senpai_player", "senpai_warframe",
           "senpai_8ball"]

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



