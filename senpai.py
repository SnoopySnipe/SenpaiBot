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

answers = ["It is certain",
           "It is decidedly so",
           "Without a doubt",
           "Yes definitely",
           "You may rely on it",
           "As I see it yes",
           "Most likely",
           "Outlook good",
           "Yes",
           "Signs point to yes",
           "Reply hazy try again",
           "Ask again later",
           "Better not tell you now",
           "Cannot predict now",
           "Concentrate and ask again",
           "Don't count on it",
           "My reply is no",
           "My sources say no",
           "Outlook not so good",
           "Very doubtful"]
num_answers = len(answers) - 1

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    """Answers your question with a yes or no."""
    message_content = message.content

    if (message_content.startswith("!fortune")):
        offset = len("!fortune")
        question = message_content[offset+1:]
        reply = ("`Question: " + question + "\n" +
          "Answer: " + answers[random.randint(0, num_answers)] + "`")

        await bot.send_message(message.channel, reply)

# @bot.command()
# async def fortune(question : str):

#    reply = "`" + answers[random.randint(0, num_answers)] + "`"
#    await bot.say(reply)

bot.run(token)
bot.logout()
