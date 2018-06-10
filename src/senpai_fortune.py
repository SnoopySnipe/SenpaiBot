import requests

from discord.ext import commands


class SenpaiFortune:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fortunecookie():
        await bot.say(_helloacm_get_fortune_cookie())


def setup(bot):
    bot.add_cog(SenpaiFortune(bot))


def _helloacm_get_fortune_cookie():

    api_url = "https://helloacm.com/api/fortune/"

    # get json contents
    json_content = requests.get(api_url).json()

    return json_content

if (__name__ == "__main__"):
    fortune = _helloacm_get_fortune_cookie()
    print(fortune)
