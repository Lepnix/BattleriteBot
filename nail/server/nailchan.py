import dill as pickle

import operator
import discord

from elo import rate_1vs1

from nail.server.dao import User, Match

from nail.settings.br_settings import CHARACTER_LIST

class NailChan:
    def __init__(self):
        self.character_stats = {
            champ: [0, 0, 0, 0, 0] for champ in CHARACTER_LIST
        }
        self.character_stats['stat counter'] = 0

        self.stats_cache = []
        self.queue_channel = []
        self.user_dictionary = {}
        self.match_dictionary = {}
        self.match_counter = 0

        self.purge_voters = []
        self.queue_table_data = [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']]
        self.queue_table_message = 0
        self.rankings = []
        self.ranking_names = []
        self.ranking_scores = []
        self.user_pickle_information = []
        self.banned_champs = []
        self.banned_players = []
        self.complaints = {}
        self.complaint_pickle_info = {}


        self.queue_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        self.queue_embed.add_field(name='Fill', value='---', inline=False)
        self.queue_embed.add_field(name='DPS', value='---', inline=False)
        self.queue_embed.add_field(name='Support', value='---', inline=False)

        self.match_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        self.field_value_1 = ''
        self.field_value_2 = ''
        self.field_value_3 = ''


    def updateQueueEmbed(self):
        updated_queue_embed = discord.Embed(
            title=None,
            description=None,
            color=discord.Color.magenta()
        )

        self.field_value_1 = ''
        self.field_value_2 = ''
        self.field_value_3 = ''

        for i in self.queue_table_data[0]:
            if i == '':
                self.field_value_1 += '---\n'
                break
            else:
                self.field_value_1 += f'{i}\n'

        for i in self.queue_table_data[1]:
            if i == '':
                self.field_value_2 += '---\n'
                break
            else:
                self.field_value_2 += f'{i}\n'

        for i in self.queue_table_data[2]:
            if i == '':
                self.field_value_3 += '---\n'
                break
            else:
                self.field_value_3 += f'{i}\n'

        updated_queue_embed.add_field(name='Fill', value=self.field_value_1, inline=False)
        updated_queue_embed.add_field(name='DPS', value=self.field_value_2, inline=False)
        updated_queue_embed.add_field(name='Support', value=self.field_value_3, inline=False)

        self.queue_embed = updated_queue_embed

    def updateQueueTableData(self):
        f = 0
        d = 0
        s = 0
        self.queue_table_data = [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']]
        for person in self.queue_channel:
            if person[1] == 'Fill':
                self.queue_table_data[0][f] = person[0].name
                f += 1
            if person[1] == 'DPS':
                self.queue_table_data[1][d] = person[0].name
                d += 1
            if person[1] == 'Support':
                self.queue_table_data[2][s] = person[0].name
                s += 1

    def createMatchEmbed(self, id):
        updated_match_embed = discord.Embed(
        title=None,
        description=None,
        color=discord.Color.magenta()
        )

        team1 = f"{self.match_dictionary[id].team1[0].name} - {self.match_dictionary[id].players[self.match_dictionary[id].team1[0]]}" \
            f"\n{self.match_dictionary[id].team1[1].name} - {self.match_dictionary[id].players[self.match_dictionary[id].team1[1]]}" \
            f"\n{self.match_dictionary[id].team1[2].name} - {self.match_dictionary[id].players[self.match_dictionary[id].team1[2]]}"
        team2 = f"{self.match_dictionary[id].team2[0].name} - {self.match_dictionary[id].players[self.match_dictionary[id].team2[0]]}" \
            f"\n{self.match_dictionary[id].team2[1].name} - {self.match_dictionary[id].players[self.match_dictionary[id].team2[1]]}" \
            f"\n{self.match_dictionary[id].team2[2].name} - {self.match_dictionary[id].players[self.match_dictionary[id].team2[2]]}"

        updated_match_embed.add_field(name='Team 1', value=team1, inline=True)
        updated_match_embed.add_field(name='Team 2', value=team2, inline=True)
        updated_match_embed.add_field(name='Map', value=self.match_dictionary[id].map, inline=False)
        updated_match_embed.set_author(name=f'Match #{id}')

        self.match_embed = updated_match_embed


    def createUser(self, name):
        self.user_dictionary[name] = User(name)


    def createMatch(self):
        self.match_counter += 1
        self.match_dictionary[self.match_counter] = Match(self)


    def sortRankings(self):
        self.rankings = []
        self.ranking_names = []
        self.ranking_scores = []

        i = 0
        for name in self.user_dictionary:
            if self.user_dictionary[name].wins + self.user_dictionary[name].losses > 9:
                self.rankings.append([name, self.user_dictionary[name].display_rating, i + 1])
                i += 1
        self.rankings = sorted(self.rankings, key=operator.itemgetter(1), reverse=True)
        k = 0
        while k < len(self.rankings):
            self.ranking_names.append(self.rankings[k][0])
            k += 1
        k = 0
        while k < len(self.rankings):
            self.ranking_scores.append(self.rankings[k][1])
            k += 1


    def closeMatch(self, _id, result):
        _sum = 0
        for player in self.match_dictionary[_id].team1:
            _sum += self.user_dictionary[player].points
            team1_avg = _sum / 3

        _sum = 0
        for player in self.match_dictionary[_id].team2:
            _sum += self.user_dictionary[player].points
            team2_avg = _sum / 3

        if result == 1:   #team 1 wins
            updated_team1_avg, updated_team2_avg = rate_1vs1(team1_avg, team2_avg)
            team1_change = (updated_team1_avg - team1_avg) * 2
            team2_change = (updated_team2_avg - team2_avg) * 2
            for player in self.match_dictionary[_id].team1:
                self.user_dictionary[player].wins += 1
                self.user_dictionary[player].points += team1_change
            for player in self.match_dictionary[_id].team2:
                self.user_dictionary[player].losses += 1
                self.user_dictionary[player].points += team2_change

        elif result == 2:   #team 2 wins
            updated_team2_avg, updated_team1_avg = rate_1vs1(team2_avg, team1_avg)
            team1_change = (updated_team1_avg - team1_avg) * 2
            team2_change = (updated_team2_avg - team2_avg) * 2
            for player in self.match_dictionary[_id].team2:
                self.user_dictionary[player].wins += 1
                self.user_dictionary[player].points += team2_change
            for player in self.match_dictionary[_id].team1:
                self.user_dictionary[player].losses += 1
                self.user_dictionary[player].points += team1_change

        for player in self.match_dictionary[_id].players.keys():
            if (self.user_dictionary[player].wins + self.user_dictionary[player].losses) <= 10:
                self.user_dictionary[player].points = (self.user_dictionary[player].wins - self.user_dictionary[player].losses) * 20 + 1000

        for player in self.match_dictionary[_id].players.keys():
            self.user_dictionary[player].in_match = False
            self.user_dictionary[player].is_captain1 = False
            self.user_dictionary[player].is_captain2 = False
            self.user_dictionary[player].reported = False
            self.user_dictionary[player].dropped = False
            self.user_dictionary[player].display_rating = round(self.user_dictionary[player].points)

        self.match_dictionary[_id].closed = True

        self.user_pickle_information = []

        for user in self.user_dictionary.keys():
            self.user_pickle_information.append([self.user_dictionary[user]._id, self.user_dictionary[user].points, self.user_dictionary[user].wins, self.user_dictionary[user].losses, self.user_dictionary[user].strikes])

        self.user_pickle_out = open("user.pickle", "wb")
        pickle.dump(self.user_pickle_information, self.user_pickle_out)
        self.user_pickle_out.close()

        self.match_pickle_out = open("match.pickle", "wb")
        pickle.dump(match_counter, self.match_pickle_out)
        self.match_pickle_out.close()


    # dont call function if ID not in match_dictionary.keys()
    def matchAnalysis(self, info):
        _id = int(info[0])
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

        self.character_stats[b1][0] += 1
        self.character_stats[b2][0] += 1
        self.character_stats[b3][0] += 1
        self.character_stats[b4][0] += 1

        self.character_stats[p1][1] += 1
        self.character_stats[p2][1] += 1
        self.character_stats[p3][1] += 1
        self.character_stats[p4][1] += 1
        self.character_stats[p5][1] += 1
        self.character_stats[p6][1] += 1

        if self.match_dictionary[_id].team1_win_votes >= 4:
            self.character_stats[p1][2] += 1
            self.character_stats[p2][2] += 1
            self.character_stats[p3][2] += 1
            self.character_stats[p4][3] += 1
            self.character_stats[p5][3] += 1
            self.character_stats[p6][3] += 1
        elif self.match_dictionary[_id].team2_win_votes >= 4:
            self.character_stats[p1][3] += 1
            self.character_stats[p2][3] += 1
            self.character_stats[p3][3] += 1
            self.character_stats[p4][2] += 1
            self.character_stats[p5][2] += 1
            self.character_stats[p6][2] += 1

        self.character_stats['stat counter'] += 2

        self.stats_pickle_out = open("stats.pickle", "wb")
        pickle.dump(self.character_stats, self.stats_pickle_out)
        self.stats_pickle_out.close()


    def matchPickBan(self, info):
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

        self.character_stats[b1][0] += 1
        self.character_stats[b2][0] += 1
        self.character_stats[b3][0] += 1
        self.character_stats[b4][0] += 1

        self.character_stats[p1][1] += 1
        self.character_stats[p2][1] += 1
        self.character_stats[p3][1] += 1
        self.character_stats[p4][1] += 1
        self.character_stats[p5][1] += 1
        self.character_stats[p6][1] += 1

        self.character_stats['stat counter'] += 2

        self.stats_pickle_out = open("stats.pickle", "wb")
        pickle.dump(self.character_stats, self.stats_pickle_out)
        self.stats_pickle_out.close()

