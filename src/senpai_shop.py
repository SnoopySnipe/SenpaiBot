import discord
import random
from discord.ext import commands
import database_helper
import pokebase as pb
import asyncio
import datetime
import time
from PIL import Image

SNOOPY_ID = 103634047929962496
KANTO = ('Kanto', 1, 151)
JOHTO = ('Johto', 152, 251)
HOENN = ('Hoenn', 252, 386)
SINNOH = ('Sinnoh', 387, 493)
UNOVA = ('Unova', 494, 649)
KALOS = ('Kalos', 650, 721)
ALOLA = ('Alola', 722, 809)
REGIONS = [KANTO, JOHTO, HOENN]#, SINNOH, UNOVA, KALOS, ALOLA]
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

    @commands.command(name="fullroll")
    async def fullroll(self, context, region=None):
        PRICE = 30
        database_helper.adjust_pity(context.message.author.id)
        details = database_helper.get_user_details(context.message.author.id)
        if details is None:
            await context.send("You have no pikapoints! Join voice and start earning!")
        elif PRICE <= details[0]:
            balance = details[0]
            rolls = balance // 30

            if region == 'kanto':
                region = KANTO
            elif region == 'johto':
                region = JOHTO
            elif region == 'hoenn':
                region = HOENN
            # elif region == 'sinnoh':
            #     region = SINNOH
            # elif region == 'unova':
            #     region = UNOVA
            # elif region == 'kalos':
            #     region = KALOS
            # elif region == 'alola':
            #     region = ALOLA
            elif region is not None:
                await context.send("Region must be in ('kanto', 'johto', None)")
                return
            await context.send("You currently have {} pikapoints.\nRolling {} times...".format(str(balance), str(rolls)))
            database_helper.adjust_points(context.message.author.id, -(PRICE*rolls))
            for i in range(rolls):
                details = database_helper.get_user_details(context.message.author.id)
                r = random.randint(0, 1003)
                if r == 0:
                    options = database_helper.get_roll(7, region)
                    database_helper.adjust_pity(context.message.author.id, True)
                elif 1001 <= r <= 1003:
                    options = database_helper.get_roll(6, region)
                    database_helper.adjust_pity(context.message.author.id, True)
                elif 1 <= r <= details[1]:
                    options = database_helper.get_roll(3, region)
                    database_helper.adjust_pity(context.message.author.id, False)
                elif details[1] < r <= details[1] + details[2]:
                    options = database_helper.get_roll(4, region)
                    database_helper.adjust_pity(context.message.author.id, False)
                elif details[1] + details[2] < r <= details[1] + details[2] + details[3]:
                    options = database_helper.get_roll(5, region)
                    database_helper.adjust_pity(context.message.author.id, True)
                elif details[1] + details[2] + details[3] < r <= 1000:
                    options = database_helper.get_roll(1, region)
                    database_helper.adjust_pity(context.message.author.id, True)
                gacha = options[random.randint(0, len(options) - 1)]
                title = "{} Summoned: \n".format(context.message.author.name)
                if gacha[2] <= 5:
                    description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
                elif gacha[2] == 6:
                    description = gacha[0] + "\nRarity: Legendary"
                elif gacha[2] == 7:
                    description = gacha[0] + "\nRarity: Mythic"
                database_helper.add_inventory(context.message.author.id, gacha[1])
                embed = discord.Embed(title=title, description=description, color=0x9370db)
                str_id = "{:03}".format(gacha[1])
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
                embed.set_thumbnail(url=url)
                await context.send(embed=embed)
            balance = database_helper.get_pikapoints(context.message.author.id)
            await context.send("You now have {} pikapoints.".format(str(balance)))
        else:
            await context.send("You don't have enough pikapoints to summon! It costs {} pikapoints per roll!".format(str(PRICE)))

    @commands.command(name="roll")
    async def roll(self, context, region=None):
        PRICE = 30
        database_helper.adjust_pity(context.message.author.id)
        details = database_helper.get_user_details(context.message.author.id)
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
            # elif region == 'sinnoh':
            #     region = SINNOH
            # elif region == 'unova':
            #     region = UNOVA
            # elif region == 'kalos':
            #     region = KALOS
            # elif region == 'alola':
            #     region = ALOLA
            elif region is not None:
                await context.send("Region must be in ('kanto', 'johto', None)")
                return

            if r == 0:
                options = database_helper.get_roll(7, region)
                database_helper.adjust_pity(context.message.author.id, True)
            elif 1001 <= r <= 1003:
                options = database_helper.get_roll(6, region)
                database_helper.adjust_pity(context.message.author.id, True)
            elif 1 <= r <= details[1]:
                options = database_helper.get_roll(3, region)
                database_helper.adjust_pity(context.message.author.id, False)
            elif details[1] < r <= details[1] + details[2]:
                options = database_helper.get_roll(4, region)
                database_helper.adjust_pity(context.message.author.id, False)
            elif details[1] + details[2] < r <= details[1] + details[2] + details[3]:
                options = database_helper.get_roll(5, region)
                database_helper.adjust_pity(context.message.author.id, True)
            elif details[1] + details[2] + details[3] < r <= 1000:
                options = database_helper.get_roll(1, region)
                database_helper.adjust_pity(context.message.author.id, True)
            gacha = options[random.randint(0, len(options) - 1)]
            title = "{} Summoned: \n".format(context.message.author.name)
            if gacha[2] <= 5:
                description = gacha[0] + "\nRarity: {}⭐".format(gacha[2])
            elif gacha[2] == 6:
                description = gacha[0] + "\nRarity: Legendary"
            elif gacha[2] == 7:
                description = gacha[0] + "\nRarity: Mythic"
            database_helper.adjust_points(context.message.author.id, -PRICE)
            balance = database_helper.get_pikapoints(context.message.author.id)
            database_helper.add_inventory(context.message.author.id, gacha[1])
            embed = discord.Embed(title=title, description=description, color=0x9370db)
            str_id = "{:03}".format(gacha[1])
            url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            embed.set_thumbnail(url=url)
            await context.send("You now have " + str(balance) + " pikapoints.", embed=embed)
        else:
            await context.send("You don't have enough pikapoints to summon! It costs {} pikapoints per roll!".format(str(PRICE)))

    @commands.command(name="pokedex")
    async def pokedex(self, context, name=None):
        if name is None:
            await context.send("`Usage:`\n```!senpai pokedex pokemon_name```")
            return
        poke_id = database_helper.get_pokemon(name)
        if poke_id is not None:
            str_id = "{:03}".format(poke_id[0])
            url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
            dex = discord.Embed(title="ID: {}\nName: {}".format(str(poke_id[0]), name), color=0xffb6c1)
            dex.set_image(url=url)
            await context.send(embed=dex)
        else:
            await context.send("Invalid Pokemon name!")

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
                await context.send("You do not have that Pokemon!")
                return
        else:
            await context.send("Invalid Pokemon name!")
            return

        pokemon2_id = database_helper.get_pokemon(pokemon2)
        if pokemon2_id is not None:
            if database_helper.get_from_inventory(id2, pokemon2_id[0]):
                rarity2 = pokemon2_id[1]
            else:
                await context.send("They do not have that Pokemon!")
                return
        else:
            await context.send("Invalid Pokemon name!")
            return

        if pokemon1 == pokemon2:
            await context.send("Pokemon must be different!")
            return

        if rarity1 == rarity2:
            cost = 60 * rarity1
        else:
            await context.send("Pokemon's rarities must match!")
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
            await context.send("You have no pokemon on page {}! Start rolling!".format(page_num))
        else:
            page_indices = {1:(0,0)}
            num_pokemon = 0
            for pokemon in inventory:
                num_pokemon += pokemon[4]
            (save_location, curr_index, remain_num) = self.draw_box(context, inventory, 0, 0)
            file = discord.File(save_location, filename='inventory.png')
            msg = await context.channel.send(username+"'s inventory (page " + str(page_num) +")", file=file)
            await msg.add_reaction("⬅")
            await msg.add_reaction("➡")
            def check(reaction, user):
                return user == context.message.author and (str(reaction.emoji) == "⬅" or str(reaction.emoji) == "➡")
            timed_out = False
            while(not timed_out):
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
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
                        file = discord.File(save_location, filename='inventory.png')
                        await msg.delete()
                        msg = await context.channel.send(username+"'s inventory (page " + str(page_num) +")", file=file)
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
        # elif region == 'sinnoh':
        #     region = SINNOH
        # elif region == 'unova':
        #     region = UNOVA
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

    @commands.command(name="fullrelease")
    async def fullrelease(self, context, rarity=None, region=None):
        if rarity is None:
            await context.send("`Usage:`\n```!senpai fullrelease rarity [region]```")
            return
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        elif region == 'hoenn':
            region = HOENN
        # elif region == 'sinnoh':
        #     region = SINNOH
        # elif region == 'unova':
        #     region = UNOVA
        # elif region == 'kalos':
        #     region = KALOS
        # elif region == 'alola':
        #     region = ALOLA
        elif region is not None:
            await context.send("Region must be in ('kanto', 'johto', None)")
            return

        if rarity not in ('3', '4'):
            await context.send("You can only full release 3⭐ and 4⭐ rarity Pokemon!")
        else:
            balance = database_helper.get_pikapoints(context.message.author.id)
            if region is None:
                str_region = "all regions"
            else:
                str_region = "the " + region[0] + " region"
            rows = database_helper.full_remove_inventory(context.message.author.id, rarity, region)
            await context.send("You currently have {} pikapoints.\nReleasing {} {}⭐ Pokemon from {}...".format(str(balance), rows, rarity, str_region))
            if rarity == '3':
                gain = 5
            elif rarity == '4':
                gain = 10
            database_helper.adjust_points(context.message.author.id, gain*rows)
            total_gain = gain*rows
            await context.send("You got {} pikapoints!\nYou now have {} pikapoints.".format(total_gain, database_helper.get_pikapoints(context.message.author.id)))

    @commands.command(name="releasedupes")
    async def releasedupes(self, context, rarity=None, region=None):
        if rarity is None:
            await context.send("`Usage:`\n```!senpai releasedupes rarity [region]```")
            return
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        elif region == 'hoenn':
            region = HOENN
        # elif region == 'sinnoh':
        #     region = SINNOH
        # elif region == 'unova':
        #     region = UNOVA
        # elif region == 'kalos':
        #     region = KALOS
        # elif region == 'alola':
        #     region = ALOLA
        elif region is not None:
            await context.send("Region must be in ('kanto', 'johto', None)")
            return

        if rarity not in ('3', '4'):
            await context.send("You can only dupe release 3⭐ and 4⭐ rarity Pokemon!")
        else:
            balance = database_helper.get_pikapoints(context.message.author.id)
            if region is None:
                str_region = "all regions"
            else:
                str_region = "the " + region[0] + " region"
            rows = database_helper.remove_dupes(context.message.author.id, rarity, region)
            await context.send(
                "You currently have {} pikapoints.\nReleasing {} {}⭐ Pokemon from {}...".format(str(balance), rows,
                                                                                                rarity, str_region))
            if rarity == '3':
                gain = 5
            elif rarity == '4':
                gain = 10
            database_helper.adjust_points(context.message.author.id, gain * rows)
            total_gain = gain * rows
            await context.send("You got {} pikapoints!\nYou now have {} pikapoints.".format(total_gain,
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
                await context.send("You do not have that Pokemon!")
        else:
            await context.send("Invalid Pokemon name!")

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
        # elif region == 'sinnoh':
        #     region = SINNOH
        # elif region == 'unova':
        #     region = UNOVA
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
                if not 4 < next_quiz.hour < 13:
                    await channel.send("{} is on a {}-streak! Next quiz will be at approximately {}:{:02}. Shut them down!".format(self.bot.get_user(high_streak[0]).name, high_streak[1], (next_quiz - datetime.timedelta(hours=5)).hour % 12, next_quiz.minute))
            await asyncio.sleep(t) # generate quizzes every 10 - 30 minutes
            if not 4 < datetime.datetime.now().hour < 13: # generate quizzes only from 8am - 12am
                r = random.randint(1, 251) # generate random pokemon
                pokemon = database_helper.get_pokemon_name(r)[0]
                str_id = "{:03}".format(r)
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
                quiz = discord.Embed(title="Who's That Pokémon?", color=0x00bfff)
                quiz.set_image(url=url)
                await channel.send(embed=quiz)

                def check(m):
                    return m.content == pokemon and m.channel == channel

                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)
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
