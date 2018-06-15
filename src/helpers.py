def get_existing_voice(bot):
    bot_voice = None

    # check if bot is already connected.
    for voice in bot.voice_clients:
        if (voice.is_connected()):
            bot_voice = voice
            break
    return bot_voice


def help_message():
    return ("8ball <question> \t Senpai knows all...\n" +
        "daily <imageboard> \t" +
            "Grabs the latest anime image from an image board.\n" +
            "Currently supports: yandere, danbooru, konachan, gelbooru\n" +
        "coin \t Flips a coin\n" +
        "guess <number> \t Guess a number between 1 and 10\n" +
        "drop/wherewedroppingbois" + "\t" + "Tells you where to drop for a victory royale\n" +
        "play <link> \t Play YouTube videos\n" +
            "pause/resume/stop/skip" + "\t" +
            "does exactly that to the playlist\n"
        "playlocal <link>\t" +
            "Downloads YouTube video before playing for smooth playback\n"
        "queue \t show song queue\n")

def bot_in_voice_channel(bot, voice_channel):
    ''' check if bot is already connected to given voice channel '''
    already_connected = False
    for voice_client in bot.voice_clients:
        channel = voice_client.channel
        if (channel.id == voice_channel.id):
            already_connected = True
            break

    return already_connected
