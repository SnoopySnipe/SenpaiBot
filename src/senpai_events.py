import discord
from events import *
from discord.ext import commands

class SenpaiEvents:
    event_list = Event_List()

    # Manages events
    @commands.command()
    async def event(self, context, *, arg):
        offset = len("!senpai event")

        question = context.message.content[offset+1:]
        # check for action arguments
        if (len(question) == 0):
            await context.send("`Use !senpai event list, !senpai event create [event name] [event time], !senpai event join [event number], or !senpai event leave [event number]`")
            return
        res = ""
        args = arg.split()
        await context.send(args)
        if(args[0] == "create"):
            res = event_list.add_event(args[1], args[2])
        elif (args[0] == "join"):
            res = event_list.add_attendee(args[1], context.message.author.mention)
        elif(args[0] == "leave"):
            res = event_list.remove_attendee(args[1], context.message.author.mention)
        elif(args[0] == "list"):
            res = event_list.list_events()
        else:
            res = "Command not found!"

        await context.send(res)

def setup(bot):
    bot.add_cog(SenpaiEvents())
    
    