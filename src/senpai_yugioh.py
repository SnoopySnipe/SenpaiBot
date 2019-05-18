import asyncio

import discord
import webpreview

from discord.ext import commands

COLOR=0xff93ac

_YUGIOH_WIKIA_URL = "http://yugioh.wikia.com/wiki/{}"

class SenpaiYugioh(commands.Cog):

    @commands.command()
    async def yugioh(self, context):
        offset = len("!yugioh")

        card_name = context.message.content[offset+1:].strip()

        # check if user actually asked a question
        if (len(card_name) == 0):
            await context.send("`Usage: !yugioh [card name]`")
            return

        tmp_list = card_name.split()
        card_name = "_".join(elem for elem in tmp_list)

        formatted_url = _YUGIOH_WIKIA_URL.format(card_name)
        print("url: ", formatted_url)

        try:
            title, description, image_url = webpreview.web_preview(formatted_url)
            embed_msg = discord.Embed(title=title,
                            url=formatted_url,
                            color=COLOR)
            embed_msg.add_field(name="Description", value=description, inline=True)
            embed_msg.set_image(url=image_url)
            await context.send(embed=embed_msg)
        except Exception as e:
            print(repr(e))
            await context.send("`KaibaCorp does not have any information on this card`")

def setup(bot):
    bot.add_cog(SenpaiYugioh())
