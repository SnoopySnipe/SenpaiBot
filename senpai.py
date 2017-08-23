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
    message_content = message.content
    """Answers question with a yes or no."""
    if (message_content.startswith("!8ball")):
        offset = len("!8ball")
        question = message_content[offset+1:]
        if len(question) > 0:
            reply = ("`Question: " + question + "\n" +
                     "Answer: " + answers[random.randint(0, num_answers)] + "`")
        else:
            reply = ("`Kouhai, dou shita no?`")
        await bot.send_message(message.channel, reply)
            
        
    """Help menu for commands."""
    if (message_content == "!help"):
        reply = "`!8ball <question>`                                            Senpai knows all..."
        await bot.send_message(message.channel, reply)        

# @bot.command()
# async def fortune(question : str):
    # reply = "`" + answers[random.randint(0, num_answers)] + "`"
    # await bot.say(reply)

bot.run(token)
bot.logout()
