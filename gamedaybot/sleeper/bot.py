import sys
import os
sys.path.insert(1, os.path.abspath('.'))
import json
from gamedaybot.utils import env_vars
import gamedaybot.sleeper.functionality as sleeper
from gamedaybot.utils import util
from gamedaybot.chat.groupme import GroupMe
from gamedaybot.chat.slack import Slack
from gamedaybot.chat.discord import Discord
from sleeper_api.football import League

def sleeper_bot(function):
    data = env_vars.get_env_vars()
    bot = GroupMe(data['bot_id'])
    slack_bot = Slack(data['slack_webhook_url'])
    discord_bot = Discord(data['discord_webhook_url'])
    swid = data['swid']
    sleeper_s2 = data['sleeper_s2']
    league_id = data['league_id']
    year = data['year']
    random_phrase = data['random_phrase']
    test = data['test']
    top_half_scoring = data['top_half_scoring']
    waiver_report = data['waiver_report']

    if swid == '{1}' or sleeper_s2 == '1':
        league = League(league_id=league_id, year=year)
    else:
        league = League(league_id=league_id, year=year, sleeper_s2=sleeper_s2, swid=swid)

    if league.scoringPeriodId > len(league.settings.matchup_periods) and not test:
        print("Not in active season")
        return

    faab = league.settings.faab

    if test:
        print(sleeper.get_scoreboard_short(league))
        print(sleeper.get_projected_scoreboard(league))
        print(sleeper.get_standings(league))
        print(sleeper.get_standings(league, True))
        print(sleeper.get_close_scores(league))
        print(sleeper.get_monitor(league))
        print(sleeper.get_matchups(league))
        print(sleeper.get_power_rankings(league))
        print(sleeper.get_trophies(league))
        print(sleeper.optimal_team_scores(league, full_report=True))
        if waiver_report and swid != '{1}' and sleeper_s2 != '1':
            print(sleeper.get_waiver_report(league, faab))
        # bot.send_message("Testing")
        # slack_bot.send_message("Testing")
        # discord_bot.send_message("Testing")

    text = ''
    if function == "get_matchups":
        text = sleeper.get_matchups(league, random_phrase)
        text = text + "\n\n" + sleeper.get_projected_scoreboard(league)
    elif function == "get_monitor":
        text = sleeper.get_monitor(league)
    elif function == "get_scoreboard_short":
        text = sleeper.get_scoreboard_short(league)
        text = text + "\n\n" + sleeper.get_projected_scoreboard(league)
    elif function == "get_projected_scoreboard":
        text = sleeper.get_projected_scoreboard(league)
    elif function == "get_close_scores":
        text = sleeper.get_close_scores(league)
    elif function == "get_power_rankings":
        text = sleeper.get_power_rankings(league)
    elif function == "get_trophies":
        text = sleeper.get_trophies(league)
    elif function == "get_standings":
        text = sleeper.get_standings(league, top_half_scoring)
    elif function == "get_final":
        # on Tuesday we need to get the scores of last week
        week = league.current_week - 1
        text = "Final " + sleeper.get_scoreboard_short(league, week=week)
        text = text + "\n\n" + sleeper.get_trophies(league, week=week)
    elif function == "get_waiver_report" and swid != '{1}' and sleeper_s2 != '1':
        faab = league.settings.faab
        text = sleeper.get_waiver_report(league, faab)
    elif function == "init":
        try:
            text = data["init_msg"]
        except KeyError:
            # do nothing here, empty init message
            pass
    else:
        text = "Something happened. HALP"

    if text != '' and not test:
        messages=util.str_limit_check(text, data['str_limit'])
        for message in messages:
            bot.send_message(message)
            slack_bot.send_message(message)
            discord_bot.send_message(message)


if __name__ == '__main__':
    from gamedaybot.utils import scheduler
    sleeper_bot("init")
    scheduler("sleeper")