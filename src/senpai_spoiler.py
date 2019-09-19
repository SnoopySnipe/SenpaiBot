import discord

from discord.ext import commands

class SenpaiSpoiler(commands.Cog):

    __slots__ = ("messages")

    def __init__(self):
        self.messages = set()
        
    @daniel.command()
    async def purge(self, context):
        msgs = len(self.messages)
        for i in range(msgs):
            await self.messages.pop().delete()
        if msgs > 0:
            await context.send("Successfully purged daniel.")
    
    @commands.command(name="spoiler")
    async def _spoiler(self, context, *arg):
        offset = len("!spoiler")
        msg = context.message.content[offset+1:]

        # check if there is a message
        if (len(msg) == 0 or len(arg) == 1):
            await context.send("`NO MESSAGE BAKA!!`")
            await context.send("`Usage:\n" + "!spoiler [title] [msg]`")
            return
        else:
            title = arg[0]
            msg = ""
            for i in range (1, len(arg)):
                msg = msg + " " + "".join(arg[i])
            msg = "||" + msg + "||"

            # Embeded message
            embed_msg = discord.Embed(color=0xff93ac)
            embed_msg.add_field(name="**Sender:**", value=context.message.author,
                inline=False)
            embed_msg.add_field(name="**Spoiler For:**", value=title,
                inline=False)
            embed_msg.add_field(name="**Spoils:**", value=msg, inline=False)
            await context.send(embed=embed_msg)

            # delete the command message
            if (len(msg) > 0):
                await context.message.delete()
                return

    @commands.command(name="daniel")
    async def _daniel(self, context, *arg):
        msg = await context.send("||https://gfycat.com/MeagerThreadbareDogfish||")
        if msg:
            self.messages.add(msg)
        
    @commands.command(name="danieI")
    async def _danieI(self, context, *arg):
        msg = await context.send("https://gfycat.com/MeagerThreadbareDogfish")
        if msg:
            self.messages.add(msg)

def setup(bot):
    bot.add_cog(SenpaiSpoiler())
