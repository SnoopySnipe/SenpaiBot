import random

import discord
from discord.ext import commands
_fortnite_location_pics = {
    "Anarchy Acres": "images/fortnite_locations/anarchy_acres.png",
    "Dusty Divot": "images/fortnite_locations/dusty_divot.png",
    "Fatal Fields": "images/fortnite_locations/fatal_fields.png",
    "Flush Factory": "images/fortnite_locations/flush_factory.png",
    "Greasy Grove": "images/fortnite_locations/greasy_grove.png",
    "Haunted Hills": "images/fortnite_locations/haunted_hills.png",
    "Junk Junction": "images/fortnite_locations/junk_junction.png",
    "Lonely Lodge": "images/fortnite_locations/lonely_lodge.png",
    "Loot Lake": "images/fortnite_locations/loot_lake.png",
    "Lucky Landing": "images/fortnite_locations/lucky_landing.png",
    "Moisty Mire": "images/fortnite_locations/moisty_mire.png",
    "Pleasant Park": "images/fortnite_locations/pleasant_park.png",
    "Retail Row": "images/fortnite_locations/retail_row.png",
    "Risky Reels": "images/fortnite_locations/risky_reels.png",
    "Salty Springs": "images/fortnite_locations/salty_springs.png",
    "Shifty Shafts": "images/fortnite_locations/shifty_shafts.png",
    "Snobby Shores": "images/fortnite_locations/snobby_shores.png",
    "Tilted Towers": "images/fortnite_locations/tilted_towers.png",
    "Tomato Town": "images/fortnite_locations/tomato_town.png",
    "Wailing Woods": "images/fortnite_locations/wailing_woods.png",
    "A37": "images/fortnite_locations/a37.jpg"
    }

_fortnite_locations = list(_fortnite_location_pics.keys())

class SenpaiFortnite:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def wherewedroppingbois(self, context):
        await _send_fortnite_location(self.bot, context.message)

    @commands.command(pass_context=True)
    async def drop(self, context):
        await _send_fortnite_location(self.bot, context.message)


def setup(bot):
    bot.add_cog(SenpaiFortnite(bot))

# Fortnite dropman
async def _send_fortnite_location(bot, message):
    answer_index = random.randint(0, len(_fortnite_locations)-1)
    location = _fortnite_locations[answer_index]
    location_pic = _fortnite_location_pics[location]
    reply = "We dropping " + location + " bois"
    drop_msg = await bot.send_file(message.channel, location_pic, content=reply)

    lensflare = discord.Emoji(id=425828826027655178, server=218898501805801472) 
    await bot.add_reaction(drop_msg, lensflare)
