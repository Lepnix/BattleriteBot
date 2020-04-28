from discord.ext import commands
from discord import *
import operator


client = commands.Bot(command_prefix = '!')
TOKEN = 'NzA0NjYzMDQwNjgyODg1MTM0.XqgasA.IkvPir7CKKm_BMoPrfl1LfjHjf8'

BUILDS = {'freya': 'r2, y2, gS, yE, gE', 'ashka': 'r2, y2, rQ, rR, rP', 'croak': 'g2, b2, yQ, yE, pE'}
queue_channel = {}
user_dictionary = {}
STARTING_POINTS = 1500
MAP_POOL = ['Araz Night', 'Blackstone Day', 'Dragon Night', 'Market Night', 'Meriko Night']
QUEUE_CHANNEL_ID = 704660113897685022
MATCH_CHANNEL_ID = 704660569319538829
MISC_COMMANDS_ID = 704660610595553350
BOT_CHANNELS = [QUEUE_CHANNEL_ID, MATCH_CHANNEL_ID, MISC_COMMANDS_ID]
COMMANDS = ['!register']
purge_voters = []
REQUIRED_VOTERS = 4






class User:
    def __init__(self, name):
        self.name = name
        self.points = STARTING_POINTS
        self.wins = 0
        self.losses = 0


def createUser(name):
    key = name
    value = User(name)
    user_dictionary.update({key: value})

def createMatch():
    x=0

def sortRankings():
    rankings = {}
    for name in user_dictionary:
        rankings[name] = user_dictionary[name].points
    rankings = sorted(rankings.items(), key=operator.itemgetter(1), reverse=True)

@client.event
async def on_ready():
    print('Battlerite Bot is online.')

#build command
@client.command()
async def build(ctx, char):
    await ctx.send(BUILDS[char.lower()])

#register new user
@client.command()
async def register(ctx):
    if not ctx.channel.id == MISC_COMMANDS_ID:
        return

    channel = await ctx.author.create_dm()

    if ctx.author in user_dictionary:
        await channel.send('You are already registered.')
    else:
        createUser(ctx.author)
        await channel.send('You have been successfully registered.')



#clear channels after message is sent and process commands
@client.event
async def on_message(ctx):
    if ctx.author == client.user:
        return

    if not ctx.channel.id in BOT_CHANNELS:
        return

    await ctx.channel.purge()
    await client.process_commands(ctx)

@client.command()
async def queue(ctx, action, role = None):
    global purge_voters
    if not ctx.channel.id == QUEUE_CHANNEL_ID:
        return

    channel = await ctx.author.create_dm()

    if ctx.author in user_dictionary.keys():
        if action == 'join':
            if not ctx.author in queue_channel.keys():
                queue_channel[ctx.author] = role
                if len(queue_channel) == 6 :
                    createMatch()
                elif len(queue_channel) > 6:
                    queue_channel =
            else:
                await channel.send("You are already in queue.")
        elif action == 'leave':
            if ctx.author in queue_channel.keys():
                del queue_channel[ctx.author]
            else:
                await channel.send("You are not in queue.")
        elif action == 'purge':
            if not ctx.author in purge_voters:
                purge_voters.append(ctx.author)
                if len(purge_voters) < REQUIRED_VOTERS:
                    await channel.send(f"You have voted to purge the queue. {REQUIRED_VOTERS-len(purge_voters)} more people must vote to purge the queue.")
                else:
                    purge_voters = []
                    for key in queue_channel:
                        channel = await key.create_dm()
                        await channel.send("The queue has been purged.")
            else:
                await channel.send(f"You have already voted to purge the queue. {REQUIRED_VOTERS-len(purge_voters)} more people must vote to purge the queue.")
        else:
            await channel.send(f"'{action}' is not a recognized command.")

    else:
        await channel.send("You have not yet registered. Please register using the '!register' command.")

@client.command()
async def info(ctx):
    if not ctx.channel.id == MISC_COMMANDS_ID:
        return

    channel = await ctx.author.create_dm()

    if ctx.author in user_dictionary:
        await channel.send(f"Rating: {user_dictionary[ctx.author].points}\nRecord: {user_dictionary[ctx.author].wins}-{user_dictionary[ctx.author].losses}")
    else:
        await channel.send("You have not yet registered. Please register using the '!register' command.")


client.run(TOKEN)
