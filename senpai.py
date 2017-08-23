import sys
import discord
from discord.ext import commands
import random

description = '''The senpai of the server.'''

# amount of arguments
argc = len(sys.argv)
# bot token
token = ""

# parse command line arguments
for i in range(argc):
    if (sys.argv[i] == "-t" and i < argc):
        token = sys.argv[i+1]

bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def fortune(question : str):
    """Answers your question with a yes or no."""
    answers = ["It is certain", \
               "It is decidedly so", \
               "Without a doubt", \
               "Yes definitely", \
               "You may rely on it", \
               "As I see it yes", \
               "Most likely", \
               "Outlook good", \
               "Yes", \
               "Signs point to yes", \
               "Reply hazy try again", \
               "Ask again later", \
               "Better not tell you now", \
               "Cannot predict now", \
               "Concentrate and ask again", \
               "Don't count on it", \
               "My reply is no", \
               "My sources say no", \
               "Outlook not so good", \
               "Very doubtful"]
    await bot.say("`" + answers[random.randint(0, len(answers))-1] + "`")

bot.run(token)
