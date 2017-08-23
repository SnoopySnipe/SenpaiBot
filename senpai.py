import discord
from discord.ext import commands
import random

description = '''The senpai of the server.'''

bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
@bot.command()
async def ball(question : str):
    """Answers your question with a yes or no."""
    await bot.say('Yes.')

bot.run("token")