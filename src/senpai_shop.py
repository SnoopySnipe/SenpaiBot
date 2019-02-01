import discord
import random
from discord.ext import commands
import database_helper


class SenpaiGacha:

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
            description = "3⭐: 54.0%\n4⭐: 42.0%\n5⭐: 1.0%\nFocus: 3.0%"
        else:
            description = "3⭐: {}%\n4⭐: {}%\n5⭐: {}%\nFocus: {}%".format(pity[0]/10, pity[1]/10, pity[2]/10, pity[3]/10)
            
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

    @commands.command(name="roll")
    async def roll(self, context):
        PRICE = 1
        database_helper.adjust_pity(context.message.author.id)
        details = database_helper.get_user_details(context.message.author.id)
        if details is None:
            await context.send("You have no pikapoints! Join voice and start earning!")
        elif PRICE <= details[0]:
            r = random.randint(0, 1003)
            if r == 0:
                options = database_helper.get_roll(7)
                database_helper.adjust_pity(context.message.author.id, True)
            elif 1001 <= r <= 1003:
                options = database_helper.get_roll(6)
                database_helper.adjust_pity(context.message.author.id, True)
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
            gacha = options[random.randint(0, len(options) - 1)]
            title = "{} Summoned: \n".format(context.message.author.name)
            if gacha[2] <= 5:
                description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
            elif gacha[2] == 6:
                description = gacha[0] + "\nRarity: Legendary"
            elif gacha[2] == 7:
                description = gacha[0] + "\nRarity: Mythic"
            database_helper.adjust_points(context.message.author.id)
            balance = database_helper.get_pikapoints(context.message.author.id)
            await context.send("You now have " + str(balance) + " pikapoints", embed=discord.Embed(title=title, description=description, color=0x9370db))
            await context.send("https://bulbapedia.bulbagarden.net/wiki/{}_(Pok%C3%A9mon)".format(gacha[0]))
        else:
            await context.send("`You don't have enough pikapoints to summon!`")

    @commands.command(name="units")
    async def units(self, context):
        units = database_helper.get_units()
        focus = []
        five = []
        four = []
        three = []
        for unit in units:
            if unit[2] == 1:
                focus.append(unit[0])
            elif unit[1] == 5:
                five.append(unit[0])
            elif unit[1] == 4:
                four.append(unit[0])
            elif unit[1] == 3:
                three.append(unit[0])
        title = "Focus Units: \n"
        description = ''
        for unit in focus:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

        title = "5⭐ Units: \n"
        description = ''
        for unit in five:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

        title = "4⭐ Units: \n"
        description = ''
        for unit in four:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))


        title = "3⭐ Units: \n"
        description = ''
        for unit in three:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))


    @commands.command(name="focus")
    async def focus(self, context):
        focus = database_helper.get_focus()
        title = "Focus Units: "
        description = ''
        for unit in focus:
            description = description + "\n" + unit[0]
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))
        


def setup(bot):
    bot.add_cog(SenpaiGacha())
