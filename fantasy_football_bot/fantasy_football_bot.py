import os

from ff_espn_api import League

from chat_clients.discord import DiscordBot
from chat_clients.groupme import GroupMeBot
from chat_clients.slack import SlackBot

from chat_functions.get_close_scores import get_close_scores
from chat_functions.get_matchups import get_matchups
from chat_functions.get_power_rankings import get_power_rankings
from chat_functions.get_scoreboard_short import get_scoreboard_short
from chat_functions.get_projected_scoreboard import get_projected_scoreboard
from chat_functions.get_trophies import get_trophies

if __name__ == '__main__':
    try:
        ff_start_date = os.environ["START_DATE"]
    except KeyError:
        ff_start_date='2019-09-04'

    try:
        ff_end_date = os.environ["END_DATE"]
    except KeyError:
        ff_end_date='2019-12-30'

    try:
        my_timezone = os.environ["TIMEZONE"]
    except KeyError:
        my_timezone='America/New_York'

    try:
        bot_id = os.environ["BOT_ID"]
    except KeyError:
        bot_id = 1

    try:
        slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    except KeyError:
        slack_webhook_url = 1

    try:
        discord_webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    except KeyError:
        discord_webhook_url = 1

    league_id = os.environ["LEAGUE_ID"]

    try:
        year = int(os.environ["LEAGUE_YEAR"])
    except KeyError:
        year=2019

    try:
        swid = os.environ["SWID"]
    except KeyError:
        swid='{1}'

    if swid.find("{",0) == -1:
        swid = "{" + swid
    if swid.find("}",-1) == -1:
        swid = swid + "}"

    try:
        espn_s2 = os.environ["ESPN_S2"]
    except KeyError:
        espn_s2 = '1'

    game_timezone='America/New_York'

    bot = GroupMeBot(bot_id)
    slack_bot = SlackBot(slack_webhook_url)
    discord_bot = DiscordBot(discord_webhook_url)
    if swid == '{1}' and espn_s2 == '1':
        league = League(league_id, year)
    else:
        league = League(league_id, year, espn_s2, swid)

    test = True
    if test:
        print(get_matchups(league))
        print(get_scoreboard_short(league))
        print(get_projected_scoreboard(league))
        print(get_close_scores(league))
        print(get_power_rankings(league))
        print(get_scoreboard_short(league))
        function="get_final"
        bot.send_message("Testing")
        slack_bot.send_message("Testing")
        discord_bot.send_message("Testing")

    text = ''
    if function=="get_matchups":
        text = get_matchups(league)
        text = text + "\n\n" + get_projected_scoreboard(league)
    elif function=="get_scoreboard_short":
        text = get_scoreboard_short(league)
        text = text + "\n\n" + get_projected_scoreboard(league)
    elif function=="get_projected_scoreboard":
        text = get_projected_scoreboard(league)
    elif function=="get_close_scores":
        text = get_close_scores(league)
    elif function=="get_power_rankings":
        text = get_power_rankings(league)
    elif function=="get_trophies":
        text = get_trophies(league)
    elif function=="get_final":
        # on Tuesday we need to get the scores of last week
        week = league.current_week - 1
        text = "Final " + get_scoreboard_short(league, week=week)
        text = text + "\n\n" + get_trophies(league, week=week)
    elif function=="init":
        try:
            text = os.environ["INIT_MSG"]
        except KeyError:
            #do nothing here, empty init message
            pass
    else:
        text = "Something bad happened. " + function

    if text != '' and not test:
        bot.send_message(text)
        slack_bot.send_message(text)
        discord_bot.send_message(text)

    if test:
        #print "get_final" function
        print(text)
