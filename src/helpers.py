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
class Event_List:
    def __init__(self):
        self.event_list = []
    def add_event(self, event_name, event_start_time):
        self.event_list.append(Event(event_name, event_start_time))
    def list_events(self):
        res = ""
        for i in range(len(self.event_list)):
            res += "#" + str(i) + ". " + self.event_list[i].event_name
        return res
    def view_attendees(self, eventIndex):
        if(eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].view_attendees()
    def add_attendee(self, eventIndex, name):
        if(eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].add_attendee()
    def remove_attendee(self, eventIndex, name):
        if(eventIndex < len(self.event_list)):
            return self.event_list[eventIndex].remove_attendee()
class Event:
    def __init__(self, event_name, event_start_time):
        self.event_name = event_name
        self.event_start_time = event_start_time
        self.attendees = []
    def view_attendees(self):
        return self.attendees
    def add_attendee(self, name):
        if(name not in self.attendees):
            self.attendees.append(name)
            return "Added to " + self.event_name
        else:
            return "Already added to event"
    def remove_attendee(self, name):
        if(name in self.attendees):
            self.attendees.remove(name)
            return "Removed from " + self.event_name
        else:
            return "Already removed from event"
