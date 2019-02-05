import discord
import random
from discord.ext import commands
import database_helper
import pokebase as pb
import asyncio
import datetime
from PIL import Image

SNOOPY_ID = 103634047929962496
KANTO = ('Kanto', 1, 151)
JOHTO = ('Johto', 152, 251)
HOENN = ('Hoenn', 252, 386)
SINNOH = ('Sinnoh', 387, 493)
UNOVA = ('Unova', 494, 649)
KALOS = ('Kalos', 650, 721)
ALOLA = ('Alola', 722, 809)
REGIONS = [KANTO, JOHTO]#, HOENN, SINNOH, UNOVA, KALOS, ALOLA]
QUIZ_CHANNEL_ID = 349942469804425216
class SenpaiGacha:
    def __init__(self, bot):
        self.bot = bot
    async def on_ready(self):
        database_helper.initialize(str(self.bot.guilds[0].id))
        self.bot.loop.create_task(self.background_quiz())        
    @commands.command(name="balance")
    async def balance(self, context):
        user_id = context.message.author.id
        balance = database_helper.get_pikapoints(user_id)
        if (balance is None):
            await context.send("You have no pikapoints! Join voice and start earning!")
        else:
            await context.send("You have " + str(balance) + " pikapoints")

    @commands.command(name="pity")
    async def pity(self, context):
        pity = database_helper.get_pity(context.message.author.id)
        title = "{}'s Pity Rates: \n".format(context.message.author.name)
        if pity is None:
            description = "3⭐: 54.0%\n4⭐: 42.0%\n5⭐: 1.0%\nFocus: 3.0%"
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
            # elif region == 'hoenn':
            #     region = HOENN
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
            for i in range(rolls):
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
                database_helper.adjust_points(context.message.author.id, -PRICE)
                database_helper.add_inventory(context.message.author.id, gacha[1])
                embed = discord.Embed(title=title, description=description, color=0x9370db)
                str_id = gacha[1]
                if gacha[1] < 10:
                    str_id = "00" + str(gacha[1])
                elif gacha[1] < 100:
                    str_id = "0" + str(gacha[1])
                url = "https://www.serebii.net/sunmoon/pokemon/{}.png".format(str_id)
                embed.set_thumbnail(url=url)
                await context.send(embed=embed)
            balance = database_helper.get_pikapoints(context.message.author.id)
            await context.send("You now have {} pikapoints.".format(str(balance)))
        else:
            await context.send("`You don't have enough pikapoints to summon!`")

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
            # elif region == 'hoenn':
            #     region = HOENN
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
            await context.send("`You don't have enough pikapoints to summon!`")

    @commands.command(name="box")
    async def box(self, context):
        await self.box_page(context, 1)
    async def box_page(self, context, page_num):
    #img = Image.open('images/crate.png', 'r')
        inventory = database_helper.get_inventory(context.message.author.id)
        if len(inventory) == 0:
            await context.send("You have no pokemon on page {}! Start rolling!".format(page_num))
        else:
            page_indices = {1:(0,0)}
            num_pokemon = 0
            for pokemon in inventory:
                num_pokemon += pokemon[4]
            (save_location, curr_index, remain_num) = self.draw_box(context, inventory, 0, 0)
            file = discord.File(save_location, filename='inventory.png')
            msg = await context.channel.send(context.message.author.name+"'s inventory (page " + str(page_num) +")", file=file)
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
                        msg = await context.channel.send(context.message.author.name+"'s inventory (page " + str(page_num) +")", file=file)
                        await msg.add_reaction("⬅")
                        await msg.add_reaction("➡")                        
    def draw_box(self, context, inventory, index, remain_num):
        #background = Image.new('RGBA', (850,450), (255, 255, 255))
        background = Image.open('images/inv_background.png', 'r')
        background = background.resize((850, 450))
        (x, y) = (0, 0)
        count = 0
        remain_overflow = 0
        init = True
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
    async def team(self, context):
        title = "{}'s Team: \n".format(context.message.author.name)
        description = ""
        for region in REGIONS:
            inventory = database_helper.get_inventory(context.message.author.id, region)
            description = description + "\n" + region[0]
            for poke in inventory:
                if poke[3] <= 5:
                    description = description + "\n    {} {} - {}⭐".format(poke[4], poke[2], poke[3])
                elif poke[3] == 6:
                    description = description + "\n    {} {} - Legendary".format(poke[4], poke[2])
                elif poke[3] == 7:
                    description = description + "\n    {} {} - Mythic".format(poke[4], poke[2])
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))

    @commands.command(name="fullrelease")
    async def fullrelease(self, context, rarity, region=None):
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        # elif region == 'hoenn':
        #     region = HOENN
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
    async def releasedupes(self, context, rarity, region=None):
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        # elif region == 'hoenn':
        #     region = HOENN
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
    async def release(self, context, name):
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
                description = description + "\n" + region[0]
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
    async def units(self, context, region):
        if region == 'kanto':
            region = KANTO
        elif region == 'johto':
            region = JOHTO
        # elif region == 'hoenn':
        #     region = HOENN
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
        five = []
        four = []
        three = []
        for unit in units:
            if unit[2] == 1:
                focus.append(unit[0])
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
            description = description + "\n" + region[0]
            for unit in focus:
                description = description + "\n    " + unit[0]
        await context.send(embed=discord.Embed(title=title, description=description, color=0x9370db))
        
    async def background_quiz(self):
        print("test")
        channel = self.bot.get_channel(QUIZ_CHANNEL_ID)
        if(channel is None):
            return
        while True:
            if not 5 < datetime.datetime.now().hour < 13: # generate quizzes only from 8am - 12am
                asyncio.sleep(300) # generate quizzes every 5 minutes
                if random.randint(0, 1) == 1: # 50% chance for quiz every 5 minutes
                    r = random.randint(1, 251) # generate random pokemon
                    pokemon = database_helper.get_pokemon_name(r)
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
                        await channel.send('Nobody guessed it in time...')
                    else:
                        await channel.send('Congratulations {.author}! You win 30 pikapoints!'.format(msg))    

def setup(bot):
    bot.add_cog(SenpaiGacha(bot))
