from discord.ext import commands

from nail.settings.discord_config import *

from nail.server.nailchan import NailChan
from nail.server.commands import on_ready_thunk, build_thunk, register_thunk,\
    on_message_thunk, queue_thunk, info_thunk, draft_thunk, mr_thunk, _help,\
    leaderboard_thunk, stats_thunk, weeklyban_thunk, bans_thunk,\
    winrates_thunk, ban_thunk, unban_thunk, seasonstart_thunk, strike_thunk,\
    strikes_thunk, complain_thunk, uncomplain_thunk, resetstrikes_thunk,\
    resetpb_thunk, complaints_thunk


if __name__ == '__main__':
    nailchan = NailChan()


    client = commands.Bot(command_prefix='!')
    client.remove_command('help')


    client.event(on_ready_thunk(nailchan))
    client.event(on_message_thunk(nailchan))


    client.command()(_help)

    client.command()(build_thunk(nailchan))
    client.command()(register_thunk(nailchan))
    client.command(aliases=['q'])(queue_thunk(nailchan))
    client.command()(info_thunk(nailchan))
    client.command()(draft_thunk(nailchan))
    client.command()(mr_thunk(nailchan))
    client.command(aliases=['lb'])(leaderboard_thunk(nailchan))
    client.command()(stats_thunk(nailchan))
    client.command(aliases=['wb'])(weeklyban_thunk(nailchan))
    client.command()(bans_thunk(nailchan))
    client.command(aliases=['wr'])(winrates_thunk(nailchan))
    client.command()(ban_thunk(nailchan))
    client.command()(unban_thunk(nailchan))
    client.command(aliases=["ss"])(seasonstart_thunk(nailchan))
    client.command()(strike_thunk(nailchan))
    client.command()(strikes_thunk(nailchan))
    client.command()(uncomplain_thunk(nailchan))
    client.command()(resetstrikes_thunk(nailchan))
    client.command()(resetpb_thunk(nailchan))
    client.command()(complaints_thunk(nailchan))


    client.run(TOKEN)
