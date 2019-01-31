import discord
from discord.ext import commands
import database_helper

class SenpaiShop:
    @commands.command(name="balance")
    async def balance(self, context):
        user_id = context.message.author.id
        balance = database_helper.get_pikapoints(user_id)
        await context.send("You have " + str(balance) + " pikapoints")
def setup(bot):
    bot.add_cog(SenpaiShop())
