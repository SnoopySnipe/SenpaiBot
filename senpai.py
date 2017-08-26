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

# keep track of volume
#global_volume = 1

def signal_handler(signal, frame):
    '''(Signal, Frame) -> null
    Upon signal, stop the bot and exit the program
    '''

    print("\nLogging out bot...")
    senpai_player.queue.clear()
    # log out bot and close connection
    bot.logout()
    bot.close()
    print("Bot has logged out.")
    # exit program
    sys.exit(0)

# map Ctrl+C to trigger signal_handler function
signal.signal(signal.SIGINT, signal_handler)

def process_song_title(title):
    new_title = title
    new_title = new_title.replace("*", "_")
    new_title = new_title.replace("/", "_")
    new_title = new_title.replace(":", " -")
    return new_title

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
            answer_index = random.randint(0, bot_answers.num_answers)
            reply = ("`Question: " + question + "\n" +
                     "Answer: " + bot_answers.answers[answer_index] + "`")

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
                 "!guess <number> " + "\t" * 4 + "Guess a number between 1 and 10\n"
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
        if (not already_connected):
            bot_voice = await senpai_player.join_voice_channel_of_user(message, bot)
        # if bot is connected
        if (bot_voice):
            # check if it is a valid url
            if (url.startswith("http")):
                # add the url to the queue
                senpai_player.queue.append(url)
                # if the bot wasn't already connected, join voice channel
                # and play the video
                if (not already_connected):
                    await senpai_player.play_song(bot, bot_voice, message)
                # if the bot was already connected, just print a message saying
                # that the song was queued
                else:
                    reply = "`Enqueued.`"
                    await bot.send_message(message.channel, reply)

            # skip to the next song in queue
            elif (url == "skip"):
                await senpai_player.player_skip()

            # clear the queue and skip
            elif (url == "stop"):
                senpai_player.queue.clear()
                await senpai_player.player_skip()

            # pause the music
            elif (url == "pause"):
                await senpai_player.player_pause()

            # resume the music
            elif (url == "resume"):
                await senpai_player.player_resume()

            # display the song queue
            elif (url == "queue"):
                reply = "`"
                if (len(senpai_player.queue) == 0):
                    reply = "`Queue is empty.`"
                else:
                    for i in range(len(senpai_player.queue)):
                        reply += (str(i) + "." + "\t" * 4 +
                                senpai_player.queue[i] + "\n")
                    reply += "`"
                await bot.send_message(message.channel, reply)

            elif (url == "localqueue"):
                reply = "`"
                if (len(senpai_player.local_queue) == 0):
                    reply = "`Queue is empty.`"
                else:
                    for i in range(len(senpai_player.local_queue)):
                        song_title = senpai_player.local_queue[i].title
                        reply += ("\t" + str(i) + "." + "\t" * 4 +
                                song_title + "\n")
                    reply += "`"
                await bot.send_message(message.channel, reply)

            elif (url.startswith("locally ")):
                url = url[len("locally "):]

                # tell user we are busy and not just not responsive
                reply = ("`Downloading video...`")
                await bot.send_message(message.channel, reply)
                # get the song's name
                song_title = download_youtube.download_song(url)
                # get the file name it was saved as
                file_title = process_song_title(song_title)
                # concat the file path to the file
                file_path = (download_youtube.download_dir +
                            file_title + "." +
                            download_youtube.audio_format)
                # create a SenpaiSong object and add it to the local queue
                song = senpai_song.SenpaiSong(file_path, song_title)
                # add the url to the queue
                senpai_player.local_queue.append(song)
                # if the bot wasn't already connected, join voice channel
                # and play the video
                if (not already_connected):
                    await senpai_player.play_local_song(bot, bot_voice, message)
                # if the bot was already connected, just print a message saying
                # that the song was queued
                else:
                    reply = "`Video has been enqueued`"
                    await bot.send_message(message.channel, reply)

            # adjust the music volume
            elif (url.startswith("volume")):
                volume_offset = len("volume")
                volume = url[volume_offset+1:]
                if (len(volume) <= 0):
                    volume = senpai_player.player_get_volume()
                    reply = "`Volume is currently at " + str(volume) + "`"
                else:
                    try:
                        # if valid volume, adjust it
                        volume = float(volume)
                        senpai_player.player_volume = volume
                        await senpai_player.player_set_volume(
                                senpai_player.player_volume)
                        reply = ("`Volume has been adjusted to " +
                            str(senpai_player.player_volume) + "`")
                    # prompt for a valid volume if invalid
                    except ValueError:
                        reply = "`Please enter a volume between 0 and 100`"
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

    # Guess a number between 1 - 10
    elif (message_content.startswith("!guess")):
        
        offset = len("!guess")
        guess_num = int(message_content[offset+1:])
        rand_num = random.randint(1,10)
        
        if (guess_num == rand_num):
            reply = ("Congratulations, you guessed it right!" + "`")
        else:
            reply = ("Sorry, the number was " + str(rand_num) + "`")
        await bot.send_message(message.channel, reply)

bot.run(token)
