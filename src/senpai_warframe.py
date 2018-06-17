import asyncio
import urllib.request

from discord.ext import commands


class SenpaiWarframe:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def codex(self, context):
        offset = len("!senpai codex")

        mod_name = context.message.content[offset+1:]

        # check if user actually asked a question
        if (len(mod_name) == 0):
            await self.bot.say("`Operator, would you like to tell me what you are looking for?`")
            return

        tmp_list = [elem.capitalize() for elem in mod_name.split()]
        mod_name = "_".join(elem for elem in tmp_list)

        try:
            f = urllib.request.urlopen("http://warframe.wikia.com/wiki/{}".format(mod_name))
        except urllib.error.HTTPError:
            await self.bot.say("`Operator, my codex does not seem to have an entry for this`")
            return

        web_content = f.read().decode("utf-8")

        index = web_content.find('<meta property="og:image" content="')
        if (index == -1):
            await self.bot.say("`Operator, my codex does not seem to have an entry for this`")
            return

        web_content = web_content[index + len('<meta property="og:image" content="'):]
        index = web_content.find('"')
        mod_url = web_content[:index]
        await self.bot.say(mod_url.format(context))

def setup(bot):
    bot.add_cog(SenpaiWarframe(bot))
