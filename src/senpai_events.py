import discord

from discord.ext import commands

_event_list = []

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

class SenpaiEventManager:

    def __init__(self, bot):
        self.bot = bot
        self.event_list = Event_List()

    # Manages events
    @commands.command(name="event", pass_context=True)
    async def _event(self, context):
        offset = len("!senpai event")

        question = context.message.content[offset+1:]
        # check for action arguments
        if (len(question) == 0):
            await self.bot.say("`Use !senpai event list, !senpai event create [event name] [event time], !senpai event join [event number], or !senpai event leave [event number]`")
            return
        args = question.split();
        res = ""
        if(args[0] == "create"):
            res = self.event_list.add_event(args[1], args[2])
        else if (args[0] == "join"):
            res = self.event_list.add_attendee(args[1], context.message.author.mention)
        else if(args[0] == "leave"):
            res = self.event_list.remove_attendee(args[1], context.message.author.mention)
        else if(args[0] == "list"):
            res = self.event_list.list_events()
        else:
            res = "Command not found!"

        await self.bot.say(res)


def setup(bot):
    bot.add_cog(SenpaiEventManager(bot))
