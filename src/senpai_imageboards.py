import random
import requests

import discord

from discord.ext import commands


class SenpaiImageboard:

    @commands.group()
    async def daily(self, context):
        if (context.invoked_subcommand is None):
            imageboards = [self.yandere, self.danbooru,
                           self.konachan, self.gelbooru]
            await random.choice(imageboards).reinvoke(context)

    @daily.command()
    async def help(self, context):
        reply = ("`usage:`\n" +
                "`!senpai daily\n" + "!senpai daily yandere\n" +
                "!senpai daily danbooru\n" + "!senpai daily konachan\n" +
                "!senpai daily gelbooru\n`")
        await context.send(reply)

    @daily.command()
    async def yandere(self, context):
        # link for yande.re's json api
        api_url = "https://yande.re/post.json?limit=1"
        post_url = "https://yande.re/post/show/{}"

        # get json contents
        json_content = requests.get(api_url).json()
        if (len(json_content) <= 0):
            await context.send("Error: API down?")
            return

        json_content = json_content[0]

        if ("id" not in json_content or "sample_url" not in json_content):
            await context.send("Error: failed to parse json")
            return

        post_id = json_content["id"]
        file_url = json_content["sample_url"]

        embed_msg = discord.Embed(title="yandere: #{}".format(post_id),
                            url=post_url.format(post_id),
                            color=0xff93ac)
        embed_msg.set_image(url=file_url)

        await context.send(embed=embed_msg)

    @daily.command()
    async def danbooru(self, context):
        api_url = "http://danbooru.donmai.us/posts.json?limit=1"
        post_url = "https://danbooru.donmai.us/posts/{}"

        # get json contents
        json_content = requests.get(api_url).json()
        if (len(json_content) <= 0):
            await context.send("Error: API down?")
            return

        json_content = json_content[0]

        if ("id" not in json_content or "file_url" not in json_content):
            await context.send("Error: failed to parse json")
            return

        post_id = json_content["id"]
        file_url = json_content["file_url"]
        if ("donmai.us" not in file_url):
            file_url = "https://danbooru.donmai.us" + file_url

        embed_msg = discord.Embed(title="danbooru: #{}".format(post_id),
                            url=post_url.format(post_id),
                            color=0xff93ac)
        embed_msg.set_image(url=file_url)

        await context.send(embed=embed_msg)

    @daily.command()
    async def gelbooru(self, context):
        api_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=1"
        post_url = "https://gelbooru.com/index.php?page=post&s=view&id={}"

        # get json contents
        json_content = requests.get(api_url).json()
        if (len(json_content) <= 0):
            await context.send("Error: API down?")
            return

        json_content = json_content[0]

        if ("id" not in json_content or "file_url" not in json_content):
            await context.send("Error: failed to parse json")
            return

        post_id = json_content["id"]
        file_url = json_content["file_url"]

        embed_msg = discord.Embed(title="gelbooru: #{}".format(post_id),
                            url=post_url.format(post_id),
                            color=0xff93ac)
        embed_msg.set_image(url=file_url)

        await context.send(embed=embed_msg)

    @daily.command()
    async def konachan(self, context):
        # link for konachan.com's json api
        api_url = "https://konachan.com/post.json?limit=1"
        post_url = "http://konachan.com/post/show/{}"

        # get json contents
        json_content = requests.get(api_url).json()
        if (len(json_content) <= 0):
            await context.send("Error: API down?")
            return

        json_content = json_content[0]

        if ("id" not in json_content or "file_url" not in json_content):
            await context.send("Error: failed to parse json")
            return

        post_id = json_content["id"]
        file_url = json_content["sample_url"]

        embed_msg = discord.Embed(title="konachan: #{}".format(post_id),
                            url=post_url.format(post_id),
                            color=0xff93ac)
        embed_msg.set_image(url=file_url)

        await context.send(embed=embed_msg)

def setup(bot):
    bot.add_cog(SenpaiImageboard())
