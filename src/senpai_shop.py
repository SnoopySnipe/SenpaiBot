import discord
import random
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

    @commands.command(name="roll")
    async def roll(self, context):
        PRICE = 1
        database_helper.adjust_pity(context.message.author.id)
        details = database_helper.get_user_details(context.message.author.id)
        if PRICE < details[0]:
            r = random.randint(1, 1000)
            if 1 <= r <= details[1]:
                options = database_helper.get_roll(3)
                database_helper.adjust_pity(context.message.author.id, False)
            elif details[1] < r <= details[1] + details[2]:
                options = database_helper.get_roll(4)
                database_helper.adjust_pity(context.message.author.id, False)
            elif details[1] + details[2] < r <= details[1] + details[2] + details[3]:
                options = database_helper.get_roll(5)
                database_helper.adjust_pity(context.message.author.id, True)
            elif details[1] + details[2] + details[3] < r <= 1000:
                options = database_helper.get_roll(1)
                database_helper.adjust_pity(context.message.author.id, True)
            gacha = options[random.randint(0, len(options) - 1)][0]
            title = "{} Summoned: \n".format(context.message.author.name)
            description = gacha
            database_helper.adjust_points(context.message.author.id)
            balance = database_helper.get_pikapoints(context.message.author.id)
            await context.send("You now have " + str(balance) + " pikapoints", embed=discord.Embed(title=title, description=description, color=0x9370db))
        else:
            await context.send("`You don't have enough pikapoints to summon!")


    @commands.command(name="focus")
    async def focus(self, context):
        focus = database_helper.get_focus()
        title = "Focus Units: "
        description = ''
        for unit in focus:
            description = description + "\n" + unit[0]
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))
        


def setup(bot):
    bot.add_cog(SenpaiShop())
