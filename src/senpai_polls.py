import discord
import senpai

from discord.ext import commands
from helpers import *
from polls import *

class SenpaiPolls:
    def __init__(self):
        self.poll_list = Poll_List()

    @commands.group(invoke_without_command=True)
    async def poll(self, context, *arg):
        offset = len("!senpai poll")
        details = context.message.content[offset + 1:]
        if len(details) == 0:
            await context.send("`Usage:\n" +
                               "!senpai poll create [description]\n" +
                               "!senpai poll create [description] [option1] [option2] ...\n" +
                               "!senpai poll remove [poll_number]\n" +
                               "!senpai poll remove [poll_number] [option_number]\n" +
                               "!senpai poll add [poll_number] [option]\n" +
                               "!senpai poll view\n" +
                               "!senpai poll view [poll_number]\n" +
                               "!senpai poll vote [poll_number] [option_number]`")
            return

        if arg[0] == "create":
            if len(arg) == 2:
                msg = await context.send("New poll added: ", embed=self.poll_list.add_poll(arg[1]))
                await msg.add_reaction(self.check)
                await msg.add_reaction(self.cross)
            elif len(arg) > 2:
                options = []
                for i in range(2, len(arg)):
                    options.append(arg[i])
                await context.send("New poll added: ", embed=self.poll_list.add_poll(arg[1], options=options))
            else:
                await context.send("`Usage: !senpai poll create \"description\" \"option1\" \"option2\" ...`")

        else:
            await context.send("`Command not found`")

    @poll.command()
    async def remove(self, context, index1=None, index2=None):
        if index1 is None and index2 is None:
            await context.send("`Usage:\n" +
                               "!senpai poll remove [poll_number]\n" +
                               "!senpai poll remove [poll_number] [option_number]`")
            return

        if index1 and index2 is None:
            try:
                index = int(index1)
                await context.send(self.poll_list.remove_poll(index))
            except:
                await context.send("`Invalid poll`")

        elif index1 and index2:
            try:
                poll_i = int(index1)
                option_i = int(index2)
                await context.send(self.poll_list.poll_list[poll_i].remove_option(option_i), embed=self.poll_list.poll_list[poll_i].view(poll_i))
            except:
                await context.send("`Invalid poll or option`")

    @poll.command()
    async def add(self, context, index=None, option=None):
        if index is None or option is None:
            await context.send ("`Usage: !senpai poll add [poll_number] [option]`")
            return

        try:
            i = int(index)
            self.poll_list.poll_list[i].add_option(option)
            await context.send("New option added: ", embed=self.poll_list.poll_list[i].view(i))
        except:
            await context.send("`Invalid poll`")

    @poll.command()
    async def vote(self, context, poll=None, option=None):
        if poll is None or option is None:
            await context.send("`Usage: !senpai poll vote [poll_number] [option_number]`")
            return
        try:
            poll_i = int(poll)
            option_i = int(option)
            self.poll_list.poll_list[poll_i].vote(option_i, context.message.author)
            await context.send("Vote sent: ", embed=self.poll_list.poll_list[poll_i].view(poll_i))
        except:
            await context.send("`Invalid poll or option`")

    @poll.command()
    async def view(self, context, poll=None):
        if poll:
            try:
                poll_i = int(poll)
                await context.send(embed=self.poll_list.poll_list[poll_i].view(poll_i))
            except:
                await context.send("`Invalid poll`")
        else:
            for i in range(len(self.poll_list.poll_list)):
                await context.send(embed=self.poll_list.poll_list[i].view(i))

    @poll.command()
    async def votekick(self, context, name=None):
        if name is None:
            await context.send("`Usage: !senpai poll votekick [name]`")
            return
        msg = await context.send("New poll added: ", embed=self.poll_list.add_poll('Kick ' + name + '?'))
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

    @poll.command()
    async def votegay(self, context, name=None):
        if name is None:
            await context.send("`Usage: !senpai poll votegay [name]`")
            return
        msg = await context.send("New poll added: ", embed=self.poll_list.add_poll('Is ' + name + ' gay?'))
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

def setup(bot):
    bot.add_cog(SenpaiPolls())
