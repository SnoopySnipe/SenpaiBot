import random

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
        reply = ("`Question: " + question + "\n" +
                 "Answer: " + _8ball_answers[answer_index] + "`")

        await self.bot.say(reply)


def setup(bot):
    bot.add_cog(Senpai8ball(bot))

