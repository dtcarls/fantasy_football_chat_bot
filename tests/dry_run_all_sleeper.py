import sys
import os
sys.path.insert(1, os.path.abspath('.'))

from sleeper.api import LeagueAPIClient
from sleeper.api import PlayerAPIClient
from sleeper.enum import Sport
import gamedaybot.sleeper.functionality as _sleeper

# league_id = 992179861063786496 #4 man
# league_id = 932291846812827648 # 10 man, no median
league_id = 916114371233808384 # 10 man includes top half wins
week = 1

matchups = LeagueAPIClient.get_matchups_for_week(league_id=league_id, week=week)
users = LeagueAPIClient.get_users_in_league(league_id=league_id)
rosters = LeagueAPIClient.get_rosters(league_id=league_id)
players = PlayerAPIClient.get_all_players(sport=Sport.NFL)

# Create a mapping of user_id to display name
user_id_to_name = {user.user_id: user.display_name for user in users}

# Create a mapping of roster_id to user_id
roster_id_to_user_id = {roster.roster_id: roster.owner_id for roster in rosters}

print(_sleeper.get_scoreboard() + '\n')
print(_sleeper.get_standings() + '\n')
print(_sleeper.get_monitor() + '\n')
print(_sleeper.get_upcoming_matchups() + '\n')
print(_sleeper.get_trophies() + '\n')
print(_sleeper.print_power_rankings(2) + '\n')