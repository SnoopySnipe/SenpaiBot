import discord
import random
from discord.ext import commands
import database_helper
import pokebase as pb
import asyncio
import datetime
import time
from PIL import Image
import requests
from io import BytesIO

SNOOPY_ID = 103634047929962496
KANTO = ('Kanto', 1, 151)
JOHTO = ('Johto', 152, 251)
HOENN = ('Hoenn', 252, 386)
SINNOH = ('Sinnoh', 387, 493)
UNOVA = ('Unova', 494, 649)
KALOS = ('Kalos', 650, 721)
ALOLA = ('Alola', 722, 809)
REGIONS = [KANTO, JOHTO, HOENN, SINNOH, UNOVA]#, KALOS, ALOLA]
QUIZ_CHANNEL_ID = 542441381210226748 #349942469804425216
COMMANDS_CHANNEL_ID = 282336977418715146
LEAGUE_ID = 401518684763586560
class SenpaiGacha:
    def __init__(self, bot):
        self.bot = bot
        self.league_players = list()
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

    @commands.command(name="forceroll")
    async def forceroll(self, context, region=None, user_id=None):
        if context.message.author.id != SNOOPY_ID:
            await context.send("You're not Snoopy-san...")
            return

        PRICE = 30
        if user_id is None:
            await context.send("user_id cannot be None!")
            return
        user = self.bot.get_user(int(user_id))
        username = user.name
        database_helper.adjust_pity(user_id)
        details = database_helper.get_user_details(user_id)
        if details is None:
            await context.send("{} has no pikapoints! Join voice and start earning!".format(username))
        elif PRICE <= details[0]:
            balance = details[0]
            rolls = balance // 30

            if region is None:
                await context.send("`Usage:`\n```!senpai forceroll region user_id```")
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
            # elif region == 'kalos':
            #     region = KALOS
            # elif region == 'alola':
            #     region = ALOLA
            elif region == 'all':
                region = None
            else:
                await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'all')")
                return

            if rolls == 0:
                await context.send("There is nothing to roll...")
                return

            await context.send("{} currently has {} pikapoints.\nRolling {} times...".format(username, str(balance), str(rolls)))
            database_helper.adjust_points(user_id, -(PRICE * rolls))
            for i in range(rolls):
                details = database_helper.get_user_details(user_id)
                r = random.randint(0, 1003)
                if r == 0:
                    options = database_helper.get_roll(7, region)
                    database_helper.adjust_pity(user_id, True)
                    database_helper.update_jackpot(user_id, False)
                elif 1001 <= r <= 1003:
                    options = database_helper.get_roll(6, region)
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
                database_helper.add_inventory(user_id, gacha[1])
                embed = discord.Embed(title=title, description=description, color=0x9370db)
                str_id = "{:03}".format(gacha[1])
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
                embed.set_thumbnail(url=url)
                await context.send(embed=embed)
                if gacha[2] > 5:
                    jackpot = database_helper.get_jackpot(True)[0]
                    no_contributors = len(database_helper.get_jackpot_rewards())
                    if no_contributors == 0:
                        if gacha[2] == 6:
                            str_rarity = 'Legendary'
                        elif gacha[2] == 7:
                            str_rarity = 'Mythic'
                        await context.send(
                            '{} summoned a {} Pokémon! The jackpot contained {} pikapoints. No users contributed at least 3 points to the jackpot, therefore the jackpot will not be reset.'.format(
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
                        msg = msg + 'Legendary Pokémon! The jackpot contained {} pikapoints. The following users contributed at least 3 points to the jackpot and will each receive {} pikapoints and a **{}**:```'.format(
                            jackpot, payout, ball_str)
                    elif gacha[2] == 7:
                        payout = (jackpot * 2) // no_contributors
                        msg = msg + 'Mythic Pokémon! The jackpot contained {} pikapoints --> x2 Mythic Multiplier --> {} pikapoints. The following users contributed at least 3 points to the jackpot and will each receive {} pikapoints and a **{}**:```'.format(
                            jackpot, jackpot * 2, payout, ball_str)
                    contributors = database_helper.get_jackpot(False)
                    for contributor in contributors:
                        if contributor[1] >= 3:
                            database_helper.adjust_points(contributor[0], payout)
                            database_helper.add_item(contributor[0], ball_id)
                            msg = msg + '\n' + self.bot.get_user(contributor[0]).name
                    msg = msg + '```'
                    database_helper.update_jackpot(user_id, True)
                    await context.send(msg)
            balance = database_helper.get_pikapoints(user_id)
            await context.send("{} now has {} pikapoints.".format(username, str(balance)))
        else:
            await context.send("{} doesn't have enough pikapoints to summon! It costs {} pikapoints per roll!".format(username, str(PRICE)))

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
                await context.send("`Usage:`\n```!senpai fullroll region [no_rolls]```")
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
            # elif region == 'kalos':
            #     region = KALOS
            # elif region == 'alola':
            #     region = ALOLA
            elif region == 'all':
                region = None
            else:
                await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'all')")
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

            await context.send("You currently have {} pikapoints.\nRolling {} times...".format(str(balance), str(rolls)))
            database_helper.adjust_points(user_id, -(PRICE*rolls))
            for i in range(rolls):
                details = database_helper.get_user_details(user_id)
                r = random.randint(0, 1003)
                if r == 0:
                    options = database_helper.get_roll(7, region)
                    database_helper.adjust_pity(user_id, True)
                    database_helper.update_jackpot(user_id, False)
                elif 1001 <= r <= 1003:
                    options = database_helper.get_roll(6, region)
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
                database_helper.add_inventory(user_id, gacha[1])
                embed = discord.Embed(title=title, description=description, color=0x9370db)
                str_id = "{:03}".format(gacha[1])
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
                embed.set_thumbnail(url=url)
                await context.send(embed=embed)
                if gacha[2] > 5:
                    jackpot = database_helper.get_jackpot(True)[0]
                    no_contributors = len(database_helper.get_jackpot_rewards())
                    if no_contributors == 0:
                        if gacha[2] == 6:
                            str_rarity = 'Legendary'
                        elif gacha[2] == 7:
                            str_rarity = 'Mythic'
                        await context.send(
                            '{} summoned a {} Pokémon! The jackpot contained {} pikapoints. No users contributed at least 3 points to the jackpot, therefore the jackpot will not be reset.'.format(
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
                        msg = msg + 'Legendary Pokémon! The jackpot contained {} pikapoints. The following users contributed at least 3 points to the jackpot and will each receive {} pikapoints and a **{}**:```'.format(
                            jackpot, payout, ball_str)
                    elif gacha[2] == 7:
                        payout = (jackpot * 2) // no_contributors
                        msg = msg + 'Mythic Pokémon! The jackpot contained {} pikapoints --> x2 Mythic Multiplier --> {} pikapoints. The following users contributed at least 3 points to the jackpot and will each receive {} pikapoints and a **{}**:```'.format(
                            jackpot, jackpot * 2, payout, ball_str)
                    contributors = database_helper.get_jackpot(False)
                    for contributor in contributors:
                        if contributor[1] >= 3:
                            database_helper.adjust_points(contributor[0], payout)
                            database_helper.add_item(contributor[0], ball_id)
                            msg = msg + '\n' + self.bot.get_user(contributor[0]).name
                    msg = msg + '```'
                    database_helper.update_jackpot(user_id, True)
                    await context.send(msg)
            balance = database_helper.get_pikapoints(user_id)
            await context.send("You now have {} pikapoints.".format(str(balance)))
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
            # elif region == 'kalos':
            #     region = KALOS
            # elif region == 'alola':
            #     region = ALOLA
            elif region is not None:
                await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', None)")
                return

            if r == 0:
                options = database_helper.get_roll(7, region)
                database_helper.adjust_pity(user_id, True)
                database_helper.update_jackpot(user_id, False)
            elif 1001 <= r <= 1003:
                options = database_helper.get_roll(6, region)
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
            database_helper.adjust_points(user_id, -PRICE)
            balance = database_helper.get_pikapoints(user_id)
            database_helper.add_inventory(user_id, gacha[1])
            embed = discord.Embed(title=title, description=description, color=0x9370db)
            str_id = "{:03}".format(gacha[1])
            url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            embed.set_thumbnail(url=url)
            await context.send("You now have " + str(balance) + " pikapoints.", embed=embed)
            if gacha[2] > 5:
                jackpot = database_helper.get_jackpot(True)[0]
                no_contributors = len(database_helper.get_jackpot_rewards())
                if no_contributors == 0:
                    if gacha[2] == 6:
                        str_rarity = 'Legendary'
                    elif gacha[2] == 7:
                        str_rarity = 'Mythic'
                    await context.send('{} summoned a {} Pokémon! The jackpot contained {} pikapoints. No users contributed at least 3 points to the jackpot, therefore the jackpot will not be reset.'.format(username, str_rarity, jackpot))
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
                    msg = msg + 'Legendary Pokémon! The jackpot contained {} pikapoints. The following users contributed at least 3 points to the jackpot and will each receive {} pikapoints and a **{}**:```'.format(
                        jackpot, payout, ball_str)
                elif gacha[2] == 7:
                    payout = (jackpot * 2) // no_contributors
                    msg = msg + 'Mythic Pokémon! The jackpot contained {} pikapoints --> x2 Mythic Multiplier --> {} pikapoints. The following users contributed at least 3 points to the jackpot and will each receive {} pikapoints and a **{}**:```'.format(
                        jackpot, jackpot * 2, payout, ball_str)
                contributors = database_helper.get_jackpot(False)
                for contributor in contributors:
                    if contributor[1] >= 3:
                        database_helper.adjust_points(contributor[0], payout)
                        database_helper.add_item(contributor[0], ball_id)
                        msg = msg + '\n' + self.bot.get_user(contributor[0]).name
                msg = msg + '```'
                database_helper.update_jackpot(user_id, True)
                await context.send(msg)
        else:
            await context.send("You don't have enough pikapoints to summon! It costs {} pikapoints per roll!".format(str(PRICE)))

    @commands.command(name="pokedex")
    async def pokedex(self, context, name=None):
        if name is None:
            await context.send("`Usage:`\n```!senpai pokedex pokemon_name_or_id```")
            return
        poke_id = database_helper.get_pokemon(name)
        poke_name = database_helper.get_pokemon_name(name)
        if poke_id is not None:
            str_id = "{:03}".format(poke_id[0])
            url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            dex = discord.Embed(title="ID: {}\nName: {}".format(str(poke_id[0]), name), color=0xffb6c1)
            dex.set_image(url=url)
            await context.send(embed=dex)
        elif poke_name is not None:
            str_id = "{:03}".format(int(name))
            url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            dex = discord.Embed(title="ID: {}\nName: {}".format(str(name), poke_name[0]), color=0xffb6c1)
            dex.set_image(url=url)
            await context.send(embed=dex)
        else:
            await context.send("Pokémon name or ID doesn't exist!")

    @commands.command(name="trade")
    async def trade(self, context, pokemon1=None, pokemon2=None, id2=None):
        if pokemon1 is None or pokemon2 is None or id2 is None:
            await context.send("`Usage:`\n```!senpai trade your_pokemon their_pokemon their_id```")
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

        balance1 = database_helper.get_pikapoints(id1)
        balance2 = database_helper.get_pikapoints(id2)
        if balance1 < cost:
            await context.send("You don't have enough pikapoints to perform this trade! This trade requires both users to have {} pikapoints.\nYou have {} pikapoints. They have {} pikapoints.".format(str(cost), str(balance1), str(balance2)))
            return
        if balance2 < cost:
            await context.send("They don't have enough pikapoints to perform this trade! This trade requires both users to have {} pikapoints.\nYou have {} pikapoints. They have {} pikapoints.".format(str(cost), str(balance1), str(balance2)))
            return

        user1 = self.bot.get_user(int(id1))
        user2 = self.bot.get_user(int(id2))
        username1 = user1.name
        username2 = user2.name

        title = "Trade Request"
        description = "{} wants to trade: {}\nFor {}'s: {}".format(username1, pokemon1, username2, pokemon2)
        msg = await context.send(embed=discord.Embed(title=title, description=description, color=0xff0000))
        await msg.add_reaction('✅')

        def check(reaction, user):
            return user == user2 and str(reaction.emoji) == '✅'
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await context.send("Trade timed out...")
        else:
            database_helper.perform_trade(id1, id2, pokemon1_id[0], pokemon2_id[0])
            database_helper.adjust_points(id1, -cost)
            database_helper.adjust_points(id2, -cost)
            new_balance1 = database_helper.get_pikapoints(id1)
            new_balance2 = database_helper.get_pikapoints(id2)
            await context.send("{} has {} pikapoints. {} has {} pikapoints.\nPerforming trade...\nTrade successful! {} now has {} pikapoints. {} now has {} pikapoints.".format(
                username1, str(balance1), username2, str(balance2), username1, str(new_balance1), username2, str(new_balance2)
            ))

    @commands.command(name="forceopen")
    async def forceopen(self, context, user_id=None, ball=None):
        if context.message.author.id != SNOOPY_ID:
            await context.send("You're not Snoopy-san...")
            return

        if user_id is None:
            await context.send("`Usage:`\n```!senpai forceopen user_id```")
            return

        if ball is None:
            bag = database_helper.get_bag(user_id)
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
                await context.invoke(self.forceopen, user_id, ball)
            return

        if ball == 'pokeball':
            ball_id = 1
        elif ball == 'greatball':
            ball_id = 2
        elif ball == 'ultraball':
            ball_id = 3
        elif ball == 'masterball':
            ball_id = 4

        user = self.bot.get_user(int(user_id))
        username = user.name

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
            await context.send("{} opened a {} and got {} pikapoints! They now have {} pikapoints.".format(username, ball_str,
                                                                                                     pt_prize, balance))
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
                elif roll_range[5] + roll_range[6] < roll <= 100:
                    options = database_helper.get_roll(7)
            gacha = random.choice(options)
            title = "{} Opened: \n".format(username)
            if gacha[2] <= 5:
                description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
            elif gacha[2] == 6:
                description = gacha[0] + "\nRarity: Legendary"
            elif gacha[2] == 7:
                description = gacha[0] + "\nRarity: Mythic"
            database_helper.add_inventory(user_id, gacha[1])
            embed = discord.Embed(title=title, description=description, color=0x9370db)
            str_id = "{:03}".format(gacha[1])
            url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            embed.set_thumbnail(url=url)
            await context.send("{} opened a {} and got a {}!".format(username, ball_str, gacha[0]), embed=embed)

    @commands.command(name="open")
    async def open(self, context, ball=None):
        if ball is None:
            await context.send("`Usage:`\n```!senpai open ball_name```")
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
                elif roll_range[5] + roll_range[6] < roll <= 100:
                    options = database_helper.get_roll(7)
            gacha = random.choice(options)
            title = "{} Opened: \n".format(username)
            if gacha[2] <= 5:
                description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
            elif gacha[2] == 6:
                description = gacha[0] + "\nRarity: Legendary"
            elif gacha[2] == 7:
                description = gacha[0] + "\nRarity: Mythic"
            database_helper.add_inventory(user_id, gacha[1])
            embed = discord.Embed(title=title, description=description, color=0x9370db)
            str_id = "{:03}".format(gacha[1])
            url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            embed.set_thumbnail(url=url)
            await context.send("{} opened a {} and got a {}!".format(username, ball_str, gacha[0]), embed=embed)



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
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
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
                        (save_location, curr_index, remain_num) = self.draw_box(context, bag, curr_index,
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
    async def box(self, context, user_id=None):
        await self.box_page(context, 1, user_id)
    async def box_page(self, context, page_num, user_id):
    #img = Image.open('images/crate.png', 'r')
        if user_id is None:
            user_id = context.message.author.id
        username = self.bot.get_user(int(user_id)).name
        inventory = database_helper.get_inventory(user_id)
        if len(inventory) == 0:
            await context.send("You have no pokémon on page {}! Start rolling!".format(page_num))
        else:
            page_indices = {1:(0,0)}
            num_pokemon = 0
            for pokemon in inventory:
                num_pokemon += pokemon[4]
            (save_location, curr_index, remain_num) = self.draw_box(context, inventory, 0, 0)
            file = discord.File(save_location, filename='team.png')
            msg = await context.channel.send(username+"'s team (page " + str(page_num) +")", file=file)
            await msg.add_reaction("⬅")
            await msg.add_reaction("➡")
            def check(reaction, user):
                return user == context.message.author and (str(reaction.emoji) == "⬅" or str(reaction.emoji) == "➡")
            timed_out = False
            while(not timed_out):
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
                except asyncio.TimeoutError:
                    timed_out = True
                else:
                    is_left = (str(reaction.emoji) == "⬅")
                    is_right = (str(reaction.emoji) == "➡")
                    if(( is_left and page_num-1>=1) or (is_right and (num_pokemon -(page_num)*32) > 0)):
                        inc = -1 if is_left else 1
                        page_num += inc
                        if(page_num in page_indices):
                            (curr_index, remain_num) = page_indices[page_num]
                        if(page_num not in page_indices):
                            page_indices[page_num] = (curr_index, remain_num)
                        (save_location, curr_index, remain_num) = self.draw_box(context, inventory, curr_index, remain_num)
                        file = discord.File(save_location, filename='team.png')
                        await msg.delete()
                        msg = await context.channel.send(username+"'s team (page " + str(page_num) +")", file=file)
                        await msg.add_reaction("⬅")
                        await msg.add_reaction("➡")
    def draw_box(self, context, inventory, index, remain_num):
        #background = Image.new('RGBA', (850,450), (255, 255, 255))
        background = Image.open('images/inv_background.png', 'r')
        background = background.resize((850, 450))
        (x, y) = (0, 0)
        count = 0
        remain_overflow = 0
        if(remain_num != 0):
            init = True
        else:
            init = False
        while(count < 32 and index < len(inventory)):
            pokemon = inventory[index]
            if(init):
                pokemon_num = remain_num
                init = False
            else:
                pokemon_num = pokemon[4]
            index += 1
            pokemon_id = pokemon[1]
            sprite = pb.SpriteResource('pokemon', pokemon_id)
            img = Image.open(sprite.path).convert("RGBA")
            img = img.resize((150,150))
            for i in range(pokemon_num):
                #img = Image.open("images/pokemon/"+pokemon[2]+".png")
                offset = (x*100, y*100)
                background.paste(img, offset, img)
                count += 1
                if(count >= 32):
                    remain_overflow = pokemon_num - i - 1
                    break;
                x += 1
                if(x == 8):
                    x = 0
                    y += 1
        save_location = 'images/'+str(context.message.author.id)+'.png'
        background.save(save_location)
        if(remain_overflow > 0):
            index-=1
        return (save_location, index, remain_overflow)
    @commands.command(name="team")
    async def team(self, context, region=None, user_id=None):
        if region is None:
            await context.send("`Usage:`\n```!senpai team region [user_id]```")
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
        # elif region == 'kalos':
        #     region = KALOS
        # elif region == 'alola':
        #     region = ALOLA
        else:
            return
        if user_id is None:
            user_id = context.message.author.id
        username = self.bot.get_user(int(user_id)).name
        title = "{}'s {} Team: \n".format(username, region[0])
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
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

    @commands.command(name="forcerelease")
    async def forcerelease(self, context, user_id=None, rarity=None):
        if context.message.author.id != SNOOPY_ID:
            await context.send("You're not Snoopy-san...")
            return

        if user_id is None:
            await context.send("`Usage:`\n```!senpai forcerelease user_id```")
            return

        if rarity is None:
            rarities = ['3', '4', '5']
            for r in rarities:
                await context.invoke(self.forcerelease, user_id, r)
            return

        user = self.bot.get_user(int(user_id))
        username = user.name
        balance = database_helper.get_pikapoints(user_id)
        region = None
        str_region = "all regions"
        rows = database_helper.full_remove_inventory(user_id, rarity, region)
        if rows == 0:
            await context.send("There is no {}⭐ pokémon to release...".format(rarity))
            return
        if rarity == '3':
            gain = 5
        elif rarity == '4':
            gain = 10
        elif rarity == '5':
            gain = 15
        database_helper.adjust_points(user_id, gain * rows)
        total_gain = gain * rows
        await context.send(
            "{} currently has {} pikapoints.\nReleasing {} {}⭐ Pokémon from {}...\n{} got {} pikapoints!\n{} now has {} pikapoints.".format(
                username, str(balance), rows, rarity, str_region, username, total_gain, username,
                database_helper.get_pikapoints(user_id)))



    @commands.command(name="fullrelease")
    async def fullrelease(self, context, rarity=None, region=None):
        if rarity is None:
            await context.send("`Usage:`\n```!senpai fullrelease rarity [region]```")
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
        # elif region == 'kalos':
        #     region = KALOS
        # elif region == 'alola':
        #     region = ALOLA
        elif region is not None:
            await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', None)")
            return

        if rarity == 'all':
            rarities = ['3', '4', 'five']
            for r in rarities:
                await context.invoke(self.fullrelease, r, region_str)
            return

        if rarity == 'five':
            rarity = '5'
        elif rarity == '5':
            await context.send("`Usage:`\n```!senpai fullrelease five [region]```")
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

    @commands.command(name="releasedupes")
    async def releasedupes(self, context, rarity=None, region=None):
        if rarity is None:
            await context.send("`Usage:`\n```!senpai releasedupes rarity [region]```")
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
        # elif region == 'kalos':
        #     region = KALOS
        # elif region == 'alola':
        #     region = ALOLA
        elif region is not None:
            await context.send("Region must be in ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', None)")
            return

        if rarity == 'all':
            rarities = ['3', '4', 'five']
            for r in rarities:
                await context.invoke(self.releasedupes, r, region_str)
            return

        if rarity == 'five':
            rarity = '5'
        elif rarity == '5':
            await context.send("`Usage:`\n```!senpai releasedupes five [region]```")
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

    @commands.command(name="release")
    async def release(self, context, name=None):
        if name is None:
            await context.send("`Usage:`\n```!senpai release pokemon_name```")
            return
        pokemon = database_helper.get_pokemon(name)
        if pokemon is not None:
            if database_helper.get_from_inventory(context.message.author.id, pokemon[0]):
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
                database_helper.adjust_points(context.message.author.id, gain)
                await context.send("Successfully released {}. You got {} pikapoints!\nYou now have {} pikapoints.".format(name, gain, database_helper.get_pikapoints(context.message.author.id)))
            else:
                await context.send("You do not have that Pokémon!")
        else:
            await context.send("Invalid Pokémon name!")

    @commands.command(name="fav")
    async def fav(self, context, name=None):
        if name is None:
            await context.send("`Usage:`\n```!senpai fav pokemon_name```")
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
            await context.send("`Usage:`\n```!senpai unfav pokemon_name```")
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
            await context.send("You're not Snoopy-san...")

    @commands.command(name="sql")
    async def sql(self, context, query):
        if context.message.author.id == SNOOPY_ID:
            database_helper.run_sql(query)
        else:
            await context.send("You're not Snoopy-san...")


    @commands.command(name="units")
    async def units(self, context, region=None):
        if region is None:
            await context.send("`Usage:`\n```!senpai units region```")
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
        # elif region == 'kalos':
        #     region = KALOS
        # elif region == 'alola':
        #     region = ALOLA
        else:
            return
        units = database_helper.get_units(region)
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
            await context.send("`Usage:`\n```!senpai deposit amount```")
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
            await context.send("`Usage:`\n```!senpai withdraw amount```")
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

    async def background_quiz(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(QUIZ_CHANNEL_ID)
        if(channel is None):
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
                r = random.randint(1, 649) # generate random pokemon
                pokemon = database_helper.get_pokemon_name(r)[0]
                if r in (29, 32):
                    pokemon = 'Nidoran'
                str_id = "{:03}".format(r)
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
                quiz = discord.Embed(title="Who's That Pokémon?", color=0x00bfff)
                quiz.set_image(url=url)
                await channel.send(embed=quiz)

                def check(m):
                    return m.content == pokemon and m.channel == channel

                try:
                    msg = await self.bot.wait_for('message', timeout=300.0, check=check)
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
                    gain = min(30 + 15 * curr_streak, 90) + shutdown
                    database_helper.adjust_points(msg.author.id, gain)
                    balance = database_helper.get_pikapoints(msg.author.id)
                    database_helper.update_streak(msg.author.id)
                    new_streak = database_helper.get_streak(msg.author.id)[0]
                    shutdown_msg = ''
                    if shutdown > 0:
                        shutdown_msg = 'You shutdown {} for an additional {} pikapoints! '.format(self.bot.get_user(int(streak_user)).name, str(shutdown))
                    await channel.send('Congratulations {.author}! {}You win {} pikapoints!\nYou now have {} pikapoints.\nStreak: {}'.format(msg, shutdown_msg, str(gain), str(balance), new_streak))


def setup(bot):
    bot.add_cog(SenpaiGacha(bot))
