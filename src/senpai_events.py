import discord

from discord.ext import commands
from helpers import *
from events import *

class SenpaiEvents:
    __slots__ = ('event_list')

    def __init__(self):
        self.event_list = EventList()

    # Manages events
    @commands.group(invoke_without_command=True)
    async def event(self, context, *arg):
        offset = len("!event")
        question = context.message.content[offset+1:]
        # check for action arguments
        if (len(question) == 0):
            await context.send("`Usage:\n" +
                                "!event list\n" +
                                "!event create [event name] [event time]\n" +
                                "!event join [event number]\n" +
                                "!event leave [event number]`")
            return

        if (arg[0] == "create"):
            if (len(arg) == 3):
                index, new_event = self.event_list.add_event(arg[1], arg[2])
                embed_msg = new_event.to_embed_msg(index)
                await context.send("New event added: ", embed=embed_msg)
            else:
                await context.send("Usage: !event create \"event name\" \"event time\"")
        else:
            await context.send("Command not found!")

    @event.command()
    async def list(self, context):
        for event_msg in self.event_list.to_embed_msg_list():
            await context.send(embed=event_msg)

    @event.command()
    async def join(self, context, index=None):
        if (index is None):
            await context.send("Usage: !event join [event number]")
            return

        try:
            index = int(index)

            msg = self.event_list.add_attendee(index, context.message.author)
            await context.send(msg)
        except:
            await context.send("Invalid event number")

    @event.command()
    async def leave(self, context, index=None):
        if (index is None):
            await context.send("Usage: !event leave [event number]")
            return

        try:
            index = int(index)
            msg = self.event_list.remove_attendee(index, context.message.author)
            await context.send(msg)
        except:
            await context.send("Invalid event number")

    @event.command()
    async def remove(self, context, index=None):
        if (index is None):
            await context.send("Usage: !event remove [event number]")
            return

        try:
            index = int(index)
            msg = self.event_list.remove_event(index)
            await context.send(msg)
        except:
            await context.send("Invalid event number")

def setup(bot):
    bot.add_cog(SenpaiEvents())

