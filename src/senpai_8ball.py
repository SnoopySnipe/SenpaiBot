import random

import discord

from discord.ext import commands

_8ball_answers = [
           # yes like answers
           "Yes",
           "It is certain",
           "It is decidedly so",
           "Without a doubt",
           "Yes definitely",
           "You may rely on it",
           "As I see it yes",
           "Most likely",
           "Outlook good",
           "Signs point to yes",

           # no like answers
           "No",
           "My reply is no",
           "My sources say no",
           "Don't count on it",
           "Outlook not so good",
           "As I see it no",
           "Signs point to no",
           "Not likely",
           "Very doubtful",

           # bad answers
           "Reply hazy try again",
           "Ask again later",
           "Better not tell you now",
           "Cannot predict now",
           "Concentrate and ask again",
           ]

class Senpai8ball:

    def __init__(self, bot):
        self.bot = bot

    # Answers question with a yes or no
    @commands.command(name="8ball", pass_context=True)
    async def _8ball(self, context):
        offset = len("!senpai 8ball")

        question = context.message.content[offset+1:]

        # check if user actually asked a question
        if (len(question) == 0):
            await self.bot.say("`Kouhai, dou shita no?`")
            return

        answer_index = random.randint(0, len(_8ball_answers)-1)

        embed_msg = discord.Embed(color=0xff93ac)
        embed_msg.add_field(name="`Question:`", value=question, inline=False)
        embed_msg.add_field(name="`Answer:`", value=_8ball_answers[answer_index],
                        inline=False)

        await self.bot.say(embed=embed_msg)

    @commands.command()
    async def guess(self, guess_num):
        rand_num = random.randint(1,10)
        try:
            guess_num = int(guess_num)
            if (guess_num == rand_num):
                reply = "`Congratulations, you guessed it right!`"
            else:
                reply = ("`Sorry, the number was " + str(rand_num) + "`")
        # Prompt for a valid input
        except ValueError:
            reply = "Please enter a number between 1 and 10."
        await self.bot.say(reply)

    @commands.command()
    async def coin(self):
        flip = random.randint(0,1)
        if (flip == 0):
            reply = "`Tails`"
        elif (flip == 1):
            reply = "`Heads`"
        await self.bot.say(reply)


def setup(bot):
    bot.add_cog(Senpai8ball(bot))

