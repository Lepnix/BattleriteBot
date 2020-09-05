from discord.ext import commands
from discord import *
import discord
import random
import discord.member

DEFAULT_BEST_OF = 3

MAP_POOL_ONE = ["Blackstone Arena - Day", "Dragon Garden - Night", "Meriko Summit - Night", "Mount Araz - Night",
                "Orman Temple - Night"]
MAP_POOL_THREE = ["Blackstone Arena - Day", "Daharin Battlegrounds - Night", "Dragon Garden - Night",
                  "Great Market - Night", "Meriko Summit - Night", "Mount Araz - Night", "Orman Temple - Night"]

MAP_ALIASES = {"blackstone arena - day": "Blackstone Arena - Day",
               "blackstone arena day": "Blackstone Arena - Day",
               "blackstone arena": "Blackstone Arena - Day",
               "blackstone day": "Blackstone Arena - Day",
               "blackstone": "Blackstone Arena - Day",
               "black day": "Blackstone Arena - Day",
               "black": "Blackstone Arena - Day",

               "daharin battlegrounds - night": "Daharin Battlegrounds - Night",
               "daharin battlegrounds": "Daharin Battlegrounds - Night",
               "daharin night": "Daharin Battlegrounds - Night",
               "daharin": "Daharin Battlegrounds - Night",

               "dragon garden - night": "Dragon Garden - Night",
               "dragon garden night": "Dragon Garden - Night",
               "dragon garden": "Dragon Garden - Night",
               "dragon night": "Dragon Garden - Night",
               "dragon": "Dragon Garden - Night",

               "great market - night": "Great Market - Night",
               "great market": "Great Market - Night",
               "market night": "Great Market - Night",
               "market": "Great Market - Night",

               "meriko summit - night": "Meriko Summit - Night",
               "meriko summit": "Meriko Summit - Night",
               "meriko night": "Meriko Summit - Night",
               "meriko": "Meriko Summit - Night",

               "mount araz - night": "Mount Araz - Night",
               "araz night": "Mount Araz - Night",
               "mount araz": "Mount Araz - Night",
               "araz": "Mount Araz - Night",

               "orman temple - night": "Orman Temple - Night",
               "orman temple": "Orman Temple - Night",
               "orman night": "Orman Temple - Night",
               "orman": "Orman Temple - Night"}

CHAMP_ALIASES = {
    "alysia": "Alysia",
    "aly": "Alysia",
    "ashka": "Ashka",
    "ash": "Ashka",
    "bakko": "Bakko",
    "blossom": "Blossom",
    "bloss": "Blossom",
    "blos": "Blossom",
    "croak": "Croak",
    "destiny": "Destiny",
    "dest": "Destiny",
    "ezmo": "Ezmo",
    "freya": "Freya",
    "iva": "Iva",
    "jade": "Jade",
    "jamila": "Jamila",
    "jam": "Jamila",
    "jumong": "Jumong",
    "ju": "Jumong",
    "lucie": "Lucie",
    "luc": "Lucie",
    "oldur": "Oldur",
    "pearl": "Pearl",
    "pestilus": "Pestilus",
    "pest": "Pestilus",
    "poloma": "Poloma",
    "polo": "Poloma",
    "raigon": "Raigon",
    "rai": "Raigon",
    "rook": "Rook",
    "ruh kaan": "Ruh Kaan",
    "ruh": "Ruh Kaan",
    "ru": "Ruh Kaan",
    "rk": "Ruh Kaan",
    "shen rao": "Shen Rao",
    "shen": "Shen Rao",
    "shifu": "Shifu",
    "sirius": "Sirius",
    "taya": "Taya",
    "thorn": "Thorn",
    "ulric": "Ulric",
    "varesh": "Varesh",
    "var": "Varesh",
    "zander": "Zander",
    "zan": "Zander",
}

CHAMP_ROLES = {
    "Alysia": 'r',
    "Ashka": 'r',
    "Bakko": 'm',
    "Blossom": 's',
    "Croak": 'm',
    "Destiny": 'r',
    "Ezmo": 'r',
    "Freya": 'm',
    "Iva": 'r',
    "Jade": 'r',
    "Jamila": 'm',
    "Jumong": 'r',
    "Lucie": 's',
    "Oldur": 's',
    "Pearl": 's',
    "Pestilus": 's',
    "Poloma": 's',
    "Raigon": 'm',
    "Rook": 'm',
    "Ruh Kaan": 'm',
    "Shen Rao": 'r',
    "Shifu": 'm',
    "Sirius": 's',
    "Taya": 'r',
    "Thorn": 'm',
    "Ulric": 's',
    "Varesh": 'r',
    "Zander": 's',
}

BANNED_1v1 = [
    "Blossom",
    "Lucie",
    "Oldur",
    "Pearl",
    "Pestilus",
    "Poloma",
    "Shen Rao",
    "Sirius",
    "Ulric",
    "Zander"
]

SERVER_ID = 744406275864920085
DRAFT_CHANNEL_ID = 751593893824299049

active_captains = {}
match_dict = {}

client = commands.Bot(command_prefix='!')
client.remove_command('help')
TOKEN = open('token.secret', 'r').read()


class MatchState:
    def __init__(self, match_id, match_format, captain1, best_of, map_pool):
        self.match_id = match_id
        self.first_ban = random.randint(1, 2)
        self.current_game = 0
        self.champ_stage = 0
        self.match_format = match_format
        self.map_pool = map_pool
        self.best_of = best_of
        self.wins_needed = (best_of + 1) / 2
        self.captain1_wins = 0
        self.captain2_wins = 0
        self.captain1 = captain1
        self.captain2 = None
        self.active_captain = None
        self.inactive_captain = None
        self.map_embed = None
        self.cap1_champ_embed = None
        self.cap2_champ_embed = None
        self.channel_embed = None
        self.channel_embed_message = None
        self.cap1_1v1_embed = None
        self.cap2_1v1_embed = None
        self.cap1_1v1_champ = None
        self.cap2_1v1_champ = None
        self.active_map_message = None
        self.active_map_message_2 = None
        self.inactive_map_message = None
        self.inactive_map_message_2 = None
        self.cap1_champ_message = None
        self.cap1_champ_message_2 = None
        self.cap2_champ_message = None
        self.cap2_champ_message_2 = None
        # map_drafts format: [[[remaining_maps], [banned_maps]], [[remaining_maps], [banned_maps]]]
        self.map_drafts = []
        # champ_drafts format: [[[[cap1_reserve], [cap1_picks], [cap1_bans]],
        # [[cap2_reserve], [cap2_picks], [cap2_bans]]],...]
        self.champ_drafts = []
        self.current_draft = None
        self.map_drafts.append([map_pool, []])
        self.last_game_result = [9, 9]
        self.show_both_1v1 = False
        self.bans_1v1 = [None, None]

    def update_map_embed(self):
        self.map_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        map_pool_field = ''
        ban_field = ''

        for i in self.map_drafts[-1][0]:
            map_pool_field += f"{i}\n"
        map_pool_field.rstrip("\n")

        for i in self.map_drafts[-1][1]:
            ban_field += f"{i}\n"
        ban_field.rstrip("\n")

        if len(self.map_drafts[-1][1]) == 0:
            ban_field = '\u200b'

        self.map_embed.add_field(name='Map Pool', value=map_pool_field, inline=False)
        self.map_embed.add_field(name='Banned Maps', value=ban_field, inline=False)

    def update_champ_embed(self):
        self.cap1_champ_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        self.cap2_champ_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        self.channel_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        label_field = "Reserve\n\nPicks\n\n\n\nBans"

        cap1_field = f"{self.champ_drafts[-1][0][0][0]}\n\n"\
            f"{self.champ_drafts[-1][0][1][0]}\n{self.champ_drafts[-1][0][1][1]}\n{self.champ_drafts[-1][0][1][2]}\n\n"\
            f"{self.champ_drafts[-1][0][2][0]}\n{self.champ_drafts[-1][0][2][1]}\n{self.champ_drafts[-1][0][2][2]}"

        cap2_field = f"{self.champ_drafts[-1][1][0][0]}\n\n"\
            f"{self.champ_drafts[-1][1][1][0]}\n{self.champ_drafts[-1][1][1][1]}\n{self.champ_drafts[-1][1][1][2]}\n\n"\
            f"{self.champ_drafts[-1][1][2][0]}\n{self.champ_drafts[-1][1][2][1]}\n{self.champ_drafts[-1][1][2][2]}"

        self.cap1_champ_embed.add_field(name='Captains', value=label_field)
        self.cap1_champ_embed.add_field(name='You', value=cap1_field)
        self.cap1_champ_embed.add_field(name=f'{self.captain2.name}', value=cap2_field)

        self.cap2_champ_embed.add_field(name='Captains', value=label_field)
        self.cap2_champ_embed.add_field(name='You', value=cap2_field)
        self.cap2_champ_embed.add_field(name=f'{self.captain1.name}', value=cap1_field)

        self.channel_embed.add_field(name='Captains', value=label_field)
        self.channel_embed.add_field(name=f'{self.captain1.name}', value=cap1_field)
        self.channel_embed.add_field(name=f'{self.captain2.name}', value=cap2_field)

    def update_1v1_embed(self):
        self.cap1_1v1_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        self.cap2_1v1_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        cap1_field = '\u200b'
        for i in self.champ_drafts[-1][0]:
            if i != self.bans_1v1[1]:
                cap1_field += f"{i}\n"
        cap1_field.rstrip("\n")

        cap2_field = '\u200b'
        for i in self.champ_drafts[-1][1]:
            if i != self.bans_1v1[0]:
                cap2_field += f"{i}\n"
        cap2_field.rstrip("\n")

        self.cap1_1v1_embed.add_field(name="You", value=cap1_field)
        self.cap2_1v1_embed.add_field(name="You", value=cap2_field)

        '''
        if self.show_both_1v1:
            self.cap1_1v1_embed.add_field(name=self.captain2.name, value=cap2_field)
            self.cap2_1v1_embed.add_field(name=self.captain1.name, value=cap1_field)
        '''

        self.cap1_1v1_embed.add_field(name=self.captain2.name, value=cap2_field)
        self.cap2_1v1_embed.add_field(name=self.captain1.name, value=cap1_field)


@client.event
async def on_ready():
    print('TourneyChan is online.')


@client.event
async def on_message(ctx):
    if ctx.author == client.user:
        return

    await client.process_commands(ctx)


@client.command()
async def match(ctx, arg=None):
    if ctx.guild is not None:
        return

    if ctx.author in active_captains:
        channel = await ctx.author.create_dm()
        await channel.send("You are already in a match.")
        return

    if arg == '3' or arg == '3v3' or arg is None:
        match_format = '3v3'
    elif arg == '1' or arg == '1v1':
        match_format = '1v1'
    else:
        channel = await ctx.author.create_dm()
        await channel.send("You have entered an invalid match format. Use `!match 3` or `!match 1`")
        return

    message = f"You have created a {match_format} match."

    if match_format == '1v1':
        best_of = 9
        map_pool = ["Blackstone Arena - Day", "Dragon Garden - Night", "Meriko Summit - Night", "Mount Araz - Night",
                "Orman Temple - Night"]

    if match_format == '3v3':
        best_of = DEFAULT_BEST_OF
        map_pool = ["Blackstone Arena - Day", "Daharin Battlegrounds - Night", "Dragon Garden - Night",
                  "Great Market - Night", "Meriko Summit - Night", "Mount Araz - Night", "Orman Temple - Night"]

        message += f"\nThe current match length is best of {best_of}. You may use `!bo 1`, `!bo 3` or `!bo 5` to change it."

    match_id = 0
    while match_id == 0 or match_id in match_dict:
        match_id = random.randint(100, 999)

    match_dict[match_id] = MatchState(match_id, match_format, ctx.author, best_of, map_pool)

    active_captains[ctx.author] = match_id

    message += f"\nSend this code to the other captain:\n`!join {match_id}`"
    channel = await ctx.author.create_dm()
    await channel.send(message)


@client.command(aliases=["bo"])
async def bestof(ctx, arg=None):
    if ctx.guild is not None:
        return

    if ctx.author not in active_captains:
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently in a draft.")
        return

    match_id = active_captains[ctx.author]

    if match_dict[match_id].match_format != '3v3':
        channel = await ctx.author.create_dm()
        await channel.send("You can only change the match length for 3v3 matches.")
        return

    if match_dict[match_id].current_game == 0:
        if arg == '3':
            match_dict[match_id].best_of = 3
            channel = await ctx.author.create_dm()
            await channel.send("The match has been changed to a best of 3.")
        elif arg == '5':
            match_dict[match_id].best_of = 5
            channel = await ctx.author.create_dm()
            await channel.send("The match has been changed to a best of 5.")
        elif arg == '1':
            match_dict[match_id].best_of = 1
            channel = await ctx.author.create_dm()
            await channel.send("The match has been changed to a best of 1.")
        else:
            channel = await ctx.author.create_dm()
            await channel.send("You have not entered a valid match length.")

        match_dict[match_id].wins_needed = (match_dict[match_id].best_of + 1) / 2
    else:
        channel = await ctx.author.create_dm()
        await channel.send("The match has already begun. You will have to exit this match and create a new one to "
                           "change the match length.")


@client.command()
async def join(ctx, arg):
    if ctx.guild is not None:
        return

    if ctx.author in active_captains:
        channel = await ctx.author.create_dm()
        await channel.send("You are already in a match.")
        return

    match_id = int(arg)

    if match_id in match_dict:
        if match_dict[match_id].captain2 is None:
            match_dict[match_id].captain2 = ctx.author
            active_captains[ctx.author] = match_id

            # initiate draft here
            match_dict[match_id].current_game = 1

            if match_dict[match_id].first_ban == 1:
                match_dict[match_id].active_captain = match_dict[match_id].captain1
                match_dict[match_id].inactive_captain = match_dict[match_id].captain2

            elif match_dict[match_id].first_ban == 2:
                match_dict[match_id].active_captain = match_dict[match_id].captain2
                match_dict[match_id].inactive_captain = match_dict[match_id].captain1

            # 1v1 and 3v3 map draft initiation
            if match_dict[match_id].match_format == '3v3':
                match_dict[match_id].current_draft = 'map'

                channel = await match_dict[match_id].active_captain.create_dm()
                match_dict[match_id].update_map_embed()
                match_dict[match_id].active_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].active_map_message_2 = await channel.send(
                    "You will ban first. Ban with:\n`!ban name`")

                channel = await match_dict[match_id].inactive_captain.create_dm()
                match_dict[match_id].update_map_embed()
                match_dict[match_id].inactive_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].inactive_map_message_2 = await channel.send("Waiting for other captain to ban.")

            elif match_dict[match_id].match_format == '1v1':
                match_dict[match_id].current_draft = 'champ'
                match_dict[match_id].champ_drafts.append([[], []])

                channel = await match_dict[match_id].captain1.create_dm()
                match_dict[match_id].cap1_champ_message_2 = await channel.send(
                    "Pick 5 characters that you wish to play with: `!pick name`")

                channel = await match_dict[match_id].captain2.create_dm()
                match_dict[match_id].cap2_champ_message_2 = await channel.send(
                    "Pick 5 characters that you wish to play with: `!pick name`")

        else:
            channel = await ctx.author.create_dm()
            await channel.send("That match already has two captains.")
    else:
        channel = await ctx.author.create_dm()
        await channel.send("You have not entered a valid match code.")


@client.command()
async def exit(ctx):
    if ctx.guild is not None:
        return

    if ctx.author not in active_captains:
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently in a match.")
        return

    match_id = active_captains[ctx.author]

    captain1 = match_dict[match_id].captain1
    captain2 = match_dict[match_id].captain2

    if captain1 == ctx.author:
        channel = await captain1.create_dm()
        await channel.send("You have exited the match.")
        if captain2 is not None:
            channel = await captain2.create_dm()
            await channel.send("The other captain has exited the match.")

    if captain2 == ctx.author:
        channel = await captain2.create_dm()
        await channel.send("You have exited the match.")
        channel = await captain1.create_dm()
        await channel.send("The other captain has exited the match.")

    active_captains.pop(captain1, None)
    active_captains.pop(captain2, None)
    match_dict.pop(match_id)


@client.command()
async def ban(ctx, *, arg):
    if ctx.guild is not None:
        return

    if ctx.author not in active_captains:
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently in a match.")
        return

    match_id = active_captains[ctx.author]

    # handle all 3v3 scenarios here
    if match_dict[match_id].match_format == '3v3':
        # 3v3 map draft
        if match_dict[match_id].current_draft == 'map':
            # first game rules
            if ctx.author != match_dict[match_id].active_captain:
                channel = await ctx.author.create_dm()
                await channel.send("It is not currently your turn to ban.")
                return

            if match_dict[match_id].current_game == 1:
                banned_map = arg.lower()
                if banned_map not in MAP_ALIASES:
                    channel = await ctx.author.create_dm()
                    await channel.send(f"`{arg}` is not recognized as a valid map name.")
                    return

                banned_map = MAP_ALIASES[banned_map]

                if banned_map not in match_dict[match_id].map_drafts[-1][0]:
                    channel = await ctx.author.create_dm()
                    await channel.send("That map is not in the remaining pool.")
                    return

                # process map ban
                match_dict[match_id].map_drafts[-1][0].remove(banned_map)
                match_dict[match_id].map_drafts[-1][1].append(banned_map)

                if len(match_dict[match_id].map_drafts[-1][0]) == 1:
                    match_dict[match_id].current_draft = 'champ'
                    match_dict[match_id].champ_stage = 1

                    match_dict[match_id].champ_drafts.append([[['----'], ['----', '----', '----'], ['----', '----', '----']],
                                                              [['----'], ['----', '----', '----'], ['----', '----', '----']]])
                    match_dict[match_id].update_champ_embed()

                    channel = await match_dict[match_id].captain1.create_dm()
                    await channel.send(f"The chosen map is: `{match_dict[match_id].map_drafts[-1][0][0]}`")
                    match_dict[match_id].cap1_champ_message = await channel.send(embed=match_dict[match_id].cap1_champ_embed)
                    match_dict[match_id].cap1_champ_message_2 = await channel.send("The champion draft will now begin. "
                                                                                   "You will draft your characters in the following order: R > Bx > By > Pr > Pr > B > P. "
                                                                                   "Reserve a champion with: "
                                                                                   "`!res name`")

                    channel = await match_dict[match_id].captain2.create_dm()
                    await channel.send(f"The chosen map is: `{match_dict[match_id].map_drafts[-1][0][0]}`")
                    match_dict[match_id].cap2_champ_message = await channel.send(embed=match_dict[match_id].cap2_champ_embed)
                    match_dict[match_id].cap2_champ_message_2 = await channel.send("The champion draft will now begin. "
                                                                                   "You will draft your characters in the following order: R > Bx > By > Pr > Pr > B > P. "
                                                                                   "Reserve a champion with: "
                                                                                   "`!res name`")

                    channel = await client.get_guild(SERVER_ID).get_channel(DRAFT_CHANNEL_ID)
                    match_dict[match_id].channel_embed_message = await channel.send(embed=match_dict[match_id].channel_embed)

                    return

                if len(match_dict[match_id].map_drafts[-1][0]) in [2, 5]:
                    temp_cap = match_dict[match_id].inactive_captain
                    match_dict[match_id].inactive_captain = match_dict[match_id].active_captain
                    match_dict[match_id].active_captain = temp_cap

                channel = await match_dict[match_id].active_captain.create_dm()
                await match_dict[match_id].active_map_message_2.delete()
                match_dict[match_id].update_map_embed()
                await match_dict[match_id].active_map_message.delete()
                match_dict[match_id].active_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].active_map_message_2 = await channel.send("It is your turn to ban a map. Ban with:\n`!ban name`")

                channel = await match_dict[match_id].inactive_captain.create_dm()
                await match_dict[match_id].inactive_map_message.delete()
                await match_dict[match_id].inactive_map_message_2.delete()
                match_dict[match_id].update_map_embed()
                match_dict[match_id].inactive_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].inactive_map_message_2 = await channel.send("Waiting for other captain to ban.")

            elif match_dict[match_id].current_game > 1 and len(match_dict[match_id].map_drafts[-1][0]) > 5:
                banned_map = arg.lower()
                if banned_map not in MAP_ALIASES:
                    channel = await ctx.author.create_dm()
                    await channel.send(f"`{arg}` is not recognized as a valid map name.")
                    return

                banned_map = MAP_ALIASES[banned_map]

                if banned_map not in match_dict[match_id].map_drafts[-1][0]:
                    channel = await ctx.author.create_dm()
                    await channel.send("That map is not in the remaining pool.")
                    return

                # process map ban
                match_dict[match_id].map_drafts[-1][0].remove(banned_map)
                match_dict[match_id].map_drafts[-1][1].append(banned_map)

                if len(match_dict[match_id].map_drafts[-1][0]) == 6:

                    channel = await match_dict[match_id].active_captain.create_dm()
                    await match_dict[match_id].active_map_message_2.delete()
                    match_dict[match_id].update_map_embed()
                    await match_dict[match_id].active_map_message.delete()
                    match_dict[match_id].active_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                    match_dict[match_id].active_map_message_2 = await channel.send(
                        "It is your turn to ban a map. Ban with:\n`!ban name`")

                    channel = await match_dict[match_id].inactive_captain.create_dm()
                    await match_dict[match_id].inactive_map_message.delete()
                    await match_dict[match_id].inactive_map_message_2.delete()
                    match_dict[match_id].update_map_embed()
                    match_dict[match_id].inactive_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                    match_dict[match_id].inactive_map_message_2 = await channel.send(
                        "Waiting for other captain to ban.")

                elif len(match_dict[match_id].map_drafts[-1][0]) == 5:
                    temp_cap = match_dict[match_id].inactive_captain
                    match_dict[match_id].inactive_captain = match_dict[match_id].active_captain
                    match_dict[match_id].active_captain = temp_cap

                    channel = await match_dict[match_id].active_captain.create_dm()
                    await match_dict[match_id].active_map_message_2.delete()
                    match_dict[match_id].update_map_embed()
                    await match_dict[match_id].active_map_message.delete()
                    match_dict[match_id].active_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                    match_dict[match_id].active_map_message_2 = await channel.send("Pick a map with:\n`!pick name`")

                    channel = await match_dict[match_id].inactive_captain.create_dm()
                    await match_dict[match_id].inactive_map_message.delete()
                    await match_dict[match_id].inactive_map_message_2.delete()
                    match_dict[match_id].update_map_embed()
                    match_dict[match_id].inactive_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                    match_dict[match_id].inactive_map_message_2 = await channel.send("Waiting for other captain to pick.")

            elif match_dict[match_id].current_game > 1 and len(match_dict[match_id].map_drafts[-1][0]) < 5:
                channel = await ctx.author.create_dm()
                await channel.send("You are not currently banning a map.")
                return

        elif match_dict[match_id].current_draft == 'champ':

            ban_champ = arg.lower()

            if ban_champ not in CHAMP_ALIASES:
                channel = await ctx.author.create_dm()
                await channel.send(f"`{arg}` is not recognized as valid champion name.")
                return

            ban_champ = CHAMP_ALIASES[ban_champ]

            if match_dict[match_id].champ_stage == 2:
                if ctx.author == match_dict[match_id].captain1:

                    if ban_champ == match_dict[match_id].champ_drafts[-1][1][0][0]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot ban a champion that is reserved by the other team.")
                        return

                    match_dict[match_id].champ_drafts[-1][0][2][0] = ban_champ
                    match_dict[match_id].update_champ_embed()

                    if match_dict[match_id].champ_drafts[-1][1][2][0] == '----':
                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        channel = await ctx.author.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            f"Waiting for the other captain to ban.")

                    else:
                        match_dict[match_id].champ_stage = 3

                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()

                        channel = await match_dict[match_id].captain1.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            "Ban a champion with:\n`!ban name`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            "Ban a champion with:\n`!ban name`")

                        await match_dict[match_id].channel_embed_message.edit(embed=match_dict[match_id].channel_embed)

                elif ctx.author == match_dict[match_id].captain2:

                    if ban_champ == match_dict[match_id].champ_drafts[-1][0][0][0]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot ban a champion that is reserved by the other team.")
                        return

                    match_dict[match_id].champ_drafts[-1][1][2][0] = ban_champ
                    match_dict[match_id].update_champ_embed()

                    if match_dict[match_id].champ_drafts[-1][0][2][0] == '----':
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()
                        channel = await ctx.author.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            f"Waiting for the other captain to ban.")

                    else:
                        match_dict[match_id].champ_stage = 3

                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()

                        channel = await match_dict[match_id].captain1.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            "Ban a champion with:\n`!ban name`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            "Ban a champion with:\n`!ban name`")

                        await match_dict[match_id].channel_embed_message.edit(embed=match_dict[match_id].channel_embed)

            elif match_dict[match_id].champ_stage == 3:
                if ctx.author == match_dict[match_id].captain1:

                    if ban_champ == match_dict[match_id].champ_drafts[-1][1][0][0]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot ban a champion that is reserved by the other team.")
                        return

                    if ban_champ in [match_dict[match_id].champ_drafts[-1][0][2][0],
                                     match_dict[match_id].champ_drafts[-1][0][2][1],
                                     match_dict[match_id].champ_drafts[-1][0][2][2]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You have already banned that champion.")
                        return

                    if CHAMP_ROLES[ban_champ] == CHAMP_ROLES[match_dict[match_id].champ_drafts[-1][0][2][0]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"Your first two bans cannot be the same role.")
                        return

                    match_dict[match_id].champ_drafts[-1][0][2][1] = ban_champ
                    match_dict[match_id].update_champ_embed()

                    if match_dict[match_id].champ_drafts[-1][1][2][1] == '----':
                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        channel = await ctx.author.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            f"Waiting for the other captain to ban.")

                    else:
                        match_dict[match_id].champ_stage = 4

                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()

                        channel = await match_dict[match_id].captain1.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            "Pick a champion with:\n`!pick name`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            "Pick a champion with:\n`!pick name`")

                        await match_dict[match_id].channel_embed_message.edit(embed=match_dict[match_id].channel_embed)

                elif ctx.author == match_dict[match_id].captain2:

                    if ban_champ == match_dict[match_id].champ_drafts[-1][0][0][0]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot ban a champion that is reserved by the other team.")
                        return

                    if ban_champ in [match_dict[match_id].champ_drafts[-1][1][2][0],
                                     match_dict[match_id].champ_drafts[-1][1][2][1],
                                     match_dict[match_id].champ_drafts[-1][1][2][2]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You have already banned that champion.")
                        return

                    if CHAMP_ROLES[ban_champ] == CHAMP_ROLES[match_dict[match_id].champ_drafts[-1][1][2][0]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"Your first two bans cannot be the same role.")
                        return

                    match_dict[match_id].champ_drafts[-1][1][2][1] = ban_champ
                    match_dict[match_id].update_champ_embed()

                    if match_dict[match_id].champ_drafts[-1][0][2][1] == '----':
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()
                        channel = await ctx.author.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            f"Waiting for the other captain to ban.")

                    else:
                        match_dict[match_id].champ_stage = 4

                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()

                        channel = await match_dict[match_id].captain1.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            "Pick a champion with:\n`!pick name`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            "Pick a champion with:\n`!pick name`")

                        await match_dict[match_id].channel_embed_message.edit(embed=match_dict[match_id].channel_embed)

            elif match_dict[match_id].champ_stage == 6:
                if ctx.author == match_dict[match_id].captain1:

                    if ban_champ in [match_dict[match_id].champ_drafts[-1][0][2][0],
                                     match_dict[match_id].champ_drafts[-1][0][2][1],
                                     match_dict[match_id].champ_drafts[-1][0][2][2]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You have already banned that champion.")
                        return

                    if ban_champ in [match_dict[match_id].champ_drafts[-1][1][1][0],
                                     match_dict[match_id].champ_drafts[-1][1][1][1]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot ban a champion that has been picked by the other team.")
                        return

                    match_dict[match_id].champ_drafts[-1][0][2][2] = ban_champ
                    match_dict[match_id].update_champ_embed()

                    if match_dict[match_id].champ_drafts[-1][1][2][2] == '----':
                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        channel = await ctx.author.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            f"Waiting for the other captain to ban.")

                    else:
                        match_dict[match_id].champ_stage = 7

                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()

                        channel = await match_dict[match_id].captain1.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            "Pick a champion with:\n`!pick name`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            "Pick a champion with:\n`!pick name`")

                        await match_dict[match_id].channel_embed_message.edit(embed=match_dict[match_id].channel_embed)

                if ctx.author == match_dict[match_id].captain2:

                    if ban_champ in [match_dict[match_id].champ_drafts[-1][1][2][0],
                                     match_dict[match_id].champ_drafts[-1][1][2][1],
                                     match_dict[match_id].champ_drafts[-1][1][2][2]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You have already banned that champion.")
                        return

                    if ban_champ in [match_dict[match_id].champ_drafts[-1][0][1][0],
                                     match_dict[match_id].champ_drafts[-1][0][1][1]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot ban a champion that has been picked by the other team.")
                        return

                    match_dict[match_id].champ_drafts[-1][1][2][2] = ban_champ
                    match_dict[match_id].update_champ_embed()

                    if match_dict[match_id].champ_drafts[-1][0][2][2] == '----':
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()
                        channel = await ctx.author.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            f"Waiting for the other captain to ban.")

                    else:
                        match_dict[match_id].champ_stage = 7

                        await match_dict[match_id].cap1_champ_message.delete()
                        await match_dict[match_id].cap1_champ_message_2.delete()
                        await match_dict[match_id].cap2_champ_message.delete()
                        await match_dict[match_id].cap2_champ_message_2.delete()

                        channel = await match_dict[match_id].captain1.create_dm()
                        match_dict[match_id].cap1_champ_message = await channel.send(
                            embed=match_dict[match_id].cap1_champ_embed)
                        match_dict[match_id].cap1_champ_message_2 = await channel.send(
                            "Pick a champion with:\n`!pick name`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        match_dict[match_id].cap2_champ_message = await channel.send(
                            embed=match_dict[match_id].cap2_champ_embed)
                        match_dict[match_id].cap2_champ_message_2 = await channel.send(
                            "Pick a champion with:\n`!pick name`")

                        await match_dict[match_id].channel_embed_message.edit(embed=match_dict[match_id].channel_embed)

    # 1v1 scenarios
    if match_dict[match_id].match_format == '1v1':
        # 1v1 map draft
        if match_dict[match_id].current_draft == 'map':
            # first game rules
            if ctx.author != match_dict[match_id].active_captain:
                return

            if match_dict[match_id].current_game == 1:
                banned_map = arg.lower()
                if banned_map not in MAP_ALIASES:
                    channel = await ctx.author.create_dm()
                    await channel.send("You have entered an invalid map name.")
                    return

                banned_map = MAP_ALIASES[banned_map]

                if banned_map not in match_dict[match_id].map_drafts[-1][0]:
                    channel = await ctx.author.create_dm()
                    await channel.send("That map is not in the remaining pool.")
                    return

                # process map ban
                match_dict[match_id].map_drafts[-1][0].remove(banned_map)
                match_dict[match_id].map_drafts[-1][1].append(banned_map)

                if len(match_dict[match_id].map_drafts[-1][0]) == 1:
                    match_dict[match_id].current_draft = 'champ'
                    match_dict[match_id].champ_stage = 1

                    match_dict[match_id].update_1v1_embed()

                    channel = await match_dict[match_id].captain1.create_dm()
                    await channel.send(embed=match_dict[match_id].cap1_1v1_embed)
                    await channel.send(f"The chosen map is: `{match_dict[match_id].map_drafts[-1][0][0]}`")
                    await channel.send(f"Choose your champion for the first game with: `!pick name`")

                    channel = await match_dict[match_id].captain2.create_dm()
                    await channel.send(embed=match_dict[match_id].cap2_1v1_embed)
                    await channel.send(f"The chosen map is: `{match_dict[match_id].map_drafts[-1][0][0]}`")
                    await channel.send(f"Choose your champion for the first game with: `!pick name`")

                    return

                if len(match_dict[match_id].map_drafts[-1][0]) in [2, 4]:
                    temp_cap = match_dict[match_id].inactive_captain
                    match_dict[match_id].inactive_captain = match_dict[match_id].active_captain
                    match_dict[match_id].active_captain = temp_cap

                channel = await match_dict[match_id].active_captain.create_dm()
                await match_dict[match_id].active_map_message_2.delete()
                match_dict[match_id].update_map_embed()
                await match_dict[match_id].active_map_message.delete()
                match_dict[match_id].active_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].active_map_message_2 = await channel.send(
                    "It is your turn to ban a map. Ban with:\n`!ban name`")

                channel = await match_dict[match_id].inactive_captain.create_dm()
                await match_dict[match_id].inactive_map_message.delete()
                await match_dict[match_id].inactive_map_message_2.delete()
                match_dict[match_id].update_map_embed()
                match_dict[match_id].inactive_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].inactive_map_message_2 = await channel.send(
                    "Waiting for other captain to ban.")

        elif match_dict[match_id].current_draft == 'champ':
            if len(match_dict[match_id].champ_drafts[-1][0]) + len(match_dict[match_id].champ_drafts[-1][1]) == 10:

                ban_champ = arg.lower()

                if ban_champ not in CHAMP_ALIASES:
                    channel = await ctx.author.create_dm()
                    await channel.send(f"`{arg}` is not recognized as valid champion name.")
                    return

                ban_champ = CHAMP_ALIASES[ban_champ]

                if ctx.author == match_dict[match_id].captain1:

                    if ban_champ not in match_dict[match_id].champ_drafts[-1][1]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot ban a champion that the other player did not choose.")
                        return

                    match_dict[match_id].bans_1v1[0] = ban_champ

                    if match_dict[match_id].bans_1v1[1] is None:
                        try:
                            await match_dict[match_id].cap1_champ_message_2.delete()
                        except:
                            pass
                        channel = await ctx.author.create_dm()
                        await channel.send(f"Waiting for other player to ban.")
                        return

                    else:
                        try:
                            await match_dict[match_id].cap1_champ_message.delete()
                        except:
                            pass

                        try:
                            await match_dict[match_id].cap1_champ_message_2.delete()
                        except:
                            pass

                        try:
                            await match_dict[match_id].cap2_champ_message.delete()
                        except:
                            pass

                        try:
                            await match_dict[match_id].cap2_champ_message_2.delete()
                        except:
                            pass

                        match_dict[match_id].update_1v1_embed()

                        channel = await match_dict[match_id].captain1.create_dm()
                        match_dict[match_id].cap1_champ_message = channel.send(
                            embed=match_dict[match_id].cap1_1v1_embed)
                        await channel.send(f"Your opponent has banned: `{match_dict[match_id].bans_1v1[1]}`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        match_dict[match_id].cap2_champ_message = channel.send(
                            embed=match_dict[match_id].cap2_1v1_embed)
                        await channel.send(f"Your opponent has banned: `{match_dict[match_id].bans_1v1[0]}`")

                        match_dict[match_id].current_draft = 'map'

                        channel = await match_dict[match_id].active_captain.create_dm()
                        match_dict[match_id].update_map_embed()
                        match_dict[match_id].active_map_message = await channel.send(
                            embed=match_dict[match_id].map_embed)
                        match_dict[match_id].active_map_message_2 = await channel.send(
                            "You will ban a map first. Ban with:\n`!ban name`")

                        channel = await match_dict[match_id].inactive_captain.create_dm()
                        match_dict[match_id].update_map_embed()
                        match_dict[match_id].inactive_map_message = await channel.send(
                            embed=match_dict[match_id].map_embed)
                        match_dict[match_id].inactive_map_message_2 = await channel.send(
                            "Waiting for other captain to ban map.")

                elif ctx.author == match_dict[match_id].captain2:

                    if ban_champ not in match_dict[match_id].champ_drafts[-1][0]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot ban a champion that the other player did not choose.")
                        return

                    match_dict[match_id].bans_1v1[1] = ban_champ

                    if match_dict[match_id].bans_1v1[0] is None:
                        try:
                            await match_dict[match_id].cap2_champ_message_2.delete()
                        except:
                            pass
                        channel = await ctx.author.create_dm()
                        await channel.send(f"Waiting for other player to ban.")
                        return

                    else:
                        try:
                            await match_dict[match_id].cap1_champ_message.delete()
                        except:
                            pass

                        try:
                            await match_dict[match_id].cap1_champ_message_2.delete()
                        except:
                            pass

                        try:
                            await match_dict[match_id].cap2_champ_message.delete()
                        except:
                            pass

                        try:
                            await match_dict[match_id].cap2_champ_message_2.delete()
                        except:
                            pass

                        match_dict[match_id].update_1v1_embed()

                        channel = await match_dict[match_id].captain1.create_dm()
                        match_dict[match_id].cap1_champ_message = channel.send(
                            embed=match_dict[match_id].cap1_1v1_embed)
                        await channel.send(f"Your opponent has banned: `{match_dict[match_id].bans_1v1[1]}`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        match_dict[match_id].cap2_champ_message = channel.send(
                            embed=match_dict[match_id].cap2_1v1_embed)
                        await channel.send(f"Your opponent has banned: `{match_dict[match_id].bans_1v1[0]}`")

                        match_dict[match_id].current_draft = 'map'

                        channel = await match_dict[match_id].active_captain.create_dm()
                        match_dict[match_id].update_map_embed()
                        match_dict[match_id].active_map_message = await channel.send(
                            embed=match_dict[match_id].map_embed)
                        match_dict[match_id].active_map_message_2 = await channel.send(
                            "You will ban a map first. Ban with:\n`!ban name`")

                        channel = await match_dict[match_id].inactive_captain.create_dm()
                        match_dict[match_id].update_map_embed()
                        match_dict[match_id].inactive_map_message = await channel.send(
                            embed=match_dict[match_id].map_embed)
                        match_dict[match_id].inactive_map_message_2 = await channel.send(
                            "Waiting for other captain to ban map.")



@client.command(aliases=['res'])
async def reserve(ctx, *, arg):
    if ctx.guild is not None:
        return

    if ctx.author not in active_captains:
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently in a match.")
        return

    match_id = active_captains[ctx.author]

    if match_dict[match_id].current_draft != "champ":
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently in a champion draft.")
        return

    if match_dict[match_id].champ_stage != 1:
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently reserving a champion.")
        return

    reserve_champ = arg.lower()

    if reserve_champ not in CHAMP_ALIASES:
        channel = await ctx.author.create_dm()
        await channel.send(f"`{arg}` is not recognized as valid champion name.")
        return

    reserve_champ = CHAMP_ALIASES[reserve_champ]

    if ctx.author == match_dict[match_id].captain1:
        match_dict[match_id].champ_drafts[-1][0][0][0] = reserve_champ
        match_dict[match_id].update_champ_embed()

        if match_dict[match_id].champ_drafts[-1][1][0][0] == '----':
            try:
                await match_dict[match_id].cap1_champ_message.delete()
            except:
                pass
            try:
                await match_dict[match_id].cap1_champ_message_2.delete()
            except:
                pass

            channel = await ctx.author.create_dm()
            match_dict[match_id].cap1_champ_message = await channel.send(embed=match_dict[match_id].cap1_champ_embed)
            match_dict[match_id].cap1_champ_message_2 = await channel.send(f"Waiting for the other captain to reserve.")

        else:
            match_dict[match_id].champ_stage = 2

            try:
                await match_dict[match_id].cap1_champ_message.delete()
            except:
                pass
            try:
                await match_dict[match_id].cap1_champ_message_2.delete()
            except:
                pass
            try:
                await match_dict[match_id].cap2_champ_message.delete()
            except:
                pass
            try:
                await match_dict[match_id].cap2_champ_message_2.delete()
            except:
                pass

            channel = await match_dict[match_id].captain1.create_dm()
            match_dict[match_id].cap1_champ_message = await channel.send(embed=match_dict[match_id].cap1_champ_embed)
            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                "Ban a champion with:\n`!ban name`")

            channel = await match_dict[match_id].captain2.create_dm()
            match_dict[match_id].cap2_champ_message = await channel.send(embed=match_dict[match_id].cap2_champ_embed)
            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                "Ban a champion with:\n`!ban name`")

            await match_dict[match_id].channel_embed_message.edit(embed=match_dict[match_id].channel_embed)

    elif ctx.author == match_dict[match_id].captain2:
        match_dict[match_id].champ_drafts[-1][1][0][0] = reserve_champ
        match_dict[match_id].update_champ_embed()

        if match_dict[match_id].champ_drafts[-1][0][0][0] == '----':
            await match_dict[match_id].cap2_champ_message.delete()
            await match_dict[match_id].cap2_champ_message_2.delete()
            channel = await ctx.author.create_dm()
            match_dict[match_id].cap2_champ_message = await channel.send(embed=match_dict[match_id].cap2_champ_embed)
            match_dict[match_id].cap2_champ_message_2 = await channel.send(f"Waiting for the other captain to reserve.")

        else:
            match_dict[match_id].champ_stage = 2

            await match_dict[match_id].cap1_champ_message.delete()
            await match_dict[match_id].cap1_champ_message_2.delete()
            await match_dict[match_id].cap2_champ_message.delete()
            await match_dict[match_id].cap2_champ_message_2.delete()

            channel = await match_dict[match_id].captain1.create_dm()
            match_dict[match_id].cap1_champ_message = await channel.send(embed=match_dict[match_id].cap1_champ_embed)
            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                "Ban a champion with:\n`!ban name`")

            channel = await match_dict[match_id].captain2.create_dm()
            match_dict[match_id].cap2_champ_message = await channel.send(embed=match_dict[match_id].cap2_champ_embed)
            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                "Ban a champion with:\n`!ban name`")

            await match_dict[match_id].channel_embed_message.edit(embed=match_dict[match_id].channel_embed)


@client.command()
async def pick(ctx, *, arg):
    if ctx.guild is not None:
        return

    if ctx.author not in active_captains:
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently in a match.")
        return

    match_id = active_captains[ctx.author]

    if match_dict[match_id].match_format == '3v3':
        if match_dict[match_id].current_draft == 'map':
            if len(match_dict[match_id].map_drafts[-1][0]) == 5:

                pick_map = arg.lower()
                if pick_map not in MAP_ALIASES:
                    channel = await ctx.author.create_dm()
                    await channel.send("You have entered an invalid map name.")
                    return

                pick_map = MAP_ALIASES[pick_map]

                if pick_map not in match_dict[match_id].map_drafts[-1][0]:
                    channel = await ctx.author.create_dm()
                    await channel.send("That map is not in the remaining pool.")
                    return

                # process map ban
                match_dict[match_id].current_draft = 'champ'
                match_dict[match_id].champ_stage = 1

                match_dict[match_id].champ_drafts.append(
                    [[['----'], ['----', '----', '----'], ['----', '----', '----']],
                     [['----'], ['----', '----', '----'], ['----', '----', '----']]])
                match_dict[match_id].update_champ_embed()

                channel = await match_dict[match_id].captain1.create_dm()
                await channel.send(f"The chosen map is: `{pick_map}`")
                match_dict[match_id].map_drafts[-1][0][0] = pick_map
                match_dict[match_id].cap1_champ_message = await channel.send(
                    embed=match_dict[match_id].cap1_champ_embed)
                match_dict[match_id].cap1_champ_message_2 = await channel.send("The champion draft will now begin. "
                                                                               "Reserve a champion with:\n"
                                                                               "`!res name`")

                channel = await match_dict[match_id].captain2.create_dm()
                await channel.send(f"The chosen map is: `{pick_map}`")
                match_dict[match_id].map_drafts[-1][0][0] = pick_map
                match_dict[match_id].cap2_champ_message = await channel.send(
                    embed=match_dict[match_id].cap2_champ_embed)
                match_dict[match_id].cap2_champ_message_2 = await channel.send("The champion draft will now begin. "
                                                                               "Reserve a champion with:\n"
                                                                               "`!res name`")

        elif match_dict[match_id].current_draft == 'champ':
            pick_champ = arg.lower()

            if pick_champ not in CHAMP_ALIASES:
                channel = await ctx.author.create_dm()
                await channel.send(f"`{arg}` is not recognized as valid champion name.")
                return

            pick_champ = CHAMP_ALIASES[pick_champ]

            if match_dict[match_id].champ_stage not in [4, 5, 7]:
                channel = await ctx.author.create_dm()
                await channel.send(f"It is not currently time to pick a champion.")
                return

            if match_dict[match_id].champ_stage in [4, 5, 7]:
                if ctx.author == match_dict[match_id].captain1:

                    if pick_champ in [match_dict[match_id].champ_drafts[-1][1][2][0],
                                      match_dict[match_id].champ_drafts[-1][1][2][1],
                                      match_dict[match_id].champ_drafts[-1][1][2][2]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot pick a champion that is banned by the other team.")
                        return

                    if pick_champ in [match_dict[match_id].champ_drafts[-1][0][1][0],
                                      match_dict[match_id].champ_drafts[-1][0][1][1],
                                      match_dict[match_id].champ_drafts[-1][0][1][2]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot pick a champion that you have already picked.")
                        return

                    if match_dict[match_id].champ_stage == 4:
                        match_dict[match_id].champ_drafts[-1][0][1][0] = pick_champ
                        match_dict[match_id].update_champ_embed()

                        if match_dict[match_id].champ_drafts[-1][1][1][0] == '----':
                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            channel = await ctx.author.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                f"Waiting for the other captain to pick.")

                        else:
                            match_dict[match_id].champ_stage = 5

                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()

                            channel = await match_dict[match_id].captain1.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                "Pick a champion with:\n`!pick name`")

                            channel = await match_dict[match_id].captain2.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                "Pick a champion with:\n`!pick name`")

                            await match_dict[match_id].channel_embed_message.edit(
                                embed=match_dict[match_id].channel_embed)

                    elif match_dict[match_id].champ_stage == 5:
                        match_dict[match_id].champ_drafts[-1][0][1][1] = pick_champ
                        match_dict[match_id].update_champ_embed()

                        if match_dict[match_id].champ_drafts[-1][1][1][1] == '----':
                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            channel = await ctx.author.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                f"Waiting for the other captain to pick.")

                        else:
                            match_dict[match_id].champ_stage = 6

                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()

                            channel = await match_dict[match_id].captain1.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                "Ban a champion with:\n`!ban name`")

                            channel = await match_dict[match_id].captain2.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                "Ban a champion with:\n`!ban name`")

                            await match_dict[match_id].channel_embed_message.edit(
                                embed=match_dict[match_id].channel_embed)

                    elif match_dict[match_id].champ_stage == 7:
                        match_dict[match_id].champ_drafts[-1][0][1][2] = pick_champ
                        match_dict[match_id].update_champ_embed()

                        if match_dict[match_id].champ_drafts[-1][1][1][2] == '----':
                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            channel = await ctx.author.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                f"Waiting for the other captain to pick.")

                        else:
                            match_dict[match_id].champ_stage = 0
                            match_dict[match_id].current_draft = 'report'

                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()

                            channel = await match_dict[match_id].captain1.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                f"The champion draft has completed. You are playing on: `{match_dict[match_id].map_drafts[-1][0][0]}`\n"
                                f"Report whether you win or lose with: `!r w/l`")

                            channel = await match_dict[match_id].captain2.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                f"The champion draft has completed. You are playing on: `{match_dict[match_id].map_drafts[-1][0][0]}`\n"
                                f"Report whether you win or lose with: `!r w/l`")

                            await match_dict[match_id].channel_embed_message.edit(
                                embed=match_dict[match_id].channel_embed)

                if ctx.author == match_dict[match_id].captain2:

                    if pick_champ in [match_dict[match_id].champ_drafts[-1][0][2][0],
                                      match_dict[match_id].champ_drafts[-1][0][2][1],
                                      match_dict[match_id].champ_drafts[-1][0][2][2]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot pick a champion that is banned by the other team.")
                        return

                    if pick_champ in [match_dict[match_id].champ_drafts[-1][1][1][0],
                                      match_dict[match_id].champ_drafts[-1][1][1][1],
                                      match_dict[match_id].champ_drafts[-1][1][1][2]]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot pick a champion that you have already picked.")
                        return

                    if match_dict[match_id].champ_stage == 4:
                        match_dict[match_id].champ_drafts[-1][1][1][0] = pick_champ
                        match_dict[match_id].update_champ_embed()

                        if match_dict[match_id].champ_drafts[-1][0][1][0] == '----':
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()
                            channel = await ctx.author.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                f"Waiting for the other captain to pick.")

                        else:
                            match_dict[match_id].champ_stage = 5

                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()

                            channel = await match_dict[match_id].captain1.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                "Pick a champion with:\n`!pick name`")

                            channel = await match_dict[match_id].captain2.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                "Pick a champion with:\n`!pick name`")

                    elif match_dict[match_id].champ_stage == 5:
                        match_dict[match_id].champ_drafts[-1][1][1][1] = pick_champ
                        match_dict[match_id].update_champ_embed()

                        if match_dict[match_id].champ_drafts[-1][0][1][1] == '----':
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()
                            channel = await ctx.author.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                f"Waiting for the other captain to pick.")

                        else:
                            match_dict[match_id].champ_stage = 6

                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()

                            channel = await match_dict[match_id].captain1.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                "Ban a champion with:\n`!ban name`")

                            channel = await match_dict[match_id].captain2.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                "Ban a champion with:\n`!ban name`")

                    elif match_dict[match_id].champ_stage == 7:
                        match_dict[match_id].champ_drafts[-1][1][1][2] = pick_champ
                        match_dict[match_id].update_champ_embed()

                        if match_dict[match_id].champ_drafts[-1][0][1][2] == '----':
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()
                            channel = await ctx.author.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                f"Waiting for the other captain to pick.")

                        else:
                            match_dict[match_id].champ_stage = 0
                            match_dict[match_id].current_draft = 'report'

                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()
                            await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()

                            channel = await match_dict[match_id].captain1.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_champ_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                f"The champion draft has completed. You are playing on: `{match_dict[match_id].map_drafts[-1][0][0]}`\n"
                                f"Report whether you win or lose with: `!r w/l`")

                            channel = await match_dict[match_id].captain2.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_champ_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                f"The champion draft has completed. You are playing on: `{match_dict[match_id].map_drafts[-1][0][0]}`\n"
                                f"Report whether you win or lose with: `!r w/l`")

    if match_dict[match_id].match_format == '1v1':
        # 1v1 champ draft
        if match_dict[match_id].current_draft == 'champ' and match_dict[match_id].current_game == 1:

            pick_champ = arg.lower()

            if pick_champ not in CHAMP_ALIASES:
                channel = await ctx.author.create_dm()
                await channel.send(f"`{arg}` is not recognized as valid champion name.")
                return

            pick_champ = CHAMP_ALIASES[pick_champ]

            if match_dict[match_id].champ_stage == 0:

                if pick_champ in BANNED_1v1:
                    channel = await ctx.author.create_dm()
                    await channel.send(f"That character is banned in 1v1 matches.")
                    return

                if ctx.author == match_dict[match_id].captain1:

                    if pick_champ in match_dict[match_id].champ_drafts[-1][0]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot pick a champion that you have already chosen.")
                        return

                    if len(match_dict[match_id].champ_drafts[-1][0]) < 5:

                        match_dict[match_id].champ_drafts[-1][0].append(pick_champ)

                        if len(match_dict[match_id].champ_drafts[-1][0]) < 5:
                            if match_dict[match_id].cap1_champ_message is not None:
                                await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()

                            match_dict[match_id].update_1v1_embed()

                            channel = await ctx.author.create_dm()
                            match_dict[match_id].cap1_champ_message = await channel.send(
                                embed=match_dict[match_id].cap1_1v1_embed)
                            match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                f"Pick {5 - len(match_dict[match_id].champ_drafts[-1][0])} more champions with: `!pick name`")

                        elif len(match_dict[match_id].champ_drafts[-1][0]) == 5:

                            await match_dict[match_id].cap1_champ_message.delete()
                            await match_dict[match_id].cap1_champ_message_2.delete()

                            channel = await ctx.author.create_dm()

                            if len(match_dict[match_id].champ_drafts[-1][1]) < 5:

                                match_dict[match_id].update_1v1_embed()

                                match_dict[match_id].cap1_champ_message = await channel.send(
                                    embed=match_dict[match_id].cap1_1v1_embed)
                                match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                    "Waiting for other player to finish picking.")

                            elif len(match_dict[match_id].champ_drafts[-1][1]) == 5:
                                match_dict[match_id].show_both_1v1 = True
                                match_dict[match_id].update_1v1_embed()

                                channel = await match_dict[match_id].captain1.create_dm()
                                match_dict[match_id].cap1_champ_message = await channel.send(
                                    embed=match_dict[match_id].cap1_1v1_embed)
                                match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                    "Champion selection has finished. Ban one of your opponent's champions for game 1 with: `!ban name`")

                                await match_dict[match_id].cap2_champ_message.delete()
                                await match_dict[match_id].cap2_champ_message_2.delete()

                                channel = await match_dict[match_id].captain2.create_dm()
                                match_dict[match_id].cap2_champ_message = await channel.send(
                                    embed=match_dict[match_id].cap2_1v1_embed)
                                match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                    "Champion selection has finished. Ban one of your opponent's champions for game 1 with: `!ban name`")

                if ctx.author == match_dict[match_id].captain2:

                    if pick_champ in match_dict[match_id].champ_drafts[-1][1]:
                        channel = await ctx.author.create_dm()
                        await channel.send(f"You cannot pick a champion that you have already chosen.")
                        return

                    if len(match_dict[match_id].champ_drafts[-1][1]) < 5:

                        match_dict[match_id].champ_drafts[-1][1].append(pick_champ)

                        if len(match_dict[match_id].champ_drafts[-1][1]) < 5:
                            if match_dict[match_id].cap2_champ_message is not None:
                                await match_dict[match_id].cap2_champ_message.delete()
                            await match_dict[match_id].cap2_champ_message_2.delete()

                            match_dict[match_id].update_1v1_embed()

                            channel = await ctx.author.create_dm()
                            match_dict[match_id].cap2_champ_message = await channel.send(
                                embed=match_dict[match_id].cap2_1v1_embed)
                            match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                f"Pick {5 - len(match_dict[match_id].champ_drafts[-1][1])} more champions with: `!pick name`")

                        elif len(match_dict[match_id].champ_drafts[-1][1]) == 5:

                            try:
                                await match_dict[match_id].cap2_champ_message.delete()
                            except:
                                pass
                            try:
                                await match_dict[match_id].cap2_champ_message_2.delete()
                            except:
                                pass

                            channel = await ctx.author.create_dm()

                            if len(match_dict[match_id].champ_drafts[-1][0]) < 5:

                                match_dict[match_id].update_1v1_embed()

                                match_dict[match_id].cap2_champ_message = await channel.send(
                                    embed=match_dict[match_id].cap2_1v1_embed)
                                match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                    "Waiting for other player to finish picking.")

                            elif len(match_dict[match_id].champ_drafts[-1][0]) == 5:
                                match_dict[match_id].show_both_1v1 = True
                                match_dict[match_id].update_1v1_embed()

                                await match_dict[match_id].cap1_champ_message.delete()
                                await match_dict[match_id].cap1_champ_message_2.delete()

                                channel = await match_dict[match_id].captain1.create_dm()
                                match_dict[match_id].cap1_champ_message = await channel.send(
                                    embed=match_dict[match_id].cap1_1v1_embed)
                                match_dict[match_id].cap1_champ_message_2 = await channel.send(
                                    "Champion selection has finished. Ban one of your opponent's champions for game 1 with: `!ban name`")

                                channel = await match_dict[match_id].captain2.create_dm()
                                match_dict[match_id].cap2_champ_message = await channel.send(
                                    embed=match_dict[match_id].cap2_1v1_embed)
                                match_dict[match_id].cap2_champ_message_2 = await channel.send(
                                    "Champion selection has finished. Ban one of your opponent's champions for game 1 with: `!ban name`")

            elif match_dict[match_id].champ_stage == 1:
                if ctx.author == match_dict[match_id].captain1:

                    if pick_champ not in match_dict[match_id].champ_drafts[-1][0]:
                        channel = await ctx.author.create_dm()
                        await channel.send("You cannot pick a champion that is not in your remaining pool.")
                        return

                    if pick_champ == match_dict[match_id].bans_1v1[1]:
                        channel = await ctx.author.create_dm()
                        await channel.send("You cannot pick a champion that is banned by the other player.")
                        return

                    match_dict[match_id].cap1_1v1_champ = pick_champ

                    if match_dict[match_id].cap2_1v1_champ is None:
                        channel = await ctx.author.create_dm()
                        await channel.send("Waiting for the other player to pick a champion.")
                    else:
                        match_dict[match_id].current_draft = 'report'

                        channel = await match_dict[match_id].captain1.create_dm()
                        await channel.send(f"You are playing: `{match_dict[match_id].cap1_1v1_champ}`\n"
                                           f"`{match_dict[match_id].captain2.name}` is playing: `{match_dict[match_id].cap2_1v1_champ}`\n"
                                           f"The map is: `{match_dict[match_id].map_drafts[-1][0][0]}`\n"
                                           f"Report the result of your game with: `!report w/l`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        await channel.send(f"You are playing: `{match_dict[match_id].cap2_1v1_champ}`\n"
                                           f"`{match_dict[match_id].captain1.name}` is playing: `{match_dict[match_id].cap1_1v1_champ}`\n"
                                           f"The map is: `{match_dict[match_id].map_drafts[-1][0][0]}`\n"
                                           f"Report the result of your game with: `!report w/l`")

                elif ctx.author == match_dict[match_id].captain2:

                    if pick_champ not in match_dict[match_id].champ_drafts[-1][1]:
                        channel = await ctx.author.create_dm()
                        await channel.send("You cannot pick a champion that is not in your remaining pool.")
                        return

                    if pick_champ == match_dict[match_id].bans_1v1[0]:
                        channel = await ctx.author.create_dm()
                        await channel.send("You cannot pick a champion that is banned by the other player.")
                        return

                    match_dict[match_id].cap2_1v1_champ = pick_champ

                    if match_dict[match_id].cap1_1v1_champ is None:
                        channel = await ctx.author.create_dm()
                        await channel.send("Waiting for the other player to pick a champion.")
                    else:
                        match_dict[match_id].current_draft = 'report'

                        channel = await match_dict[match_id].captain1.create_dm()
                        await channel.send(f"You are playing: `{match_dict[match_id].cap1_1v1_champ}`\n"
                                           f"`{match_dict[match_id].captain2.name}` is playing: `{match_dict[match_id].cap2_1v1_champ}`\n"
                                           f"The map is: `{match_dict[match_id].map_drafts[-1][0][0]}`\n"
                                           f"Report the result of your game with: `!report w/l`")

                        channel = await match_dict[match_id].captain2.create_dm()
                        await channel.send(f"You are playing: `{match_dict[match_id].cap2_1v1_champ}`\n"
                                           f"`{match_dict[match_id].captain1.name}` is playing: `{match_dict[match_id].cap1_1v1_champ}`\n"
                                           f"The map is: `{match_dict[match_id].map_drafts[-1][0][0]}`\n"
                                           f"Report the result of your game with: `!report w/l`")

        elif match_dict[match_id].current_draft == 'champ' and match_dict[match_id].current_game > 1:

            if ctx.author != match_dict[match_id].active_captain:
                return

            pick_champ = arg.lower()

            if pick_champ not in CHAMP_ALIASES:
                channel = await ctx.author.create_dm()
                await channel.send(f"`{arg}` is not recognized as valid champion name.")
                return

            pick_champ = CHAMP_ALIASES[pick_champ]

            if ctx.author == match_dict[match_id].captain1:

                if pick_champ not in match_dict[match_id].champ_drafts[-1][0]:
                    channel = await ctx.author.create_dm()
                    await channel.send("You cannot pick a champion that is not in your remaining pool.")
                    return

                match_dict[match_id].cap1_1v1_champ = pick_champ

                match_dict[match_id].current_draft = 'report'

                channel = await match_dict[match_id].captain1.create_dm()
                await channel.send(f"You are playing: `{match_dict[match_id].cap1_1v1_champ}`\n"
                                   f"`{match_dict[match_id].captain2.name}` is playing: `{match_dict[match_id].cap2_1v1_champ}`\n"
                                   f"Report the result of your game with: `!report w/l`")

                channel = await match_dict[match_id].captain2.create_dm()
                await channel.send(f"You are playing: `{match_dict[match_id].cap2_1v1_champ}`\n"
                                   f"`{match_dict[match_id].captain1.name}` is playing: `{match_dict[match_id].cap1_1v1_champ}`\n"
                                   f"Report the result of your game with: `!report w/l`")

            elif ctx.author == match_dict[match_id].captain2:

                if pick_champ not in match_dict[match_id].champ_drafts[-1][1]:
                    channel = await ctx.author.create_dm()
                    await channel.send("You cannot pick a champion that is not in your remaining pool.")
                    return

                match_dict[match_id].cap2_1v1_champ = pick_champ

                match_dict[match_id].current_draft = 'report'

                channel = await match_dict[match_id].captain1.create_dm()
                await channel.send(f"You are playing: `{match_dict[match_id].cap1_1v1_champ}`\n"
                                   f"`{match_dict[match_id].captain2.name}` is playing: `{match_dict[match_id].cap2_1v1_champ}`\n"
                                   f"Report the result of your game with: `!report w/l`")

                channel = await match_dict[match_id].captain2.create_dm()
                await channel.send(f"You are playing: `{match_dict[match_id].cap2_1v1_champ}`\n"
                                   f"`{match_dict[match_id].captain1.name}` is playing: `{match_dict[match_id].cap1_1v1_champ}`\n"
                                   f"Report the result of your game with: `!report w/l`")

        elif match_dict[match_id].current_draft == 'map' and match_dict[match_id].current_game > 1:

            if ctx.author != match_dict[match_id].active_captain:
                return

            pick_map = arg.lower()
            if pick_map not in MAP_ALIASES:
                channel = await ctx.author.create_dm()
                await channel.send("You have entered an invalid map name.")
                return

            pick_map = MAP_ALIASES[pick_map]

            if pick_map not in match_dict[match_id].map_drafts[-1][0]:
                channel = await ctx.author.create_dm()
                await channel.send("That map is not in the remaining pool.")
                return

            match_dict[match_id].current_draft = 'champ'
            match_dict[match_id].show_both_1v1 = False
            match_dict[match_id].update_1v1_embed()

            channel = await match_dict[match_id].inactive_captain.create_dm()
            await channel.send(f"The chosen map is: `{pick_map}`")

            channel = await match_dict[match_id].active_captain.create_dm()
            await channel.send(f"The chosen map is: `{pick_map}`")

            if ctx.author == match_dict[match_id].captain1:
                await channel.send(embed=match_dict[match_id].cap1_1v1_embed)
            elif ctx.author == match_dict[match_id].captain2:
                await channel.send(embed=match_dict[match_id].cap2_1v1_embed)
            await channel.send(f"Pick your next champion with: `!pick name`")

            match_dict[match_id].show_both_1v1 = True
            match_dict[match_id].update_1v1_embed()


@client.command(aliases=['r'])
async def report(ctx, *, arg):
    if ctx.guild is not None:
        return

    if ctx.author not in active_captains:
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently in a match.")
        return

    match_id = active_captains[ctx.author]

    if match_dict[match_id].current_draft != "report":
        channel = await ctx.author.create_dm()
        await channel.send("You are not currently in the report phase.")
        return

    if arg.lower() in ['w', 'win']:
        result = 1
    elif arg.lower() in ['l', 'loss', 'lose']:
        result = -1
    else:
        channel = await ctx.author.create_dm()
        await channel.send(f"`{arg}` not accepted as a valid result.")
        return

    if match_dict[match_id].match_format == '3v3' or '1v1':

        if ctx.author == match_dict[match_id].captain1:
            match_dict[match_id].last_game_result[0] = result
        elif ctx.author == match_dict[match_id].captain2:
            match_dict[match_id].last_game_result[1] = result

        if (match_dict[match_id].last_game_result[0] + match_dict[match_id].last_game_result[1]) != 0:
            channel = await ctx.author.create_dm()
            await channel.send(f"Waiting for both captains to report the same result.")
            return
        else:
            if match_dict[match_id].last_game_result[0] == 1:
                match_dict[match_id].captain1_wins += 1
            elif match_dict[match_id].last_game_result[1] == 1:
                match_dict[match_id].captain2_wins += 1

            if match_dict[match_id].captain1_wins == match_dict[match_id].wins_needed:
                channel = await match_dict[match_id].captain1.create_dm()
                await channel.send("The match has concluded. Your team has won.")
                channel = await match_dict[match_id].captain2.create_dm()
                await channel.send("The match has concluded. Your team has lost.")
                active_captains.pop(match_dict[match_id].captain1, None)
                active_captains.pop(match_dict[match_id].captain2, None)
                match_dict.pop(match_id)
                return

            elif match_dict[match_id].captain2_wins == match_dict[match_id].wins_needed:
                channel = await match_dict[match_id].captain1.create_dm()
                await channel.send("The match has concluded. Your team has lost.")
                channel = await match_dict[match_id].captain2.create_dm()
                await channel.send("The match has concluded. Your team has won.")
                active_captains.pop(match_dict[match_id].captain1, None)
                active_captains.pop(match_dict[match_id].captain2, None)
                match_dict.pop(match_id)
                return

            elif match_dict[match_id].match_format == '3v3':
                match_dict[match_id].current_draft = 'map'
                match_dict[match_id].current_game += 1
                match_dict[match_id].map_drafts.append([["Blackstone Arena - Day", "Daharin Battlegrounds - Night", "Dragon Garden - Night",
                  "Great Market - Night", "Meriko Summit - Night", "Mount Araz - Night", "Orman Temple - Night"], []])

                if match_dict[match_id].last_game_result[0] == 1:
                    match_dict[match_id].active_captain = match_dict[match_id].captain1
                    match_dict[match_id].inactive_captain = match_dict[match_id].captain2
                    channel = await match_dict[match_id].captain1.create_dm()
                    await channel.send("Your team has won the last game. The next map draft will now begin.")
                    channel = await match_dict[match_id].captain2.create_dm()
                    await channel.send("Your team has lost the last game. The next map draft will now begin.")
                elif match_dict[match_id].last_game_result[1] == 1:
                    match_dict[match_id].active_captain = match_dict[match_id].captain2
                    match_dict[match_id].inactive_captain = match_dict[match_id].captain1
                    channel = await match_dict[match_id].captain1.create_dm()
                    await channel.send("Your team has lost the last game. The next map draft will now begin.")
                    channel = await match_dict[match_id].captain2.create_dm()
                    await channel.send("Your team has won the last game. The next map draft will now begin.")

                match_dict[match_id].last_game_result = [9, 9]
                match_dict[match_id].update_map_embed()
                channel = await match_dict[match_id].active_captain.create_dm()
                match_dict[match_id].active_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].active_map_message_2 = await channel.send(
                    "Ban with:\n`!ban name`")

                channel = await match_dict[match_id].inactive_captain.create_dm()
                match_dict[match_id].update_map_embed()
                match_dict[match_id].inactive_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].inactive_map_message_2 = await channel.send(
                    "Waiting for other captain to ban.")

            elif match_dict[match_id].match_format == '1v1':
                match_dict[match_id].current_draft = 'map'
                match_dict[match_id].current_game += 1
                match_dict[match_id].map_drafts.append([["Blackstone Arena - Day", "Dragon Garden - Night",
                                                         "Meriko Summit - Night", "Mount Araz - Night",
                                                         "Orman Temple - Night"], []])

                if match_dict[match_id].last_game_result[0] == 1:
                    match_dict[match_id].champ_drafts[-1][1].remove(match_dict[match_id].cap2_1v1_champ)

                    match_dict[match_id].active_captain = match_dict[match_id].captain2
                    match_dict[match_id].inactive_captain = match_dict[match_id].captain1
                    channel = await match_dict[match_id].captain1.create_dm()
                    await channel.send("You won the last game.")
                    channel = await match_dict[match_id].captain2.create_dm()
                    await channel.send("You lost the last game.")

                elif match_dict[match_id].last_game_result[1] == 1:
                    match_dict[match_id].champ_drafts[-1][0].remove(match_dict[match_id].cap1_1v1_champ)

                    match_dict[match_id].active_captain = match_dict[match_id].captain1
                    match_dict[match_id].inactive_captain = match_dict[match_id].captain2
                    channel = await match_dict[match_id].captain1.create_dm()
                    await channel.send("You lost the last game.")
                    channel = await match_dict[match_id].captain2.create_dm()
                    await channel.send("You won the last game.")

                match_dict[match_id].last_game_result = [9, 9]
                match_dict[match_id].bans_1v1 = [None, None]
                match_dict[match_id].update_map_embed()
                match_dict[match_id].update_1v1_embed()
                channel = await match_dict[match_id].active_captain.create_dm()
                match_dict[match_id].active_map_message = await channel.send(embed=match_dict[match_id].map_embed)
                match_dict[match_id].active_map_message_2 = await channel.send(
                    "Pick with: `!pick name`")


@client.command()
async def rules(ctx, arg=None):

    channel = await ctx.author.create_dm()
    if arg is None:
        await channel.send("No argument given.")
    else:
        await channel.send(arg)

client.run(TOKEN)
