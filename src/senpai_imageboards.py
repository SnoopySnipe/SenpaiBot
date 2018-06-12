import random
import requests

from discord.ext import commands


class SenpaiImageboard:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def daily(self, context):
        if (context.invoked_subcommand is None):
            imageboards = [self.yandere, self.danbooru,
                           self.konachan, self.gelbooru]
            await random.choice(imageboards).invoke(context)

    @daily.command()
    async def help(self):
        reply = ("`usage:`\n" +
                "`!senpai daily\n" + "!senpai daily yandere\n" +
                "!senpai daily danbooru\n" + "!senpai daily konachan\n" +
                "!senpai daily gelbooru\n`")
        await self.bot.say(reply)

    @daily.command()
    async def yandere(self):
        json_content = _yandere_get_latest_post()
        if (json_content is None):
            await self.bot.say("Error: API down?")
            return
        if ("id" not in json_content or "sample_url" not in json_content):
            await self.bot.say("Error: json parse failed")
            return

        post_id = json_content["id"]
        file_url = json_content["sample_url"]

        bot_reply = "`yandere #" + str(post_id) + "`\n" + file_url
        await self.bot.say(bot_reply)

    @daily.command()
    async def danbooru(self):
        json_content = _danbooru_get_latest_post()
        if (json_content is None):
            await self.bot.say("Error: API down?")
            return
        if ("id" not in json_content or "file_url" not in json_content):
            await self.bot.say("Error: json parse failed")
            return

        post_id = json_content["id"]
        file_url = json_content["file_url"]
        if ("donmai.us" not in file_url):
            file_url = "https://danbooru.donmai.us" + file_url

        bot_reply = "`danbooru #" + str(post_id) + "`\n" + file_url
        await self.bot.say(bot_reply)

    @daily.command()
    async def gelbooru(self):
        json_content = _gelbooru_get_latest_post()
        if (json_content is None):
            await self.bot.say("Error: API down?")
            return
        if ("id" not in json_content or "file_url" not in json_content):
            await self.bot.say("Error: json parse failed")
            return

        post_id = json_content["id"]
        file_url = json_content["file_url"]

        bot_reply = "`gelbooru #" + str(post_id) + "`\n" + file_url
        await self.bot.say(bot_reply)

    @daily.command()
    async def konachan(self):
        json_content = _konachan_get_latest_post()
        if (json_content is None):
            await self.bot.say("Error: API down?")
            return
        if ("id" not in json_content or "file_url" not in json_content):
            await self.bot.say("Error: json parse failed")
            return

        post_id = json_content["id"]
        file_url = json_content["sample_url"]

        bot_reply = "`konachan #" + str(post_id) + "`\n" + file_url
        await self.bot.say(bot_reply)


def setup(bot):
    bot.add_cog(SenpaiImageboard(bot))


def _yandere_get_latest_post():
    '''(void) -> dict


    '''

    # link for yande.re's json api
    api_url = "https://yande.re/post.json?limit=1"

    # get json contents
    json_content = requests.get(api_url).json()
    if (len(json_content) > 0):
        return json_content[0]


def _danbooru_get_latest_post():

    api_url = "http://danbooru.donmai.us/posts.json?limit=1"

    # get json contents
    json_content = requests.get(api_url).json()
    if (len(json_content) > 0):
        return json_content[0]


def _gelbooru_get_latest_post():

    api_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=1"

    json_content = requests.get(api_url).json()
    if (len(json_content) > 0):
        return json_content[0]


def _konachan_get_latest_post():
    '''(void) -> dict


    '''

    # link for konachan.com's json api
    api_url = "https://konachan.com/post.json?limit=1"

    # get json contents
    json_content = requests.get(api_url).json()
    if (len(json_content) > 0):
        return json_content[0]


if (__name__ == "__main__"):
    print("Yandere:")
    json_content = yandere_get_latest_post()
    print(json_content["id"])
    print(json_content["sample_url"])

    print("Danbooru:")
    json_content = danbooru_get_latest_post()
    print(json_content["id"])
    print(json_content["file_url"])

    print("Gelbooru")
    json_content = gelbooru_get_latest_post()
    print(json_content["id"])
    print(json_content["file_url"])

    print("Konachan:")
    json_content = konachan_get_latest_post()
    print(json_content["id"])
    print(json_content["sample_url"])
