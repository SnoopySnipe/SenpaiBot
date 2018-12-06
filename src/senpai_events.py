import discord

from discord.ext import commands
from helpers import *
event_list = Event_List()
class SenpaiEvents:

    def __init__(self, bot):
        self.bot = bot()

    # Manages events
    @commands.command(pass_context=True)
    async def event(self, context):
        offset = len("!senpai event")

        question = context.message.content[offset+1:]
        # check for action arguments
        if (len(question) == 0):
            await self.bot.say("`Use !senpai event list, !senpai event create [event name] [event time], !senpai event join [event number], or !senpai event leave [event number]`")
            return
        args = question.split();
        res = ""
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

        await self.bot.say(res)


def setup(bot):
    bot.add_cog(SenpaiEvents(bot))
