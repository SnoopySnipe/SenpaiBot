import random
import requests

import discord

from discord.ext import commands


class SenpaiImageboard:

    @commands.group()
    async def daily(self, context):
        if (context.invoked_subcommand is None):
            imageboards = [self.yandere, self.danbooru,
                           self.konachan, self.gelbooru, self.safebooru]
            await random.choice(imageboards).reinvoke(context)

    @daily.command()
    async def yandere(self, context):
        # link for yande.re's json api
        api_url = "https://yande.re/post.json?limit=1"

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
        post_url = "https://yande.re/post/show/{}".format(post_id)

        await _send_embed_imageboard_msg(context,
                                   title="yandere: #{}".format(post_id),
                                   post_url=post_url,
                                   file_url=file_url)

    @daily.command()
    async def danbooru(self, context):
        api_url = "http://danbooru.donmai.us/posts.json?limit=1"

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
        post_url = "https://danbooru.donmai.us/posts/{}".format(post_id)

        if ("donmai.us" not in file_url):
            file_url = "https://danbooru.donmai.us" + file_url

        await _send_embed_imageboard_msg(context,
                                   title="danbooru: #{}".format(post_id),
                                   post_url=post_url,
                                   file_url=file_url)

    @daily.command()
    async def gelbooru(self, context):
        api_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=1"

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
        post_url = "https://gelbooru.com/index.php?page=post&s=view&id={}".format(post_id)

        await _send_embed_imageboard_msg(context,
                                   title="gelbooru: #{}".format(post_id),
                                   post_url=post_url,
                                   file_url=file_url)

    @daily.command()
    async def safebooru(self, context):
        api_url = "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit=1"

        # get json contents
        json_content = requests.get(api_url).json()
        if (len(json_content) <= 0):
            await context.send("Error: API down?")
            return

        json_content = json_content[0]

        for key in ["id", "image", "directory"]:
            if (key not in json_content):
                await context.send("Error: failed to parse json")
                return

        post_id = json_content["id"]
        file_url = "https://safebooru.org/images/{}/{}".format(
                        json_content["directory"], json_content["image"])
        post_url = "https://safebooru.org/index.php?page=post&s=view&id={}".format(post_id)


        await _send_embed_imageboard_msg(context,
                                   title="safebooru: #{}".format(post_id),
                                   post_url=post_url,
                                   file_url=file_url)

    @daily.command()
    async def konachan(self, context):
        # link for konachan.com's json api
        api_url = "https://konachan.com/post.json?limit=1"

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
        post_url = "http://konachan.com/post/show/{}".format(post_id)

        await _send_embed_imageboard_msg(context,
                                   title="konachan: #{}".format(post_id),
                                   post_url=post_url,
                                   file_url=file_url)


async def _send_embed_imageboard_msg(context, title, post_url, file_url):
        embed_msg = discord.Embed(title=title,
                            url=post_url,
                            color=0xff93ac)
        embed_msg.set_image(url=file_url)

        await context.send(embed=embed_msg)


def setup(bot):
    bot.add_cog(SenpaiImageboard())
