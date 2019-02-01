import discord
from discord.ext import commands
import database_helper


class SenpaiShop:

    @commands.command(name="balance")
    async def balance(self, context):
        user_id = context.message.author.id
        balance = database_helper.get_pikapoints(user_id)
        if (balance is None):
            await context.send("You have no pikapoints! Join voice and start earning!")
        else:
            await context.send("You have " + str(balance) + " pikapoints")

    @commands.command(name="pity")
    async def pity(self, context):
        pity = database_helper.get_pity(context.message.author.id)
        title = "{}'s Pity Rates: \n".format(context.message.author.name)
        if pity is None:
            description = "3⭐: 40%\n4⭐: 50%\n5⭐: 4%\nFocus: 6%"
        else:
            description = "3⭐: {}\n4⭐: {}\n5⭐: {}\nFocus: {}".format(pity[0], pity[1], pity[2], pity[3])
            
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

    #@commands.command(name="roll"
    #async def roll(self, context):

    @commands.command(name="focus")
    async def focus(self, context):
        focus = database_helper.get_focus()
        title = "Focus Units: "
        description = ''
        description = description + "\n" + focus[0]
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))


def setup(bot):
    bot.add_cog(SenpaiShop())
