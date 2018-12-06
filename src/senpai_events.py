import discord
from events import *
from discord.ext import commands

class SenpaiEvents:
    def __init__(self):
        self.event_list = Event_List()

    # Manages events
    @commands.command()
    async def event(self, context, *arg):
        offset = len("!senpai event")

        question = context.message.content[offset+1:]
        # check for action arguments
        if (len(question) == 0):
            await context.send("`Use !senpai event list, !senpai event create [event name] [event time], !senpai event join [event number], or !senpai event leave [event number]`")
            return
        res = "Something went wrong"
        if(arg[0] == "create"):
            if(len(arg) == 3):
                res = self.event_list.add_event(arg[1], arg[2])
            else:
                res = "Usage: !senpai event create \"event name\" \"event time\""
        elif (arg[0] == "remove"):
            if(len(arg) == 2):
                res = self.event_list.remove_event(int(arg[1]))
            else:
                res = "Usage: !senpai event remove [event number]"
        elif (arg[0] == "join"):
            if(len(arg) == 2):
                res = self.event_list.add_attendee(int(arg[1]), context.message.author)
            else:
                res = "Usage: !senpai event join [event number]"
        elif(arg[0] == "leave"):
            if(len(arg) == 2):
                res = self.event_list.remove_attendee(int(arg[1]), context.message.author)
            else:
                res = "Usage: !senpai event leave [event number]"
        elif(arg[0] == "list"):
            res = self.event_list.list_events()
            if(res == ""):
                res = "No events found"
        else:
            res = "Command not found!"

        await context.send(res)

def setup(bot):
    bot.add_cog(SenpaiEvents())
    
    
