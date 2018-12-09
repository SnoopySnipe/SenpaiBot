import asyncio

import discord
import webpreview

from discord.ext import commands

COLOR=0xff93ac

_WARFRAME_WIKIA_URL = "http://warframe.wikia.com/wiki/{}"

class SenpaiWarframe:

    @commands.command()
    async def codex(self, context):
        offset = len("!senpai codex")

        mod_name = context.message.content[offset+1:].strip()

        # check if user actually asked a question
        if (len(mod_name) == 0):
            await context.send("`Operator, what codex entry are looking for?`")
            return

        tmp_list = [elem.capitalize() for elem in mod_name.split()]
        mod_name = "_".join(elem for elem in tmp_list)

        mod_url = _WARFRAME_WIKIA_URL.format(mod_name)

        try:
            title, description, image_url = webpreview.web_preview(mod_url)
            embed_msg = discord.Embed(title=title,
                            url=mod_url,
                            color=COLOR)
            embed_msg.add_field(name="Description", value=description, inline=True)
            embed_msg.set_image(url=image_url)
            await context.send(embed=embed_msg)
        except Exception as e:
            print(repr(e))
            await context.send("`Operator, my codex does not seem to have an entry for this`")

def setup(bot):
    bot.add_cog(SenpaiWarframe())
