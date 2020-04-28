import discord
from discord.ext import commands

client = commands.Bot(command_prefix = '!')

builds = {'freya': 'r2, y2, gS, yE, gE', 'ashka': 'r2, y2, rQ, rR, rP', 'croak': 'g2, b2, yQ, yE, pE'}

@client.event
async def on_ready():
    print('Battlerite Bot is online.')

@client.command()
async def build(ctx, char):
    await ctx.send(builds[char.lower()])

client.run('NzA0NjYzMDQwNjgyODg1MTM0.XqgasA.IkvPir7CKKm_BMoPrfl1LfjHjf8')
