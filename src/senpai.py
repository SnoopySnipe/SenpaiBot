import sys
import signal
import asyncio
import random

from discord.ext import commands
from discord.utils import get

from helpers import *

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
    # log out bot and close connection
    bot.logout()
    bot.close()
    print("Bot has logged out.")
    # exit program
    sys.exit(0)

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

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def coin():
    flip = random.randint(0,1)
    if (flip == 0):
        reply = "`Tails`"
    elif (flip == 1):
        reply = "`Heads`"
    await bot.say(reply)

@bot.command()
async def guess(guess_num):
    rand_num = random.randint(1,10)
    try:
        guess_num = int(guess_num)
        if (guess_num == rand_num):
            reply = ("`Congratulations, you guessed it right!`")
        else:
            reply = ("`Sorry, the number was " + str(rand_num) + "`")
    # Prompt for a valid input
    except ValueError:
        reply = "Please enter a number between 1 and 10."
    await bot.say(reply)

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
    await leave_all_voice_channels(bot)
    print("Left all voice channels")


@bot.event
async def on_message(message : str):
    message_content = message.content

    if (message_content.startswith("!help")):
        bot_reply = help_message()
        await bot.say(bot_reply)

    else:
        try:
            await bot.process_commands(message)
        except commands.errors.CommandNotFound:
            bot.say("command not supported")

modules = ["senpai_fortnite", "senpai_fortune",
           "senpai_imageboards", "senpai_player", "senpai_8ball"]

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



