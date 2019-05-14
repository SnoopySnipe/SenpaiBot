import discord
import random
from discord.ext import commands
import database_helper
import pokebase as pb
import asyncio
import datetime
import time
from PIL import Image, ImageFont, ImageDraw
import requests
from io import BytesIO
import math

SNOOPY_ID = 103634047929962496
KANTO = ('Kanto', 1, 151)
JOHTO = ('Johto', 152, 251)
HOENN = ('Hoenn', 252, 386)
SINNOH = ('Sinnoh', 387, 493)
UNOVA = ('Unova', 494, 649)
KALOS = ('Kalos', 650, 721)
ALOLA = ('Alola', 722, 809)
SPECIAL = ('Special', 10000, 11000)
REGIONS = [KANTO, JOHTO, HOENN, SINNOH, UNOVA, KALOS, ALOLA]
COMMANDS_CHANNEL_ID = 282336977418715146
LEAGUE_ID = 401518684763586560

SPECIAL_POKEMON = {
    10000: 'https://cdn.bulbagarden.net/upload/a/aa/Flying_Pikachu_Dash.png',
    10001: 'https://www.serebii.net/sunmoon/pokemon/384-m.png',
    10002: 'https://www.serebii.net/sunmoon/pokemon/382-p.png',
    10003: 'https://www.serebii.net/sunmoon/pokemon/383-p.png',
    10004: 'https://www.serebii.net/sunmoon/pokemon/428-m.png',
    10005: 'https://www.serebii.net/sunmoon/pokemon/648-s.png',
    10006: 'https://www.serebii.net/sunmoon/pokemon/658-a.png',
    10007: 'https://www.serebii.net/sunmoon/pokemon/800-u.png',
	10008: 'https://cdn.bulbagarden.net/upload/f/f5/Detective_Pikachu_artwork_2.png'
}

SPRITE_MAPPING = {
    10000: 'https://cdn.bulbagarden.net/upload/a/aa/Flying_Pikachu_Dash.png',
    10001: 10079,
    10002: 10077,
    10003: 10078,
    10004: 10088,
    10005: 10018,
    10006: 'https://www.serebii.net/sunmoon/pokemon/658-a.png',
    10007: 'https://www.serebii.net/sunmoon/pokemon/800-u.png',
	10008: 'https://cdn.bulbagarden.net/upload/f/f5/Detective_Pikachu_artwork_2.png'
}

class SenpaiGacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.league_players = []

    @commands.Cog.listener()
    async def on_ready(self):
        database_helper.initialize(str(self.bot.guilds[0].id))
        self.bot.loop.create_task(self.background_quiz())

    async def on_member_update(self, before, after):
        if(type(after.activity) == discord.activity.Activity and self.in_champ_select(before)):
            if(after.id not in self.league_players):
                self.league_players.append(after.id)
        elif(self.in_game(before) and not self.in_game(after) and after.id in self.league_players):
            for activity in before.activities:
                if(type(activity) == discord.activity.Activity and activity.application_id == LEAGUE_ID):
                    channel = self.bot.get_channel(COMMANDS_CHANNEL_ID)
                    end_time = int(time.time())
                    start = str(activity.timestamps["start"])
                    start_time = int(start[:len(str(end_time))])
                    game_minutes = (int(time.time()) - start_time)//60
                    self.league_players.remove(after.id)
                    if(game_minutes >= 15):
                        database_helper.add_pikapoints(after.id, 30)
                        earn_string = " and earned 30 pikapoints!"
                    else:
                        earn_string = ""
                    await channel.send("`{} was in a league game for {} minutes{}`".format(after.name, game_minutes, earn_string))
    def in_champ_select(self, member):
        for activity in member.activities:
            if(type(activity) == discord.activity.Activity and activity.state == "In Champion Select" and  "Custom" not in activity.details and activity.application_id == LEAGUE_ID):
                return True
        return False
    def in_game(self, member):
        for activity in member.activities:
            if(type(activity) == discord.activity.Activity and activity.state == "In Game" and activity.application_id == LEAGUE_ID):
                return True
        return False

    @commands.command(name="balance")
    async def balance(self, context, user_id=None):
        if user_id is None:
            user_id = context.message.author.id
        username = self.bot.get_user(int(user_id)).name
        balance = database_helper.get_pikapoints(user_id)
        if (balance is None):
            await context.send("{} has no pikapoints!".format(username))
        else:
            await context.send(username + " has " + str(balance) + " pikapoints")

    @commands.command(name="pity")
    async def pity(self, context, user_id=None):
        if user_id is None:
            user_id = context.message.author.id
        username = self.bot.get_user(int(user_id)).name
        pity = database_helper.get_pity(user_id)
        title = "{}'s Pity Rates: \n".format(username)
        if pity is None:
            description = "3⭐: 54.0%\n4⭐: 42.0%\n5⭐: 3.0%\nFocus: 1.0%"
        else:
            description = "3⭐: {}%\n4⭐: {}%\n5⭐: {}%\nFocus: {}%".format(pity[0]/10, pity[1]/10, pity[2]/10, pity[3]/10)

        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

    # @commands.command(name="forceroll")
    # async def forceroll(self, context, region=None, user_id=None):
    #     if context.message.author.id != SNOOPY_ID:
    #         await context.send("Y'all'th'st'd've'ish ain't Snoopy")
    #         return
    #
    #     PRICE = 30
    #     if user_id is None:
    #         await context.send("user_id cannot be None!")
    #         return
    #     user = self.bot.get_user(int(user_id))
    #     username = user.name
    #     database_helper.adjust_pity(user_id)
    #     details = database_helper.get_user_details(user_id)
    #     if details is None:
    #         await context.send("{} has no pikapoints! Join voice and start earning!".format(username))
    #     elif PRICE <= details[0]:
    #         balance = details[0]
    #         rolls = balance // 30
    #
    #         if region is None:
    #             await context.send("`Usage:`\n\n```!forceroll region user_id```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
    #             return
    #
    #         if region == 'kanto':
    #             region = KANTO
    #         elif region == 'johto':
    #             region = JOHTO
    #         elif region == 'hoenn':
    #             region = HOENN
    #         elif region == 'sinnoh':
    #             region = SINNOH
    #         elif region == 'unova':
    #             region = UNOVA
    #         # elif region == 'kalos':
    #         #     region = KALOS
    #         # elif region == 'alola':
    #         #     region = ALOLA
    #         elif region == 'all':
    #             region = None
    #         else:
    #             await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'all')")
    #             return
    #
    #         if rolls == 0:
    #             await context.send("There is nothing to roll...")
    #             return
    #
    #         await context.send("{} currently has {} pikapoints.\nRolling {} times...".format(username, str(balance), str(rolls)))
    #         database_helper.adjust_points(user_id, -(PRICE * rolls))
    #         for i in range(rolls):
    #             details = database_helper.get_user_details(user_id)
    #             r = random.randint(0, 1003)
    #             if r == 0:
    #                 options = database_helper.get_roll(7, region)
    #                 database_helper.adjust_pity(user_id, True)
    #                 database_helper.update_jackpot(user_id, False)
    #             elif 1001 <= r <= 1003:
    #                 options = database_helper.get_roll(6, region)
    #                 database_helper.adjust_pity(user_id, True)
    #                 database_helper.update_jackpot(user_id, False)
    #             elif 1 <= r <= details[1]:
    #                 options = database_helper.get_roll(3, region)
    #                 database_helper.adjust_pity(user_id, False)
    #                 database_helper.update_jackpot(user_id, False)
    #             elif details[1] < r <= details[1] + details[2]:
    #                 options = database_helper.get_roll(4, region)
    #                 database_helper.adjust_pity(user_id, False)
    #                 database_helper.update_jackpot(user_id, False)
    #             elif details[1] + details[2] < r <= details[1] + details[2] + details[3]:
    #                 options = database_helper.get_roll(5, region)
    #                 database_helper.adjust_pity(user_id, True)
    #                 database_helper.update_jackpot(user_id, False)
    #             elif details[1] + details[2] + details[3] < r <= 1000:
    #                 options = database_helper.get_roll(1, region)
    #                 database_helper.adjust_pity(user_id, True)
    #                 database_helper.update_jackpot(user_id, False)
    #             gacha = options[random.randint(0, len(options) - 1)]
    #             title = "{} Summoned: \n".format(username)
    #             if gacha[2] <= 5:
    #                 description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
    #             elif gacha[2] == 6:
    #                 description = gacha[0] + "\nRarity: Legendary"
    #             elif gacha[2] == 7:
    #                 description = gacha[0] + "\nRarity: Mythic"
    #             database_helper.add_inventory(user_id, gacha[1])
    #             embed = discord.Embed(title=title, description=description, color=0x9370db)
    #             str_id = "{:03}".format(gacha[1])
    #             url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
    #             embed.set_thumbnail(url=url)
    #             await context.send(embed=embed)
    #             if gacha[2] > 5:
    #                 jackpot = database_helper.get_jackpot(True)[0]
    #                 no_contributors = len(database_helper.get_jackpot_rewards())
    #                 if no_contributors == 0:
    #                     if gacha[2] == 6:
    #                         str_rarity = 'Legendary'
    #                     elif gacha[2] == 7:
    #                         str_rarity = 'Mythic'
    #                     await context.send(
    #                         '{} summoned a {} Pokémon! The jackpot contained {} pikapoints. No users contributed at least 3 pikapoints to the jackpot, therefore the jackpot will not be reset.'.format(
    #                             username, str_rarity, jackpot))
    #                     continue
    #
    #                 ball = random.randint(1, 10000)
    #                 master_chance = min(jackpot, 1000)
    #                 ultra_chance = master_chance * 3
    #                 great_chance = master_chance * 6
    #                 if 1 <= ball <= master_chance:
    #                     ball_str = 'Master Ball'
    #                     ball_id = 4
    #                 elif master_chance < ball <= master_chance + ultra_chance:
    #                     ball_str = 'Ultra Ball'
    #                     ball_id = 3
    #                 elif master_chance + ultra_chance < ball <= master_chance + ultra_chance + great_chance:
    #                     ball_str = 'Great Ball'
    #                     ball_id = 2
    #                 elif master_chance + ultra_chance + great_chance < ball <= 10000:
    #                     ball_str = 'Poké Ball'
    #                     ball_id = 1
    #
    #                 msg = username + ' summoned a '
    #                 if gacha[2] == 6:
    #                     payout = jackpot // no_contributors
    #                     msg = msg + 'Legendary Pokémon! The jackpot contained {} pikapoints. The following users contributed at least 3 pikapoints to the jackpot and will each receive {} pikapoints and a **{}**:```'.format(
    #                         jackpot, payout, ball_str)
    #                 elif gacha[2] == 7:
    #                     payout = (jackpot * 2) // no_contributors
    #                     msg = msg + 'Mythic Pokémon! The jackpot contained {} pikapoints --> x2 Mythic Multiplier --> {} pikapoints. The following users contributed at least 3 pikapoints to the jackpot and will each receive {} pikapoints and a **{}**:```'.format(
    #                         jackpot, jackpot * 2, payout, ball_str)
    #                 contributors = database_helper.get_jackpot(False)
    #                 for contributor in contributors:
    #                     if contributor[1] >= 3:
    #                         database_helper.adjust_points(contributor[0], payout)
    #                         database_helper.add_item(contributor[0], ball_id)
    #                         msg = msg + '\n' + self.bot.get_user(contributor[0]).name
    #                 msg = msg + '```'
    #                 database_helper.update_jackpot(user_id, True)
    #                 await context.send(msg)
    #         balance = database_helper.get_pikapoints(user_id)
    #         await context.send("{} now has {} pikapoints.".format(username, str(balance)))
    #     else:
    #         await context.send("{} doesn't have enough pikapoints to summon! It costs {} pikapoints per roll!".format(username, str(PRICE)))

    @commands.command(name="fullroll")
    async def fullroll(self, context, region=None, no_rolls=None):
        PRICE = 30
        user_id = context.message.author.id
        user = self.bot.get_user(user_id)
        username = user.name
        database_helper.adjust_pity(user_id)
        details = database_helper.get_user_details(user_id)
        if details is None:
            await context.send("You have no pikapoints! Join voice and start earning!")
        elif PRICE <= details[0]:
            balance = details[0]
            rolls = balance // 30

            if region is None:
                await context.send("`Usage:`\n\n```!fullroll region [no_rolls]```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
                return

            if region == 'kanto':
                region = KANTO
            elif region == 'johto':
                region = JOHTO
            elif region == 'hoenn':
                region = HOENN
            elif region == 'sinnoh':
                region = SINNOH
            elif region == 'unova':
                region = UNOVA
            elif region == 'kalos':
                region = KALOS
            elif region == 'alola':
                region = ALOLA
            elif region == 'all':
                region = None
            else:
                await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'kalos', 'alola', 'all')")
                return

            if no_rolls == 'jackpot':
                no_rolls = rolls - 3
                rolls = max(no_rolls, 0)
            elif no_rolls is not None:
                try:
                    no_rolls = int(no_rolls)
                    is_int = True
                except:
                    is_int = False

                if is_int:
                    if no_rolls <= rolls:
                        rolls = max(no_rolls, 0)
                    else:
                        await context.send("You cannot roll that many times!")
                        return
                else:
                    await context.send("Number of rolls must be an integer or 'jackpot'")
                    return

            if rolls == 0:
                await context.send("There is nothing to roll...")
                return

            brick = True

            await context.send("You currently have {} pikapoints.\nRolling {} times...".format(str(balance), str(rolls)))
            database_helper.adjust_points(user_id, -(PRICE*rolls))
            for i in range(rolls):
                details = database_helper.get_user_details(user_id)
                r = random.randint(0, 1003)
                if r == 0:
                    options = database_helper.get_roll(7, region)
                    specials = database_helper.get_roll(8, None)
                    for special in specials:
                        options.append(special)
                    database_helper.adjust_pity(user_id, True)
                    database_helper.update_jackpot(user_id, False)
                    if rolls >= 50:
                        brick = False
                elif 1001 <= r <= 1003:
                    options = database_helper.get_roll(6, region)
                    specials = database_helper.get_roll(8, None)
                    for special in specials:
                        options.append(special)
                    database_helper.adjust_pity(user_id, True)
                    database_helper.update_jackpot(user_id, False)
                    if rolls >= 50:
                        brick = False
                elif 1 <= r <= details[1]:
                    options = database_helper.get_roll(3, region)
                    database_helper.adjust_pity(user_id, False)
                    database_helper.update_jackpot(user_id, False)
                elif details[1] < r <= details[1] + details[2]:
                    options = database_helper.get_roll(4, region)
                    database_helper.adjust_pity(user_id, False)
                    database_helper.update_jackpot(user_id, False)
                elif details[1] + details[2] < r <= details[1] + details[2] + details[3]:
                    options = database_helper.get_roll(5, region)
                    database_helper.adjust_pity(user_id, True)
                    database_helper.update_jackpot(user_id, False)
                elif details[1] + details[2] + details[3] < r <= 1000:
                    options = database_helper.get_roll(1, region)
                    database_helper.adjust_pity(user_id, True)
                    database_helper.update_jackpot(user_id, False)
                gacha = options[random.randint(0, len(options) - 1)]
                title = "{} Summoned: \n".format(username)
                if gacha[2] <= 5:
                    description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
                elif gacha[2] == 6:
                    description = gacha[0] + "\nRarity: Legendary"
                elif gacha[2] == 7:
                    description = gacha[0] + "\nRarity: Mythic"
                elif gacha[2] == 8:
                    description = gacha[0] + "\nRarity: Special"
                database_helper.add_inventory(user_id, gacha[1])
                embed = discord.Embed(title=title, description=description, color=0x9370db)
                if gacha[1] >= 10000:
                    url = SPECIAL_POKEMON[gacha[1]]
                else:
                    str_id = "{:03}".format(gacha[1])
                    url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
                embed.set_thumbnail(url=url)
                await context.send(embed=embed)
                database_helper.increment_stat(user_id, "rolls")
                database_helper.update_exp(user_id, 1)
                promote = database_helper.promote(user_id)
                if promote is not None:
                    await context.send(promote)
                if gacha[2] > 5:
                    jackpot = database_helper.get_jackpot(True)[0]
                    no_contributors = len(database_helper.get_jackpot_rewards())
                    if no_contributors == 0:
                        if gacha[2] == 6:
                            str_rarity = 'Legendary'
                        elif gacha[2] == 7:
                            str_rarity = 'Mythic'
                        elif gacha[2] == 8:
                            str_rarity = 'Special'
                        await context.send(
                            '{} summoned a {} Pokémon! The jackpot contained {} pikapoints. No users contributed at least 3 pikapoints to the jackpot, therefore the jackpot will not be reset.'.format(
                                username, str_rarity, jackpot))
                        continue

                    ball = random.randint(1, 10000)
                    master_chance = min(jackpot, 1000)
                    ultra_chance = master_chance * 3
                    great_chance = master_chance * 6
                    if 1 <= ball <= master_chance:
                        ball_str = 'Master Ball'
                        ball_id = 4
                    elif master_chance < ball <= master_chance + ultra_chance:
                        ball_str = 'Ultra Ball'
                        ball_id = 3
                    elif master_chance + ultra_chance < ball <= master_chance + ultra_chance + great_chance:
                        ball_str = 'Great Ball'
                        ball_id = 2
                    elif master_chance + ultra_chance + great_chance < ball <= 10000:
                        ball_str = 'Poké Ball'
                        ball_id = 1

                    msg = username + ' summoned a '
                    if gacha[2] == 6:
                        payout = jackpot // no_contributors
                        msg = msg + 'Legendary Pokémon! The jackpot contained {} pikapoints. The following users contributed at least 3 pikapoints to the jackpot and will each receive {} pikapoints and a **{}**:'.format(
                            jackpot, payout, ball_str)
                    elif gacha[2] == 7:
                        payout = (jackpot * 2) // no_contributors
                        msg = msg + 'Mythic Pokémon! The jackpot contained {} pikapoints --> x2 Mythic Multiplier --> {} pikapoints. The following users contributed at least 3 pikapoints to the jackpot and will each receive {} pikapoints and a **{}**:'.format(
                            jackpot, jackpot * 2, payout, ball_str)
                    elif gacha[2] == 8:
                        ball_id = max(3, ball_id)
                        if ball_id == 3:
                            ball_str = 'Ultra Ball'
                        elif ball_id == 4:
                            ball_str = 'Master Ball'
                        payout = jackpot // no_contributors
                        msg = msg + 'Special Pokémon! The jackpot contained {} pikapoints. The following users contributed at least 3 pikapoints to the jackpot and will each receive {} pikapoints and a **{}**:'.format(
                            jackpot, payout, ball_str)
                    contributors = database_helper.get_jackpot(False)
                    for contributor in contributors:
                        if contributor[1] >= 3:
                            database_helper.adjust_points(contributor[0], payout)
                            database_helper.add_item(contributor[0], ball_id)
                            database_helper.increment_stat(contributor[0], "jackpots")
                            msg = msg + '\n' + self.bot.get_user(contributor[0]).mention
                    database_helper.update_jackpot(user_id, True)
                    await context.send(msg)
            balance = database_helper.get_pikapoints(user_id)
            await context.send("You now have {} pikapoints.".format(str(balance)))
            if brick and rolls >= 50:
                database_helper.increment_stat(user_id, "bricks")
        else:
            await context.send("You don't have enough pikapoints to summon! It costs {} pikapoints per roll!".format(str(PRICE)))

    @commands.command(name="roll")
    async def roll(self, context, region=None):
        PRICE = 30
        user_id = context.message.author.id
        user = self.bot.get_user(user_id)
        username = user.name
        database_helper.adjust_pity(user_id)
        details = database_helper.get_user_details(user_id)
        if details is None:
            await context.send("You have no pikapoints! Join voice and start earning!")
        elif PRICE <= details[0]:
            r = random.randint(0, 1003)
            if region == 'kanto':
                region = KANTO
            elif region == 'johto':
                region = JOHTO
            elif region == 'hoenn':
                region = HOENN
            elif region == 'sinnoh':
                region = SINNOH
            elif region == 'unova':
                region = UNOVA
            elif region == 'kalos':
                region = KALOS
            elif region == 'alola':
                region = ALOLA
            elif region is not None:
                await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'kalos', 'alola', None)")
                return

            if r == 0:
                options = database_helper.get_roll(7, region)
                specials = database_helper.get_roll(8, None)
                for special in specials:
                    options.append(special)
                database_helper.adjust_pity(user_id, True)
                database_helper.update_jackpot(user_id, False)
            elif 1001 <= r <= 1003:
                options = database_helper.get_roll(6, region)
                specials = database_helper.get_roll(8, None)
                for special in specials:
                    options.append(special)
                database_helper.adjust_pity(user_id, True)
                database_helper.update_jackpot(user_id, False)
            elif 1 <= r <= details[1]:
                options = database_helper.get_roll(3, region)
                database_helper.adjust_pity(user_id, False)
                database_helper.update_jackpot(user_id, False)
            elif details[1] < r <= details[1] + details[2]:
                options = database_helper.get_roll(4, region)
                database_helper.adjust_pity(user_id, False)
                database_helper.update_jackpot(user_id, False)
            elif details[1] + details[2] < r <= details[1] + details[2] + details[3]:
                options = database_helper.get_roll(5, region)
                database_helper.adjust_pity(user_id, True)
                database_helper.update_jackpot(user_id, False)
            elif details[1] + details[2] + details[3] < r <= 1000:
                options = database_helper.get_roll(1, region)
                database_helper.adjust_pity(user_id, True)
                database_helper.update_jackpot(user_id, False)
            gacha = options[random.randint(0, len(options) - 1)]
            title = "{} Summoned: \n".format(username)
            if gacha[2] <= 5:
                description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
            elif gacha[2] == 6:
                description = gacha[0] + "\nRarity: Legendary"
            elif gacha[2] == 7:
                description = gacha[0] + "\nRarity: Mythic"
            elif gacha[2] == 8:
                description = gacha[0] + "\nRarity: Special"
            database_helper.adjust_points(user_id, -PRICE)
            balance = database_helper.get_pikapoints(user_id)
            database_helper.add_inventory(user_id, gacha[1])
            embed = discord.Embed(title=title, description=description, color=0x9370db)
            if gacha[1] >= 10000:
                url = SPECIAL_POKEMON[gacha[1]]
            else:
                str_id = "{:03}".format(gacha[1])
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            embed.set_thumbnail(url=url)
            await context.send("You now have " + str(balance) + " pikapoints.", embed=embed)
            database_helper.increment_stat(user_id, "rolls")
            database_helper.update_exp(user_id, 1)
            promote = database_helper.promote(user_id)
            if promote is not None:
                await context.send(promote)
            if gacha[2] > 5:
                jackpot = database_helper.get_jackpot(True)[0]
                no_contributors = len(database_helper.get_jackpot_rewards())
                if no_contributors == 0:
                    if gacha[2] == 6:
                        str_rarity = 'Legendary'
                    elif gacha[2] == 7:
                        str_rarity = 'Mythic'
                    elif gacha[2] == 8:
                        str_rarity = 'Special'
                    await context.send('{} summoned a {} Pokémon! The jackpot contained {} pikapoints. No users contributed at least 3 pikapoints to the jackpot, therefore the jackpot will not be reset.'.format(username, str_rarity, jackpot))
                    return

                ball = random.randint(1, 10000)
                master_chance = min(jackpot, 1000)
                ultra_chance = master_chance * 3
                great_chance = master_chance * 6
                if 1 <= ball <= master_chance:
                    ball_str = 'Master Ball'
                    ball_id = 4
                elif master_chance < ball <= master_chance + ultra_chance:
                    ball_str = 'Ultra Ball'
                    ball_id = 3
                elif master_chance + ultra_chance < ball <= master_chance + ultra_chance + great_chance:
                    ball_str = 'Great Ball'
                    ball_id = 2
                elif master_chance + ultra_chance + great_chance < ball <= 10000:
                    ball_str = 'Poké Ball'
                    ball_id = 1

                msg = username + ' summoned a '
                if gacha[2] == 6:
                    payout = jackpot // no_contributors
                    msg = msg + 'Legendary Pokémon! The jackpot contained {} pikapoints. The following users contributed at least 3 pikapoints to the jackpot and will each receive {} pikapoints and a **{}**:'.format(
                        jackpot, payout, ball_str)
                elif gacha[2] == 7:
                    payout = (jackpot * 2) // no_contributors
                    msg = msg + 'Mythic Pokémon! The jackpot contained {} pikapoints --> x2 Mythic Multiplier --> {} pikapoints. The following users contributed at least 3 pikapoints to the jackpot and will each receive {} pikapoints and a **{}**:'.format(
                        jackpot, jackpot * 2, payout, ball_str)
                elif gacha[2] == 8:
                    ball_id = max(3, ball_id)
                    if ball_id == 3:
                        ball_str = 'Ultra Ball'
                    elif ball_id == 4:
                        ball_str = 'Master Ball'
                    payout = jackpot // no_contributors
                    msg = msg + 'Special Pokémon! The jackpot contained {} pikapoints. The following users contributed at least 3 pikapoints to the jackpot and will each receive {} pikapoints and a **{}**:'.format(
                        jackpot, payout, ball_str)
                contributors = database_helper.get_jackpot(False)
                for contributor in contributors:
                    if contributor[1] >= 3:
                        database_helper.adjust_points(contributor[0], payout)
                        database_helper.add_item(contributor[0], ball_id)
                        database_helper.increment_stat(contributor[0], "jackpots")
                        msg = msg + '\n' + self.bot.get_user(contributor[0]).mention
                database_helper.update_jackpot(user_id, True)
                await context.send(msg)
        else:
            await context.send("You don't have enough pikapoints to summon! It costs {} pikapoints per roll!".format(str(PRICE)))

    @commands.command(name="pokedex")
    async def pokedex(self, context, name=None, special=False):
        if name is None:
            await context.send("`Usage:`\n\n```!pokedex pokemon_name_or_id```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return
        poke_id = database_helper.get_pokemon(name)
        poke_name = database_helper.get_pokemon_name(name)
        if poke_id is not None:
            id = poke_id[0]
            if id >= 10000:
                url = SPECIAL_POKEMON[id]
            else:
                str_id = "{:03}".format(id)
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            if 1 <= id <= 151:
                region = 'Kanto'
            elif 152 <= id <= 251:
                region = 'Johto'
            elif 252 <= id <= 386:
                region = 'Hoenn'
            elif 387 <= id <= 493:
                region = 'Sinnoh'
            elif 494 <= id <= 649:
                region = 'Unova'
            elif 650 <= id <= 721:
                region = 'Kalos'
            elif 722 <= id <= 809:
                region = 'Alola'
            elif id >= 10000:
                region = 'Special'
            dex = discord.Embed(title="ID: {}\nName: {}\nBST: {}\nRegion: {}".format(str(poke_id[0]), name, poke_id[2], region), color=0xffb6c1)
            dex.set_image(url=url)
            if special:
                await context.send("Current Special Unit", embed=dex)
            else:
                await context.send(embed=dex)
        elif poke_name is not None:
            id = int(name)
            if id >= 10000:
                url = SPECIAL_POKEMON[id]
            else:
                str_id = "{:03}".format(id)
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            if 1 <= id <= 151:
                region = 'Kanto'
            elif 152 <= id <= 251:
                region = 'Johto'
            elif 252 <= id <= 386:
                region = 'Hoenn'
            elif 387 <= id <= 493:
                region = 'Sinnoh'
            elif 494 <= id <= 649:
                region = 'Unova'
            elif 650 <= id <= 721:
                region = 'Kalos'
            elif 722 <= id <= 809:
                region = 'Alola'
            elif id >= 10000:
                region = 'Special'
            dex = discord.Embed(title="ID: {}\nName: {}\nBST: {}\nRegion: {}".format(str(name), poke_name[0], poke_name[1], region), color=0xffb6c1)
            dex.set_image(url=url)
            if special:
                await context.send("Current Special Unit", embed=dex)
            else:
                await context.send(embed=dex)
        else:
            await context.send("Pokémon name or ID doesn't exist!")

    @commands.command(name="trade")
    async def trade(self, context, pokemon1=None, pokemon2=None, id2=None):
        if pokemon1 is None or pokemon2 is None or id2 is None:
            await context.send("`Usage:`\n\n```!trade your_pokemon their_pokemon their_id```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return
        id1 = context.message.author.id

        pokemon1_id = database_helper.get_pokemon(pokemon1)
        if pokemon1_id is not None:
            if database_helper.get_from_inventory(id1, pokemon1_id[0]):
                rarity1 = pokemon1_id[1]
            else:
                await context.send("You do not have that Pokémon!")
                return
        else:
            await context.send("Invalid Pokémon name!")
            return

        pokemon2_id = database_helper.get_pokemon(pokemon2)
        if pokemon2_id is not None:
            if database_helper.get_from_inventory(id2, pokemon2_id[0]):
                rarity2 = pokemon2_id[1]
            else:
                await context.send("They do not have that Pokémon!")
                return
        else:
            await context.send("Invalid Pokémon name!")
            return

        if pokemon1 == pokemon2:
            await context.send("Pokémon must be different!")
            return

        if rarity1 == rarity2:
            cost = 60 * rarity1
        else:
            await context.send("Pokémon's rarities must match!")
            return

        user1 = self.bot.get_user(int(id1))
        user2 = self.bot.get_user(int(id2))
        username1 = user1.name
        username2 = user2.name

        if user1 == user2:
            await context.send("You cannot trade with yourself!")
            return

        balance1 = database_helper.get_pikapoints(id1)
        balance2 = database_helper.get_pikapoints(id2)
        if balance1 < cost:
            await context.send("You don't have enough pikapoints to perform this trade! This trade requires both users to have {} pikapoints.\nYou have {} pikapoints. They have {} pikapoints.".format(str(cost), str(balance1), str(balance2)))
            return
        if balance2 < cost:
            await context.send("They don't have enough pikapoints to perform this trade! This trade requires both users to have {} pikapoints.\nYou have {} pikapoints. They have {} pikapoints.".format(str(cost), str(balance1), str(balance2)))
            return

        title = "Trade Request"
        description = "{} wants to trade: {}\nFor {}'s: {}".format(username1, pokemon1, username2, pokemon2)
        msg = await context.send(embed=discord.Embed(title=title, description=description, color=0xff0000))
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        def check(reaction, user):
            return (user == user2 and str(reaction.emoji) == '✅') or ((user == user1 or user == user2) and str(reaction.emoji) == '❌')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await context.send("Trade timed out...")
        else:
            if str(reaction.emoji) == '❌':
                await context.send("Trade declined...")
            elif str(reaction.emoji) == '✅':
                database_helper.perform_trade(id1, id2, pokemon1_id[0], pokemon2_id[0])
                database_helper.adjust_points(id1, -cost)
                database_helper.adjust_points(id2, -cost)
                new_balance1 = database_helper.get_pikapoints(id1)
                new_balance2 = database_helper.get_pikapoints(id2)
                await context.send("{} has {} pikapoints. {} has {} pikapoints.\nPerforming trade...\nTrade successful! {} now has {} pikapoints. {} now has {} pikapoints.".format(
                    username1, str(balance1), username2, str(balance2), username1, str(new_balance1), username2, str(new_balance2)
                ))
                database_helper.increment_stat(id1, "trades")
                database_helper.increment_stat(id2, "trades")

    # @commands.command(name="forceopen")
    # async def forceopen(self, context, user_id=None, ball=None):
    #     if context.message.author.id != SNOOPY_ID:
    #         await context.send("Y'all'th'st'd've'ish ain't Snoopy")
    #         return
    #
    #     if user_id is None:
    #         await context.send("`Usage:`\n\n```!forceopen user_id```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
    #         return
    #
    #     if ball is None:
    #         bag = database_helper.get_bag(user_id)
    #         bag_list = []
    #         for item in bag:
    #             for i in range(item[1]):
    #                 if item[0] == 1:
    #                     bag_list.append('pokeball')
    #                 elif item[0] == 2:
    #                     bag_list.append('greatball')
    #                 elif item[0] == 3:
    #                     bag_list.append('ultraball')
    #                 elif item[0] == 4:
    #                     bag_list.append('masterball')
    #         for ball in bag_list:
    #             await context.invoke(self.forceopen, user_id, ball)
    #         return
    #
    #     if ball == 'pokeball':
    #         ball_id = 1
    #     elif ball == 'greatball':
    #         ball_id = 2
    #     elif ball == 'ultraball':
    #         ball_id = 3
    #     elif ball == 'masterball':
    #         ball_id = 4
    #
    #     user = self.bot.get_user(int(user_id))
    #     username = user.name
    #
    #     database_helper.use_item(user_id, ball_id)
    #
    #     option = random.randint(0, 1)
    #     if option == 0:
    #         if ball_id == 1:
    #             pt_range = (1, 15)
    #             ball_str = 'Poké Ball'
    #         elif ball_id == 2:
    #             pt_range = (15, 30)
    #             ball_str = 'Great Ball'
    #         elif ball_id == 3:
    #             pt_range = (30, 60)
    #             ball_str = 'Ultra Ball'
    #         elif ball_id == 4:
    #             pt_range = (60, 150)
    #             ball_str = 'Master Ball'
    #         pt_prize = random.randint(pt_range[0], pt_range[1])
    #         database_helper.adjust_points(user_id, pt_prize)
    #         balance = database_helper.get_pikapoints(user_id)
    #         await context.send("{} opened a {} and got {} pikapoints! They now have {} pikapoints.".format(username, ball_str,
    #                                                                                                  pt_prize, balance))
    #     elif option == 1:
    #         if ball_id == 1:
    #             ball_str = 'Poké Ball'
    #             roll_range = {
    #                 3: 60,
    #                 4: 40,
    #             }
    #             roll = random.randint(1, 100)
    #             if 1 <= roll <= roll_range[3]:
    #                 options = database_helper.get_roll(3)
    #             elif roll_range[3] < roll <= 100:
    #                 options = database_helper.get_roll(4)
    #         elif ball_id == 2:
    #             ball_str = 'Great Ball'
    #             roll_range = {
    #                 3: 50,
    #                 4: 40,
    #                 5: 10
    #             }
    #             roll = random.randint(1, 100)
    #             if 1 <= roll <= roll_range[3]:
    #                 options = database_helper.get_roll(3)
    #             elif roll_range[3] < roll <= roll_range[3] + roll_range[4]:
    #                 options = database_helper.get_roll(4)
    #             elif roll_range[3] + roll_range[4] < roll <= 100:
    #                 options = database_helper.get_roll(5)
    #         elif ball_id == 3:
    #             ball_str = 'Ultra Ball'
    #             roll_range = {
    #                 4: 60,
    #                 5: 35,
    #                 6: 5
    #             }
    #             roll = random.randint(1, 100)
    #             if 1 <= roll <= roll_range[4]:
    #                 options = database_helper.get_roll(4)
    #             elif roll_range[4] < roll <= roll_range[4] + roll_range[5]:
    #                 options = database_helper.get_roll(5)
    #             elif roll_range[4] + roll_range[5] < roll <= 100:
    #                 options = database_helper.get_roll(6)
    #         elif ball_id == 4:
    #             ball_str = 'Master Ball'
    #             roll_range = {
    #                 5: 85,
    #                 6: 10,
    #                 7: 5
    #             }
    #             roll = random.randint(1, 100)
    #             if 1 <= roll <= roll_range[5]:
    #                 options = database_helper.get_roll(5)
    #             elif roll_range[5] < roll <= roll_range[5] + roll_range[6]:
    #                 options = database_helper.get_roll(6)
    #             elif roll_range[5] + roll_range[6] < roll <= 100:
    #                 options = database_helper.get_roll(7)
    #         gacha = random.choice(options)
    #         title = "{} Opened: \n".format(username)
    #         if gacha[2] <= 5:
    #             description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
    #         elif gacha[2] == 6:
    #             description = gacha[0] + "\nRarity: Legendary"
    #         elif gacha[2] == 7:
    #             description = gacha[0] + "\nRarity: Mythic"
    #         database_helper.add_inventory(user_id, gacha[1])
    #         embed = discord.Embed(title=title, description=description, color=0x9370db)
    #         str_id = "{:03}".format(gacha[1])
    #         url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
    #         embed.set_thumbnail(url=url)
    #         await context.send("{} opened a {} and got a {}!".format(username, ball_str, gacha[0]), embed=embed)

    @commands.command(name="open")
    async def open(self, context, ball=None):
        if ball is None:
            await context.send("`Usage:`\n\n```!open ball_name```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        if ball not in ('pokeball', 'greatball', 'ultraball', 'masterball', 'all'):
            await context.send("Ball name must be in ('pokeball', 'greatball', 'ultraball', 'masterball', 'all')")
            return

        if ball == 'pokeball':
            ball_id = 1
        elif ball == 'greatball':
            ball_id = 2
        elif ball == 'ultraball':
            ball_id = 3
        elif ball == 'masterball':
            ball_id = 4
        elif ball == 'all':
            bag = database_helper.get_bag(context.message.author.id)
            bag_list = []
            for item in bag:
                for i in range(item[1]):
                    if item[0] == 1:
                        bag_list.append('pokeball')
                    elif item[0] == 2:
                        bag_list.append('greatball')
                    elif item[0] == 3:
                        bag_list.append('ultraball')
                    elif item[0] == 4:
                        bag_list.append('masterball')
            for ball in bag_list:
                await context.invoke(self.open, ball)
            return

        user_id = context.message.author.id
        user = self.bot.get_user(user_id)
        username = user.name
        if not database_helper.check_bag(user_id, ball_id):
            await context.send("You do not have that item!")
            return

        database_helper.use_item(user_id, ball_id)

        option = random.randint(0, 1)
        if option == 0:
            if ball_id == 1:
                pt_range = (1, 15)
                ball_str = 'Poké Ball'
            elif ball_id == 2:
                pt_range = (15, 30)
                ball_str = 'Great Ball'
            elif ball_id == 3:
                pt_range = (30, 60)
                ball_str = 'Ultra Ball'
            elif ball_id == 4:
                pt_range = (60, 150)
                ball_str = 'Master Ball'
            pt_prize = random.randint(pt_range[0], pt_range[1])
            database_helper.adjust_points(user_id, pt_prize)
            balance = database_helper.get_pikapoints(user_id)
            await context.send("{} opened a {} and got {} pikapoints! They now have {} pikapoints.".format(username, ball_str, pt_prize, balance))
            database_helper.increment_stat(user_id, "opens")
        elif option == 1:
            if ball_id == 1:
                ball_str = 'Poké Ball'
                roll_range = {
                    3: 60,
                    4: 40,
                }
                roll = random.randint(1, 100)
                if 1 <= roll <= roll_range[3]:
                    options = database_helper.get_roll(3)
                elif roll_range[3] < roll <= 100:
                    options = database_helper.get_roll(4)
            elif ball_id == 2:
                ball_str = 'Great Ball'
                roll_range = {
                    3: 50,
                    4: 40,
                    5: 10
                }
                roll = random.randint(1, 100)
                if 1 <= roll <= roll_range[3]:
                    options = database_helper.get_roll(3)
                elif roll_range[3] < roll <= roll_range[3] + roll_range[4]:
                    options = database_helper.get_roll(4)
                elif roll_range[3] + roll_range[4] < roll <= 100:
                    options = database_helper.get_roll(5)
            elif ball_id == 3:
                ball_str = 'Ultra Ball'
                roll_range = {
                    4: 60,
                    5: 35,
                    6: 5
                }
                roll = random.randint(1, 100)
                if 1 <= roll <= roll_range[4]:
                    options = database_helper.get_roll(4)
                elif roll_range[4] < roll <= roll_range[4] + roll_range[5]:
                    options = database_helper.get_roll(5)
                elif roll_range[4] + roll_range[5] < roll <= 100:
                    options = database_helper.get_roll(6)
                    specials = database_helper.get_roll(8, None)
                    for special in specials:
                        options.append(special)
            elif ball_id == 4:
                ball_str = 'Master Ball'
                roll_range = {
                    5: 85,
                    6: 10,
                    7: 5
                }
                roll = random.randint(1, 100)
                if 1 <= roll <= roll_range[5]:
                    options = database_helper.get_roll(5)
                elif roll_range[5] < roll <= roll_range[5] + roll_range[6]:
                    options = database_helper.get_roll(6)
                    specials = database_helper.get_roll(8, None)
                    for special in specials:
                        options.append(special)
                elif roll_range[5] + roll_range[6] < roll <= 100:
                    options = database_helper.get_roll(7)
                    specials = database_helper.get_roll(8, None)
                    for special in specials:
                        options.append(special)
            gacha = random.choice(options)
            title = "{} Opened: \n".format(username)
            if gacha[2] <= 5:
                description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
            elif gacha[2] == 6:
                description = gacha[0] + "\nRarity: Legendary"
            elif gacha[2] == 7:
                description = gacha[0] + "\nRarity: Mythic"
            elif gacha[2] == 8:
                description = gacha[0] + "\nRarity: Special"
            database_helper.add_inventory(user_id, gacha[1])
            embed = discord.Embed(title=title, description=description, color=0x9370db)
            if gacha[1] >= 10000:
                url = SPECIAL_POKEMON[gacha[1]]
            else:
                str_id = "{:03}".format(gacha[1])
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            embed.set_thumbnail(url=url)
            await context.send("{} opened a {} and got a {}!".format(username, ball_str, gacha[0]), embed=embed)
            database_helper.increment_stat(user_id, "opens")



    @commands.command(name="bag")
    async def bag(self, context, user_id=None):
        await self.bag_page(context, 1, user_id)

    async def bag_page(self, context, page_num, user_id):
        # img = Image.open('images/crate.png', 'r')
        if user_id is None:
            user_id = context.message.author.id
        username = self.bot.get_user(int(user_id)).name
        bag = database_helper.get_bag(user_id)
        if len(bag) == 0:
            await context.send("{} has no items in their bag!".format(username))
        else:
            page_indices = {1: (0, 0)}
            num_items = 0
            for item in bag:
                num_items += item[1]
            (save_location, curr_index, remain_num) = self.draw_bag(context, bag, 0, 0)
            file = discord.File(save_location, filename='bag.png')
            msg = await context.channel.send(username + "'s bag (page " + str(page_num) + ")", file=file)
            await msg.add_reaction("⬅")
            await msg.add_reaction("➡")

            def check(reaction, user):
                return user == context.message.author and (str(reaction.emoji) == "⬅" or str(reaction.emoji) == "➡")

            timed_out = False
            while (not timed_out):
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=5.0, check=check)
                except asyncio.TimeoutError:
                    timed_out = True
                else:
                    is_left = (str(reaction.emoji) == "⬅")
                    is_right = (str(reaction.emoji) == "➡")
                    if ((is_left and page_num - 1 >= 1) or (is_right and (num_items - (page_num) * 32) > 0)):
                        inc = -1 if is_left else 1
                        page_num += inc
                        if (page_num in page_indices):
                            (curr_index, remain_num) = page_indices[page_num]
                        if (page_num not in page_indices):
                            page_indices[page_num] = (curr_index, remain_num)
                        (save_location, curr_index, remain_num) = self.draw_bag(context, bag, curr_index,
                                                                                remain_num)
                        file = discord.File(save_location, filename='bag.png')
                        await msg.delete()
                        msg = await context.channel.send(username + "'s bag (page " + str(page_num) + ")", file=file)
                        await msg.add_reaction("⬅")
                        await msg.add_reaction("➡")

    def draw_bag(self, context, bag, index, remain_num):
        # background = Image.new('RGBA', (850,450), (255, 255, 255))
        background = Image.open('images/inv_background.png', 'r')
        background = background.resize((850, 450))
        (x, y) = (0, 0)
        count = 0
        remain_overflow = 0
        if (remain_num != 0):
            init = True
        else:
            init = False
        while (count < 32 and index < len(bag)):
            item = bag[index]
            if (init):
                item_num = remain_num
                init = False
            else:
                item_num = item[1]
            index += 1
            item_id = item[0]
            # sprite = pb.SpriteResource('pokemon', pokemon_id)
            # img = Image.open(sprite.path).convert("RGBA")
            if item_id == 1:
                item_str = 'pokeball'
            elif item_id == 2:
                item_str = 'greatball'
            elif item_id == 3:
                item_str = 'ultraball'
            elif item_id == 4:
                item_str = 'masterball'
            response = requests.get("https://www.serebii.net/itemdex/sprites/pgl/{}.png".format(item_str))
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            img = img.resize((150, 150))
            for i in range(item_num):
                # img = Image.open("images/pokemon/"+pokemon[2]+".png")
                offset = (x * 100, y * 100)
                background.paste(img, offset, img)
                count += 1
                if (count >= 32):
                    remain_overflow = item_num - i - 1
                    break;
                x += 1
                if (x == 8):
                    x = 0
                    y += 1
        save_location = 'images/' + str(context.message.author.id) + '.png'
        background.save(save_location)
        if (remain_overflow > 0):
            index -= 1
        return (save_location, index, remain_overflow)

    @commands.command(name="box")
    async def box(self, context, user_id=None, page_num=None):
        BOX_SIZE = 32

        if user_id is None or user_id == 'self':
            user_id = context.message.author.id

        user = self.bot.get_user(int(user_id))
        username = user.name
        box_list = database_helper.get_box(user_id)

        if page_num is None:
            page_num = 1

        if page_num == 'last':
            last_page = math.ceil(len(box_list) / BOX_SIZE)
            await context.invoke(self.box, user_id, last_page)
            return

        if page_num != 1:
            try:
                page_num = int(page_num)
            except:
                await context.send("Page number must be a positive integer or 'last'!")
                return
        if not page_num > 0:
            await context.send("Page number must be a positive integer or 'last'!")
            return

        if page_num == 1:
            begin = True
        else:
            begin = False
        end = False

        if len(box_list) <= (page_num - 1) * BOX_SIZE:
            await context.send("{} has no pokémon in box page {}!".format(username, page_num))
            return

        try:
            display = box_list[(page_num - 1) * BOX_SIZE:page_num * BOX_SIZE]
        except:
            display = box_list[(page_num - 1) * BOX_SIZE:]

        if len(box_list[page_num * BOX_SIZE:]) < 1:
            end = True

        background = Image.open('images/inv_background.png', 'r')
        background = background.resize((850, 450))
        (x, y) = (0, 0)
        for pokemon in display:
            pokemon_id = pokemon[0]
            if pokemon_id >= 10000:
                if pokemon_id in [10000, 10006, 10007, 10008]:
                    response = requests.get(SPRITE_MAPPING[pokemon_id])
                    img = Image.open(BytesIO(response.content)).convert("RGBA")
                    img = img.resize((100, 100))
                else:
                    sprite = pb.SpriteResource('pokemon', SPRITE_MAPPING[pokemon_id])
                    img = Image.open(sprite.path).convert("RGBA")
                    img = img.resize((150, 150))
            else:
                sprite = pb.SpriteResource('pokemon', pokemon_id)
                img = Image.open(sprite.path).convert("RGBA")
                img = img.resize((150,150))
            offset = (x * 100, y * 100)
            background.paste(img, offset, img)
            x += 1
            if (x == 8):
                x = 0
                y += 1
        save_location = 'images/' + str(context.message.author.id) + '.png'
        background.save(save_location)

        file = discord.File(save_location, filename='party.png')
        msg = await context.channel.send(username + "'s party (page " + str(page_num) + ")", file=file)
        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")

        def check(reaction, user):
            return user == context.message.author and ((str(reaction.emoji) == "⬅" and not begin) or (str(reaction.emoji) == "➡" and not end))

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            return
        else:
            if str(reaction.emoji) == '⬅' and not begin:
                await msg.delete()
                await context.invoke(self.box, user_id, page_num - 1)
            elif str(reaction.emoji) == '➡' and not end:
                await msg.delete()
                await context.invoke(self.box, user_id, page_num + 1)

    # @commands.command(name="box")
    # async def box(self, context, user_id=None):
    #     await self.box_page(context, 1, user_id)
    # async def box_page(self, context, page_num, user_id):
    # #img = Image.open('images/crate.png', 'r')
    #     if user_id is None:
    #         user_id = context.message.author.id
    #     username = self.bot.get_user(int(user_id)).name
    #     inventory = database_helper.get_inventory(user_id)
    #     if len(inventory) == 0:
    #         await context.send("You have no pokémon on page {}! Start rolling!".format(page_num))
    #     else:
    #         page_indices = {1:(0,0)}
    #         num_pokemon = 0
    #         for pokemon in inventory:
    #             num_pokemon += pokemon[4]
    #         (save_location, curr_index, remain_num) = self.draw_box(context, inventory, 0, 0)
    #         file = discord.File(save_location, filename='party.png')
    #         msg = await context.channel.send(username+"'s party (page " + str(page_num) +")", file=file)
    #         await msg.add_reaction("⬅")
    #         await msg.add_reaction("➡")
    #         def check(reaction, user):
    #             return user == context.message.author and (str(reaction.emoji) == "⬅" or str(reaction.emoji) == "➡")
    #         timed_out = False
    #         while(not timed_out):
    #             try:
    #                 reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
    #             except asyncio.TimeoutError:
    #                 timed_out = True
    #             else:
    #                 is_left = (str(reaction.emoji) == "⬅")
    #                 is_right = (str(reaction.emoji) == "➡")
    #                 if(( is_left and page_num-1>=1) or (is_right and (num_pokemon -(page_num)*32) > 0)):
    #                     inc = -1 if is_left else 1
    #                     page_num += inc
    #                     if(page_num in page_indices):
    #                         (curr_index, remain_num) = page_indices[page_num]
    #                     if(page_num not in page_indices):
    #                         page_indices[page_num] = (curr_index, remain_num)
    #                     (save_location, curr_index, remain_num) = self.draw_box(context, inventory, curr_index, remain_num)
    #                     file = discord.File(save_location, filename='party.png')
    #                     await msg.delete()
    #                     msg = await context.channel.send(username+"'s party (page " + str(page_num) +")", file=file)
    #                     await msg.add_reaction("⬅")
    #                     await msg.add_reaction("➡")
    # def draw_box(self, context, inventory, index, remain_num):
    #     #background = Image.new('RGBA', (850,450), (255, 255, 255))
    #     background = Image.open('images/inv_background.png', 'r')
    #     background = background.resize((850, 450))
    #     (x, y) = (0, 0)
    #     count = 0
    #     remain_overflow = 0
    #     if(remain_num != 0):
    #         init = True
    #     else:
    #         init = False
    #     while(count < 32 and index < len(inventory)):
    #         pokemon = inventory[index]
    #         if(init):
    #             pokemon_num = remain_num
    #             init = False
    #         else:
    #             pokemon_num = pokemon[4]
    #         index += 1
    #         pokemon_id = pokemon[1]
    #         if pokemon_id >= 10000:
    #             response = requests.get(SPECIAL_POKEMON[pokemon_id])
    #             img = Image.open(BytesIO(response.content)).convert("RGBA")
    #             img = img.resize((150, 150))
    #         else:
    #             sprite = pb.SpriteResource('pokemon', pokemon_id)
    #             img = Image.open(sprite.path).convert("RGBA")
    #             img = img.resize((150,150))
    #         for i in range(pokemon_num):
    #             #img = Image.open("images/pokemon/"+pokemon[2]+".png")
    #             offset = (x*100, y*100)
    #             background.paste(img, offset, img)
    #             count += 1
    #             if(count >= 32):
    #                 remain_overflow = pokemon_num - i - 1
    #                 break;
    #             x += 1
    #             if(x == 8):
    #                 x = 0
    #                 y += 1
    #     save_location = 'images/'+str(context.message.author.id)+'.png'
    #     background.save(save_location)
    #     if(remain_overflow > 0):
    #         index-=1
    #     return (save_location, index, remain_overflow)
    @commands.command(name="party")
    async def party(self, context, region=None, user_id=None):
        if region is None:
            await context.send("`Usage:`\n\n```!party region [user_id]```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        elif region == 'hoenn':
            region = HOENN
        elif region == 'sinnoh':
            region = SINNOH
        elif region == 'unova':
            region = UNOVA
        elif region == 'kalos':
            region = KALOS
        elif region == 'alola':
            region = ALOLA
        elif region == 'special':
            region = SPECIAL
        elif region is not None:
            await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'kalos', 'alola', 'special')")
            return
        if user_id is None:
            user_id = context.message.author.id
        username = self.bot.get_user(int(user_id)).name
        title = "{}'s {} Party: \n".format(username, region[0])
        description = ""
        inventory = database_helper.get_inventory(user_id, region)
        description = description + "\n**__" + region[0] + "__**"
        for poke in inventory:
            if poke[3] <= 5:
                description = description + "\n    {} {} - {}⭐".format(poke[4], poke[2], poke[3])
            elif poke[3] == 6:
                description = description + "\n    {} {} - Legendary".format(poke[4], poke[2])
            elif poke[3] == 7:
                description = description + "\n    {} {} - Mythic".format(poke[4], poke[2])
            elif poke[3] == 8:
                description = description + "\n    {} {} - Special".format(poke[4], poke[2])
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

    # @commands.command(name="forcerelease")
    # async def forcerelease(self, context, user_id=None, rarity=None):
    #     if context.message.author.id != SNOOPY_ID:
    #         await context.send("Y'all'th'st'd've'ish ain't Snoopy")
    #         return
    #
    #     if user_id is None:
    #         await context.send("`Usage:`\n\n```!forcerelease user_id```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
    #         return
    #
    #     if rarity is None:
    #         rarities = ['3', '4', '5']
    #         for r in rarities:
    #             await context.invoke(self.forcerelease, user_id, r)
    #         return
    #
    #     user = self.bot.get_user(int(user_id))
    #     username = user.name
    #     balance = database_helper.get_pikapoints(user_id)
    #     region = None
    #     str_region = "all regions"
    #     rows = database_helper.full_remove_inventory(user_id, rarity, region)
    #     if rows == 0:
    #         await context.send("There is no {}⭐ pokémon to release...".format(rarity))
    #         return
    #     if rarity == '3':
    #         gain = 5
    #     elif rarity == '4':
    #         gain = 10
    #     elif rarity == '5':
    #         gain = 15
    #     database_helper.adjust_points(user_id, gain * rows)
    #     total_gain = gain * rows
    #     await context.send(
    #         "{} currently has {} pikapoints.\nReleasing {} {}⭐ Pokémon from {}...\n{} got {} pikapoints!\n{} now has {} pikapoints.".format(
    #             username, str(balance), rows, rarity, str_region, username, total_gain, username,
    #             database_helper.get_pikapoints(user_id)))



    @commands.command(name="fullrelease")
    async def fullrelease(self, context, rarity=None, region=None):
        if rarity is None:
            await context.send("`Usage:`\n\n```!fullrelease rarity [region]```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return
        region_str = region
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        elif region == 'hoenn':
            region = HOENN
        elif region == 'sinnoh':
            region = SINNOH
        elif region == 'unova':
            region = UNOVA
        elif region == 'kalos':
            region = KALOS
        elif region == 'alola':
            region = ALOLA
        elif region is not None:
            await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'kalos', 'alola', None)")
            return

        if rarity == 'all':
            rarities = ['3', '4', 'five']
            for r in rarities:
                await context.invoke(self.fullrelease, r, region_str)
            return

        if rarity == 'five':
            rarity = '5'
        elif rarity == '5':
            await context.send("`Usage:`\n\n```!fullrelease five [region]```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        if rarity not in ('3', '4', '5'):
            await context.send("You can only full release 3⭐, 4⭐, and 5⭐ rarity Pokémon!")
        else:
            balance = database_helper.get_pikapoints(context.message.author.id)
            if region is None:
                str_region = "all regions"
            else:
                str_region = "the " + region[0] + " region"
            rows = database_helper.full_remove_inventory(context.message.author.id, rarity, region)
            if rows == 0:
                await context.send("There is no {}⭐ pokémon to release...".format(rarity))
                return
            if rarity == '3':
                gain = 5
            elif rarity == '4':
                gain = 10
            elif rarity == '5':
                gain = 15
            database_helper.adjust_points(context.message.author.id, gain*rows)
            total_gain = gain*rows
            await context.send("You currently have {} pikapoints.\nReleasing {} {}⭐ Pokémon from {}...\nYou got {} pikapoints!\nYou now have {} pikapoints.".format(str(balance), rows, rarity, str_region, total_gain, database_helper.get_pikapoints(context.message.author.id)))
            for i in range(rows):
                database_helper.increment_stat(context.message.author.id, "releases")

    @commands.command(name="releasedupes")
    async def releasedupes(self, context, rarity=None, region=None):
        if rarity is None:
            await context.send("`Usage:`\n\n```!releasedupes rarity [region]```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return
        region_str = region
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        elif region == 'hoenn':
            region = HOENN
        elif region == 'sinnoh':
            region = SINNOH
        elif region == 'unova':
            region = UNOVA
        elif region == 'kalos':
            region = KALOS
        elif region == 'alola':
            region = ALOLA
        elif region is not None:
            await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'kalos', 'alola', None)")
            return

        if rarity == 'all':
            rarities = ['3', '4', 'five']
            for r in rarities:
                await context.invoke(self.releasedupes, r, region_str)
            return

        if rarity == 'five':
            rarity = '5'
        elif rarity == '5':
            await context.send("`Usage:`\n\n```!releasedupes five [region]```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        if rarity not in ('3', '4', '5'):
            await context.send("You can only full release 3⭐, 4⭐, and 5⭐ rarity Pokémon!")
        else:
            balance = database_helper.get_pikapoints(context.message.author.id)
            if region is None:
                str_region = "all regions"
            else:
                str_region = "the " + region[0] + " region"
            rows = database_helper.remove_dupes(context.message.author.id, rarity, region)
            if rows == 0:
                await context.send("There is no {}⭐ pokémon to release...".format(rarity))
                return
            if rarity == '3':
                gain = 5
            elif rarity == '4':
                gain = 10
            elif rarity == '5':
                gain = 15
            database_helper.adjust_points(context.message.author.id, gain * rows)
            total_gain = gain * rows
            await context.send("You currently have {} pikapoints.\nReleasing {} {}⭐ Pokémon from {}...\nYou got {} pikapoints!\nYou now have {} pikapoints.".format(str(balance), rows, rarity, str_region, total_gain,
                                                                                            database_helper.get_pikapoints(
                                                                                                context.message.author.id)))
            for i in range(rows):
                database_helper.increment_stat(context.message.author.id, "releases")

    @commands.command(name="release")
    async def release(self, context, name=None, option=None):
        if name is None:
            await context.send("`Usage:`\n\n```!release pokemon_name [option]```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return
        pokemon = database_helper.get_pokemon(name)
        if pokemon is not None:
            if database_helper.get_from_inventory(context.message.author.id, pokemon[0]):
                if option is None:
                    database_helper.remove_inventory(context.message.author.id, pokemon[0])
                    if pokemon[1] == 3:
                        gain = 5
                    elif pokemon[1] == 4:
                        gain = 10
                    elif pokemon[1] == 5:
                        gain = 15
                    elif pokemon[1] == 6:
                        gain = 30
                    elif pokemon[1] == 7:
                        gain = 60
                    elif pokemon[1] == 8:
                        gain = 45
                    database_helper.adjust_points(context.message.author.id, gain)
                    await context.send("Successfully released {}. You got {} pikapoints!\nYou now have {} pikapoints.".format(name, gain, database_helper.get_pikapoints(context.message.author.id)))
                    database_helper.increment_stat(context.message.author.id, "releases")
                elif option == 'all':
                    rows = database_helper.fullrelease_pokemon(context.message.author.id, pokemon[0])
                    if pokemon[1] == 3:
                        gain = 5
                    elif pokemon[1] == 4:
                        gain = 10
                    elif pokemon[1] == 5:
                        gain = 15
                    elif pokemon[1] == 6:
                        gain = 30
                    elif pokemon[1] == 7:
                        gain = 60
                    elif pokemon[1] == 8:
                        gain = 45
                    gain = gain * rows
                    database_helper.adjust_points(context.message.author.id, gain)
                    await context.send("Successfully released {} {}. You got {} pikapoints!\nYou now have {} pikapoints.".format(rows, name, gain, database_helper.get_pikapoints(context.message.author.id)))
                    for i in range(rows):
                        database_helper.increment_stat(context.message.author.id, "releases")
                elif option == 'dupes':
                    rows = database_helper.releasedupes_pokemon(context.message.author.id, pokemon[0])
                    if pokemon[1] == 3:
                        gain = 5
                    elif pokemon[1] == 4:
                        gain = 10
                    elif pokemon[1] == 5:
                        gain = 15
                    elif pokemon[1] == 6:
                        gain = 30
                    elif pokemon[1] == 7:
                        gain = 60
                    elif pokemon[1] == 8:
                        gain = 45
                    gain = gain * rows
                    database_helper.adjust_points(context.message.author.id, gain)
                    await context.send("Successfully released {} {}. You got {} pikapoints!\nYou now have {} pikapoints.".format(rows, name, gain, database_helper.get_pikapoints(context.message.author.id)))
                    for i in range(rows):
                        database_helper.increment_stat(context.message.author.id, "releases")
                else:
                    try:
                        option = int(option)
                        if option > 0:
                            is_int = True
                        else:
                            is_int = False
                    except:
                        is_int = False

                    if is_int:
                        if option > database_helper.get_from_inventory(context.message.author.id, pokemon[0], True):
                            await context.send("You do not have that much of that Pokémon!")
                        else:
                            rows = database_helper.limitrelease_pokemon(context.message.author.id, pokemon[0], option)
                            if pokemon[1] == 3:
                                gain = 5
                            elif pokemon[1] == 4:
                                gain = 10
                            elif pokemon[1] == 5:
                                gain = 15
                            elif pokemon[1] == 6:
                                gain = 30
                            elif pokemon[1] == 7:
                                gain = 60
                            elif pokemon[1] == 8:
                                gain = 45
                            gain = gain * rows
                            database_helper.adjust_points(context.message.author.id, gain)
                            await context.send(
                                "Successfully released {} {}. You got {} pikapoints!\nYou now have {} pikapoints.".format(
                                    rows, name, gain, database_helper.get_pikapoints(context.message.author.id)))
                            for i in range(rows):
                                database_helper.increment_stat(context.message.author.id, "releases")
                    else:
                        await context.send("Option must be 'all', 'dupes', a positive integer, or None")
            else:
                await context.send("You do not have that Pokémon!")
        else:
            await context.send("Invalid Pokémon name!")

    @commands.command(name="fav")
    async def fav(self, context, name=None):
        if name is None:
            await context.send("`Usage:`\n\n```!fav pokemon_name```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        pokemon = database_helper.get_pokemon(name)
        if pokemon is None:
            await context.send("Invalid Pokémon name!")
            return

        user_id = context.message.author.id
        user = self.bot.get_user(int(user_id))
        username = user.name

        favs = database_helper.get_favs(user_id)
        fav_list = []
        for fav in favs:
            fav_list.append(fav[0])
        if pokemon[0] in fav_list:
            await context.send("You already have this pokémon favourited!")
            return

        database_helper.add_fav(user_id, pokemon[0])
        await context.send("Successfully favourited {}!".format(name))

    @commands.command(name="unfav")
    async def unfav(self, context, name=None):
        if name is None:
            await context.send("`Usage:`\n\n```!unfav pokemon_name```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        user_id = context.message.author.id
        user = self.bot.get_user(int(user_id))
        username = user.name

        if name == 'all':
            database_helper.del_all_favs(user_id)
            await context.send("Successfully unfavourited all pokémon!")
            return

        pokemon = database_helper.get_pokemon(name)
        if pokemon is None:
            await context.send("Invalid Pokémon name!")
            return

        favs = database_helper.get_favs(user_id)
        fav_list = []
        for fav in favs:
            fav_list.append(fav[0])
        if pokemon[0] not in fav_list:
            await context.send("You don't have this pokémon favourited!")
            return

        database_helper.del_fav(user_id, pokemon[0])
        await context.send("Successfully unfavourited {}!".format(name))

    @commands.command(name="favs")
    async def favs(self, context, user_id=None):
        if user_id is None:
            user_id = context.message.author.id
        user = self.bot.get_user(int(user_id))
        username = user.name

        favs = database_helper.get_favs(user_id)
        if not len(favs) > 0:
            await context.send ("{} has no favourite pokémon!".format(username))
            return

        title = "{}'s Favourite Pokémon:".format(username)
        description = ''
        for fav in favs:
            description = description + "\n" + database_helper.get_pokemon_name(fav[0])[0]

        await context.send(embed=discord.Embed(title=title, description=description, color=0xffa500))


    @commands.command(name="newfocus")
    async def newfocus(self, context, *args):
        if context.message.author.id == SNOOPY_ID:
            database_helper.change_focus(*args)
            title = "New Focus Units: "
            description = ''
            for region in REGIONS:
                focus = database_helper.get_focus(region)
                description = description + "\n\n**__" + region[0] + "__**"
                for unit in focus:
                    description = description + "\n    " + unit[0]
            await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))
        else:
            await context.send("Y'all'th'st'd've'ish ain't Snoopy")

    @commands.command(name="newspecial")
    async def newspecial(self, context, *args):
        if context.message.author.id == SNOOPY_ID:
            database_helper.change_special(*args)
            for arg in args:
                await context.invoke(self.pokedex, arg, True)
        else:
            await context.send("Y'all'th'st'd've'ish ain't Snoopy")

    @commands.command(name="special")
    async def special(self, context):
        special = database_helper.get_special()
        if len(special) <= 0:
            await context.send("There is no currently active Special Pokémon!")
            return
        for unit in special:
            await context.invoke(self.pokedex, unit[0], True)

    @commands.command(name="sql")
    async def sql(self, context, query):
        if context.message.author.id == SNOOPY_ID:
            database_helper.run_sql(query)
        else:
            await context.send("Y'all'th'st'd've'ish ain't Snoopy")

    @commands.command(name="get")
    async def get(self, context, query):
        if context.message.author.id == SNOOPY_ID:
            result = database_helper.get_sql(query)
            if result is None:
                await context.send("That query yielded no results...")
                return
            if len(result) > 0:
                msg = ""
                for row in result:
                    for column in row:
                        msg = msg + str(column) + "\t"
                    msg = msg + "\n"
                await context.send(msg)
            else:
                await context.send("That query yielded no results...")
        else:
            await context.send("Y'all'th'st'd've'ish ain't Snoopy")


    @commands.command(name="units")
    async def units(self, context, region=None):
        if region is None:
            await context.send("`Usage:`\n\n```!units region```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        elif region == 'hoenn':
            region = HOENN
        elif region == 'sinnoh':
            region = SINNOH
        elif region == 'unova':
            region = UNOVA
        elif region == 'kalos':
            region = KALOS
        elif region == 'alola':
            region = ALOLA
        elif region == 'special':
            region = SPECIAL
        elif region is not None:
            await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'kalos', 'alola', 'special')")
            return
        units = database_helper.get_units(region)
        if region[0] == 'Special':
            active = []
            inactive = []

            for unit in units:
                if unit[3] == 1:
                    active.append(unit[0])
                elif unit[3] == 0:
                    inactive.append(unit[0])

            title = "Active Special Units: \n"
            description = ''
            for unit in active:
                description = description + "\n" + unit
            await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

            title = "Inactive Special Units: \n"
            description = ''
            for unit in inactive:
                description = description + "\n" + unit
            await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))
            return

        focus = []
        seven = []
        six = []
        five = []
        four = []
        three = []
        for unit in units:
            if unit[2] == 1:
                focus.append(unit[0])
            elif unit[1] == 7:
                seven.append(unit[0])
            elif unit[1] == 6:
                six.append(unit[0])
            elif unit[1] == 5:
                five.append(unit[0])
            elif unit[1] == 4:
                four.append(unit[0])
            elif unit[1] == 3:
                three.append(unit[0])
        title = "Focus Units: \n"
        description = ''
        for unit in focus:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

        title = "Mythic Units: \n"
        description = ''
        for unit in seven:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

        title = "Legendary Units: \n"
        description = ''
        for unit in six:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

        title = "5⭐ Units: \n"
        description = ''
        for unit in five:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

        title = "4⭐ Units: \n"
        description = ''
        for unit in four:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))


        title = "3⭐ Units: \n"
        description = ''
        for unit in three:
            description = description + "\n" + unit
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))


    @commands.command(name="focus")
    async def focus(self, context):
        title = "Focus Units: "
        description = ''
        for region in REGIONS:
            focus = database_helper.get_focus(region)
            description = description + "\n\n**__" + region[0] + "__**"
            for unit in focus:
                description = description + "\n    " + unit[0]
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

    @commands.command(name="jackpot")
    async def jackpot(self, context):
        title = "Current Jackpot Contribution:"
        description = ''
        contributors = database_helper.get_jackpot(False)
        if len(contributors) == 0:
            await context.send("The jackpot is currently empty!")
            return
        for contributor in contributors:
            if context.message.author == self.bot.get_user(contributor[0]):
                description = description + "\n`" + self.bot.get_user(contributor[0]).name + " - {} pikapoints`".format(contributor[1])
            else:
                description = description + "\n" + self.bot.get_user(contributor[0]).name + " - {} pikapoints".format(
                    contributor[1])
        jackpot_sum = database_helper.get_jackpot(True)[0]
        no_contributors = len(database_helper.get_jackpot_rewards())
        if no_contributors == 0:
            payout = 0
        else:
            payout = jackpot_sum // no_contributors
        multiplier = 2
        description = description + "\n\n**You need to have contributed at least 3 pikapoints to the current jackpot to receive rewards!\n\nCurrent Jackpot Total: {} pikapoints\nTotal Number of Contributors: {}\nCurrent Number of Reward Earners: {}\nCurrent Payout: {} pikapoints\nMythic Multiplier: x{} pikapoints**".format(jackpot_sum, len(contributors), no_contributors, payout, multiplier)
        await context.send(embed=discord.Embed(title=title, description=description, color=0x00ff7f))

    @commands.command(name="bank")
    async def bank(self, context, user_id=None):
        if user_id is None:
            user_id = context.message.author.id
        user = self.bot.get_user(int(user_id))
        username = user.name
        balance = database_helper.get_savings(user_id)
        if (balance is None):
            await context.send("{} has no pikapoints saved in their bank!".format(username))
        else:
            await context.send(username + " has " + str(balance) + " pikapoints saved in their bank")

    @commands.command(name="points")
    async def points(self, context, user_id=None):
        if user_id is None:
            user_id = context.message.author.id
        user = self.bot.get_user(int(user_id))
        username = user.name
        balance = database_helper.get_pikapoints(user_id)
        savings = database_helper.get_savings(user_id)
        if (balance is None):
            balance = 0
        if (savings is None):
            savings = 0
        title = "{}'s Account".format(username)
        description = "Balance: {} pikapoints\nSavings: {} pikapoints".format(balance, savings)
        await context.send(embed=discord.Embed(title=title, description=description, color=0xffff99))

    @commands.command(name="account")
    async def account(self, context, user_id=None):
        user_details = [self.points, self.bag, self.box]
        for user_detail in user_details:
            await context.invoke(user_detail, user_id)

    @commands.command(name="deposit")
    async def deposit(self, context, amount=None):
        if amount is None:
            await context.send("`Usage:`\n\n```!deposit amount```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        user_id = context.message.author.id
        user = self.bot.get_user(int(user_id))
        username = user.name

        balance = database_helper.get_pikapoints(user_id)

        if amount == 'all':
            amount = balance
        elif amount is not None:
            try:
                amount = int(amount)
                is_int = True
            except:
                is_int = False

            if is_int:
                if amount > balance:
                    await context.send("You don't have that many pikapoints!")
                    return
            else:
                await context.send("Amount of pikapoints to deposit must be an integer or 'all'")
                return

        if amount <= 0 or balance is None:
            await context.send("There is no pikapoints to deposit...")
            return

        database_helper.adjust_points(user_id, -amount)
        database_helper.adjust_savings(user_id, amount)

        balance = database_helper.get_pikapoints(user_id)
        savings = database_helper.get_savings(user_id)
        await context.send("Successfully deposited {} pikapoints into the bank!\nNew balance: {} pikapoints\nNew savings: {} pikapoints".format(amount, balance, savings))

    @commands.command(name="withdraw")
    async def withdraw(self, context, amount=None):
        if amount is None:
            await context.send("`Usage:`\n\n```!withdraw amount```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        user_id = context.message.author.id
        user = self.bot.get_user(int(user_id))
        username = user.name

        balance = database_helper.get_savings(user_id)

        if amount == 'all':
            amount = balance
        elif amount is not None:
            try:
                amount = int(amount)
                is_int = True
            except:
                is_int = False

            if is_int:
                if amount > balance:
                    await context.send("You don't have that many pikapoints saved in your bank!")
                    return
            else:
                await context.send("Amount of pikapoints to withdraw must be an integer or 'all'")
                return

        if amount <= 0 or balance is None:
            await context.send("There is no pikapoints to withdraw...")
            return

        database_helper.adjust_points(user_id, amount)
        database_helper.adjust_savings(user_id, -amount)

        balance = database_helper.get_pikapoints(user_id)
        savings = database_helper.get_savings(user_id)
        await context.send("Successfully withdrew {} pikapoints from the bank!\nNew balance: {} pikapoints\nNew savings: {} pikapoints".format(amount, balance, savings))

    @commands.command(name="battle")
    async def battle(self, context, id2=None, wager=None):
        if id2 is None or wager is None:
            await context.send("`Usage:`\n\n```!battle their_id wager```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        if database_helper.get_stadium():
            await context.send("The Pokémon Stadium is currently occupied!")
            return
        else:
            database_helper.update_stadium(True)

        try:
            wager = int(wager)
            is_int = True
            if not 1 <= wager <= 100:
                is_int = False
        except:
            is_int = False
        if not is_int:
            await context.send("Wager must be between 1 and 100 pikapoints!")
            database_helper.update_stadium(False)
            return

        id1 = int(context.message.author.id)
        user1 = self.bot.get_user(id1)
        username1 = user1.name

        try:
            id2 = int(id2)
            user2 = self.bot.get_user(id2)
            username2 = user2.name
        except:
            await context.send("Player 2's ID is invalid!")
            database_helper.update_stadium(False)
            return
        else:
            if database_helper.get_pikapoints(id2) is None:
                await context.send("Player 2's ID is invalid!")
                database_helper.update_stadium(False)
                return

        if user1 == user2:
            await context.send("You cannot battle yourself!")
            database_helper.update_stadium(False)
            return

        MIN_POINTS = -100
        balance1 = database_helper.get_pikapoints(id1)
        balance2 = database_helper.get_pikapoints(id2)
        if balance1 < MIN_POINTS:
            await context.send("You don't have enough pikapoints to battle!\nYou have {} pikapoints".format(balance1))
            database_helper.update_stadium(False)
            return
        if balance2 < MIN_POINTS:
            await context.send("{} doesn't have enough pikapoints to battle!\n{} has {} pikapoints".format(username2, username2, balance2))
            database_helper.update_stadium(False)
            return

        title = "Battle Challenge"
        description = "{} is challenged by {}!".format(username2, username1)
        msg = await context.send(embed=discord.Embed(title=title, description=description, color=0x000080))
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        timed_out = False
        def check(reaction, user):
            return (user == user2 and str(reaction.emoji) == '✅') or ((user == user1 or user == user2) and str(reaction.emoji) == '❌')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await context.send("{} got away safely!".format(username2))
            timed_out = True
        else:
            if str(reaction.emoji) == '❌':
                await context.send("{} got away safely!".format(username2))
                timed_out = True
        if timed_out:
            database_helper.update_stadium(False)
            return

        await context.send("{}, Choose a Pokémon!".format(username1))
        def check(m):
            return database_helper.get_pokemon(m.content) is not None and database_helper.get_from_inventory(id1, database_helper.get_pokemon(m.content)[0]) and m.channel == context.message.channel and m.author == user1
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await context.send("{} didn't choose their pokémon in time...".format(username1))
            timed_out = True
        else:
            pokemon1 = msg.content
        if timed_out:
            database_helper.update_stadium(False)
            return

        await context.send("{}, Choose a Pokémon!".format(username2))
        def check(m):
            return database_helper.get_pokemon(m.content) is not None and database_helper.get_from_inventory(id2, database_helper.get_pokemon(m.content)[0]) and m.channel == context.message.channel and m.author == user2
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await context.send("{} didn't choose their pokémon in time...".format(username2))
            timed_out = True
        else:
            pokemon2 = msg.content
        if timed_out:
            database_helper.update_stadium(False)
            return

        await self.do_battle(context, user1, user2, pokemon1, pokemon2, wager)
        database_helper.update_stadium(False)

    async def do_battle(self, context, user1, user2, pokemon1, pokemon2, wager):
        id1 = user1.id
        id2 = user2.id
        username1 = user1.name
        username2 = user2.name

        poke1_details = database_helper.get_pokemon(pokemon1)
        poke1_id = poke1_details[0]
        poke1_rarity = poke1_details[1]
        poke1_bst = poke1_details[2]
        poke1_count = database_helper.get_poke_count(id1, poke1_id)[0]
        poke1_dupes = poke1_count - 1
        poke1_multiplier_details = await self.get_multiplier(poke1_rarity, poke1_dupes)
        poke1_multiplier = poke1_multiplier_details[0]
        poke1_plus = poke1_multiplier_details[1]
        poke1_new_bst = math.floor(poke1_bst * poke1_multiplier)
        poke1_bst_bonus = poke1_new_bst - poke1_bst

        poke2_details = database_helper.get_pokemon(pokemon2)
        poke2_id = poke2_details[0]
        poke2_rarity = poke2_details[1]
        poke2_bst = poke2_details[2]
        poke2_count = database_helper.get_poke_count(id2, poke2_id)[0]
        poke2_dupes = poke2_count - 1
        poke2_multiplier_details = await self.get_multiplier(poke2_rarity, poke2_dupes)
        poke2_multiplier = poke2_multiplier_details[0]
        poke2_plus = poke2_multiplier_details[1]
        poke2_new_bst = math.floor(poke2_bst * poke2_multiplier)
        poke2_bst_bonus = poke2_new_bst - poke2_bst

        bst_total = poke1_new_bst + poke2_new_bst
        poke1_odds = round((poke1_new_bst / bst_total) * 100, 2)
        poke2_odds = round((poke2_new_bst / bst_total) * 100, 2)

        str_poke1_plus = ''
        if poke1_plus > 0:
            str_poke1_plus = ' +{}'.format(poke1_plus)
        str_poke2_plus = ''
        if poke2_plus > 0:
            str_poke2_plus = ' +{}'.format(poke2_plus)

        str_poke1_bst_bonus = ''
        if poke1_bst_bonus > 0:
            str_poke1_bst_bonus = ' +{}'.format(poke1_bst_bonus)
        str_poke2_bst_bonus = ''
        if poke2_bst_bonus > 0:
            str_poke2_bst_bonus = ' +{}'.format(poke2_bst_bonus)

        p1_win_payout = math.floor((100 / poke1_odds) * wager)
        p2_win_payout = math.floor((100 / poke2_odds) * wager)
        p1_balance = database_helper.get_pikapoints(id1)
        p2_balance = database_helper.get_pikapoints(id2)

        # title = "Battle!"
        # description = "{}'s {}{}\nBST: {}{}\nChance to Win: {}%\n\nVS\n\n{}'s {}{}\nBST: {}{}\nChance to Win: {}%\n\n{} currently has {} pikapoints\n{} currently has {} pikapoints\n\nBase Wager: {}\nPayout if {} wins: {} pikapoints\nPayout if {} wins: {} pikapoints\n\n**Both players must confirm if they wish for the battle to proceed**".format(
        #     username1, pokemon1, str_poke1_plus, poke1_bst, str_poke1_bst_bonus, poke1_odds,
        #     username2, pokemon2, str_poke2_plus, poke2_bst, str_poke2_bst_bonus, poke2_odds,
        #     username1, p1_balance, username2, p2_balance, wager, username1, p1_win_payout, username2, p2_win_payout)

        file = await self.draw_battle(username1, pokemon1, str_poke1_plus, poke1_bst, str_poke1_bst_bonus, poke1_odds,
                          username2, pokemon2, str_poke2_plus, poke2_bst, str_poke2_bst_bonus, poke2_odds,
                          p1_balance, p2_balance, wager, p1_win_payout, p2_win_payout, poke1_id, poke2_id)
        msg = await context.send(file=file)
        # msg = await context.send(embed=discord.Embed(title=title, description=description, color=0x000080))
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        timed_out = False
        accepted = []
        battling = False
        def check(reaction, user):
            return ((user == user1 or user == user2) and str(reaction.emoji) == '✅') or ((user == user1 or user == user2) and str(reaction.emoji) == '❌')
        while not timed_out:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await context.send("Battle confirmation timed out...")
                timed_out = True
            else:
                if str(reaction.emoji) == '❌':
                    await context.send("{} declined the battle.".format(user.name))
                    timed_out = True
                elif str(reaction.emoji) == '✅':
                    accepted.append(user)
                    if user1 in accepted and user2 in accepted:
                        timed_out = True
                        battling = True
        if timed_out and not battling:
            return

        r = random.randint(1, 10000)
        if 1 <= r <= poke1_odds * 100:
            winner = user1
            loser = user2
            loser_pokemon = pokemon2
            payout = p1_win_payout
            winner_odds = poke1_odds / 100
        else:
            winner = user2
            loser = user1
            loser_pokemon = pokemon1
            payout = p2_win_payout
            winner_odds = poke2_odds / 100
        database_helper.adjust_points(winner.id, payout)
        database_helper.adjust_points(loser.id, -payout)

        await context.send("Battling...")
        await asyncio.sleep(5)
        await context.send("{}'s {} fainted!".format(loser.name, loser_pokemon))
        await asyncio.sleep(3)
        await context.send("{} won the battle and {} paid them {} pikapoints!\n{} now has {} pikapoints.\n{} now has {} pikapoints.".format(
            winner.name, loser.name, payout, username1, database_helper.get_pikapoints(id1), username2, database_helper.get_pikapoints(id2)
        ))
        database_helper.increment_stat(winner.id, "battles")
        database_helper.increment_stat(loser.id, "battles")
        database_helper.increment_stat(winner.id, "wins")
        database_helper.increment_stat(loser.id, "losses")
        if (poke1_odds <= 35 and winner == user1) or (poke2_odds <= 35 and winner == user2):
            database_helper.increment_stat(winner.id, "underdogs")
            database_helper.increment_stat(loser.id, "neverlucky")
        if wager >= 85:
            database_helper.increment_stat(winner.id, "highstakewins")
            database_helper.increment_stat(loser.id, "highstakeloss")
        database_helper.update_exp(winner.id, math.ceil((payout * (1 - winner_odds)) / 5))
        promote = database_helper.promote(winner.id)
        if promote is not None:
            await context.send(promote)

    async def draw_battle(self, username1, pokemon1, str_poke1_plus, poke1_bst, str_poke1_bst_bonus, poke1_odds,
                          username2, pokemon2, str_poke2_plus, poke2_bst, str_poke2_bst_bonus, poke2_odds,
                          p1_balance, p2_balance, wager, p1_win_payout, p2_win_payout, poke1_id, poke2_id):
        background = Image.open('images/battle_background.png', 'r').resize((850, 450))

        # draw pokemon
        if poke1_id >= 10000:
            if poke1_id in [10000, 10006, 10007, 10008]:
                response = requests.get(SPRITE_MAPPING[poke1_id])
                img = Image.open(BytesIO(response.content)).transpose(Image.FLIP_LEFT_RIGHT).convert("RGBA")
                img = img.resize((150, 150))
            else:
                sprite = pb.SpriteResource('pokemon', SPRITE_MAPPING[poke1_id])
                img = Image.open(sprite.path).transpose(Image.FLIP_LEFT_RIGHT).convert("RGBA")
                img = img.resize((200, 200))
        else:
            sprite = pb.SpriteResource('pokemon', poke1_id)
            img = Image.open(sprite.path).transpose(Image.FLIP_LEFT_RIGHT).convert("RGBA")
            img = img.resize((200, 200))
        coordinates = (50, 225)
        background.paste(img, coordinates, img)

        if poke2_id >= 10000:
            if poke2_id in [10000, 10006, 10007, 10008]:
                response = requests.get(SPRITE_MAPPING[poke2_id])
                img = Image.open(BytesIO(response.content)).convert("RGBA")
                img = img.resize((150, 150))
            else:
                sprite = pb.SpriteResource('pokemon', SPRITE_MAPPING[poke2_id])
                img = Image.open(sprite.path).convert("RGBA")
                img = img.resize((200, 200))
        else:
            sprite = pb.SpriteResource('pokemon', poke2_id)
            img = Image.open(sprite.path).convert("RGBA")
            img = img.resize((200, 200))
        coordinates = (550, 50)
        background.paste(img, coordinates, img)

        # draw boxes
        img = Image.open('images/battle_text_box.png', 'r').resize((300, 150))
        coordinates = (25, 75)
        background.paste(img, coordinates, img)
        coordinates = (525, 275)
        background.paste(img, coordinates, img)

        # draw title
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("images/arial.ttf", 30)
        draw.text((400,5), "Battle!", (255, 0, 0), font=font)
        font = ImageFont.truetype("images/arial.ttf", 25)
        draw.text((300, 40), "Base Wager: {} pikapoints".format(wager), (255, 0, 0), font=font)

        # draw middle
        font = ImageFont.truetype("images/arial.ttf", 50)
        draw.text((415, 200), "VS", (255, 0, 0), font=font)
        font = ImageFont.truetype("images/arial.ttf", 15)
        draw.text((240, 250), "Both players must confirm if they wish for the battle to proceed", (255, 0, 0), font=font)

        # populate text boxes
        font = ImageFont.truetype("images/arial.ttf", 20)
        draw.text((38, 88), "{}".format(username2), (255, 255, 255), font=font)
        draw.text((38, 108), "{}{}".format(pokemon2, str_poke2_plus), (255, 255, 255), font=font)
        draw.text((38, 128), "BST: {}{}".format(poke2_bst, str_poke2_bst_bonus), (255, 255, 255), font=font)
        draw.text((38, 148), "Odds: {}%".format(poke2_odds), (255, 255, 255), font=font)
        draw.text((38, 168), "Balance: {} pikapoints".format(p2_balance), (255, 255, 255), font=font)
        draw.text((38, 188), "Earnings: {} pikapoints".format(p2_win_payout), (255, 255, 255), font=font)

        draw.text((538, 288), "{}".format(username1), (255, 255, 255), font=font)
        draw.text((538, 308), "{}{}".format(pokemon1, str_poke1_plus), (255, 255, 255), font=font)
        draw.text((538, 328), "BST: {}{}".format(poke1_bst, str_poke1_bst_bonus), (255, 255, 255), font=font)
        draw.text((538, 348), "Odds: {}%".format(poke1_odds), (255, 255, 255), font=font)
        draw.text((538, 368), "Balance: {} pikapoints".format(p1_balance), (255, 255, 255), font=font)
        draw.text((538, 388), "Earnings: {} pikapoints".format(p1_win_payout), (255, 255, 255), font=font)

        save_location = "images/battle_{}_{}.png".format(poke1_id, poke2_id)
        background.save(save_location)
        file = discord.File(save_location, filename='battle.png')
        return file



    async def get_multiplier(self, rarity, dupes):
        if rarity == 8:
            inc = 0.1
        else:
            inc = (rarity - 2) / 100

        count = 1
        bonus = 1
        while dupes >= count:
            bonus += inc
            dupes -= count
            count += 1
        return bonus, count - 1

    @commands.command(name="register")
    async def register(self, context, name=None):
        if name is None or name.strip() == "":
            await context.send("`Usage:`\n\n```!register name```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        name = name.strip()
        if not 4 <= len(name) <= 20:
            await context.send("name length must be between 4 and 20 characters!")
            return
        if " " in name:
            await context.send("name cannot contain whitespace!")
            return
        if not name.isalnum():
            await context.send("name must be alphanumeric!")
            return

        user_id = context.message.author.id
        user = self.bot.get_user(user_id)
        username = user.name

        result = database_helper.register(user_id, name)

        if result == 0:
            await context.send("Successfully registered {} as Pokémon Trainer {}!".format(username, name))
        elif result == 1:
            await context.send("Successfully changed name to {}!".format(name))
        elif result == 2:
            await context.send("You are already registered with the name {}!".format(name))
        elif result == 3:
            await context.send("Someone already has the name {}!".format(name))

    @commands.command("trainer")
    async def trainer(self, context, name=None):
        if name is None:
            await context.send("`Usage:`\n\n```!trainer name```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        trainer = database_helper.get_trainer(name)
        if trainer is None:
            await context.send("There is no registered Pokémon Trainer with the name {}!".format(name))
            return

        user_id = trainer[0]
        user = self.bot.get_user(user_id)
        username = user.name

        trainer_team = trainer[19]
        if trainer[19] != '':
            trainer_team += ' '
        title = "{}'s Trainer Card".format(username)
        description = "{}{} {}\nID: {}\n\n".format(trainer_team, trainer[2], trainer[1], trainer[0])

        if trainer_team == '':
            exp_until_promotion = 'N/A'
        elif database_helper.get_next_rank(trainer[2]) is None:
            exp_until_promotion = 'Eligible for Prestige!'
        else:
            exp_until_promotion = max(0, database_helper.get_next_rank(trainer[2])[1] - trainer[21])

        description += "Total EXP Gained: {}\nEXP Gained in Current Rank: {}\nEXP Until Promotion: {}\nPrestige: {}\n\n".format(trainer[20], trainer[21], exp_until_promotion, trainer[22])
        description += "**__Summoning Stats__**\n"
        description += "Pokémon Rolled: {}\nBricks: {}\nJackpot Participation: {}\nBalls Opened: {}\nPokémon Released: {}\nPokémon Traded: {}\n\n".format(trainer[3], trainer[4], trainer[5], trainer[6], trainer[7], trainer[8])
        description += "**__Quiz Stats__**\n"
        description += "Quizzes Answered: {}\nHot Streaks: {}\nHot Streak Shutdowns: {}\nHighest Streak: {}\n\n".format(trainer[9], trainer[10], trainer[11], trainer[23])
        description += "**__Battle Stats__**\n"
        description += "Total Battles: {}\nTotal Wins: {}\nUnderdog Wins: {}\nHigh Stake Wins: {}\nTotal Losses: {}\nNever Lucky Losses: {}\nHigh Stake Losses: {}".format(trainer[12], trainer[13], trainer[14], trainer[15], trainer[16], trainer[17], trainer[18])
        embed = discord.Embed(title=title, description=description, color=0xffffff)
        embed.set_thumbnail(url=self.bot.get_user(trainer[0]).avatar_url)
        await context.send(embed=embed)

    @commands.command("trainers")
    async def trainers(self, context):
        trainers = database_helper.get_trainers()
        if len(trainers) < 1:
            await context.send("There are no Pokémon Trainers registered yet!")
            return
        title = "All Registered Pokémon Trainers"
        description = ""
        for trainer in trainers:
            username = self.bot.get_user(trainer[0]).name
            trainer_team = trainer[3]
            if trainer[3] != '':
                trainer_team += ' '
            description += "\n**{}** - {}{} {}".format(username, trainer_team, trainer[2], trainer[1])
        embed = discord.Embed(title=title, description=description, color=0xffffff)
        await context.send(embed=embed)

    @commands.command("team")
    async def team(self, context, team_emoji=None):
        if team_emoji is None:
            await context.send("`Usage:`\n\n```!team team_emoji```\n`Use !gachahelp to view the help menu for more information on all PikaGacha commands`")
            return

        team = ''
        thumb = ''

        if ":electrocution:" in team_emoji and ":lensflare:" not in team_emoji and ":hyperjoy:" not in team_emoji:
            team = 'Team Electrocution'
            thumb = "https://cdn.discordapp.com/emojis/496081109558362134.png?v=1"
        elif ":electrocution:" not in team_emoji and ":lensflare:" in team_emoji and ":hyperjoy:" not in team_emoji:
            team = 'Team Lensflare'
            thumb = 'https://cdn.discordapp.com/emojis/496138997391687710.png?v=1'
        elif ":electrocution:" not in team_emoji and ":lensflare:" not in team_emoji and ":hyperjoy:" in team_emoji:
            team = 'Team Hyperjoy'
            thumb = 'https://cdn.discordapp.com/emojis/431882995289554978.png?v=1'

        if team == '' and thumb == '':
            await context.send("team_emoji must be in only one of ('electrocution', 'lensflare', 'hyperjoy')")
            return

        members = database_helper.get_team(team)
        description = ''
        for member in members:
            description += "\n{} - {}".format(member[0], member[1])
        embed = discord.Embed(title=team, description=description, color=0x4b0082)
        embed.set_thumbnail(url=thumb)
        await context.send(embed=embed)

    @commands.command("switch")
    async def switch(self, context):
        curr_team = database_helper.get_trainer_team(context.message.author.id)[0]
        COST = 420
        if curr_team == '':
            await context.send("You have not joined a team yet!")
            return

        balance = database_helper.get_pikapoints(context.message.author.id)
        if balance < COST:
            await context.send("Switching teams costs {} pikapoints! You currently only have {} pikapoints.".format(COST, balance))
            return

        title = "Team Switch"
        description = "Which team would you like to switch to?\n\n**Remember, switching teams causes you to lose all your progress and costs {} pikapoints!**".format(COST)
        msg = await context.send(embed=discord.Embed(title=title, description=description, color=0x4b0082))
        await msg.add_reaction(':electrocution:496081109558362134')
        await msg.add_reaction(':lensflare:496138997391687710')
        await msg.add_reaction(':hyperjoy:431882995289554978')

        def check(reaction, user):
            return user == context.message.author and reaction.emoji.name in ('lensflare', 'hyperjoy', 'electrocution') and reaction.emoji.id in (496081109558362134, 496138997391687710, 431882995289554978)
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await context.send("Team switch timed out...")
        else:
            if reaction.emoji.name == 'electrocution' and reaction.emoji.id == 496081109558362134:
                team = 'Team Electrocution'
                thumb = "https://cdn.discordapp.com/emojis/496081109558362134.png?v=1"
            elif reaction.emoji.name == 'lensflare' and reaction.emoji.id == 496138997391687710:
                team = 'Team Lensflare'
                thumb = 'https://cdn.discordapp.com/emojis/496138997391687710.png?v=1'
            elif reaction.emoji.name == 'hyperjoy' and reaction.emoji.id == 431882995289554978:
                team = 'Team Hyperjoy'
                thumb = 'https://cdn.discordapp.com/emojis/431882995289554978.png?v=1'

            if curr_team == team:
                await context.send("You are already a member of {}!".format(curr_team))
                return

            title = 'Accept Team Switch Confirmation'
            description = "Are you sure you want to switch to {}?\n\n**Switching teams will force you to leave your current team as well as lose all progress including rank and exp! You will also be charged {} pikapoints.**".format(team, COST)
            embed = discord.Embed(title=title, description=description, color=0x4b0082)
            embed.set_thumbnail(url=thumb)
            msg = await context.send(embed=embed)
            await msg.add_reaction('✅')
            await msg.add_reaction('❌')

            def check(reaction, user):
                return user == context.message.author and str(reaction.emoji) in ('✅', '❌')

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await context.send("Team switch timed out...")
            else:
                if str(reaction.emoji) == '❌':
                    await context.send("Team switch declined...")
                elif str(reaction.emoji) == '✅':
                    database_helper.update_team(context.message.author.id, team)
                    database_helper.update_rank(context.message.author.id, 'Recruit')
                    database_helper.update_exp(context.message.author.id, 0, True)
                    database_helper.prestige(context.message.author.id, True)
                    database_helper.adjust_points(context.message.author.id, -COST)
                    await context.send("{} has successfully left {} and joined {}! They now have {} pikapoints.".format(database_helper.get_trainer_team(context.message.author.id)[1], curr_team, team, database_helper.get_pikapoints(context.message.author.id)))

    @commands.command("join")
    async def join(self, context):
        if database_helper.get_trainer_team(context.message.author.id) is None:
            await context.send("You have not registered yourself as a Pokémon Trainer yet!")
            return
        curr_team = database_helper.get_trainer_team(context.message.author.id)[0]
        if curr_team != '':
            await context.send("You are already a member of {}!".format(curr_team))
            return
        title = "Team Invitation"
        description = "You have been invited by 3 different teams to join their ranks - Team Electrocution, Team Lensflare, and Team Hyperjoy! However, you can only choose one.\n\n**Choose wisely - if you switch teams in the future, you will lose all your progress and will be charged pikapoints!**"
        msg = await context.send(embed=discord.Embed(title=title, description=description, color=0x4b0082))
        await msg.add_reaction(':electrocution:496081109558362134')
        await msg.add_reaction(':lensflare:496138997391687710')
        await msg.add_reaction(':hyperjoy:431882995289554978')
        def check(reaction, user):
            return user == context.message.author and reaction.emoji.name in ('lensflare', 'hyperjoy', 'electrocution') and reaction.emoji.id in (496081109558362134, 496138997391687710, 431882995289554978)
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await context.send("Team invitation timed out...")
        else:
            if reaction.emoji.name == 'electrocution' and reaction.emoji.id == 496081109558362134:
                team = 'Team Electrocution'
                thumb = "https://cdn.discordapp.com/emojis/496081109558362134.png?v=1"
            elif reaction.emoji.name == 'lensflare' and reaction.emoji.id == 496138997391687710:
                team = 'Team Lensflare'
                thumb = 'https://cdn.discordapp.com/emojis/496138997391687710.png?v=1'
            elif reaction.emoji.name == 'hyperjoy' and reaction.emoji.id == 431882995289554978:
                team = 'Team Hyperjoy'
                thumb = 'https://cdn.discordapp.com/emojis/431882995289554978.png?v=1'

            title = 'Accept Team Invitation Confirmation'
            description = "Are you sure you want to accept the invitation to join {}?\n\n**Accepting an invitation to join another team in the future will force you to leave this team as well as lose all progress including rank and exp! You will also be charged pikapoints!**".format(team)
            embed = discord.Embed(title=title, description=description, color=0x4b0082)
            embed.set_thumbnail(url=thumb)
            msg = await context.send(embed=embed)
            await msg.add_reaction('✅')
            await msg.add_reaction('❌')
            def check(reaction, user):
                return user == context.message.author and str(reaction.emoji) in ('✅', '❌')
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await context.send("Team invitation timed out...")
            else:
                if str(reaction.emoji) == '❌':
                    await context.send("Team invitation declined...")
                elif str(reaction.emoji) == '✅':
                    database_helper.update_team(context.message.author.id, team)
                    database_helper.update_rank(context.message.author.id, 'Recruit')
                    await context.send("{} has successfully joined {}!".format(database_helper.get_trainer_team(context.message.author.id)[1], team))

    @commands.command(name="prestige")
    async def prestige(self, context):
        trainer = database_helper.get_trainer_team(context.message.author.id)
        trainer_rank = trainer[2]
        trainer_team = trainer[0]
        if trainer_rank != 'Boss':
            await context.send("You are ineligible to prestige!")
            return

        title = 'Prestige Confirmation'
        description = 'Are you sure you want to prestige? Your rank will be reset but you get to flex on those below you.'
        if trainer_team == 'Team Electrocution':
            thumb = "https://cdn.discordapp.com/emojis/496081109558362134.png?v=1"
        elif trainer_team == 'Team Lensflare':
            thumb = 'https://cdn.discordapp.com/emojis/496138997391687710.png?v=1'
        elif trainer_team == 'Team Hyperjoy':
            thumb = 'https://cdn.discordapp.com/emojis/431882995289554978.png?v=1'
        embed = discord.Embed(title=title, description=description, color=0x4b0082)
        embed.set_thumbnail(url=thumb)
        msg = await context.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        def check(reaction, user):
            return user == context.message.author and str(reaction.emoji) in ('✅', '❌')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await context.send("Prestige confirmation timed out...")
        else:
            if str(reaction.emoji) == '❌':
                await context.send("Prestige confirmation declined...")
            elif str(reaction.emoji) == '✅':
                database_helper.prestige(context.message.author.id)
                result = database_helper.get_trainer_team(context.message.author.id)
                database_helper.add_item(context.message.author.id, 4)
                await context.send("{} has reached Prestige Level {} and got a Master Ball!".format(result[1], result[3]))

    @commands.command(name="teams")
    async def teams(self, context):
        teams = [':electrocution:', ':lensflare:', ':hyperjoy:']
        for team in teams:
            await context.invoke(self.team, team)

    @commands.command(name="leaderboard")
    async def leaderboard(self, context, page='totalxp'):
        pages = {
            'totalxp': 0,
            'rolls': 1,
            'bricks': 2,
            'jackpots': 3,
            'opens': 4,
            'releases': 5,
            'trades': 6,
            'quizzes': 7,
            'streaks': 8,
            'shutdowns': 9,
            'highstreak': 10,
            'battles': 11,
            'wins': 12,
            'underdogs': 13,
            'highstakewins': 14,
            'losses': 15,
            'neverlucky': 16,
            'highstakeloss': 17
        }
        inv_pages = {v: k for k, v in pages.items()}
        titles = {
            'totalxp': 'Total EXP Gained',
            'rolls': 'Pokémon Rolled',
            'bricks': 'Bricks',
            'jackpots': 'Jackpot Participation',
            'opens': 'Balls Opened',
            'releases': 'Pokémon Released',
            'trades': 'Pokémon Traded',
            'quizzes': 'Quizzes Answered',
            'streaks': 'Hot Streaks',
            'shutdowns': 'Hot Streak Shutdowns',
            'highstreak': 'Highest Streak',
            'battles': 'Total Battles',
            'wins': 'Total Wins',
            'underdogs': 'Underdog Wins',
            'highstakewins': 'High Stake Wins',
            'losses': 'Total Losses',
            'neverlucky': 'Never Lucky Losses',
            'highstakeloss': 'High Stake Losses'
        }
        try:
            title = "**__{} Leaderboard__**".format(titles[page])
        except KeyError:
            title = "**__Available Leaderboards__**"
            description = ""
            for i in range(len(inv_pages)):
                stat = inv_pages.get(i)
                description += "\n" + stat
            await context.send(embed=discord.Embed(title=title, description=description, color=0x000080))
            return

        leaderboards = database_helper.get_leaderboard(page)
        description = ""
        for leaderboard in leaderboards:
            description += "\n{} --- {}".format(leaderboard[0], leaderboard[1])
        sent_msg = await context.send(embed=discord.Embed(title=title, description=description, color=0x000080))
        page_number = pages[page]
        if 1 <= page_number <= 17:
            await sent_msg.add_reaction("⬅")
        if 0 <= page_number <= 16:
            await sent_msg.add_reaction("➡")

        def check(reaction, user):
            return user == context.message.author and ((str(reaction.emoji) == '⬅' and 1 <= page_number <= 17) or (str(reaction.emoji) == '➡' and 0 <= page_number <= 16))
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return
        else:
            if str(reaction.emoji) == '⬅' and 1 <= page_number <= 17:
                await sent_msg.delete()
                await context.invoke(self.leaderboard, inv_pages[page_number - 1])
            elif str(reaction.emoji) == '➡' and 0 <= page_number <= 16:
                await sent_msg.delete()
                await context.invoke(self.leaderboard, inv_pages[page_number + 1])


    @commands.command(name="gachahelp")
    async def gachahelp(self, context, page=0):
        summon_help = [
            ("focus", "View all pokémon that have a focus summoning rate"),
            ("fullrelease", "Release all pokémon you have of a given rarity (and region) other than those that have been favourited"),
            ("fullroll", "Summon pokémon from an optionally specified region either until you no longer can or for a specified number of times"),
            ("open", "Open a specified ball from your bag"),
            ("pity", "View your pity rates"),
            ("release", "Release a pokémon for pikapoints"),
            ("releasedupes", "See fullroll, but will let you keep one pokémon of every species"),
            ("roll", "Summon a pokémon from an optionally specified region"),
            ("special", "View the currently active Special Pokémon")
        ]
        account_help = [
            ("account", "See points, bag, and box"),
            ("bag", "View the items in your bag"),
            ("balance", "View how many usable pikapoints you have right now"),
            ("bank", "View how many pikapoints you have saved in the bank"),
            ("box", "View all the pokémon you have"),
            ("deposit", "Deposit pikapoints into the bank"),
            ("fav", "Mark a pokémon as favourited so they will not be released when calling fullrelease or releasedupes"),
            ("favs", "View your favourited pokémon"),
            ("party", "View the pokémon you have from a specified region in text form"),
            ("points", "View how many pikapoints you have both on you and in your bank"),
            ("unfav", "Unfavourite a pokémon"),
            ("withdraw", "Withdraw pikapoints from the bank")
        ]
        general_help = [
            ("jackpot", "View the current status of the jackpot"),
            ("pokedex", "View the details of a given pokémon (you may specify a name or ID)"),
            ("units", "View all pokémon and their rarities from a specified region")
        ]
        other_help = [
            ("battle", "Challenge another player to a pokémon battle for a wager of pikapoints"),
            ("trade", "Trade pokémon with another player (both players will be charged pikapoints depending on the rarities of the traded pokémon)")
        ]
        profile_help = [
            ("join", "Join a team"),
            ("leaderboard", "View the top 5 pokémon trainers in each stat"),
            ("prestige", "Prestige your pokémon trainer"),
            ("register", "Register as a pokémon trainer"),
            ("switch", "Switch teams"),
            ("team", "View the members of a team"),
            ("teams", "View all teams"),
            ("trainer", "View a trainer's details and statistics"),
            ("trainers", "View all registered trainers")
        ]
        help_menu = [
            ("Summoning Management Help", summon_help),
            ("Player & Pokémon Management Help", account_help),
            ("Trainer Profile Management Help", profile_help),
            ("General Help", general_help),
            ("Other Help", other_help)
        ]
        page_title = help_menu[page][0]
        commands = help_menu[page][1]
        title = "**__{}__**".format(page_title)
        description = ''
        for command in commands:
            description += "\n**{}** - {}".format(command[0], command[1])
        description += "\n\n**Note that some commands can be called with a user id to view that user's details instead of your own**"
        sent_msg = await context.send(embed=discord.Embed(title=title, description=description, color=0x000000))
        if 1 <= page <= 4:
            await sent_msg.add_reaction("⬅")
        if 0 <= page <= 3:
            await sent_msg.add_reaction("➡")

        def check(reaction, user):
            return user == context.message.author and ((str(reaction.emoji) == '⬅' and 1 <= page <= 4) or (str(reaction.emoji) == '➡' and 0 <= page <= 3))
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return
        else:
            if str(reaction.emoji) == '⬅' and 1 <= page <= 4:
                await sent_msg.delete()
                await context.invoke(self.gachahelp, page - 1)
            elif str(reaction.emoji) == '➡' and 0 <= page <= 3:
                await sent_msg.delete()
                await context.invoke(self.gachahelp, page + 1)

    async def background_quiz(self):
        await self.bot.wait_until_ready()
        SERVER = "server"
        QUIZ_CHANNEL = "quiz_channel"
        if (SERVER not in self.bot.config):
            print("Error: No server configuration found")

        server_config = self.bot.config[SERVER]
        if (QUIZ_CHANNEL not in server_config):
            print("Error: No quiz channel configured")
            return

        quiz_channel_id = server_config[QUIZ_CHANNEL]

        channel = self.bot.get_channel(quiz_channel_id)
        if (channel is None):
            print("Error: Cannot find quiz channel")
            return

        while True:
            t = random.randint(600, 1800)
            high_streak = database_helper.get_high_streak()
            if high_streak is not None:
                next_quiz = datetime.datetime.now() + datetime.timedelta(seconds=t)
                if not 3 < next_quiz.hour < 12:
                    display_hour = (next_quiz - datetime.timedelta(hours=4)).hour % 12
                    if display_hour == 0:
                        display_hour = 12
                    await channel.send("{} is on a {}-streak! Next quiz will be at approximately {}:{:02}. Shut them down!".format(self.bot.get_user(high_streak[0]).name, high_streak[1], display_hour, next_quiz.minute))

            await asyncio.sleep(t) # generate quizzes every 10 - 30 minutes
            if not 3 < datetime.datetime.now().hour < 12: # generate quizzes only from 8am - 12am
                r = random.randint(1, 809) # generate random pokemon
                pokemon = database_helper.get_pokemon_name(r)[0]
                if r in (29, 32):
                    pokemon = 'Nidoran'
                elif r == 669:
                    pokemon = 'Flabebe'
                str_id = "{:03}".format(r)
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
                quiz = discord.Embed(title="Who's That Pokémon?", color=0x00bfff)
                quiz.set_image(url=url)
                await channel.send(embed=quiz)

                def check(m):
                    return m.content == pokemon and m.channel == channel

                try:
                    msg = await self.bot.wait_for('message', timeout=600.0, check=check)
                except asyncio.TimeoutError:
                    await channel.send("It's... {}!".format(pokemon))
                else:
                    curr_streak = database_helper.get_streak(msg.author.id)[0]
                    streaker = database_helper.get_streaker()
                    streak_user = streaker[0]
                    streak = streaker[1]
                    shutdown = 0
                    if self.bot.get_user(int(streak_user)) != msg.author and streak != 1:
                        shutdown = 10 * (streak - 1)
                    gain = min(20 + 10 * curr_streak, 60) + shutdown
                    database_helper.adjust_points(msg.author.id, gain)
                    balance = database_helper.get_pikapoints(msg.author.id)
                    database_helper.update_streak(msg.author.id)
                    new_streak = database_helper.get_streak(msg.author.id)[0]
                    shutdown_msg = ''
                    if shutdown > 0:
                        shutdown_msg = 'You shutdown {} for an additional {} pikapoints! '.format(self.bot.get_user(int(streak_user)).name, str(shutdown))
                    ball_msg = ''
                    if new_streak == 5:
                        database_helper.add_item(msg.author.id, 1)
                        ball_msg = "You got a Poké Ball!"
                    elif new_streak == 10:
                        database_helper.add_item(msg.author.id, 2)
                        ball_msg = "You got a Great Ball!"
                    elif new_streak == 15:
                        database_helper.add_item(msg.author.id, 3)
                        ball_msg = "You got an Ultra Ball!"
                    elif new_streak % 5 == 0 and new_streak >= 20:
                        database_helper.add_item(msg.author.id, 4)
                        ball_msg = "You got a Master Ball!"
                    team_split = database_helper.team_split(msg.author.id, streak_user, streak, gain)
                    team_split_msg = ''
                    if team_split is not None:
                        team_name = database_helper.get_trainer_team(msg.author.id)[0]
                        team = database_helper.get_team(team_name)
                        for member in team:
                            if member[2] != msg.author.id:
                                database_helper.adjust_points(member[2], team_split)
                        team_split_msg = "All other {} members received {} pikapoints!".format(team_name, team_split)
                    await channel.send('Congratulations {}! {}You win {} pikapoints!\nYou now have {} pikapoints.\n\nStreak: {}\n{}\n\n{}'.format(msg.author.name, shutdown_msg, str(gain), str(balance), new_streak, ball_msg, team_split_msg))
                    database_helper.increment_stat(msg.author.id, "quizzes")
                    database_helper.update_exp(msg.author.id, 1)
                    promote = database_helper.promote(msg.author.id)
                    if promote is not None:
                        await channel.send(promote)
                    if new_streak == 5:
                        database_helper.increment_stat(msg.author.id, "streaks")
                    if shutdown >= 40:
                        database_helper.increment_stat(msg.author.id, "shutdowns")
                    if database_helper.get_trainer_team(msg.author.id) is not None and new_streak > database_helper.get_trainer_team(msg.author.id)[5]:
                        database_helper.update_high_streak(msg.author.id, new_streak)


def setup(bot):
    bot.add_cog(SenpaiGacha(bot))
