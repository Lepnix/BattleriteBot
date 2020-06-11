import random

from nail.settings.br_settings import MAP_POOL


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
    def __init__(self, nailchan): # nc is a nailchan instance
        self.players = {}
        self.support_counter = 0

        for player in nailchan.queue_channel:
            if len(self.players) < 6:
                if player[1] == 'Fill' or player[1] == 'DPS':
                    self.players[player[0]] = player[1]
                elif self.support_counter < 2:
                    self.players[player[0]] = player[1]
                    self.support_counter += 1

        for player in self.players:
            if player in [item[0] for item in nailchan.queue_channel]:
                del nailchan.queue_channel[[item[0] for item in nailchan.queue_channel].index(player)]

        self.draft_pool = list(self.players.keys())
        self.team1 = []
        self.team2 = []
        self.match_id = nailchan.match_counter
        self.team1_win_votes = 0
        self.team2_win_votes = 0
        self.drop_votes = 0
        self.map = MAP_POOL[random.randint(0, 15)]
        self.closed = False

        nailchan.purge_voters.clear()

        _max = nailchan.user_dictionary[self.draft_pool[0]].display_rating

        self.captain1 = self.draft_pool[0]

        for player in self.draft_pool:     #finds highest and second highest rated players, makes them captain1 and captain2, and removes them from pool
            nailchan.user_dictionary[player].in_match = True  #sets inmatch to true for each player in the game
            nailchan.user_dictionary[player].last_match_id = self.match_id
            if nailchan.user_dictionary[player].display_rating > _max:
                self.captain1 = player
                _max = nailchan.user_dictionary[player].display_rating

        self.team1.append(self.captain1)
        nailchan.user_dictionary[self.captain1].is_captain1 = True
        self.draft_pool.remove(self.captain1)

        _max = nailchan.user_dictionary[self.draft_pool[0]].display_rating
        self.captain2 = self.draft_pool[0]
        for player in self.draft_pool:
            if nailchan.user_dictionary[player].display_rating > _max:
                self.captain2 = player
                _max = nailchan.user_dictionary[player].display_rating

        self.team2.append(self.captain2)
        nailchan.user_dictionary[self.captain2].is_captain2 = True
        self.draft_pool.remove(self.captain2)

        self.nailchan = nailchan
