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

        OG_IMAGE_TAG = '<meta property="og:image" content="'

        index = web_content.find(OG_IMAGE_TAG)
        if (index == -1):
            await context.send("`Operator, my codex does not seem to have an entry for this`")
            return

        og_img_url = web_content[index + len(OG_IMAGE_TAG):]
        index = og_img_url.find('"')
        og_img_url = og_img_url[:index]

        embed_msg = discord.Embed(title=mod_name,
                            url=mod_url,
                            color=0xff93ac)
        embed_msg.set_image(url=og_img_url)

        TWITTER_DESC_TAG = '<meta name="twitter:description" content="'

        index = web_content.find(TWITTER_DESC_TAG)
        if (index != -1):
            twitter_desc = web_content[index + len(TWITTER_DESC_TAG):]
            index = twitter_desc.find('"')
            twitter_desc = twitter_desc[:index]
            embed_msg.add_field(name="Description", value=twitter_desc, inline=True)

        await context.send(embed=embed_msg)

def setup(bot):
    bot.add_cog(SenpaiWarframe())
