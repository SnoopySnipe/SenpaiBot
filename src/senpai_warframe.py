import asyncio
import urllib.request

import discord

from discord.ext import commands

class SenpaiWarframe:

    @commands.command()
    async def codex(self, context):
        offset = len("!senpai codex")

        mod_name = context.message.content[offset+1:]

        # check if user actually asked a question
        if (len(mod_name) == 0):
            await context.send("`Operator, would you like to tell me what you are looking for?`")
            return

        tmp_list = [elem.capitalize() for elem in mod_name.split()]
        mod_name = "_".join(elem for elem in tmp_list)

        mod_url = "http://warframe.wikia.com/wiki/{}".format(mod_name)

        try:
            f = urllib.request.urlopen(mod_url)
        except urllib.error.HTTPError:
            await context.send("`Operator, my codex does not seem to have an entry for this`")
            return

        web_content = f.read().decode("utf-8")

        index = web_content.find('<meta property="og:image" content="')
        if (index == -1):
            await context.send("`Operator, my codex does not seem to have an entry for this`")
            return

        web_content = web_content[index + len('<meta property="og:image" content="'):]
        index = web_content.find('"')
        mod_img_url = web_content[:index]

        embed_msg = discord.Embed(title=mod_name,
                            url=mod_url,
                            color=0xff93ac)
        embed_msg.set_image(url=mod_img_url)

        await context.send(embed=embed_msg)

def setup(bot):
    bot.add_cog(SenpaiWarframe())
