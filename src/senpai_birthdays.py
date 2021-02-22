import discord
import asyncio
import datetime
import time
import birthday_db_helper
from discord.ext import commands

NEWS_CHANNEL_ID = 568068520965963790
TEST_CHANNEL_ID = 601616446694621235
EV_CHANNEL_ID = 414213254781468674
SNOOPY_ID = 103634047929962496
SFLARE_ID = 225081018728710144


class SenpaiBirthdays(commands.Cog):
    __slots__ = ("messages")

    def __init__(self, bot):
        self.bot = bot
        self.messages = set()

    @commands.Cog.listener()
    async def on_ready(self):
        birthday_db_helper.initialize()
        self.bot.loop.create_task(self.background_birthdays())
        #print("task created")

    async def background_birthdays(self):
        await self.bot.wait_until_ready()
        #channel = self.bot.get_channel(NEWS_CHANNEL_ID)
        channel = self.bot.get_channel(EV_CHANNEL_ID)
        if(channel is None):
            return
        while True:
            if datetime.datetime.now().hour == 0:
                mm = datetime.datetime.now().month
                dd = datetime.datetime.now().day
                list = birthday_db_helper.get_today_birthdays(mm, dd)
                if list:
                    title = "🎊HAPPY BIRTHDAY TO🎊"

                    description = ""
                    for entry in list:
                        #username = self.bot.get_user(entry[0]).name
                        try:
                            username = self.bot.get_user(entry[0]).name
                        except:
                            username = entry[0]
                        description += "{}".format(username)
                    embed = discord.Embed(title=title, description=description, color=0xffffff)
                    msg = await channel.send(embed=embed)
                    if msg:
                        self.messages.add(msg)
            await asyncio.sleep(3600)

    async def get_birthdays():
        return None

    @commands.group(invoke_without_command=True)
    async def birthday(self, context, *arg):
        offset = len("!birthday")
        question = context.message.content[offset+1:]
        # check for action arguments
        if (len(question) == 0):
            await context.send("`Usage:\n" +
                                "!blist\n" +
                                "!birthday add [user_id] [mm] [dd]\n" +
                                "!birthday del [user_id]\n`")
            return
        if (arg[0] == "add"):
            if (len(arg) == 4):
                if context.message.author.id == SNOOPY_ID  or context.message.author.id == SFLARE_ID:
                    birthday_db_helper.add(arg[1], arg[2], arg[3])
                    await context.send("Birthday Created")
                else:
                    await context.send("Y'all'th'st'd've'ish ain't Snoopy or Sflare")
            else:
                await context.send("Usage: !birthday add \"user_id\" \"mm\" \"dd\"")
        elif (arg[0] == "del"):
            if (len(arg) == 2):
                if context.message.author.id == SNOOPY_ID  or context.message.author.id == SFLARE_ID:
                    birthday_db_helper.delete(arg[1])
                    await context.send("Birthday Deleted")
                else:
                    await context.send("Y'all'th'st'd've'ish ain't Snoopy or Sflare")
            else:
                await context.send("Usage: !birthday del \"user_id\"")
        # elif (arg[0] == "list"):
        #     list = birthday_db_helper.list()
        #     # clean up the formatting here
        #
        #     channel = self.bot.get_channel(TEST_CHANNEL_ID)
        #     msg = await channel.send(list)
        #     if msg:
        #         self.messages.add(msg)
        # else:
        #     await context.send("Command not found!")


    @commands.command(name="blist")
    async def blist(self, context):
        list = birthday_db_helper.list()
        # clean up the formatting here
        # embed = self.format_list(list)
        title = "Birthdays"
        # description = "this1\n"
        # description += "this"
        description = "Person | Month | Day\n\n"
        for entry in list:
            #username = self.bot.get_user(entry[0]).name
            try:
                username = self.bot.get_user(entry[0]).name
            except:
                username = entry[0]
            description += "{}: {}/{}\n".format(username, entry[1], entry[2])
        embed = discord.Embed(title=title, description=description, color=0xffffff)
        #channel = self.bot.get_channel(TEST_CHANNEL_ID)
        await context.send(embed=embed)
        # else:
        #     await context.send("Command not found!")

    # async def format_list(self, arr):
    #     title = "Birthdays"
    #     # for entry in arr:
    #     #     description += "{}".format(entry)
    #     description = "this1\n"
    #     description += "this"
    #     embed = discord.Embed(title=title, description=description, color=0xffffff)
    #     return embed


def setup(bot):
    bot.add_cog(SenpaiBirthdays(bot))
