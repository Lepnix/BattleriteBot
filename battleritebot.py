from discord.ext import commands
from discord import *
import discord
import operator
import random
import dill as pickle
import discord.member
from elo import rate_1vs1

client = commands.Bot(command_prefix='!')
client.remove_command('help')
TOKEN = open('token.secret', 'r').read()

BUILDS = {'freya': 'r2, y2, gS, yE, gE', 'ashka': 'r2, y2, rQ, rR, rP', 'croak': 'g2, b2, yQ, yE, pE',
          'bakko': 'p2, yQ, tS, rE, yE', 'jamila': 'p2, rS, yE, pE, pR', 'raigon': 'tS, gS, tQ, rQ, bR',
          'rook': 't2, rE, rS, yS, gQ', 'ruh kaan': 'g1, p1, wS, wE, rE', 'rk': 'g1, p1, wS, wE, rE',
          'shifu': 'p2, rS, rQ, gQ, rR', 'thorn': 'r1, gS, pE, rE, wR', 'alysia': 'p2, tQ, rQ, tE, rR',
          'destiny': 'g1, rS, yS, yE, pR', 'ezmo': "p2, b2, rS', rS'', bE", 'iva': "r2', yQ, pE, bE, pR",
          'jade': 'b1, r2, p2, bS, rQ', 'jumong': 'p2, pE, rQ, pQ, yR', 'shen rao': 'b2, tS, bQ, yE, yR',
          'shen': 'b2, tS, bQ, yE, yR', 'taya': 'p1, g1, y2, yQ, yE', 'varesh': 'g1, r2, p2, pS, bE',
          'blossom': 't1, t2, yS, yQ, pE', 'lucie': 'g1, t2, r2, yS, wQ', 'oldur': 'w1, b1, t2, tS, yQ',
          'pearl': 'r1, p1, t2, pQ, tE', 'pestilus': 'tQ, pQ, pE, rE, wR', 'pest': 'tQ, pQ, pE, rE, wR',
          'poloma': 't1, tS, pE, rE, tR', 'sirius': 't1, g2, yS, bE, rR', 'ulric': 'r1, w1, yS, pE, yR',
          'zander': 't1, b2, p2, wS, bS'}

character_stats = {'freya': [0, 0, 0, 0, 0], 'ashka': [0, 0, 0, 0, 0], 'croak': [0, 0, 0, 0, 0], 'bakko': [0, 0, 0, 0, 0],
                   'jamila': [0, 0, 0, 0, 0], 'raigon': [0, 0, 0, 0, 0], 'rook': [0, 0, 0, 0, 0], 'ruh kaan': [0, 0, 0, 0, 0],
                   'shifu': [0, 0, 0, 0, 0], 'thorn': [0, 0, 0, 0, 0], 'alysia': [0, 0, 0, 0, 0], 'destiny': [0, 0, 0, 0, 0],
                   'ezmo': [0, 0, 0, 0, 0], 'iva': [0, 0, 0, 0, 0], 'jade': [0, 0, 0, 0, 0], 'jumong': [0, 0, 0, 0, 0],
                   'shen rao': [0, 0, 0, 0, 0], 'taya': [0, 0, 0, 0, 0], 'varesh': [0, 0, 0, 0, 0], 'blossom': [0, 0, 0, 0, 0],
                   'lucie': [0, 0, 0, 0, 0], 'oldur': [0, 0, 0, 0, 0], 'pearl': [0, 0, 0, 0, 0], 'pestilus': [0, 0, 0, 0, 0],
                   'poloma': [0, 0, 0, 0, 0], 'sirius': [0, 0, 0, 0, 0], 'ulric': [0, 0, 0, 0, 0], 'zander': [0, 0, 0, 0, 0],
                   'stat counter': 0}

stats_cache = []
queue_channel = []
user_dictionary = {}
match_dictionary = {}
match_counter = 0
MAP_POOL = ['Mount Araz - Night', 'Blackstone Arena - Day', 'Dragon Garden - Night', 'Great Market - Night',
            'Meriko Summit - Night', 'Mount Araz - Day', 'Meriko Summit - Day', 'Blackstone Arena - Night',
            'Orman Temple - Day', 'Orman Temple - Night', 'Sky Ring - Day', 'Sky Ring - Night', 'Dragon Garden - Day',
            'Daharin Battlegrounds - Day', 'Daharin Battlegrounds - Night', 'Great Market - Day']
QUEUE_CHANNEL_ID = 712809382487785472
MATCH_CHANNEL_ID = 712809411243933697
MISC_COMMANDS_ID = 712809437034709133
DRAFT_CHANNEL_ID = 712809357988986980
SERVER_ID = 712808385204060202
NAIL_CONTROL_ID = 712810025462136853
NAIL_MEMBER_ID = 712809993673637930
NAIL_TRIAL_ID = 712858389264334861
DRAFT_BOT_ID = 709635454252613643
BOT_CHANNELS = [QUEUE_CHANNEL_ID, MATCH_CHANNEL_ID, MISC_COMMANDS_ID]
purge_voters = []
REQUIRED_VOTERS = 4
queue_table_data = [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']]
queue_table_message = 0
rankings = []
ranking_names = []
ranking_scores = []
user_pickle_information = []
banned_champs = []
banned_players = []
complaints = {}
complaint_pickle_info = {}


queue_embed = discord.Embed(
    title=None,
    description=None,
    color=discord.Color.magenta()
)

queue_embed.add_field(name='Fill', value='---', inline=False)
queue_embed.add_field(name='DPS', value='---', inline=False)
queue_embed.add_field(name='Support', value='---', inline=False)

match_embed = discord.Embed(
    title=None,
    description=None,
    color=discord.Color.magenta()
)


field_value_1 = ''
field_value_2 = ''
field_value_3 = ''


class User:
    def __init__(self, name):
        self.name = name
        self.id = name.id
        self.points = 1000
        self.display_rating = round(self.points)
        self.wins = 0
        self.losses = 0
        self.strikes = 0
        self.in_match = False
        self.is_captain1 = False
        self.is_captain2 = False
        self.last_match_id = 0
        self.reported = False
        self.dropped = False


class Match:
    def __init__(self):
        global queue_channel
        global purge_voters
        global match_counter
        global user_dictionary
        self.players = {}
        self.support_counter = 0
        for player in queue_channel:
            if len(self.players) < 6:
                if player[1] == 'Fill' or player[1] == 'DPS':
                    self.players[player[0]] = player[1]
                elif self.support_counter < 2:
                    self.players[player[0]] = player[1]
                    self.support_counter += 1
        for player in self.players:
            if player in [item[0] for item in queue_channel]:
                del queue_channel[[item[0] for item in queue_channel].index(player)]
        self.draft_pool = list(self.players.keys())
        self.team1 = []
        self.team2 = []
        self.match_id = match_counter
        self.team1_win_votes = 0
        self.team2_win_votes = 0
        self.drop_votes = 0
        self.map = MAP_POOL[random.randint(0, 15)]
        self.closed = False
        purge_voters.clear()
        max = user_dictionary[self.draft_pool[0]].display_rating
        self.captain1 = self.draft_pool[0]
        for player in self.draft_pool:     #finds highest and second highest rated players, makes them captain1 and captain2, and removes them from pool
            user_dictionary[player].in_match = True  #sets inmatch to true for each player in the game
            user_dictionary[player].last_match_id = self.match_id
            if user_dictionary[player].display_rating > max:
                self.captain1 = player
                max = user_dictionary[player].display_rating
        self.team1.append(self.captain1)
        user_dictionary[self.captain1].is_captain1 = True
        self.draft_pool.remove(self.captain1)
        max = user_dictionary[self.draft_pool[0]].display_rating
        self.captain2 = self.draft_pool[0]
        for player in self.draft_pool:
            if user_dictionary[player].display_rating > max:
                self.captain2 = player
                max = user_dictionary[player].display_rating
        self.team2.append(self.captain2)
        user_dictionary[self.captain2].is_captain2 = True
        self.draft_pool.remove(self.captain2)


def updateQueueTableData():
    global queue_channel
    global queue_table_data
    f = 0
    d = 0
    s = 0
    queue_table_data = [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']]
    for person in queue_channel:
        if person[1] == 'Fill':
            queue_table_data[0][f] = person[0].name
            f += 1
        if person[1] == 'DPS':
            queue_table_data[1][d] = person[0].name
            d += 1
        if person[1] == 'Support':
            queue_table_data[2][s] = person[0].name
            s += 1


def updateQueueEmbed():
    global queue_embed
    global queue_table_data
    global field_value_1
    global field_value_2
    global field_value_3

    updated_queue_embed = discord.Embed(
    title=None,
    description=None,
    color=discord.Color.magenta()
)


    field_value_1 = ''
    field_value_2 = ''
    field_value_3 = ''

    for i in queue_table_data[0]:
        if i == '':
            field_value_1 += '---\n'
            break
        else:
            field_value_1 += f'{i}\n'

    for i in queue_table_data[1]:
        if i == '':
            field_value_2 += '---\n'
            break
        else:
            field_value_2 += f'{i}\n'

    for i in queue_table_data[2]:
        if i == '':
            field_value_3 += '---\n'
            break
        else:
            field_value_3 += f'{i}\n'

    updated_queue_embed.add_field(name='Fill', value=field_value_1, inline=False)
    updated_queue_embed.add_field(name='DPS', value=field_value_2, inline=False)
    updated_queue_embed.add_field(name='Support', value=field_value_3, inline=False)

    queue_embed = updated_queue_embed


def createMatchEmbed(id):
    global match_embed
    global user_dictionary
    global match_dictionary
    updated_match_embed = discord.Embed(
    title=None,
    description=None,
    color=discord.Color.magenta()
    )

    team1 = f"{match_dictionary[id].team1[0].name} - {match_dictionary[id].players[match_dictionary[id].team1[0]]}" \
        f"\n{match_dictionary[id].team1[1].name} - {match_dictionary[id].players[match_dictionary[id].team1[1]]}" \
        f"\n{match_dictionary[id].team1[2].name} - {match_dictionary[id].players[match_dictionary[id].team1[2]]}"
    team2 = f"{match_dictionary[id].team2[0].name} - {match_dictionary[id].players[match_dictionary[id].team2[0]]}" \
        f"\n{match_dictionary[id].team2[1].name} - {match_dictionary[id].players[match_dictionary[id].team2[1]]}" \
        f"\n{match_dictionary[id].team2[2].name} - {match_dictionary[id].players[match_dictionary[id].team2[2]]}"

    updated_match_embed.add_field(name='Team 1', value=team1, inline=True)
    updated_match_embed.add_field(name='Team 2', value=team2, inline=True)
    updated_match_embed.add_field(name='Map', value=match_dictionary[id].map, inline=False)
    updated_match_embed.set_author(name=f'Match #{id}')

    match_embed = updated_match_embed


def createUser(name):
    user_dictionary[name] = User(name)


def createMatch():
    global match_counter
    match_counter += 1
    match_dictionary[match_counter] = Match()


def sortRankings():
    global rankings
    global ranking_names
    global ranking_scores
    rankings = []
    ranking_names = []
    ranking_scores = []
    i = 0
    for name in user_dictionary:
        if user_dictionary[name].wins + user_dictionary[name].losses > 9:
            rankings.append([name, user_dictionary[name].display_rating, i + 1])
            i += 1
    rankings = sorted(rankings, key=operator.itemgetter(1), reverse=True)
    k = 0
    while k < len(rankings):
        ranking_names.append(rankings[k][0])
        k += 1
    k = 0
    while k < len(rankings):
        ranking_scores.append(rankings[k][1])
        k += 1


def closeMatch(id, result):
    global user_dictionary
    global match_dictionary
    global user_pickle_out
    global match_pickle_out
    global user_pickle_information

    sum = 0
    for player in match_dictionary[id].team1:
        sum += user_dictionary[player].points
        team1_avg = sum / 3

    sum = 0
    for player in match_dictionary[id].team2:
        sum += user_dictionary[player].points
        team2_avg = sum / 3

    if result == 1:   #team 1 wins
        updated_team1_avg, updated_team2_avg = rate_1vs1(team1_avg, team2_avg)
        team1_change = (updated_team1_avg - team1_avg) * 2
        team2_change = (updated_team2_avg - team2_avg) * 2
        for player in match_dictionary[id].team1:
            user_dictionary[player].wins += 1
            user_dictionary[player].points += team1_change
        for player in match_dictionary[id].team2:
            user_dictionary[player].losses += 1
            user_dictionary[player].points += team2_change

    elif result == 2:   #team 2 wins
        updated_team2_avg, updated_team1_avg = rate_1vs1(team2_avg, team1_avg)
        team1_change = (updated_team1_avg - team1_avg) * 2
        team2_change = (updated_team2_avg - team2_avg) * 2
        for player in match_dictionary[id].team2:
            user_dictionary[player].wins += 1
            user_dictionary[player].points += team2_change
        for player in match_dictionary[id].team1:
            user_dictionary[player].losses += 1
            user_dictionary[player].points += team1_change

    for player in match_dictionary[id].players.keys():
        if (user_dictionary[player].wins + user_dictionary[player].losses) <= 10:
            user_dictionary[player].points = (user_dictionary[player].wins - user_dictionary[player].losses) * 20 + 1000

    for player in match_dictionary[id].players.keys():
        user_dictionary[player].in_match = False
        user_dictionary[player].is_captain1 = False
        user_dictionary[player].is_captain2 = False
        user_dictionary[player].reported = False
        user_dictionary[player].dropped = False
        user_dictionary[player].display_rating = round(user_dictionary[player].points)

    match_dictionary[id].closed = True

    user_pickle_information = []

    for user in user_dictionary.keys():
        user_pickle_information.append([user_dictionary[user].id, user_dictionary[user].points, user_dictionary[user].wins, user_dictionary[user].losses])

    user_pickle_out = open("user.pickle", "wb")
    pickle.dump(user_pickle_information, user_pickle_out)
    user_pickle_out.close()

    match_pickle_out = open("match.pickle", "wb")
    pickle.dump(match_counter, match_pickle_out)
    match_pickle_out.close()


# dont call function if ID not in match_dictionary.keys()
def matchAnalysis(info):
    global character_stats
    global stats_pickle_out
    global match_dictionary

    id = int(info[0])
    b1 = info[1]
    b2 = info[2]
    b3 = info[3]
    b4 = info[4]
    p1 = info[5]
    p2 = info[6]
    p3 = info[7]
    p4 = info[8]
    p5 = info[9]
    p6 = info[10]

    character_stats[b1][0] += 1
    character_stats[b2][0] += 1
    character_stats[b3][0] += 1
    character_stats[b4][0] += 1

    character_stats[p1][1] += 1
    character_stats[p2][1] += 1
    character_stats[p3][1] += 1
    character_stats[p4][1] += 1
    character_stats[p5][1] += 1
    character_stats[p6][1] += 1

    if match_dictionary[id].team1_win_votes >= 4:
        character_stats[p1][2] += 1
        character_stats[p2][2] += 1
        character_stats[p3][2] += 1
        character_stats[p4][3] += 1
        character_stats[p5][3] += 1
        character_stats[p6][3] += 1
    elif match_dictionary[id].team2_win_votes >= 4:
        character_stats[p1][3] += 1
        character_stats[p2][3] += 1
        character_stats[p3][3] += 1
        character_stats[p4][2] += 1
        character_stats[p5][2] += 1
        character_stats[p6][2] += 1

    character_stats['stat counter'] += 2

    stats_pickle_out = open("stats.pickle", "wb")
    pickle.dump(character_stats, stats_pickle_out)
    stats_pickle_out.close()


def matchPickBan(info):
    global character_stats
    global stats_pickle_out
    global match_dictionary

    b1 = info[1]
    b2 = info[2]
    b3 = info[3]
    b4 = info[4]
    p1 = info[5]
    p2 = info[6]
    p3 = info[7]
    p4 = info[8]
    p5 = info[9]
    p6 = info[10]

    character_stats[b1][0] += 1
    character_stats[b2][0] += 1
    character_stats[b3][0] += 1
    character_stats[b4][0] += 1

    character_stats[p1][1] += 1
    character_stats[p2][1] += 1
    character_stats[p3][1] += 1
    character_stats[p4][1] += 1
    character_stats[p5][1] += 1
    character_stats[p6][1] += 1

    character_stats['stat counter'] += 2

    stats_pickle_out = open("stats.pickle", "wb")
    pickle.dump(character_stats, stats_pickle_out)
    stats_pickle_out.close()


@client.event
async def on_ready():
    global user_pickle_information
    global queue_table_message
    global queue_table_data
    global user_dictionary
    global match_dictionary
    global match_counter
    global character_stats
    global banned_champs
    global complaint_pickle_info
    updateQueueEmbed()
    channel = client.get_channel(QUEUE_CHANNEL_ID)
    await channel.purge()
    queue_table_message = await channel.send(embed=queue_embed)
    user_pickle_information = []

    try:
        user_pickle_in = open("user.pickle", "rb")
        user_pickle_information = pickle.load(user_pickle_in)
        user_pickle_in.close()
    except:
        pass

    guild = client.get_guild(SERVER_ID)

    i = 0
    while i < len(user_pickle_information):
        name = guild.get_member(user_pickle_information[i][0])
        createUser(name)
        user_dictionary[name].points = user_pickle_information[i][1]
        user_dictionary[name].wins = user_pickle_information[i][2]
        user_dictionary[name].losses = user_pickle_information[i][3]
        user_dictionary[name].display_rating = round(user_dictionary[name].points)
        if len(user_pickle_information[i]) == 4:
            user_pickle_information[i].append(0)
        elif len(user_pickle_information[i]) == 5:
            user_dictionary[name].strikes = user_pickle_information[i][4]
        i += 1

    try:
        match_pickle_in = open("match.pickle", "rb")
        match_counter = pickle.load(match_pickle_in)
        match_pickle_in.close()
    except:
        pass

    try:
        stats_pickle_in = open("stats.pickle", "rb")
        character_stats = pickle.load(stats_pickle_in)
        stats_pickle_in.close()
    except:
        pass

    try:
        banned_champs_pickle_in = open("banned_champs.pickle", "rb")
        banned_champs = pickle.load(banned_champs_pickle_in)
        banned_champs_pickle_in.close()
    except:
        pass

    try:
        complaint_pickle_in = open("complaints.pickle", "rb")
        complaint_pickle_info = pickle.load(complaint_pickle_in)
        complaint_pickle_in.close()
    except:
        pass

    print('Battlerite Bot is online.')


@client.command()
async def build(ctx, char):
    await ctx.send("Working on it.")


#register new user
@client.command()
async def register(ctx):
    global user_dictionary
    global user_pickle_out
    global user_pickle_information
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    channel = await ctx.author.create_dm()

    if ctx.author in user_dictionary:
        await channel.send('You are already registered.')
    else:
        createUser(ctx.author)
        user_pickle_information = []
        for user in user_dictionary.keys():
            user_pickle_information.append([user_dictionary[user].id, user_dictionary[user].points, user_dictionary[user].wins, user_dictionary[user].losses])
        user_pickle_out = open("user.pickle", "wb")
        pickle.dump(user_pickle_information, user_pickle_out)
        user_pickle_out.close()
        await channel.send('You have been successfully registered.')


#clear channels after message is sent and process commands
@client.event
async def on_message(ctx):
    global match_dictionary
    if ctx.author == client.user:
        return

    if ctx.author.id == DRAFT_BOT_ID and ctx.channel.id == MISC_COMMANDS_ID:
        results = ctx.content.split(",")
        match_id = int(results[0])
        await ctx.delete()

        if match_id in match_dictionary.keys():
            stats_cache.append(results)
        else:
            matchPickBan(results)


    def is_not_me(m):
        return m.author != client.user

    if ctx.channel.id in BOT_CHANNELS:
        await ctx.channel.purge(check=is_not_me)

    await client.process_commands(ctx)


@client.command(aliases=['q'])
async def queue(ctx, action, role=None):
    global queue_embed
    global queue_table_message
    global purge_voters
    global queue_channel
    global match_dictionary
    global match_counter
    if not ctx.channel.id == QUEUE_CHANNEL_ID:
        return

    channel = await ctx.author.create_dm()
    guild = client.get_guild(SERVER_ID)
    nail_member = guild.get_role(NAIL_MEMBER_ID)
    nail_trial = guild.get_role(NAIL_TRIAL_ID)

    if (ctx.author in user_dictionary.keys()) and ((nail_member in ctx.author.roles) or (nail_trial in ctx.author.roles)) and (ctx.author.id not in banned_players):
        if action == 'join' or action == 'j':
            if not ctx.author in (item[0] for item in queue_channel):   #checks if author is in a list of the first element of queue_channel
                if not user_dictionary[ctx.author].in_match:
                    if role == 'f' or role == 's' or role == 'd' or role == 'fill' or role == 'dps' or role == 'support':
                        if role == 'f' or role == 'fill':
                            queue_channel.append([ctx.author, 'Fill'])
                        if role == 's' or role == 'support':
                            queue_channel.append([ctx.author, 'Support'])
                        if role == 'd' or role == 'dps':
                            queue_channel.append([ctx.author, 'DPS'])
                        updateQueueTableData()
                        updateQueueEmbed()
                        await queue_table_message.edit(embed=queue_embed)
                        role_list = [item[1] for item in queue_channel]
                        if (len(queue_channel) >= 6) and ((role_list.count('Fill') + role_list.count('DPS')) >= 4):
                            createMatch()
                            updateQueueTableData()
                            updateQueueEmbed()
                            await queue_table_message.edit(embed=queue_embed)
                            channel = await match_dictionary[match_counter].captain1.create_dm()
                            await channel.send(f"You are Captain 1. You will draft first. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                                               f"```1 - {match_dictionary[match_counter].draft_pool[0].name} - {match_dictionary[match_counter].players[match_dictionary[match_counter].draft_pool[0]]}\n"
                                               f"2 - {match_dictionary[match_counter].draft_pool[1].name} - {match_dictionary[match_counter].players[match_dictionary[match_counter].draft_pool[1]]}\n"
                                               f"3 - {match_dictionary[match_counter].draft_pool[2].name} - {match_dictionary[match_counter].players[match_dictionary[match_counter].draft_pool[2]]}\n"
                                               f"4 - {match_dictionary[match_counter].draft_pool[3].name} - {match_dictionary[match_counter].players[match_dictionary[match_counter].draft_pool[3]]}\n\n"
                                               f"Team 1\n"
                                               f"{match_dictionary[match_counter].team1[0].name} - {match_dictionary[match_counter].players[match_dictionary[match_counter].team1[0]]}\n\n"
                                               f"Team 2\n"
                                               f"{match_dictionary[match_counter].team2[0].name} - {match_dictionary[match_counter].players[match_dictionary[match_counter].team2[0]]}```\n")
                            channel = await match_dictionary[match_counter].captain2.create_dm()
                            await channel.send("You are Captain 2. You will draft second.")
                            for player in match_dictionary[match_counter].draft_pool:
                                channel = await player.create_dm()
                                await channel.send(f"You are not a captain. `{match_dictionary[match_counter].captain1.name}` and `{match_dictionary[match_counter].captain2.name}` are the captains.")
                    else:
                        await channel.send(f"`{role}` is not recognized as a valid role. Please enter queue with `!queue join <f/d/s/>`")
                else:
                    await channel.send("You are still in a match. Report your match in the match channel with `!mr <w/l>`")
            else:
                await channel.send("You are already in queue.")
        elif action == 'leave' or action == 'l':
            if ctx.author in (item[0] for item in queue_channel):
                for player in queue_channel:
                    if player[0] == ctx.author:
                        queue_channel.remove(player)
                updateQueueTableData()
                updateQueueEmbed()
                await queue_table_message.edit(embed=queue_embed)
            else:
                await channel.send("You are not in queue.")
        elif action == 'purge' or action == 'p':
            if not ctx.author in purge_voters:
                nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)
                if nail_control in ctx.author.roles:
                    purge_voters.extend([ctx.author, ctx.author, ctx.author, ctx.author])
                purge_voters.append(ctx.author)
                if len(purge_voters) < REQUIRED_VOTERS:
                    await channel.send(f"You have voted to purge the queue. `{REQUIRED_VOTERS-len(purge_voters)}` more people must vote to purge the queue.")
                else:
                    purge_voters.clear()
                    for player in queue_channel:
                        channel = await player[0].create_dm()
                        await channel.send("The queue has been purged.")
                    queue_channel.clear()
                    updateQueueTableData()
                    updateQueueEmbed()
                    await queue_table_message.edit(embed=queue_embed)
            else:
                await channel.send(f"You have already voted to purge the queue. `{REQUIRED_VOTERS-len(purge_voters)}` more people must vote to purge the queue.")
        else:
            await channel.send(f"`{action}` is not a recognized command.")

    elif not ((nail_member in ctx.author.roles) or (nail_trial in ctx.author.roles)):
        await channel.send("You currently do not have a NAIL role. Talk to an administrator to receive the NAIL Trial Member role.")

    elif ctx.author.id in banned_players:
        await channel.send("You are currently banned from NAIL.")

    else:
        await channel.send("You have not yet registered. Please register using the `!register` command in misc-command channel.")


@client.command()
async def info(ctx):
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    sortRankings()

    channel = await ctx.author.create_dm()

    info_embed = discord.Embed(
    title=None,
    description=None,
    color=discord.Color.magenta()
    )

    if ctx.author in user_dictionary:
        info_embed_field_value_1 = f"\nRating:"\
                                   f"\nRecord:"\
                                   f"\nRanking:"

        if ctx.author in ranking_names:
            info_embed_field_value_2 = f"{user_dictionary[ctx.author].display_rating}" \
                f"\n{user_dictionary[ctx.author].wins}-{user_dictionary[ctx.author].losses}" \
                f"\n{ranking_names.index(ctx.author) + 1}/{len(ranking_names)}"
        else:
            info_embed_field_value_2 = f"{user_dictionary[ctx.author].display_rating}" \
                f"\n{user_dictionary[ctx.author].wins}-{user_dictionary[ctx.author].losses}" \
                f"\nComplete {10 - (user_dictionary[ctx.author].wins + user_dictionary[ctx.author].losses)} more games to place."

        info_embed.add_field(name=f"{ctx.author.name}", value=info_embed_field_value_1, inline=True)
        info_embed.add_field(name="\u200b", value=info_embed_field_value_2, inline=True)

        await channel.send(embed=info_embed)
    else:
        await channel.send("You have not yet registered. Please register using the `!register` command.")


@client.command()
async def draft(ctx, arg):
    global match_embed
    global user_dictionary
    global match_dictionary
    if ctx.guild == None:
        if user_dictionary[ctx.author].is_captain1 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 4:    #checks if command user is captain 1 and has 4 players in their draft pool
            match_dictionary[user_dictionary[ctx.author].last_match_id].team1.append(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))   #removes chosen player from draft pool and adds them to team 1
            await ctx.channel.send(f"You have chosen `{match_dictionary[user_dictionary[ctx.author].last_match_id].team1[1].name}`. Waiting for other captain to draft.")
            channel = await match_dictionary[user_dictionary[ctx.author].last_match_id].captain2.create_dm()
            await channel.send(
                f"It is your turn to draft. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                f"```1 - {match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[0].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[0]]}\n"
                f"2 - {match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[1].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[1]]}\n"
                f"3 - {match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[2].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[2]]}\n\n"
                f"Team 1\n"
                f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team1[0].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].team1[0]]}\n"
                f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team1[1].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].team1[1]]}\n\n"
                f"Team 2\n"
                f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[0].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].team2[0]]}```\n"
            )
        elif user_dictionary[ctx.author].is_captain2 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 4:
            await ctx.channel.send("It is not your turn to pick.")
        elif user_dictionary[ctx.author].is_captain2 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 3:
            match_dictionary[user_dictionary[ctx.author].last_match_id].team2.append(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))   #removes chosen player from draft pool and adds them to team 1
            channel = await match_dictionary[user_dictionary[ctx.author].last_match_id].captain2.create_dm()
            await channel.send(
                f"You have chosen `{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[1].name}`."
                f" It is your turn to draft, again. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                f"```1 - {match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[0].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[0]]}\n"
                f"2 - {match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[1].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool[1]]}\n\n"
                f"Team 1\n"
                f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team1[0].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].team1[0]]}\n"
                f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team1[1].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].team1[1]]}\n\n"
                f"Team 2\n"
                f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[0].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].team2[0]]}\n"
                f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[1].name} - {match_dictionary[user_dictionary[ctx.author].last_match_id].players[match_dictionary[user_dictionary[ctx.author].last_match_id].team2[1]]}```\n"
            )
        elif user_dictionary[ctx.author].is_captain1 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 3:
            await ctx.channel.send("It is not your turn to pick.")
        elif user_dictionary[ctx.author].is_captain2 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 2:
            match_dictionary[user_dictionary[ctx.author].last_match_id].team2.append(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))
            channel = await match_dictionary[user_dictionary[ctx.author].last_match_id].captain2.create_dm()
            await channel.send(f"You have chosen `{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[2].name}`.")
            match_dictionary[user_dictionary[ctx.author].last_match_id].team1.append(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool.pop(0))
            channel = client.get_channel(MATCH_CHANNEL_ID)
            await channel.send(f"A new match has been created.\n {match_dictionary[user_dictionary[ctx.author].last_match_id].team1[0].mention} "
                               f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team1[1].mention} "
                               f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team1[2].mention} "
                               f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[0].mention} "
                               f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[1].mention} "
                               f"{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[2].mention}"
                               f"\n")
            createMatchEmbed(user_dictionary[ctx.author].last_match_id)
            await channel.send(embed=match_embed)
            await channel.send("Please report the match with `!mr <w/l>`")
            channel = await match_dictionary[user_dictionary[ctx.author].last_match_id].captain1.create_dm()
            await channel.send(embed=match_embed)
            channel = await match_dictionary[user_dictionary[ctx.author].last_match_id].captain2.create_dm()
            await channel.send(embed=match_embed)
            channel = client.get_channel(DRAFT_CHANNEL_ID)
            if len(banned_champs) == 3:
                await channel.send(f"{user_dictionary[ctx.author].last_match_id},{match_dictionary[user_dictionary[ctx.author].last_match_id].captain1.id},"
                                   f"{match_dictionary[user_dictionary[ctx.author].last_match_id].captain2.id},{banned_champs[0]},{banned_champs[1]},{banned_champs[2]}")
            else:
                await channel.send(f"{user_dictionary[ctx.author].last_match_id},{match_dictionary[user_dictionary[ctx.author].last_match_id].captain1.id},"
                                   f"{match_dictionary[user_dictionary[ctx.author].last_match_id].captain2.id}")
        elif user_dictionary[ctx.author].is_captain1 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 2:
            await ctx.channel.send("It is not your turn to pick.")
        else:
            await ctx.channel.send("You are not a captain or it is not your turn to pick.")

@client.command()
async def mr(ctx, arg):
    global user_dictionary
    global match_dictionary
    global REQUIRED_VOTERS
    if not ctx.channel.id == MATCH_CHANNEL_ID:
        return

    channel = await ctx.author.create_dm()

    if not user_dictionary[ctx.author].in_match:
        await channel.send("You are not currently in a match.")
    else:
        if (arg == 'w' or arg == 'win') and ctx.author in match_dictionary[user_dictionary[ctx.author].last_match_id].team1 and not user_dictionary[ctx.author].reported:
            match_dictionary[user_dictionary[ctx.author].last_match_id].team1_win_votes += 1
            user_dictionary[ctx.author].reported = True
            await channel.send("You have reported a win for team 1.")
        elif (arg == 'w' or arg == 'win') and ctx.author in match_dictionary[user_dictionary[ctx.author].last_match_id].team2 and not user_dictionary[ctx.author].reported:
            match_dictionary[user_dictionary[ctx.author].last_match_id].team2_win_votes += 1
            user_dictionary[ctx.author].reported = True
            await channel.send("You have reported a win for team 2.")
        elif (arg == 'l' or arg == 'loss') and ctx.author in match_dictionary[user_dictionary[ctx.author].last_match_id].team1 and not user_dictionary[ctx.author].reported:
            match_dictionary[user_dictionary[ctx.author].last_match_id].team2_win_votes += 1
            user_dictionary[ctx.author].reported = True
            await channel.send("You have reported a loss for team 1.")
        elif (arg == 'l' or arg == 'loss') and ctx.author in match_dictionary[user_dictionary[ctx.author].last_match_id].team2 and not user_dictionary[ctx.author].reported:
            match_dictionary[user_dictionary[ctx.author].last_match_id].team1_win_votes += 1
            user_dictionary[ctx.author].reported = True
            await channel.send("You have reported a loss for team 2.")
        elif (arg == 'd' or arg == 'drop') and not user_dictionary[ctx.author].dropped:
            user_dictionary[ctx.author].dropped = True
            match_dictionary[user_dictionary[ctx.author].last_match_id].drop_votes += 1
            await channel.send(f"You have voted to drop the match. `{REQUIRED_VOTERS - match_dictionary[user_dictionary[ctx.author].last_match_id].drop_votes}` more people must vote in order to drop the match.")
        elif (arg == 'd' or arg == 'drop') and user_dictionary[ctx.author].dropped:
            await channel.send(f"You have already voted to drop the match. `{REQUIRED_VOTERS - match_dictionary[user_dictionary[ctx.author].last_match_id].drop_votes}` more people must vote in order to drop the match.")
        else:
            await channel.send(f"You have already reported or have entered an invalid result. Please report the match with `!mr <w/l>`")

        if match_dictionary[user_dictionary[ctx.author].last_match_id].team1_win_votes == REQUIRED_VOTERS and not match_dictionary[user_dictionary[ctx.author].last_match_id].closed:
            closeMatch(user_dictionary[ctx.author].last_match_id, 1)
            id_list = []
            if len(stats_cache) > 0:
                id_list = [int(item[0]) for item in stats_cache]
            if user_dictionary[ctx.author].last_match_id in id_list:
                matchAnalysis(stats_cache[id_list.index(user_dictionary[ctx.author].last_match_id)])
                del stats_cache[id_list.index(user_dictionary[ctx.author].last_match_id)]
            channel = client.get_channel(MATCH_CHANNEL_ID)
            await channel.send(f"Match `#{user_dictionary[ctx.author].last_match_id}` has ended. Team 1 has won.")
            for player in match_dictionary[user_dictionary[ctx.author].last_match_id].team1:
                channel = await player.create_dm()
                await channel.send(f"Your last match has been reported as a win. Your new rating is: `{user_dictionary[player].display_rating}`")
            for player in match_dictionary[user_dictionary[ctx.author].last_match_id].team2:
                channel = await player.create_dm()
                await channel.send(f"Your last match has been reported as a loss. Your new rating is: `{user_dictionary[player].display_rating}`")
        elif match_dictionary[user_dictionary[ctx.author].last_match_id].team2_win_votes == REQUIRED_VOTERS and not match_dictionary[user_dictionary[ctx.author].last_match_id].closed:
            closeMatch(user_dictionary[ctx.author].last_match_id, 2)
            id_list = []
            if len(stats_cache) > 0:
                id_list = [int(item[0]) for item in stats_cache]
            if user_dictionary[ctx.author].last_match_id in id_list:
                matchAnalysis(stats_cache[id_list.index(user_dictionary[ctx.author].last_match_id)])
                del stats_cache[id_list.index(user_dictionary[ctx.author].last_match_id)]
            channel = client.get_channel(MATCH_CHANNEL_ID)
            await channel.send(f"Match `#{user_dictionary[ctx.author].last_match_id}` has ended. Team 2 has won.")
            for player in match_dictionary[user_dictionary[ctx.author].last_match_id].team2:
                channel = await player.create_dm()
                await channel.send(f"Your last match has been reported as a win. Your new rating is: `{user_dictionary[player].display_rating}`")
            for player in match_dictionary[user_dictionary[ctx.author].last_match_id].team1:
                channel = await player.create_dm()
                await channel.send(f"Your last match has been reported as a loss. Your new rating is: `{user_dictionary[player].display_rating}`")
        elif match_dictionary[user_dictionary[ctx.author].last_match_id].drop_votes == REQUIRED_VOTERS:
            closeMatch(user_dictionary[ctx.author].last_match_id, 3)
            channel = client.get_channel(MATCH_CHANNEL_ID)
            await channel.send(f"Match `#{user_dictionary[ctx.author].last_match_id}` has been dropped.")

@client.command()
async def help(ctx):
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    channel = await ctx.author.create_dm()

    await channel.send(f"```Miscellaneous Commands: *use in misc channel or dm bot*"
                       f"\n!register - creates a profile for you which contains your stats"
                       f"\n!info - the bot messages you your rating, W/L, and current standing"
                       f"\n!build <character> - displays the most common build for the character *non-bot channel only*"
                       f"\n!draft <#> - used if you are a captain and the bot messages you to draft a player"
                       f"\n!leaderboard(lb) - bot messages you a top 10 leaderboard"
                       f"\n!stats - bot messages you a list of all the champs and their respective winrates, pickrates, and banrates"
                       f"\n!complain <name#1234> <explanation> - submits an anonymous complaint about a player"
                       f"\n!strikes - displays how many strikes you have"
                       f"\n\nQueue Channel Commands:"
                       f"\n!queue(q) join(j) <fill(f)/dps(d)/support(s)> - joins the queue as the desired role"
                       f"\n!queue(q) leave(l) - leaves the queue"
                       f"\n!queue(q) purge(p) - requires four people to empty the queue channel!"
                       f"\n\nMatch Channel Commands"
                       f"\n!mr <win(w)/loss(l)>  - report your current match as a win or loss"
                       f"\n!mr drop(d) - requires 4 people in your match to drop the match```")

@client.command(aliases=['lb'])
async def leaderboard(ctx):
    global ranking_names
    global ranking_scores
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    sortRankings()
    channel = await ctx.author.create_dm()

    lb_embed = discord.Embed(
        title=None,
        description=None,
        color=discord.Color.magenta()
    )

    if len(rankings) > 9:
        lb_field_value_1 = f"1)"\
                         f"\n2)"\
                         f"\n3)"\
                         f"\n4)"\
                         f"\n5)"\
                         f"\n6)"\
                         f"\n7)"\
                         f"\n8)"\
                         f"\n9)"\
                         f"\n10)"

        lb_field_value_2 = f"{ranking_names[0].name}"\
                         f"\n{ranking_names[1].name}"\
                         f"\n{ranking_names[2].name}"\
                         f"\n{ranking_names[3].name}"\
                         f"\n{ranking_names[4].name}"\
                         f"\n{ranking_names[5].name}"\
                         f"\n{ranking_names[6].name}"\
                         f"\n{ranking_names[7].name}"\
                         f"\n{ranking_names[8].name}"\
                         f"\n{ranking_names[9].name}"

        lb_field_value_3 = f"{ranking_scores[0]}" \
                           f"\n{ranking_scores[1]}" \
                           f"\n{ranking_scores[2]}" \
                           f"\n{ranking_scores[3]}" \
                           f"\n{ranking_scores[4]}" \
                           f"\n{ranking_scores[5]}" \
                           f"\n{ranking_scores[6]}" \
                           f"\n{ranking_scores[7]}" \
                           f"\n{ranking_scores[8]}" \
                           f"\n{ranking_scores[9]}"

        lb_embed.add_field(name="\u200b", value=lb_field_value_1, inline=True)
        lb_embed.add_field(name="\u200b", value=lb_field_value_2, inline=True)
        lb_embed.add_field(name="\u200b", value=lb_field_value_3, inline=True)
        lb_embed.set_author(name="Leaderboard")
        await channel.send(embed=lb_embed)
    else:
        await channel.send("There are not enough players who have placed to create a leaderboard. Try again later.")
    if ctx.author in ranking_names:
        if ranking_names.index(ctx.author) > 9:
            embed = discord.Embed(
                title=None,
                description=None,
                color=discord.Color.magenta()
            )
            embed.add_field(name="\u200b", value=f"{ranking_names.index(ctx.author) + 1})", inline=True)
            embed.add_field(name="\u200b", value=f"{ctx.author.name}", inline=True)
            embed.add_field(name="\u200b", value=f"{ranking_scores[ranking_names.index(ctx.author)]}", inline=True)
            await channel.send(embed=embed)


@client.command()
async def stats(ctx):
    global character_stats

    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    for champ in character_stats.keys():
        if champ != 'stat counter':
            if character_stats[champ][2] + character_stats[champ][3] > 0:
                character_stats[champ][4] = character_stats[champ][2] / (character_stats[champ][2] + character_stats[champ][3])

    channel = await ctx.author.create_dm()

    stats_embed = discord.Embed(
    title=None,
    description=None,
    color=discord.Color.magenta()
    )
    character_field = "Bakko\nCroak\nFreya\nJamila\nRaigon\nRook\nRuh Kaan\nShifu\nThorn\nAlysia\nAshka\nDestiny\n" \
                      "Ezmo\nIva\nJade\nJumong\nShen Rao\nTaya\nVaresh\nBlossom\nLucie\nOldur\nPearl\nPestilus\n" \
                      "Poloma\nSirius\nUlric\nZander"

    win_percent_field = f"{round(character_stats['bakko'][4]*100)}\n"\
        f"{round(character_stats['croak'][4]*100)}\n"\
        f"{round(character_stats['freya'][4]*100)}\n"\
        f"{round(character_stats['jamila'][4]*100)}\n"\
        f"{round(character_stats['raigon'][4]*100)}\n"\
        f"{round(character_stats['rook'][4]*100)}\n"\
        f"{round(character_stats['ruh kaan'][4]*100)}\n"\
        f"{round(character_stats['shifu'][4]*100)}\n"\
        f"{round(character_stats['thorn'][4]*100)}\n"\
        f"{round(character_stats['alysia'][4]*100)}\n"\
        f"{round(character_stats['ashka'][4]*100)}\n"\
        f"{round(character_stats['destiny'][4]*100)}\n"\
        f"{round(character_stats['ezmo'][4]*100)}\n"\
        f"{round(character_stats['iva'][4]*100)}\n"\
        f"{round(character_stats['jade'][4]*100)}\n"\
        f"{round(character_stats['jumong'][4]*100)}\n"\
        f"{round(character_stats['shen rao'][4]*100)}\n"\
        f"{round(character_stats['taya'][4]*100)}\n"\
        f"{round(character_stats['varesh'][4]*100)}\n"\
        f"{round(character_stats['blossom'][4]*100)}\n"\
        f"{round(character_stats['lucie'][4]*100)}\n"\
        f"{round(character_stats['oldur'][4]*100)}\n"\
        f"{round(character_stats['pearl'][4]*100)}\n"\
        f"{round(character_stats['pestilus'][4]*100)}\n"\
        f"{round(character_stats['poloma'][4]*100)}\n"\
        f"{round(character_stats['sirius'][4]*100)}\n"\
        f"{round(character_stats['ulric'][4]*100)}\n"\
        f"{round(character_stats['zander'][4]*100)}\n"

    pick_ban_rate_field = f"{round(100*character_stats['bakko'][1] / character_stats['stat counter'])}/{round(100*character_stats['bakko'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['croak'][1] / character_stats['stat counter'])}/{round(100*character_stats['croak'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['freya'][1] / character_stats['stat counter'])}/{round(100*character_stats['freya'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['jamila'][1] / character_stats['stat counter'])}/{round(100*character_stats['jamila'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['raigon'][1] / character_stats['stat counter'])}/{round(100*character_stats['raigon'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['rook'][1] / character_stats['stat counter'])}/{round(100*character_stats['rook'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['ruh kaan'][1] / character_stats['stat counter'])}/{round(100*character_stats['ruh kaan'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['shifu'][1] / character_stats['stat counter'])}/{round(100*character_stats['shifu'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['thorn'][1] / character_stats['stat counter'])}/{round(100*character_stats['thorn'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['alysia'][1] / character_stats['stat counter'])}/{round(100*character_stats['alysia'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['ashka'][1] / character_stats['stat counter'])}/{round(100*character_stats['ashka'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['destiny'][1] / character_stats['stat counter'])}/{round(100*character_stats['destiny'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['ezmo'][1] / character_stats['stat counter'])}/{round(100*character_stats['ezmo'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['iva'][1] / character_stats['stat counter'])}/{round(100*character_stats['iva'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['jade'][1] / character_stats['stat counter'])}/{round(100*character_stats['jade'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['jumong'][1] / character_stats['stat counter'])}/{round(100*character_stats['jumong'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['shen rao'][1] / character_stats['stat counter'])}/{round(100*character_stats['shen rao'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['taya'][1] / character_stats['stat counter'])}/{round(100*character_stats['taya'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['varesh'][1] / character_stats['stat counter'])}/{round(100*character_stats['varesh'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['blossom'][1] / character_stats['stat counter'])}/{round(100*character_stats['blossom'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['lucie'][1] / character_stats['stat counter'])}/{round(100*character_stats['lucie'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['oldur'][1] / character_stats['stat counter'])}/{round(100*character_stats['oldur'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['pearl'][1] / character_stats['stat counter'])}/{round(100*character_stats['pearl'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['pestilus'][1] / character_stats['stat counter'])}/{round(100*character_stats['pestilus'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['poloma'][1] / character_stats['stat counter'])}/{round(100*character_stats['poloma'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['sirius'][1] / character_stats['stat counter'])}/{round(100*character_stats['sirius'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['ulric'][1] / character_stats['stat counter'])}/{round(100*character_stats['ulric'][0] / character_stats['stat counter'])}\n"\
        f"{round(100*character_stats['zander'][1] / character_stats['stat counter'])}/{round(100*character_stats['zander'][0] / character_stats['stat counter'])}\n"

    stats_embed.add_field(name='Champions', value=character_field, inline=True)
    stats_embed.add_field(name='Winrate %', value=win_percent_field, inline=True)
    stats_embed.add_field(name='Pick/Ban %', value=pick_ban_rate_field, inline=True)
    stats_embed.set_author(name='Champion Statistics')

    await channel.send(embed=stats_embed)

@client.command(aliases=['wb'])
async def weeklyban(ctx, *, champs):
    global banned_champs
    if ctx.channel.id != MISC_COMMANDS_ID:
        return

    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

    if nail_control in ctx.author.roles:
        if champs == "None":
            banned_champs.clear()
        else:
            banned_champs = champs.split(",")
        banned_champs_pickle_out = open("banned_champs.pickle", "wb")
        pickle.dump(banned_champs, banned_champs_pickle_out)
        banned_champs_pickle_out.close()

@client.command()
async def bans(ctx):
    global banned_champs
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    channel = await ctx.author.create_dm()
    if len(banned_champs) == 0:
        await channel.send("There currently are no champions banned from NAIL.")
    else:
        await channel.send(f"The current champions banned from NAIL are: `{banned_champs[0]}`, `{banned_champs[1]}`, and `{banned_champs[2]}`")

@client.command(aliases=['wr'])
async def winrates(ctx):
    if ctx.channel.id != MISC_COMMANDS_ID:
        return

    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

    if nail_control not in ctx.author.roles:
        return

    channel = await ctx.author.create_dm()

    wr_message = ""

    for player in user_dictionary:
        if user_dictionary[player].losses > 0:
            if user_dictionary[player].wins / (user_dictionary[player].losses + user_dictionary[player].wins) < .4:
                wr_message += f"{player.name}  {user_dictionary[player].wins}-{user_dictionary[player].losses}\n"
    await channel.send(f"```\n{wr_message}```")

@client.command()
async def ban(ctx, arg):
    if ctx.channel.id != MISC_COMMANDS_ID:
        return

    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

    if nail_control not in ctx.author.roles:
        return

    channel = await ctx.author.create_dm()
    if int(arg) in banned_players:
        await channel.send("That player is already banned.")
    else:
        banned_players.append(int(arg))

@client.command()
async def unban(ctx, arg):
    if ctx.channel.id != MISC_COMMANDS_ID:
        return

    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

    if nail_control not in ctx.author.roles:
        return

    channel = await ctx.author.create_dm()
    if int(arg) in banned_players:
        banned_players.remove(int(arg))
    else:
        await channel.send("That player is not banned.")

@client.command(aliases=["ss"])
async def seasonstart(ctx):
    if ctx.channel.id != MISC_COMMANDS_ID:
        return

    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

    if nail_control not in ctx.author.roles:
        return

    channel = await ctx.author.create_dm()
    for player in user_pickle_information:
        player[1] = 1000
        player[2] = 0
        player[3] = 0
    user_pickle_out = open("user.pickle", "wb")
    pickle.dump(user_pickle_information, user_pickle_out)
    user_pickle_out.close()
    await channel.send("All player stats have been reset.")

@client.command()
async def strike(ctx, arg):
    if ctx.channel.id != MISC_COMMANDS_ID:
        return

    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

    if nail_control not in ctx.author.roles:
        return

    if client.get_guild(SERVER_ID).get_member(int(arg)) in user_dictionary.keys():
        user_dictionary[client.get_guild(SERVER_ID).get_member(int(arg))].strikes += 1
        for i in user_pickle_information:
            if i[0] == int(arg):
                i[4] += 1
        user_pickle_out = open("user.pickle", "wb")
        pickle.dump(user_pickle_information, user_pickle_out)
        user_pickle_out.close()

@client.command()
async def strikes(ctx):
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    channel = await ctx.author.create_dm()

    if ctx.author in user_dictionary:
        await channel.send(f"Number of strikes: `{user_dictionary[ctx.author].strikes}`")
    else:
        await channel.send(f"You are not registered.")

@client.command()
async def complain(ctx, target, *, arg):
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    if ctx.author not in user_dictionary.keys():
        channel = await ctx.author.create_dm()
        await channel.send("You are not registered.")
        return

    if ctx.author.id == 311749899614158848:
        channel = await ctx.author.create_dm()
        await channel.send("Kas, I can't in good conscience give you the ability to file complaints.")
        return

    target_player = client.get_guild(SERVER_ID).get_member_named(target)
    if not target_player in user_dictionary.keys():
        channel = await ctx.author.create_dm()
        await channel.send(f"`{target}` is not a registered NAIL user. Make sure you have typed their discord name correctly. ex. `!complain Name#1234 explanation`")
    else:
        if ctx.author.id not in complaint_pickle_info.keys():
            complaint_pickle_info[ctx.author.id] = []
        if target_player.id in complaint_pickle_info[ctx.author.id]:
            channel = await ctx.author.create_dm()
            await channel.send(f"You have already filed a complaint about this player. You may only file one complaint for each player.")
        else:
            complaint_pickle_info[ctx.author.id].append(target_player.id)
            complaint_pickle_out = open("complaints.pickle", "wb")
            pickle.dump(complaint_pickle_info, complaint_pickle_out)
            complaint_pickle_out.close()
            channel = await ctx.author.create_dm()
            await channel.send(f"You have successfully submitted a complaint.")
            channel = await client.get_user(166670770234195978).create_dm()
            complaint = await channel.send(f"A new complaint has been filed for `{target_player.name}`:\n```\n{arg}```")
            complaints[complaint.id] = ctx.author.name

@client.command()
async def uncomplain(ctx, target):
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    target_player = client.get_guild(SERVER_ID).get_member_named(target)
    if ctx.author.id not in complaint_pickle_info.keys():
        channel = await ctx.author.create_dm()
        await channel.send("You have not filed any complaints.")
    elif target_player.id not in complaint_pickle_info[ctx.author.id]:
        channel = await ctx.author.create_dm()
        await channel.send(f"You have not filed any complaints for: `{target_player.name}`")
    else:
        complaint_pickle_info[ctx.author.id].remove(target_player.id)
        complaint_pickle_out = open("complaints.pickle", "wb")
        pickle.dump(complaint_pickle_info, complaint_pickle_out)
        complaint_pickle_out.close()
        channel = await ctx.author.create_dm()
        await channel.send(f"You have revoked a complaint for: `{target_player.name}`")
        channel = await client.get_user(166670770234195978).create_dm()
        await channel.send(f"A complaint has been revoked for: `{target_player.name}`")


@client.command()
async def sender(ctx, arg):
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return
    if ctx.author.id != 166670770234195978:
        return

    channel = await ctx.author.create_dm()
    await channel.send(f"The sender of complaint ID `{arg}` is `{complaints[int(arg)]}`.")


@client.command()
async def resetstrikes(ctx, arg):
    if ctx.channel.id != MISC_COMMANDS_ID:
        return

    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

    if nail_control not in ctx.author.roles:
        return

    if client.get_guild(SERVER_ID).get_member(int(arg)) in user_dictionary.keys():
        user_dictionary[client.get_guild(SERVER_ID).get_member(int(arg))].strikes = 0
        for i in user_pickle_information:
            if i[0] == int(arg):
                i[4] = 0
        user_pickle_out = open("user.pickle", "wb")
        pickle.dump(user_pickle_information, user_pickle_out)
        user_pickle_out.close()


@client.command()
async def resetpb(ctx):
    if ctx.channel.id != MISC_COMMANDS_ID:
        return

    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

    if nail_control not in ctx.author.roles:
        return

    for i in character_stats.keys():
        if i != 'stat counter':
            character_stats[i][0] = 0
            character_stats[i][1] = 0
        else:
            character_stats[i] = 0

    stats_pickle_out = open("stats.pickle", "wb")
    pickle.dump(character_stats, stats_pickle_out)
    stats_pickle_out.close()

@client.command()
async def complaints(ctx):
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    i = 0
    for player in complaints.keys():
        if ctx.author.id in complaints[player]:
            i += 1

    channel = await ctx.author.create_dm()
    await channel.send(f"Current # of complaints: {i}")


client.run(TOKEN)
