import discord
from discord.ext import commands
import database_helper


class SenpaiShop:

    @commands.command(name="balance")
    async def balance(self, context):
        user_id = context.message.author.id
        balance = database_helper.get_pikapoints(user_id)
        await context.send("You have " + str(balance) + " pikapoints")

    @commands.command(name="pikalogue")
    async def pikalogue(self, context):
        pikalogue = database_helper.get_pikalogue()
        for item in pikalogue:
            title = "Item #{}: {}\n".format(item[0], item[1])
            description = "Description: {}\n\nPrice: {} pikapoints"
            await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))


def setup(bot):
    bot.add_cog(SenpaiShop())
