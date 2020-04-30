from discord.ext import commands
from discord import *
import discord
import operator
import trueskill
import random
import pickle
import discord.member

client = commands.Bot(command_prefix = '!')
client.remove_command('help')
TOKEN = 'NzA0NjYzMDQwNjgyODg1MTM0.XqgasA.IkvPir7CKKm_BMoPrfl1LfjHjf8'

BUILDS = {'freya': 'r2, y2, gS, yE, gE', 'ashka': 'r2, y2, rQ, rR, rP', 'croak': 'g2, b2, yQ, yE, pE'}
queue_channel = {}
user_dictionary = {}
match_dictionary = {}
match_counter = 0
MAP_POOL = ['Mount Araz Night', 'Blackstone Arena Day', 'Dragon Garden Night', 'Great Market Night', 'Meriko Summit Night', 'Mount Araz Day', 'Sky Ring Night']
QUEUE_CHANNEL_ID = 704660113897685022
MATCH_CHANNEL_ID = 704660569319538829
MISC_COMMANDS_ID = 704660610595553350
ADMIN_ROLE_ID = 705410054542721094
SERVER_ID = 704657422857273472
NAME_OF_ADMIN_ROLE = 'actual admin'
BOT_CHANNELS = [QUEUE_CHANNEL_ID, MATCH_CHANNEL_ID, MISC_COMMANDS_ID]
purge_voters = []
REQUIRED_VOTERS = 4
queue_table_data = [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']]
queue_table_message = 0
rankings = []
ranking_names = []
ranking_scores = []
user_pickle_information = []



queue_embed = discord.Embed(
    title=None,
    description=None,
    color=discord.Color.purple()
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
        self.points = trueskill.Rating()
        self.display_rating = round(self.points.mu * 40)
        self.wins = 0
        self.losses = 0
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
        self.players = queue_channel
        self.draft_pool = list(self.players.keys())
        self.team1 = []
        self.team2 = []
        self.match_id = match_counter
        self.team1_win_votes = 0
        self.team2_win_votes = 0
        self.drop_votes = 0
        self.map = MAP_POOL[random.randint(0, 6)]
        queue_channel = {}
        purge_voters = []
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


def clearQueueTableData():
    global queue_table_data
    queue_table_data = [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']]


def updateQueueTableData():
    global queue_channel
    f = 0
    d = 0
    s = 0
    for name in queue_channel:
        if queue_channel[name] == 'Fill':
            queue_table_data[0][f] = name.display_name
            f += 1
        if queue_channel[name] == 'DPS':
            queue_table_data[1][d] = name.display_name
            d += 1
        if queue_channel[name] == 'Support':
            queue_table_data[2][s] = name.display_name
            s += 1


def updateQueueEmbed():
    global queue_embed
    global queue_table_data
    global field_value_1
    global field_value_2
    global field_value_3

    updated_queue_embed = discord.Embed(
    title = None,
    description = None,
    color = discord.Color.purple()
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

    team1 = f"{match_dictionary[id].team1[0].display_name} - {match_dictionary[id].players[match_dictionary[id].team1[0]]}" \
        f"\n{match_dictionary[id].team1[1].display_name} - {match_dictionary[id].players[match_dictionary[id].team1[1]]}" \
        f"\n{match_dictionary[id].team1[2].display_name} - {match_dictionary[id].players[match_dictionary[id].team1[2]]}"
    team2 = f"{match_dictionary[id].team2[0].display_name} - {match_dictionary[id].players[match_dictionary[id].team2[0]]}" \
        f"\n{match_dictionary[id].team2[1].display_name} - {match_dictionary[id].players[match_dictionary[id].team2[1]]}" \
        f"\n{match_dictionary[id].team2[2].display_name} - {match_dictionary[id].players[match_dictionary[id].team2[2]]}"

    updated_match_embed.add_field(name='Team 1', value=team1, inline=True)
    updated_match_embed.add_field(name='Team 2', value=team2, inline=True)
    updated_match_embed.add_field(name ='Map', value=match_dictionary[id].map, inline=False)
    updated_match_embed.set_author(name=f'Match #{id}')

    match_embed = updated_match_embed


def createUser(name):
    user_dictionary[name] = User(name)
    return


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

    if result == 1: #team 1 wins
        for player in match_dictionary[id].team1:
            user_dictionary[player].wins += 1
        for player in match_dictionary[id].team2:
            user_dictionary[player].losses += 1
        new_rating = trueskill.rate([(user_dictionary[match_dictionary[id].team2[0]].points,
                                      user_dictionary[match_dictionary[id].team2[1]].points,
                                      user_dictionary[match_dictionary[id].team2[2]].points),
                                     (user_dictionary[match_dictionary[id].team1[0]].points,
                                      user_dictionary[match_dictionary[id].team1[1]].points,
                                      user_dictionary[match_dictionary[id].team1[2]].points)])
        user_dictionary[match_dictionary[id].team1[0]].points = new_rating[0][0]
        user_dictionary[match_dictionary[id].team1[1]].points = new_rating[0][1]
        user_dictionary[match_dictionary[id].team1[2]].points = new_rating[0][2]
        user_dictionary[match_dictionary[id].team2[0]].points = new_rating[1][0]
        user_dictionary[match_dictionary[id].team2[1]].points = new_rating[1][1]
        user_dictionary[match_dictionary[id].team2[2]].points = new_rating[1][2]

    elif result == 2:   #team 2 wins
        for player in match_dictionary[id].team2:
            user_dictionary[player].wins += 1
        for player in match_dictionary[id].team1:
            user_dictionary[player].losses += 1
        new_rating = trueskill.rate([(user_dictionary[match_dictionary[id].team1[0]].points,
                                      user_dictionary[match_dictionary[id].team1[1]].points,
                                      user_dictionary[match_dictionary[id].team1[2]].points),
                                     (user_dictionary[match_dictionary[id].team2[0]].points,
                                      user_dictionary[match_dictionary[id].team2[1]].points,
                                      user_dictionary[match_dictionary[id].team2[2]].points)])
        user_dictionary[match_dictionary[id].team1[0]].points = new_rating[0][0]
        user_dictionary[match_dictionary[id].team1[1]].points = new_rating[0][1]
        user_dictionary[match_dictionary[id].team1[2]].points = new_rating[0][2]
        user_dictionary[match_dictionary[id].team2[0]].points = new_rating[1][0]
        user_dictionary[match_dictionary[id].team2[1]].points = new_rating[1][1]
        user_dictionary[match_dictionary[id].team2[2]].points = new_rating[1][2]

    for player in match_dictionary[id].players.keys():
        user_dictionary[player].in_match = False
        user_dictionary[player].is_captain1 = False
        user_dictionary[player].is_captain2 = False
        user_dictionary[player].reported = False
        user_dictionary[player].dropped = False
        user_dictionary[player].display_rating = round(user_dictionary[player].points.mu * 40)

    user_pickle_information = []

    for user in user_dictionary.keys():
        user_pickle_information.append([str(user_dictionary[user].name), user_dictionary[user].points.mu, user_dictionary[user].points.sigma, user_dictionary[user].wins, user_dictionary[user].losses])

    user_pickle_out = open("user.pickle", "wb")
    pickle.dump(user_pickle_information, user_pickle_out)
    user_pickle_out.close()

    match_pickle_out = open("match.pickle", "wb")
    pickle.dump(match_counter, match_pickle_out)
    match_pickle_out.close()


@client.event
async def on_ready():
    global user_pickle_information
    global queue_table_message
    global queue_table_data
    global user_dictionary
    global match_dictionary
    global user_pickle_in
    updateQueueEmbed()
    channel = client.get_channel(QUEUE_CHANNEL_ID)
    await channel.purge()
    queue_table_message = await channel.send(embed=queue_embed)

    user_pickle_in = open("user.pickle", "rb")
    user_pickle_information = pickle.load(user_pickle_in)
    user_pickle_in.close()
    i=0
    while i < len(user_pickle_information):

        name = user_pickle_information[i][0]
        createUser(name)
        user_dictionary[name].points = trueskill.Rating(mu=user_pickle_information[i][1], sigma=user_pickle_information[i][2])
        user_dictionary[name].wins = user_pickle_information[i][3]
        user_dictionary[name].losses = user_pickle_information[i][4]

    print('Battlerite Bot is online.')


#build command
@client.command()
async def build(ctx, char):
    await ctx.send(BUILDS[char.lower()])


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
            user_pickle_information.append([str(user_dictionary[user].name), user_dictionary[user].points.mu, user_dictionary[user].points.sigma,user_dictionary[user].wins, user_dictionary[user].losses])
        user_pickle_out = open("user.pickle", "wb")
        pickle.dump(user_pickle_information, user_pickle_out)
        user_pickle_out.close()
        await channel.send('You have been successfully registered.')


#clear channels after message is sent and process commands
@client.event
async def on_message(ctx):
    if ctx.author == client.user:
        return

    def is_not_me(m):
        return m.author != client.user

    if ctx.channel.id in BOT_CHANNELS:
        await ctx.channel.purge(check=is_not_me)

    await client.process_commands(ctx)


@client.command(aliases=['q'])
async def queue(ctx, action, role = None):
    global queue_embed
    global queue_table_message
    global purge_voters
    global queue_channel
    global match_dictionary
    global match_counter
    if not ctx.channel.id == QUEUE_CHANNEL_ID:
        return

    channel = await ctx.author.create_dm()

    if ctx.author in user_dictionary.keys():
        if action == 'join':
            if not ctx.author in queue_channel.keys():
                if not user_dictionary[ctx.author].in_match:
                    if role == 'f' or role == 's' or role == 'd' or role == 'fill' or role == 'dps' or role == 'support':
                        if role == 'f' or role == 'fill':
                            queue_channel[ctx.author] = 'Fill'
                        if role == 's' or role == 'support':
                            queue_channel[ctx.author] = 'Support'
                        if role == 'd' or role == 'dps':
                            queue_channel[ctx.author] = 'DPS'
                        clearQueueTableData()
                        updateQueueTableData()
                        updateQueueEmbed()
                        await queue_table_message.edit(embed=queue_embed)
                        if len(queue_channel) == 6:
                            createMatch()
                            clearQueueTableData()
                            updateQueueEmbed()
                            await queue_table_message.edit(embed=queue_embed)
                            channel = await match_dictionary[match_counter].captain2.create_dm()
                            await channel.send(f"You are Captain 2. You will draft first. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                                               f"```1 - {match_dictionary[match_counter].draft_pool[0].display_name}\n"
                                               f"2 - {match_dictionary[match_counter].draft_pool[1].display_name}\n"
                                               f"3 - {match_dictionary[match_counter].draft_pool[2].display_name}\n"
                                               f"4 - {match_dictionary[match_counter].draft_pool[3].display_name}```\n")
                            channel = await match_dictionary[match_counter].captain1.create_dm()
                            await channel.send("You are Captain 1. You will draft second.")
                            for player in match_dictionary[match_counter].draft_pool:
                                channel = await player.create_dm()
                                await channel.send(f"You are not a captain. `{match_dictionary[match_counter].captain1.display_name}` and `{match_dictionary[match_counter].captain2.display_name}` are the captains.")
                    else:
                        await channel.send(f"`{role}` is not recognized as a valid role. Please enter queue with `!queue join <f/d/s/>`")
                else:
                    await channel.send("You are still in a match. Report your match in the match channel with `!mr <w/l>`")
            else:
                await channel.send("You are already in queue.")
        elif action == 'leave':
            if ctx.author in queue_channel.keys():
                del queue_channel[ctx.author]
                clearQueueTableData()
                updateQueueTableData()
                updateQueueEmbed()
                await queue_table_message.edit(embed=queue_embed)
            else:
                await channel.send("You are not in queue.")
        elif action == 'purge':
            if not ctx.author in purge_voters:
                purge_voters.append(ctx.author)
                if len(purge_voters) < REQUIRED_VOTERS:
                    await channel.send(f"You have voted to purge the queue. `{REQUIRED_VOTERS-len(purge_voters)}` more people must vote to purge the queue.")
                else:
                    purge_voters = []
                    for key in queue_channel:
                        channel = await key.create_dm()
                        await channel.send("The queue has been purged.")
                    queue_channel = []
                    clearQueueTableData()
                    updateQueueTableData()
                    updateQueueEmbed()
                    await queue_table_message.edit(embed=queue_embed)
            else:
                await channel.send(f"You have already voted to purge the queue. `{REQUIRED_VOTERS-len(purge_voters)}` more people must vote to purge the queue.")
        else:
            await channel.send(f"`{action}` is not a recognized command.")

    else:
        await channel.send("You have not yet registered. Please register using the `!register` command in misc-command channel.")


@client.command()
async def info(ctx):
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    sortRankings()

    channel = await ctx.author.create_dm()

    if ctx.author in user_dictionary:
        await channel.send(f"```\n{ctx.author.display_name}"
                           f"\nRating: {user_dictionary[ctx.author].display_rating}"
                           f"\nRecord: {user_dictionary[ctx.author].wins}-{user_dictionary[ctx.author].losses}"
                           f"\nRanking: {ranking_names.index(ctx.author)+1}/{len(ranking_names)}```")
    else:
        await channel.send("You have not yet registered. Please register using the `!register` command.")


@client.command()
async def draft(ctx, arg):
    global match_embed
    global user_dictionary
    global match_dictionary
    if ctx.guild == None:
        if user_dictionary[ctx.author].is_captain2 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 4:    #checks if command user is captain 2 and has 4 players in their draft pool
            match_dictionary[user_dictionary[ctx.author].last_match_id].team2.append(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))   #removes chosen player from draft pool and adds them to team 2
            await ctx.channel.send(f"You have chosen `{match_dictionary[user_dictionary[ctx.author].last_match_id].team2[1].display_name}`. Waiting for other captain to draft.")
            channel = await match_dictionary[user_dictionary[ctx.author].last_match_id].captain1.create_dm()
            await channel.send(
                f"It is your turn to draft. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                f"```1 - {match_dictionary[match_counter].draft_pool[0].display_name}\n"
                f"2 - {match_dictionary[match_counter].draft_pool[1].display_name}\n"
                f"3 - {match_dictionary[match_counter].draft_pool[2].display_name}```\n")
        elif user_dictionary[ctx.author].is_captain1 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 4:
            await ctx.channel.send("It is not your turn to pick.")
        elif user_dictionary[ctx.author].is_captain1 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 3:
            match_dictionary[user_dictionary[ctx.author].last_match_id].team1.append(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))   #removes chosen player from draft pool and adds them to team 1
            channel = await match_dictionary[user_dictionary[ctx.author].last_match_id].captain2.create_dm()
            await channel.send(
                f"It is your turn to draft. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                f"```1 - {match_dictionary[match_counter].draft_pool[0].display_name}\n"
                f"2 - {match_dictionary[match_counter].draft_pool[1].display_name}```\n")
            channel = await match_dictionary[user_dictionary[ctx.author].last_match_id].captain1.create_dm()
            await channel.send(f"You have chosen `{match_dictionary[user_dictionary[ctx.author].last_match_id].team1[1].display_name}`. Waiting for other captain to draft.")
        elif user_dictionary[ctx.author].is_captain2 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 3:
            await ctx.channel.send("It is not your turn to pick.")
        elif user_dictionary[ctx.author].is_captain2 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 2:
            match_dictionary[user_dictionary[ctx.author].last_match_id].team2.append(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))
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
        elif user_dictionary[ctx.author].is_captain1 and len(match_dictionary[user_dictionary[ctx.author].last_match_id].draft_pool) == 2:
            await ctx.channel.send("It is not your turn to pick.")
        else:
            await ctx.channel.send("You are not a captain.")

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
            await channel.send(f"`{arg}` is not recognized as a valid result. Please report the match with `!mr <w/l>`")

        if match_dictionary[user_dictionary[ctx.author].last_match_id].team1_win_votes == REQUIRED_VOTERS:
            closeMatch(user_dictionary[ctx.author].last_match_id, 1)
            channel = client.get_channel(MATCH_CHANNEL_ID)
            await channel.send(f"Match `#{user_dictionary[ctx.author].last_match_id}` has ended. Team 1 has won.")
            for player in match_dictionary[user_dictionary[ctx.author].last_match_id].team1:
                channel = await player.create_dm()
                await channel.send(f"Your last match has been reported as a win. Your new rating is: `{user_dictionary[player].display_rating}`")
            for player in match_dictionary[user_dictionary[ctx.author].last_match_id].team2:
                channel = await player.create_dm()
                await channel.send(f"Your last match has been reported as a loss. Your new rating is: `{user_dictionary[player].display_rating}`")
        elif match_dictionary[user_dictionary[ctx.author].last_match_id].team2_win_votes == REQUIRED_VOTERS:
            closeMatch(user_dictionary[ctx.author].last_match_id, 2)
            channel = client.get_channel(MATCH_CHANNEL_ID)
            await channel.send(f"Match `#{user_dictionary[ctx.author].last_match_id}` has ended. Team 2 has won.")
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
                       f"\n!leaderboard - bot messages you a top 10 leaderboard"
                       f"\n\nQueue Channel Commands:"
                       f"\n!queue join <f/d/s> - joins the queue as the desired role"
                       f"\n!queue leave - leaves the queue"
                       f"\n!queue purge - requires four people to empty the queue channel"
                       f"\n\nMatch Channel Commands"
                       f"\n!mr <w/l> - report your current match as a win or loss"
                       f"\n!mr d - requires 4 people in your match to drop the match```")

@client.command(aliases=['lb'])
async def leaderboard(ctx):
    global ranking_names
    global ranking_scores
    if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
        return

    sortRankings()
    channel = await ctx.author.create_dm()
    if len(rankings) > 9:
        await channel.send(f"```   Leaderboard"
                           f"\n 1) {rankings[0][0].display_name} - {rankings[0][1]}"
                           f"\n 2) {rankings[1][0].display_name} - {rankings[0][1]}"
                           f"\n 3) {rankings[2][0].display_name} - {rankings[0][1]}"
                           f"\n 4) {rankings[3][0].display_name} - {rankings[0][1]}"
                           f"\n 5) {rankings[4][0].display_name} - {rankings[0][1]}"
                           f"\n 6) {rankings[5][0].display_name} - {rankings[0][1]}"
                           f"\n 7) {rankings[6][0].display_name} - {rankings[0][1]}"
                           f"\n 8) {rankings[7][0].display_name} - {rankings[0][1]}"
                           f"\n 9) {rankings[8][0].display_name} - {rankings[0][1]}"
                           f"\n10) {rankings[9][0].display_name} - {rankings[0][1]}```")
    else:
        await channel.send("There are not enough players registered to create a leaderboard. Try again later.")
    if ranking_names.index(ctx.author) > 10:
        await channel.send(f"``` {ranking_names.index(ctx.author) + 1})) {ctx.author.display_name} - {ranking_scores[ranking_names.index(ctx.author)]}```")

client.run(TOKEN)
