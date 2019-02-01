import discord

from discord.ext import commands

class SenpaiSpoiler:
    @commands.command(name="spoiler")
    async def _spoiler(self, context, *arg):
        offset = len("!senpai spoiler")
        msg = context.message.content[offset+1:]

        # check if there is a message
        if (len(msg) == 0 or len(arg) == 1):
            await context.send("`NO MESSAGE BAKA!!`")
            await context.send("`Usage:\n" + "!senpai spoiler [title] [msg]`")
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

def setup(bot):
    bot.add_cog(SenpaiSpoiler())
