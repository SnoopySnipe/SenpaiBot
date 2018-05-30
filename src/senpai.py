import sys
import signal
import asyncio
import random

import discord
from discord.ext import commands

import bot_answers
import senpai_player
import senpai_imageboards
import senpai_fortune

from helpers import *

DESCRIPTION = '''The senpai of the server.'''

# amount of arguments
argc = len(sys.argv)
# bot token
token = ""

# initialize bot
bot = commands.Bot(command_prefix="!senpai ", description=DESCRIPTION)

senpaiPlayer = senpai_player.SenpaiPlayer()
senpaiPlayerLocal = senpai_player.SenpaiPlayerLocal()

# keep track of volume
#global_volume = 1

def signal_handler(signal, frame):
    '''(Signal, Frame) -> null
    Upon signal, stop the bot and exit the program
    '''

    print("\nLogging out bot...")
    senpaiPlayer.clear_queue()
    senpaiPlayerLocal.clear_queue()
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

def is_bot(message):
    return message.author == bot.user

@bot.command(pass_context=True)
async def clean_yourself(context, lim):
    channel = context.message.channel
    lim = int(lim)

    deleted = await bot.purge_from(channel, limit=lim, check=is_bot)
    await bot.say("Deleted {} message(s)".format(len(deleted)))

@bot.command()
async def fortunecookie():
    fortune = senpai_fortune.helloacm_get_fortune_cookie()

    await bot.say(fortune)

@bot.command()
async def daily(imageboard : str):
    '''(str) -> None
    command that grabs the latest post/image from an image board imageboard
    '''
    imageboard = imageboard.lower()

    supported_boards = ["danbooru", "gelbooru", "konachan", "yandere"]

    if (imageboard == "random"):
        rand_num = random.randint(0, len(supported_boards) - 1)
        imageboard = supported_boards[rand_num]

    # yandere
    if (imageboard == supported_boards[3]):
        json_content = senpai_imageboards.yandere_get_latest_post()
        if (json_conent is None):
            await bot.say("Error: API down?")
            return
        if ("id" not in json_content or "sample_url" not in json_content):
            await bot.say("Error: json parse failed")
            return

        post_id = json_content["id"]
        file_url = json_content["sample_url"]

        bot_reply = "`" + imageboard + " #" + str(post_id) + "`\n" + file_url
        await bot.say(bot_reply)
        return

    # danbooru
    if (imageboard == supported_boards[0]):
        json_content = senpai_imageboards.danbooru_get_latest_post()
        if (json_conent is None):
            await bot.say("Error: API down?")
            return
        if ("id" not in json_content or "file_url" not in json_content):
            await bot.say("Error: json parse failed")
            return

        post_id = json_content["id"]
        file_url = json_content["file_url"]
        if ("donmai.us" not in file_url):
            file_url = "https://danbooru.donmai.us" + file_url

        bot_reply = "`" + imageboard + " #" + str(post_id) + "`\n" + file_url
        await bot.say(bot_reply)
        return

    # gelbooru
    if (imageboard == supported_boards[1]):
        json_content = senpai_imageboards.gelbooru_get_latest_post()
        if (json_conent is None):
            await bot.say("Error: API down?")
            return
        if ("id" not in json_content or "file_url" not in json_content):
            await bot.say("Error: json parse failed")
            return

        post_id = json_content["id"]
        file_url = json_content["file_url"]

        bot_reply = "`" + imageboard + " #" + str(post_id) + "`\n" + file_url
        await bot.say(bot_reply)
        return

    # konachan
    if (imageboard == supported_boards[2]):
        json_content = senpai_imageboards.konachan_get_latest_post()
        if (json_conent is None):
            await bot.say("Error: API down?")
            return
        if ("id" not in json_content or "file_url" not in json_content):
            await bot.say("Error: json parse failed")
            return

        post_id = json_content["id"]
        file_url = json_content["sample_url"]

        bot_reply = "`" + imageboard + " #" + str(post_id) + "`\n" + file_url
        await bot.say(bot_reply)
        return

# Commands regarding playing songs

@bot.command()
async def skip():
    ''' skips the current song '''
    await senpaiPlayer.skip()
    await senpaiPlayerLocal.skip()

@bot.command()
async def stop():
    ''' clears the queue and skips player to the next song which is nothing '''
    senpaiPlayer.clear_queue()
    await senpaiPlayer.skip()

    senpaiPlayerLocal.clear_queue()
    await senpaiPlayerLocal.skip()

@bot.command()
async def pause():
    ''' pauses the current song '''
    await senpaiPlayer.pause()

    await senpaiPlayerLocal.pause()

@bot.command()
async def resume():
    await senpaiPlayer.resume()

    await senpaiPlayerLocal.resume()

@bot.command()
async def queue():
    reply = queue_to_string(senpaiPlayer.get_queue())
    await bot.say(reply)

@bot.command()
async def localqueue():
    reply = queue_to_string(senpaiPlayerLocal.get_queue())
    await bot.say(reply)

@bot.command()
async def volume(new_volume=None):
    reply = ""
    if (new_volume is None):
        volume = senpaiPlayerLocal.get_volume()
        reply = "`Volume is currently at " + str(volume) + "`"
    else:
        try:
            # if valid volume, adjust it
            volume = float(new_volume)

            senpaiPlayerLocal.set_volume(volume)

            senpaiPlayer.set_volume(volume)
            reply = ("`Volume has been adjusted to " +
                 str(senpaiPlayerLocal.get_volume()) + "`")
        # prompt for a valid volume if invalid
        except ValueError:
            reply = "`Please enter a volume between 0 and 100`"
    await bot.say(reply)


@bot.command(pass_context=True)
async def play(context, url=None):
    # if no url is given
    if (url is None):
        bot_reply = "`No URL given`"
        bot.say(bot_reply)
        return

    message = context.message
    author_voice_channel = message.author.voice_channel

    # user is not in a voice channel
    if (author_voice_channel is None):
        bot_reply = ("\@" + str(message.author) +
            ", please join a voice channel to play music")
        bot.say(bot_reply)
    else:
        already_connected = bot_in_voice_channel(bot, author_voice_channel)

        song = senpaiPlayer.add_song(url)

        # bot is already in user's voice channel
        if (already_connected is True):
            # notify user
            bot_reply = "`Enqueued`"
            await bot.say(bot_reply)
        # otherwise, join voice channel before playing
        else:
            bot_voice = await bot.join_voice_channel(author_voice_channel)
            # tell bot to start playing
            await senpaiPlayer.play(bot, bot_voice, message)


@bot.command(pass_context=True)
async def playlocal(context, url=None):
    if (url is None):
        bot_reply = "`No URL given`"
        bot.say(bot_reply)
        return

    message = context.message
    author_voice_channel = message.author.voice_channel

    # user is not in a voice channel
    if (author_voice_channel is None):
        bot_reply = ("\@" + str(message.author) +
            ", please join a voice channel to play music")
        bot.say(bot_reply)
    else:
        already_connected = bot_in_voice_channel(bot, author_voice_channel)

        # tell user we are busy and not just not responsive
        bot_reply = "`Downloading video...`"
        temp_message = await bot.say(bot_reply)

        song = senpaiPlayerLocal.add_song(url)
        await bot.delete_message(temp_message)

        # bot is already in user's voice channel
        if (already_connected is True):
            bot_reply = "`Enqueued: " + str(song) + "`"
            await bot.say(bot_reply)
        # otherwise, join voice channel before playing
        else:
            bot_voice = await bot.join_voice_channel(author_voice_channel)
            await senpaiPlayerLocal.play(bot, bot_voice, message)


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

    # Answers question with a yes or no
    elif (message_content.startswith("!senpai 8ball")):
        reply = ("`Kouhai, dou shita no?`")

        offset = len("!senpai 8ball")
        question = message_content[offset+1:]

        # check if user actually asked a question
        if len(question) > 0:
            answer_index = random.randint(0, len(bot_answers.answers)-1)
            reply = ("`Question: " + question + "\n" +
                     "Answer: " + bot_answers.answers[answer_index] + "`")

        await bot.send_message(message.channel, reply)

    # Fortnite dropman
    elif (message_content.startswith("!senpai wherewedroppingbois") or
          message_content.startswith("!senpai drop")):
        answer_index = random.randint(0, len(bot_answers.fortnite_locations)-1)
        location = bot_answers.fortnite_locations[answer_index]
        if(location in bot_answers.fortnite_location_pics):
            location_pic = bot_answers.fortnite_location_pics[location]
        else:
            location_pic = "images/test.png"
        reply = ("We dropping " + location + " bois")
        await bot.send_file(message.channel, location_pic, content=reply)
    elif (message_content.startswith("We dropping") 
          and message.author == bot.user):
        add_reaction(message, ":regional_indicator_y:")
        add_reaction(message, ":regional_indicator_o:")
        add_reaction(message, ":regional_indicator_t:")
        add_reaction(message, ":regional_indicator_e:")
        
    else:
        try:
            await bot.process_commands(message)
        except commands.errors.CommandNotFound:
            bot.say("command not supported")

if (__name__ == "__main__"):

    # map Ctrl+C to trigger signal_handler function
    signal.signal(signal.SIGINT, signal_handler)

    print("Logging in...")

    # parse command line arguments
    for i in range(argc):
        if (sys.argv[i] == "-t" and i < argc):
            token = sys.argv[i+1]

    bot.run(token)



