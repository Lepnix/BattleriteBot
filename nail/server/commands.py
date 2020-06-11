from nail.settings.discord_config import *
from nail.settings.nail_settings import *
from nail.settings.br_settings import BUILDS


def on_ready_thunk(nailchan):
    async def on_ready():
        nailchan.updateQueueEmbed()
        channel = client.get_channel(QUEUE_CHANNEL_ID)
        await channel.purge()
        nailchan.queue_table_message = await channel.send(embed=queue_embed)
        nailchan.user_pickle_information = []

        try:
            user_pickle_in = open("user.pickle", "rb")
            nailchan.user_pickle_information = pickle.load(user_pickle_in)
            user_pickle_in.close()
        except:
            pass

        guild = client.get_guild(SERVER_ID)

        i = 0
        while i < len(nailchan.user_pickle_information):
            name = guild.get_member(nailchan.user_pickle_information[i][0])
            nailchan.createUser(name)
            nailchan.user_dictionary[name].points = nailchan.user_pickle_information[i][1]
            nailchan.user_dictionary[name].wins = nailchan.user_pickle_information[i][2]
            nailchan.user_dictionary[name].losses = nailchan.user_pickle_information[i][3]
            nailchan.user_dictionary[name].display_rating = round(nailchan.user_dictionary[name].points)
            if len(nailchan.user_pickle_information[i]) == 4:
                nailchan.user_pickle_information[i].append(0)
            elif len(nailchan.user_pickle_information[i]) == 5:
                nailchan.user_dictionary[name].strikes = nailchan.user_pickle_information[i][4]
            i += 1

        try:
            match_pickle_in = open("match.pickle", "rb")
            nailchan.match_counter = pickle.load(match_pickle_in)
            match_pickle_in.close()
        except:
            pass

        try:
            stats_pickle_in = open("stats.pickle", "rb")
            nailchan.character_stats = pickle.load(stats_pickle_in)
            stats_pickle_in.close()
        except:
            pass

        try:
            banned_champs_pickle_in = open("banned_champs.pickle", "rb")
            nailchan.banned_champs = pickle.load(banned_champs_pickle_in)
            banned_champs_pickle_in.close()
        except:
            pass

        try:
            complaint_pickle_in = open("complaints.pickle", "rb")
            nailchan.complaint_pickle_info = pickle.load(complaint_pickle_in)
            complaint_pickle_in.close()
        except:
            pass

        print('Battlerite Bot is online.')

    return on_ready


def build_thunk(nailchan):
    async def build(ctx, char):
        await ctx.send("Working on it.")

    return build


def register_thunk(nailchan):
    async def register(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return

        channel = await ctx.author.create_dm()

        if ctx.author in nailchan.user_dictionary:
            await channel.send('You are already registered.')
        else:
            createUser(ctx.author)
            nailchan.user_pickle_information = []
            for user in nailchan.user_dictionary.keys():
                nailchan.user_pickle_information.append([nailchan.user_dictionary[user].id, nailchan.user_dictionary[user].points, nailchan.user_dictionary[user].wins, nailchan.user_dictionary[user].losses, nailchan.user_dictionary[user].strikes])
            nailchan.user_pickle_out = open("user.pickle", "wb")
            pickle.dump(nailchan.user_pickle_information, nailchan.user_pickle_out)
            nailchan.user_pickle_out.close()
            await channel.send('You have been successfully registered.')

    return register


#clear channels after message is sent and processes commands
def on_message_thunk(nailchan):
    async def on_message(ctx):
        if ctx.author == client.user:
            return

        if ctx.author.id == DRAFT_BOT_ID and ctx.channel.id == MISC_COMMANDS_ID:
            results = ctx.content.split(",")
            match_id = int(results[0])
            await ctx.delete()

            if match_id in nailchan.match_dictionary.keys():
                stats_cache.append(results)
            else:
                matchPickBan(results)


        def is_not_me(m):
            return m.author != client.user

        if ctx.channel.id in BOT_CHANNELS:
            await ctx.channel.purge(check=is_not_me)

        await client.process_commands(ctx)

    return on_message


def queue_thunk(nailchan):
    async def queue(ctx, action, role=None):
        if not ctx.channel.id == QUEUE_CHANNEL_ID:
            return

        channel = await ctx.author.create_dm()
        guild = client.get_guild(SERVER_ID)
        nail_member = guild.get_role(NAIL_MEMBER_ID)
        nail_trial = guild.get_role(NAIL_TRIAL_ID)

        if (ctx.author in user_dictionary.keys()) and ((nail_member in ctx.author.roles) or (nail_trial in ctx.author.roles)) and (ctx.author.id not in nailchan.banned_players):
            if action == 'join' or action == 'j':
                if not ctx.author in (item[0] for item in nailchan.queue_channel):   #checks if author is in a list of the first element of nailchan.queue_channel
                    if not user_dictionary[ctx.author].in_match:
                        if role == 'f' or role == 's' or role == 'd' or role == 'fill' or role == 'dps' or role == 'support':
                            if role == 'f' or role == 'fill':
                                nailchan.queue_channel.append([ctx.author, 'Fill'])
                            if role == 's' or role == 'support':
                                nailchan.queue_channel.append([ctx.author, 'Support'])
                            if role == 'd' or role == 'dps':
                                nailchan.queue_channel.append([ctx.author, 'DPS'])
                            nailchan.updateQueueTableData()
                            nailchan.updateQueueEmbed()
                            await nailchan.queue_table_message.edit(embed=nailchan.queue_embed)
                            role_list = [item[1] for item in nailchan.queue_channel]
                            if (len(nailchan.queue_channel) >= 6) and ((role_list.count('Fill') + role_list.count('DPS')) >= 4):
                                nailchan.createMatch()
                                nailchan.updateQueueTableData()
                                nailchan.updateQueueEmbed()
                                await nailchan.queue_table_message.edit(embed=nailchan.queue_embed)
                                channel = await nailchan.match_dictionary[nailchan.match_counter].captain1.create_dm()
                                await channel.send(f"You are Captain 1. You will draft first. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                                                   f"```1 - {nailchan.match_dictionary[nailchan.match_counter].draft_pool[0].name} - {nailchan.match_dictionary[nailchan.match_counter].players[nailchan.match_dictionary[nailchan.match_counter].draft_pool[0]]}\n"
                                                   f"2 - {nailchan.match_dictionary[nailchan.match_counter].draft_pool[1].name} - {nailchan.match_dictionary[nailchan.match_counter].players[nailchan.match_dictionary[nailchan.match_counter].draft_pool[1]]}\n"
                                                   f"3 - {nailchan.match_dictionary[nailchan.match_counter].draft_pool[2].name} - {nailchan.match_dictionary[nailchan.match_counter].players[nailchan.match_dictionary[nailchan.match_counter].draft_pool[2]]}\n"
                                                   f"4 - {nailchan.match_dictionary[nailchan.match_counter].draft_pool[3].name} - {nailchan.match_dictionary[nailchan.match_counter].players[nailchan.match_dictionary[nailchan.match_counter].draft_pool[3]]}\n\n"
                                                   f"Team 1\n"
                                                   f"{nailchan.match_dictionary[nailchan.match_counter].team1[0].name} - {nailchan.match_dictionary[nailchan.match_counter].players[nailchan.match_dictionary[nailchan.match_counter].team1[0]]}\n\n"
                                                   f"Team 2\n"
                                                   f"{nailchan.match_dictionary[nailchan.match_counter].team2[0].name} - {nailchan.match_dictionary[nailchan.match_counter].players[nailchan.match_dictionary[nailchan.match_counter].team2[0]]}```\n")
                                channel = await nailchan.match_dictionary[nailchan.match_counter].captain2.create_dm()
                                await channel.send("You are Captain 2. You will draft second.")
                                for player in nailchan.match_dictionary[nailchan.match_counter].draft_pool:
                                    channel = await player.create_dm()
                                    await channel.send(f"You are not a captain. `{nailchan.match_dictionary[nailchan.match_counter].captain1.name}` and `{nailchan.match_dictionary[nailchan.match_counter].captain2.name}` are the captains.")
                        else:
                            await channel.send(f"`{role}` is not recognized as a valid role. Please enter queue with `!queue join <f/d/s/>`")
                    else:
                        await channel.send("You are still in a match. Report your match in the match channel with `!mr <w/l>`")
                else:
                    await channel.send("You are already in queue.")
            elif action == 'leave' or action == 'l':
                if ctx.author in (item[0] for item in nailchan.queue_channel):
                    for player in nailchan.queue_channel:
                        if player[0] == ctx.author:
                            nailchan.queue_channel.remove(player)
                    nailchan.updateQueueTableData()
                    nailchan.updateQueueEmbed()
                    await nailchan.queue_table_message.edit(embed=nailchan.queue_embed)
                else:
                    await channel.send("You are not in queue.")
            elif action == 'purge' or action == 'p':
                if not ctx.author in nailchan.purge_voters:
                    nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)
                    if nail_control in ctx.author.roles:
                        nailchan.purge_voters.extend([ctx.author, ctx.author, ctx.author, ctx.author])
                    nailchan.purge_voters.append(ctx.author)
                    if len(nailchan.purge_voters) < REQUIRED_VOTERS:
                        await channel.send(f"You have voted to purge the queue. `{REQUIRED_VOTERS-len(nailchan.purge_voters)}` more people must vote to purge the queue.")
                    else:
                        nailchan.purge_voters.clear()
                        for player in nailchan.queue_channel:
                            channel = await player[0].create_dm()
                            await channel.send("The queue has been purged.")
                        nailchan.queue_channel.clear()
                        nailchan.updateQueueTableData()
                        nailchan.updateQueueEmbed()
                        await nailchan.queue_table_message.edit(embed=nailchan.queue_embed)
                else:
                    await channel.send(f"You have already voted to purge the queue. `{REQUIRED_VOTERS-len(nailchan.purge_voters)}` more people must vote to purge the queue.")
            else:
                await channel.send(f"`{action}` is not a recognized command.")

        elif not ((nail_member in ctx.author.roles) or (nail_trial in ctx.author.roles)):
            await channel.send("You currently do not have a NAIL role. Talk to an administrator to receive the NAIL Trial Member role.")

        elif ctx.author.id in nailchan.banned_players:
            await channel.send("You are currently banned from NAIL.")

        else:
            await channel.send("You have not yet registered. Please register using the `!register` command in misc-command channel.")

    return queue


def info_thunk(nailchan):
    async def info(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return

        nailchan.sortRankings()

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

    return info


def draft_thunk(nailchan):
    async def draft(ctx, arg):
        if ctx.guild == None:
            if nailchan.user_dictionary[ctx.author].is_captain1 and len(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool) == 4:    #checks if command user is captain 1 and has 4 players in their draft pool
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1.append(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))   #removes chosen player from draft pool and adds them to team 1
                await ctx.channel.send(f"You have chosen `{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[1].name}`. Waiting for other captain to draft.")
                channel = await nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain2.create_dm()
                await channel.send(
                    f"It is your turn to draft. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                    f"```1 - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[0].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[0]]}\n"
                    f"2 - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[1].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[1]]}\n"
                    f"3 - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[2].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[2]]}\n\n"
                    f"Team 1\n"
                    f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[0].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[0]]}\n"
                    f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[1].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[1]]}\n\n"
                    f"Team 2\n"
                    f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[0].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[0]]}```\n"
                )
            elif nailchan.user_dictionary[ctx.author].is_captain2 and len(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool) == 4:
                await ctx.channel.send("It is not your turn to pick.")
            elif nailchan.user_dictionary[ctx.author].is_captain2 and len(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool) == 3:
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2.append(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))   #removes chosen player from draft pool and adds them to team 1
                channel = await nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain2.create_dm()
                await channel.send(
                    f"You have chosen `{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[1].name}`."
                    f" It is your turn to draft, again. To draft a player, look at the number next to the player's name and type `!draft <#>`\n"
                    f"```1 - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[0].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[0]]}\n"
                    f"2 - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[1].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool[1]]}\n\n"
                    f"Team 1\n"
                    f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[0].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[0]]}\n"
                    f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[1].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[1]]}\n\n"
                    f"Team 2\n"
                    f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[0].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[0]]}\n"
                    f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[1].name} - {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].players[nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[1]]}```\n"
                )
            elif nailchan.user_dictionary[ctx.author].is_captain1 and len(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool) == 3:
                await ctx.channel.send("It is not your turn to pick.")
            elif nailchan.user_dictionary[ctx.author].is_captain2 and len(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool) == 2:
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2.append(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool.pop(int(arg) - 1))
                channel = await nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain2.create_dm()
                await channel.send(f"You have chosen `{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[2].name}`.")
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1.append(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool.pop(0))
                channel = client.get_channel(MATCH_CHANNEL_ID)
                await channel.send(f"A new match has been created.\n {nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[0].mention} "
                                   f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[1].mention} "
                                   f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1[2].mention} "
                                   f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[0].mention} "
                                   f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[1].mention} "
                                   f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2[2].mention}"
                                   f"\n")
                nailchan.createMatchEmbed(nailchan.user_dictionary[ctx.author].last_match_id)
                await channel.send(embed=nailchan.match_embed)
                await channel.send("Please report the match with `!mr <w/l>`")
                channel = await nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain1.create_dm()
                await channel.send(embed=nailchan.match_embed)
                channel = await nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain2.create_dm()
                await channel.send(embed=nailchan.match_embed)
                channel = client.get_channel(DRAFT_CHANNEL_ID)
                if len(banned_champs) == 3:
                    await channel.send(f"{nailchan.user_dictionary[ctx.author].last_match_id},{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain1.id},"
                                       f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain2.id},{banned_champs[0]},{banned_champs[1]},{banned_champs[2]}")
                else:
                    await channel.send(f"{nailchan.user_dictionary[ctx.author].last_match_id},{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain1.id},"
                                       f"{nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].captain2.id}")
            elif nailchan.user_dictionary[ctx.author].is_captain1 and len(nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].draft_pool) == 2:
                await ctx.channel.send("It is not your turn to pick.")
            else:
                await ctx.channel.send("You are not a captain or it is not your turn to pick.")

    return draft


def mr_thunk(nailchan):
    async def mr(ctx, arg):
        if not ctx.channel.id == MATCH_CHANNEL_ID:
            return

        channel = await ctx.author.create_dm()

        if not nailchan.user_dictionary[ctx.author].in_match:
            await channel.send("You are not currently in a match.")
        else:
            if (arg == 'w' or arg == 'win') and ctx.author in nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1 and not nailchan.user_dictionary[ctx.author].reported:
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1_win_votes += 1
                nailchan.user_dictionary[ctx.author].reported = True
                await channel.send("You have reported a win for team 1.")
            elif (arg == 'w' or arg == 'win') and ctx.author in nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2 and not nailchan.user_dictionary[ctx.author].reported:
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2_win_votes += 1
                nailchan.user_dictionary[ctx.author].reported = True
                await channel.send("You have reported a win for team 2.")
            elif (arg == 'l' or arg == 'loss') and ctx.author in nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1 and not nailchan.user_dictionary[ctx.author].reported:
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2_win_votes += 1
                nailchan.user_dictionary[ctx.author].reported = True
                await channel.send("You have reported a loss for team 1.")
            elif (arg == 'l' or arg == 'loss') and ctx.author in nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2 and not nailchan.user_dictionary[ctx.author].reported:
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1_win_votes += 1
                nailchan.user_dictionary[ctx.author].reported = True
                await channel.send("You have reported a loss for team 2.")
            elif (arg == 'd' or arg == 'drop') and not nailchan.user_dictionary[ctx.author].dropped:
                nailchan.user_dictionary[ctx.author].dropped = True
                nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].drop_votes += 1
                await channel.send(f"You have voted to drop the match. `{REQUIRED_VOTERS - nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].drop_votes}` more people must vote in order to drop the match.")
            elif (arg == 'd' or arg == 'drop') and nailchan.user_dictionary[ctx.author].dropped:
                await channel.send(f"You have already voted to drop the match. `{REQUIRED_VOTERS - nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].drop_votes}` more people must vote in order to drop the match.")
            else:
                await channel.send(f"You have already reported or have entered an invalid result. Please report the match with `!mr <w/l>`")

            if nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1_win_votes == REQUIRED_VOTERS and not nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].closed:
                closeMatch(nailchan.user_dictionary[ctx.author].last_match_id, 1)
                id_list = []
                if len(stats_cache) > 0:
                    id_list = [int(item[0]) for item in stats_cache]
                if nailchan.user_dictionary[ctx.author].last_match_id in id_list:
                    nailchan.matchAnalysis(stats_cache[id_list.index(nailchan.user_dictionary[ctx.author].last_match_id)])
                    del stats_cache[id_list.index(nailchan.user_dictionary[ctx.author].last_match_id)]
                channel = client.get_channel(MATCH_CHANNEL_ID)
                await channel.send(f"Match `#{nailchan.user_dictionary[ctx.author].last_match_id}` has ended. Team 1 has won.")
                for player in nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1:
                    channel = await player.create_dm()
                    await channel.send(f"Your last match has been reported as a win. Your new rating is: `{nailchan.user_dictionary[player].display_rating}`")
                for player in nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2:
                    channel = await player.create_dm()
                    await channel.send(f"Your last match has been reported as a loss. Your new rating is: `{nailchan.user_dictionary[player].display_rating}`")
            elif nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2_win_votes == REQUIRED_VOTERS and not nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].closed:
                nailchan.closeMatch(nailchan.user_dictionary[ctx.author].last_match_id, 2)
                id_list = []
                if len(stats_cache) > 0:
                    id_list = [int(item[0]) for item in stats_cache]
                if nailchan.user_dictionary[ctx.author].last_match_id in id_list:
                    nailchan.matchAnalysis(stats_cache[id_list.index(nailchan.user_dictionary[ctx.author].last_match_id)])
                    del stats_cache[id_list.index(nailchan.user_dictionary[ctx.author].last_match_id)]
                channel = client.get_channel(MATCH_CHANNEL_ID)
                await channel.send(f"Match `#{nailchan.user_dictionary[ctx.author].last_match_id}` has ended. Team 2 has won.")
                for player in nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team2:
                    channel = await player.create_dm()
                    await channel.send(f"Your last match has been reported as a win. Your new rating is: `{nailchan.user_dictionary[player].display_rating}`")
                for player in nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].team1:
                    channel = await player.create_dm()
                    await channel.send(f"Your last match has been reported as a loss. Your new rating is: `{nailchan.user_dictionary[player].display_rating}`")
            elif nailchan.match_dictionary[nailchan.user_dictionary[ctx.author].last_match_id].drop_votes == REQUIRED_VOTERS:
                nailchan.closeMatch(nailchan.user_dictionary[ctx.author].last_match_id, 3)
                channel = client.get_channel(MATCH_CHANNEL_ID)
                await channel.send(f"Match `#{nailchan.user_dictionary[ctx.author].last_match_id}` has been dropped.")

    return mr


async def _help(ctx):
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


def leaderboard_thunk(nailchan):
    async def leaderboard(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return

        nailchan.sortRankings()
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

            lb_field_value_2 = f"{nailchan.ranking_names[0].name}"\
                             f"\n{nailchan.ranking_names[1].name}"\
                             f"\n{nailchan.ranking_names[2].name}"\
                             f"\n{nailchan.ranking_names[3].name}"\
                             f"\n{nailchan.ranking_names[4].name}"\
                             f"\n{nailchan.ranking_names[5].name}"\
                             f"\n{nailchan.ranking_names[6].name}"\
                             f"\n{nailchan.ranking_names[7].name}"\
                             f"\n{nailchan.ranking_names[8].name}"\
                             f"\n{nailchan.ranking_names[9].name}"

            lb_field_value_3 = f"{nailchan.ranking_scores[0]}" \
                               f"\n{nailchan.ranking_scores[1]}" \
                               f"\n{nailchan.ranking_scores[2]}" \
                               f"\n{nailchan.ranking_scores[3]}" \
                               f"\n{nailchan.ranking_scores[4]}" \
                               f"\n{nailchan.ranking_scores[5]}" \
                               f"\n{nailchan.ranking_scores[6]}" \
                               f"\n{nailchan.ranking_scores[7]}" \
                               f"\n{nailchan.ranking_scores[8]}" \
                               f"\n{nailchan.ranking_scores[9]}"

            lb_embed.add_field(name="\u200b", value=lb_field_value_1, inline=True)
            lb_embed.add_field(name="\u200b", value=lb_field_value_2, inline=True)
            lb_embed.add_field(name="\u200b", value=lb_field_value_3, inline=True)
            lb_embed.set_author(name="Leaderboard")
            await channel.send(embed=lb_embed)
        else:
            await channel.send("There are not enough players who have placed to create a leaderboard. Try again later.")
        if ctx.author in nailchan.ranking_names:
            if nailchan.ranking_names.index(ctx.author) > 9:
                embed = discord.Embed(
                    title=None,
                    description=None,
                    color=discord.Color.magenta()
                )
                embed.add_field(name="\u200b", value=f"{nailchan.ranking_names.index(ctx.author) + 1})", inline=True)
                embed.add_field(name="\u200b", value=f"{ctx.author.name}", inline=True)
                embed.add_field(name="\u200b", value=f"{nailchan.ranking_scores[nailchan.ranking_names.index(ctx.author)]}", inline=True)
                await channel.send(embed=embed)

    return leaderboard


def stats_thunk(nailchan):
    async def stats(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return

        for champ in nailchan.character_stats.keys():
            if champ != 'stat counter':
                if nailchan.character_stats[champ][2] + nailchan.character_stats[champ][3] > 0:
                    nailchan.character_stats[champ][4] = nailchan.character_stats[champ][2] / (nailchan.character_stats[champ][2] + nailchan.character_stats[champ][3])

        channel = await ctx.author.create_dm()

        stats_embed = discord.Embed(
        title=None,
        description=None,
        color=discord.Color.magenta()
        )
        character_field = "Bakko\nCroak\nFreya\nJamila\nRaigon\nRook\nRuh Kaan\nShifu\nThorn\nAlysia\nAshka\nDestiny\n" \
                          "Ezmo\nIva\nJade\nJumong\nShen Rao\nTaya\nVaresh\nBlossom\nLucie\nOldur\nPearl\nPestilus\n" \
                          "Poloma\nSirius\nUlric\nZander"

        win_percent_field = f"{round(nailchan.character_stats['bakko'][4]*100)}\n"\
            f"{round(nailchan.character_stats['croak'][4]*100)}\n"\
            f"{round(nailchan.character_stats['freya'][4]*100)}\n"\
            f"{round(nailchan.character_stats['jamila'][4]*100)}\n"\
            f"{round(nailchan.character_stats['raigon'][4]*100)}\n"\
            f"{round(nailchan.character_stats['rook'][4]*100)}\n"\
            f"{round(nailchan.character_stats['ruh kaan'][4]*100)}\n"\
            f"{round(nailchan.character_stats['shifu'][4]*100)}\n"\
            f"{round(nailchan.character_stats['thorn'][4]*100)}\n"\
            f"{round(nailchan.character_stats['alysia'][4]*100)}\n"\
            f"{round(nailchan.character_stats['ashka'][4]*100)}\n"\
            f"{round(nailchan.character_stats['destiny'][4]*100)}\n"\
            f"{round(nailchan.character_stats['ezmo'][4]*100)}\n"\
            f"{round(nailchan.character_stats['iva'][4]*100)}\n"\
            f"{round(nailchan.character_stats['jade'][4]*100)}\n"\
            f"{round(nailchan.character_stats['jumong'][4]*100)}\n"\
            f"{round(nailchan.character_stats['shen rao'][4]*100)}\n"\
            f"{round(nailchan.character_stats['taya'][4]*100)}\n"\
            f"{round(nailchan.character_stats['varesh'][4]*100)}\n"\
            f"{round(nailchan.character_stats['blossom'][4]*100)}\n"\
            f"{round(nailchan.character_stats['lucie'][4]*100)}\n"\
            f"{round(nailchan.character_stats['oldur'][4]*100)}\n"\
            f"{round(nailchan.character_stats['pearl'][4]*100)}\n"\
            f"{round(nailchan.character_stats['pestilus'][4]*100)}\n"\
            f"{round(nailchan.character_stats['poloma'][4]*100)}\n"\
            f"{round(nailchan.character_stats['sirius'][4]*100)}\n"\
            f"{round(nailchan.character_stats['ulric'][4]*100)}\n"\
            f"{round(nailchan.character_stats['zander'][4]*100)}\n"

        pick_ban_rate_field = f"{round(100*nailchan.character_stats['bakko'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['bakko'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['croak'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['croak'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['freya'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['freya'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['jamila'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['jamila'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['raigon'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['raigon'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['rook'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['rook'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['ruh kaan'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['ruh kaan'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['shifu'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['shifu'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['thorn'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['thorn'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['alysia'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['alysia'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['ashka'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['ashka'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['destiny'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['destiny'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['ezmo'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['ezmo'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['iva'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['iva'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['jade'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['jade'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['jumong'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['jumong'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['shen rao'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['shen rao'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['taya'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['taya'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['varesh'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['varesh'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['blossom'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['blossom'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['lucie'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['lucie'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['oldur'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['oldur'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['pearl'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['pearl'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['pestilus'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['pestilus'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['poloma'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['poloma'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['sirius'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['sirius'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['ulric'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['ulric'][0] / nailchan.character_stats['stat counter'])}\n"\
            f"{round(100*nailchan.character_stats['zander'][1] / nailchan.character_stats['stat counter'])}/{round(100*nailchan.character_stats['zander'][0] / nailchan.character_stats['stat counter'])}\n"

        stats_embed.add_field(name='Champions', value=character_field, inline=True)
        stats_embed.add_field(name='Winrate %', value=win_percent_field, inline=True)
        stats_embed.add_field(name='Pick/Ban %', value=pick_ban_rate_field, inline=True)
        stats_embed.set_author(name='Champion Statistics')

        await channel.send(embed=stats_embed)

    return stats


def weeklyban_thunk(nailchan):
    async def weeklyban(ctx, *, champs):
        if ctx.channel.id != MISC_COMMANDS_ID:
            return

        nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

        if nail_control in ctx.author.roles:
            if champs == "None":
                nailchan.banned_champs.clear()
            else:
                nailchan.banned_champs = champs.split(",")
            banned_champs_pickle_out = open("nailchan.banned_champs.pickle", "wb")
            pickle.dump(nailchan.banned_champs, banned_champs_pickle_out)
            banned_champs_pickle_out.close()

    return weeklyban


def bans_thunk(nailchan):
    async def bans(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return

        channel = await ctx.author.create_dm()
        if len(nailchan.banned_champs) == 0:
            await channel.send("There currently are no champions banned from NAIL.")
        else:
            await channel.send(f"The current champions banned from NAIL are: `{nailchan.banned_champs[0]}`, `{nailchan.banned_champs[1]}`, and `{nailchan.banned_champs[2]}`")

    return bans


def winrates_thunk(nailchan):
    async def winrates(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID:
            return

        nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

        if nail_control not in ctx.author.roles:
            return

        channel = await ctx.author.create_dm()

        wr_message = ""

        for player in nailchan.user_dictionary:
            if nailchan.user_dictionary[player].losses > 0:
                if nailchan.user_dictionary[player].wins / (nailchan.user_dictionary[player].losses + nailchan.user_dictionary[player].wins) < .4:
                    wr_message += f"{player.name}  {nailchan.user_dictionary[player].wins}-{nailchan.user_dictionary[player].losses}\n"
        await channel.send(f"```\n{wr_message}```")

    return winrates


def ban_thunk(nailchan):
    async def ban(ctx, arg):
        if ctx.channel.id != MISC_COMMANDS_ID:
            return

        nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

        if nail_control not in ctx.author.roles:
            return

        channel = await ctx.author.create_dm()
        if int(arg) in nailchan.banned_players:
            await channel.send("That player is already banned.")
        else:
            nailchan.banned_players.append(int(arg))

    return ban


def unban_thunk(nailchan):
    async def unban(ctx, arg):
        if ctx.channel.id != MISC_COMMANDS_ID:
            return

        nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

        if nail_control not in ctx.author.roles:
            return

        channel = await ctx.author.create_dm()
        if int(arg) in nailchan.banned_players:
            nailchan.banned_players.remove(int(arg))
        else:
            await channel.send("That player is not banned.")

    return unban


def seasonstart_thunk(nailchan):
    async def seasonstart(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID:
            return

        nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

        if nail_control not in ctx.author.roles:
            return

        channel = await ctx.author.create_dm()
        for player in nailchan.user_pickle_information:
            player[1] = 1000
            player[2] = 0
            player[3] = 0
            nailchan.user_dictionary[client.get_guild(SERVER_ID).get_member(player[0])].points = 1000
            nailchan.user_dictionary[client.get_guild(SERVER_ID).get_member(player[0])].display_rating = 1000
            nailchan.user_dictionary[client.get_guild(SERVER_ID).get_member(player[0])].wins = 0
            nailchan.user_dictionary[client.get_guild(SERVER_ID).get_member(player[0])].losses = 0
        user_pickle_out = open("user.pickle", "wb")
        pickle.dump(nailchan.user_pickle_information, user_pickle_out)
        user_pickle_out.close()
        await channel.send("All player stats have been reset.")

    return seasonstart


def strike_thunk(nailchan):
    async def strike(ctx, arg):
        if ctx.channel.id != MISC_COMMANDS_ID:
            return

        nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

        if nail_control not in ctx.author.roles:
            return

        if client.get_guild(SERVER_ID).get_member(int(arg)) in nailchan.user_dictionary.keys():
            nailchan.user_dictionary[client.get_guild(SERVER_ID).get_member(int(arg))].strikes += 1
            for i in nailchan.user_pickle_information:
                if i[0] == int(arg):
                    i[4] == nailchan.user_dictionary[client.get_guild(SERVER_ID).get_member(int(arg))].strikes
            user_pickle_out = open("user.pickle", "wb")
            pickle.dump(nailchan.user_pickle_information, user_pickle_out)
            user_pickle_out.close()

    return nailchan


def strikes_thunk(nailchan):
    async def strikes(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return

        channel = await ctx.author.create_dm()

        if ctx.author in nailchan.user_dictionary:
            await channel.send(f"Number of strikes: `{nailchan.user_dictionary[ctx.author].strikes}`")
        else:
            await channel.send(f"You are not registered.")

    return strikes


def complain_thunk(nailchan):
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
            if ctx.author.id not in nailchan.complaint_pickle_info.keys():
                nailchan.complaint_pickle_info[ctx.author.id] = []
            if target_player.id in nailchan.complaint_pickle_info[ctx.author.id]:
                channel = await ctx.author.create_dm()
                await channel.send(f"You have already filed a complaint about this player. You may only file one complaint for each player.")
            else:
                nailchan.complaint_pickle_info[ctx.author.id].append(target_player.id)
                complaint_pickle_out = open("complaints.pickle", "wb")
                pickle.dump(nailchan.complaint_pickle_info, complaint_pickle_out)
                complaint_pickle_out.close()
                channel = await ctx.author.create_dm()
                await channel.send(f"You have successfully submitted a complaint.")
                channel = await client.get_user(166670770234195978).create_dm()
                complaint = await channel.send(f"A new complaint has been filed for `{target_player.name}`:\n```\n{arg}```")
                nailchan.complaints[complaint.id] = ctx.author.name

    return complain


def uncomplain_thunk(nailchan):
    async def uncomplain(ctx, target):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return

        target_player = client.get_guild(SERVER_ID).get_member_named(target)
        if ctx.author.id not in nailchan.complaint_pickle_info.keys():
            channel = await ctx.author.create_dm()
            await channel.send("You have not filed any complaints.")
        elif target_player.id not in nailchan.complaint_pickle_info[ctx.author.id]:
            channel = await ctx.author.create_dm()
            await channel.send(f"You have not filed any complaints for: `{target_player.name}`")
        else:
            nailchan.complaint_pickle_info[ctx.author.id].remove(target_player.id)
            complaint_pickle_out = open("complaints.pickle", "wb")
            pickle.dump(nailchan.complaint_pickle_info, complaint_pickle_out)
            complaint_pickle_out.close()
            channel = await ctx.author.create_dm()
            await channel.send(f"You have revoked a complaint for: `{target_player.name}`")
            channel = await client.get_user(166670770234195978).create_dm()
            await channel.send(f"A complaint has been revoked for: `{target_player.name}`")

    return uncomplain


def sender_thunk(nailchan):
    async def sender(ctx, arg):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return
        if ctx.author.id != 166670770234195978:
            return

        channel = await ctx.author.create_dm()
        await channel.send(f"The sender of complaint ID `{arg}` is `{nailchan.complaints[int(arg)]}`.")

    return sender


def resetstrikes_thunk(nailchan):
    async def resetstrikes(ctx, arg):
        if ctx.channel.id != MISC_COMMANDS_ID:
            return

        nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

        if nail_control not in ctx.author.roles:
            return

        if client.get_guild(SERVER_ID).get_member(int(arg)) in nailchan.user_dictionary.keys():
            nailchan.user_dictionary[client.get_guild(SERVER_ID).get_member(int(arg))].strikes = 0
            for i in nailchan.user_pickle_information:
                if i[0] == int(arg):
                    i[4] = 0
            user_pickle_out = open("user.pickle", "wb")
            pickle.dump(nailchan.user_pickle_information, user_pickle_out)
            user_pickle_out.close()

    return resetstrikes


def resetpb_thunk(nailchan):
    async def resetpb(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID:
            return

        nail_control = client.get_guild(SERVER_ID).get_role(NAIL_CONTROL_ID)

        if nail_control not in ctx.author.roles:
            return

        for i in nailchan.character_stats.keys():
            if i != 'stat counter':
                nailchan.character_stats[i][0] = 0
                nailchan.character_stats[i][1] = 0
            else:
                nailchan.character_stats[i] = 0

        stats_pickle_out = open("stats.pickle", "wb")
        pickle.dump(nailchan.character_stats, stats_pickle_out)
        stats_pickle_out.close()

    return resetpb


def complaints_thunk(nailchan):
    async def complaints(ctx):
        if ctx.channel.id != MISC_COMMANDS_ID and ctx.guild != None:
            return

        complaint_count = 0
        for player in nailchan.complaint_pickle_info.keys():
            if ctx.author.id in nailchan.complaint_pickle_info[player]:
                complaint_count += 1

        channel = await ctx.author.create_dm()
        await channel.send(f"Current # of complaints: `{complaint_count}`")

    return complaints
