import requests

import discord

from discord.ext import commands

class SenpaiFortune:

    @commands.command()
    async def fortune(self, context):
        await context.send(_helloacm_get_fortune_cookie())

def setup(bot):
    bot.add_cog(SenpaiFortune())


def _helloacm_get_fortune_cookie():

    api_url = "https://helloacm.com/api/fortune/"

    # get json contents
    json_content = requests.get(api_url).json()

    return json_content

if (__name__ == "__main__"):
    fortune = _helloacm_get_fortune_cookie()
    print(fortune)
