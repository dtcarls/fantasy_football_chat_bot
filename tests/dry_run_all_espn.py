import sys
import os
sys.path.insert(1, os.path.abspath('.'))

from espn_api.football import League
import gamedaybot.espn.season_recap as recap
import gamedaybot.espn.functionality as espn
from gamedaybot.chat.discord import Discord
from gamedaybot.chat.slack import Slack
from gamedaybot.chat.groupme import GroupMe

# LEAGUE_ID = os.environ["LEAGUE_ID"]
# LEAGUE_YEAR = os.environ["LEAGUE_YEAR"]

## Manually populate
LEAGUE_ID = 164483
LEAGUE_YEAR = 2023

league = League(league_id=LEAGUE_ID, year=LEAGUE_YEAR)
print(espn.get_scoreboard_short(league))
print(espn.get_projected_scoreboard(league))
print(espn.get_standings(league))
print(espn.get_close_scores(league))
print(espn.get_monitor(league))
print(espn.get_matchups(league))
print(espn.get_power_rankings(league))
print(espn.get_trophies(league))
print(espn.optimal_team_scores(league, full_report=True))

print(recap.win_matrix(league))
print(recap.trophy_recap(league))

try:
    swid = os.environ["SWID"]
except KeyError:
    swid = '{1}'
try:
    espn_s2 = os.environ["ESPN_S2"]
except KeyError:
    espn_s2 = '1'

if swid != '{1}' and espn_s2 != '1':
    league = League(league_id=LEAGUE_ID, year=LEAGUE_YEAR, espn_s2=espn_s2, swid=swid)
    print(espn.get_waiver_report(league))
    print(espn.get_waiver_report(league, True))

# bot = GroupMe(os.environ['BOT_ID'])
# bot.send_message(recap.trophy_recap(league), file_path='/tmp/season_recap.png')
# bot.send_message("hi", file_path='/tmp/season_recap.png')
# bot.send_message("Testing")

# discord_bot = Discord(os.environ['DISCORD_WEBHOOK_URL'])
# discord_bot.send_message(recap.trophy_recap(league), file_path='/tmp/season_recap.png')
# discord_bot.send_message("Testing")

# slack_bot = Slack(os.environ['SLACK_WEBHOOK_URL'])
# slack_bot.send_message(recap.trophy_recap(league), file_path='/tmp/season_recap.png')
# slack_bot.send_message("Testing")
