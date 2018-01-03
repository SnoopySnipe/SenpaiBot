import sys
import signal
import asyncio

import discord
from discord.ext import commands
import random

import download_youtube
import bot_answers
import senpai_player
import senpai_song
import senpai_imageboards

DESCRIPTION = '''The senpai of the server.'''

# amount of arguments
argc = len(sys.argv)
# bot token
token = ""

# initialize bot
bot = commands.Bot(command_prefix="!senpai ", description=DESCRIPTION)

senpaiPlayer = senpai_player.SenpaiPlayer()

# keep track of volume
#global_volume = 1

def signal_handler(signal, frame):
    '''(Signal, Frame) -> null
    Upon signal, stop the bot and exit the program
    '''

    print("\nLogging out bot...")
    senpaiPlayer.player_clear()
    # log out bot and close connection
    bot.logout()
    bot.close()
    print("Bot has logged out.")
    # exit program
    sys.exit(0)

def process_song_title(title : str):
    new_title = title
    new_title = new_title.replace("*", "_")
    new_title = new_title.replace("/", "_")
    new_title = new_title.replace(":", " -")
    return new_title

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

def queue_to_string(queue : list):
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

def get_existing_voice(bot):
    bot_voice = None

    # check if bot is already connected.
    for voice in bot.voice_clients:
        if (voice.is_connected()):
            bot_voice = voice
            break
    return bot_voice

def help_message():
    help_msg = (
        "!8ball <question> " + "\t" + "Senpai knows all..." + "\n" +
        "daily <imageboard> " + "\t" +
            "Grabs the latest anime image from an image board." + "\n" +
            "Currently supports: yandere, danbooru" + "\n" +
        "play <link>" + "\t" + "Play YouTube videos" + "\n" +
            "pause/resume/stop/skip" + "\t" +
            "does exactly that to the playlist" + "\n"
        "playlocal <link>" + "\t" +
            "Downloads YouTube video before playing for smooth playback"
            + "\n" +
        "queue/localqueue" + "\t" + "show queue/localqueue" + "\n"
        "coin " + "\t" + "Flips a coin" + "\n"
        "guess <number> " + "\t" + "Guess a number between 1 and 10" + "\n"
        )
    return help_msg

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
        reply = "`Tails.`"
    elif (flip == 1):
        reply = "`Heads.`"
    await bot.say(reply)

@bot.command()
async def guess(guess_num):
    rand_num = random.randint(1,10)
    try:
        if (guess_num == rand_num):
            reply = ("`Congratulations, you guessed it right!`")
        else:
            reply = ("`Sorry, the number was " + str(rand_num) + "`")
    # Prompt for a valid input
    except ValueError:
        reply = "Please enter a number between 1 and 10."
    await bot.say(reply)



@bot.command()
async def daily(imageboard : str):
    imageboard = imageboard.lower()
    if (imageboard == "yandere"):
        json_content = senpai_imageboards.yandere_get_latest_post()
        post_id = json_content["id"]
        file_url = json_content["sample_url"]
        bot_reply = "#" + str(post_id) + "\n" + file_url
        await bot.say(bot_reply)

    elif (imageboard == "danbooru"):
        json_content = senpai_imageboards.danbooru_get_latest_post()
        post_id = json_content["id"]
        file_url = json_content["file_url"]
        file_url = "https://danbooru.donmai.us" + file_url

        bot_reply = "`#" + str(post_id) + "`\n" + file_url
        await bot.say(bot_reply)


@bot.command()
async def skip():
    ''' skips the current song '''
    await senpaiPlayer.player_skip()

@bot.command()
async def stop():
    ''' clears the queue and skips player to the next song which is nothing '''
    senpaiPlayer.player_clear()
    await senpaiPlayer.player_skip()

@bot.command()
async def pause():
    await senpaiPlayer.player_pause()

@bot.command()
async def resume():
    await senpaiPlayer.player_resume()

@bot.command()
async def queue():
    reply = queue_to_string(senpaiPlayer._queue)
    await bot.say(reply)

@bot.command()
async def localqueue():
    reply = queue_to_string(senpaiPlayer._local_queue)
    await bot.say(reply)

@bot.command()
async def volume(new_volume=None):
    reply = ""
    if (new_volume is None):
        volume = senpaiPlayer.player_get_volume()
        reply = "`Volume is currently at " + str(volume) + "`"
    else:
        try:
            # if valid volume, adjust it
            volume = float(new_volume)
            senpaiPlayer.player_volume = volume
            senpaiPlayer.player_set_volume(
                     senpaiPlayer.player_volume)
            reply = ("`Volume has been adjusted to " +
                 str(senpaiPlayer.player_volume) + "`")
        # prompt for a valid volume if invalid
        except ValueError:
            reply = "`Please enter a volume between 0 and 100`"
    await bot.say(reply)


@bot.command(pass_context=True)
async def play(context, url=None):
    bot_reply = None
    if (url is None):
        bot_reply = "`No URL given`"
        bot.say(bot_reply)
        return

    message = context.message

    # check if bot is already in an existing voice channel
    bot_voice = get_existing_voice(bot)

    # if bot is not already connected, then connect them to
    # voice channel
    if (bot_voice is None):
        try:
            bot_voice = await senpaiPlayer.join_voice_channel_of_user(
                                    message, bot)
        except senpai_player.UserNotInVoiceChannelException:
            bot_reply = ("\@" + str(message.author) +
                ", please join a voice channel to play music")
            await bot.say(bot_reply)
            return
        song = senpai_song.SenpaiSong(url)
        # add the url to the queue
        senpaiPlayer.add_song(song)
        await senpaiPlayer.play_song(bot, bot_voice, message)
    # if the bot was already connected, just print a message saying
    # that the song was queued
    else:
        song = senpai_song.SenpaiSong(url)
        # add the url to the queue
        senpaiPlayer.add_song(song)
        bot_reply = "`Enqueued.`"
        await bot.say(bot_reply)

@bot.command(pass_context=True)
async def playlocal(context, url=None):
    bot_reply = None
    if (url is None):
        bot_reply = "`No URL given`"
        bot.say(bot_reply)
        return

    message = context.message

    # check if bot is already in an existing voice channel
    bot_voice = get_existing_voice(bot)

    # if bot is not already connected, then connect them to
    # voice channel
    if (bot_voice is None):
        try:
            bot_voice = await senpaiPlayer.join_voice_channel_of_user(
                                    message, bot)
        except senpai_player.UserNotInVoiceChannelException:
            bot_reply = ("\@" + str(message.author) +
                ", please join a voice channel to play music")
            await bot.say(reply)
            return

        # tell user we are busy and not just not responsive
        reply = ("`Downloading video...`")
        await bot.say(reply)
        # get the song's name
        info_dict = download_youtube.download_song(url)
        song_title = info_dict.get('title', None)
        # get the file name it was saved as
        file_title = process_song_title(song_title)
        # concat the file path to the file
        file_path = (download_youtube.download_dir +
                    file_title + "." +
                    download_youtube.audio_format)
        # create a SenpaiSong object and add it to the local queue
        song = senpai_song.SenpaiSong(file_path, song_title)
        # add the url to the queue
        senpaiPlayer.add_song_local(song)
        await senpaiPlayer.play_song_local(bot, bot_voice, message)
    else:
        # tell user we are busy and not just not responsive
        bot_reply = ("`Downloading video...`")
        await bot.say(reply)
        # get the song's name
        info_dict = download_youtube.download_song(url)
        song_title = info_dict.get('title', None)
        # get the file name it was saved as
        file_title = process_song_title(song_title)
        # concat the file path to the file
        file_path = (download_youtube.download_dir +
                    file_title + "." +
                    download_youtube.audio_format)
        # create a SenpaiSong object and add it to the local queue
        song = senpai_song.SenpaiSong(file_path, song_title)
        # add the url to the queue
        senpaiPlayer.add_song_local(song)
        bot_reply = "`Enqueued: " + str(song) + "`"
        await bot.say(bot_reply)

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
    if (message_content.startswith("!8ball")):
        reply = ("`Kouhai, dou shita no?`")

        offset = len("!8ball")
        question = message_content[offset+1:]

        # check if user actually asked a question
        if len(question) > 0:
            answer_index = random.randint(0, bot_answers.num_answers)
            reply = ("`Question: " + question + "\n" +
                     "Answer: " + bot_answers.answers[answer_index] + "`")

        await bot.send_message(message.channel, reply)

    await bot.process_commands(message)


if (__name__ == "__main__"):

    # map Ctrl+C to trigger signal_handler function
    signal.signal(signal.SIGINT, signal_handler)

    print("Logging in...")

    # parse command line arguments
    for i in range(argc):
        if (sys.argv[i] == "-t" and i < argc):
            token = sys.argv[i+1]

    bot.run(token)



