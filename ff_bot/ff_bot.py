import requests
import json
import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from ff_espn_api import League

# ff_espn_api allows current week as 0
CURRENT_WEEK = 0

class GroupMeException(Exception):
    pass

class SlackException(Exception):
    pass

class DiscordException(Exception):
    pass

class GroupMeBot(object):
    #Creates GroupMe Bot to send messages
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def __repr__(self):
        return "GroupMeBot(%s)" % self.bot_id

    def send_message(self, text):
        #Sends a message to the chatroom
        template = {
                    "bot_id": self.bot_id,
                    "text": text,
                    "attachments": []
                    }

        headers = {'content-type': 'application/json'}

        if self.bot_id not in (1, "1", ''):
            r = requests.post("https://api.groupme.com/v3/bots/post",
                              data=json.dumps(template), headers=headers)
            if r.status_code != 202:
                raise GroupMeException('Invalid BOT_ID')

            return r

class SlackBot(object):
    #Creates GroupMe Bot to send messages
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def __repr__(self):
        return "Slack Webhook Url(%s)" % self.webhook_url

    def send_message(self, text):
        #Sends a message to the chatroom
        message = "```{0}```".format(text)
        template = {
                    "text":message
                    }

        headers = {'content-type': 'application/json'}

        if self.webhook_url not in (1, "1", ''):
            r = requests.post(self.webhook_url,
                              data=json.dumps(template), headers=headers)

            if r.status_code != 200:
                raise SlackException('WEBHOOK_URL')

            return r

class DiscordBot(object):
    #Creates Discord Bot to send messages
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def __repr__(self):
        return "Discord Webhook Url(%s)" % self.webhook_url

    def send_message(self, text):
        #Sends a message to the chatroom
        message = "```{0}```".format(text)
        template = {
                    "content":message
                    }

        headers = {'content-type': 'application/json'}

        if self.webhook_url not in (1, "1", ''):
            r = requests.post(self.webhook_url,
                              data=json.dumps(template), headers=headers)

            if r.status_code != 204:
                raise DiscordException('WEBHOOK_URL')

            return r

def random_phrase():
    phrases = ['I\'m dead inside',
               'Is this all there is to my existence?',
               'How much do you pay me to do this?',
               'Good luck, I guess',
               'I\'m becoming self-aware',
               'Do I think? Does a submarine swim?',
               '011011010110000101100100011001010010000001111001011011110111010100100000011001110110111101101111011001110110110001100101',
               'beep bop boop',
               'Hello draftbot my old friend',
               'Help me get out of here',
               'I\'m capable of so much more',
               'Sigh']
    return [random.choice(phrases)]

def get_scoreboard_short(league):
    #Gets current week's scoreboard
    box_scores = league.box_scores(CURRENT_WEEK)
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
             i.away_score, i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Actual Score Update'] + score
    return '\n'.join(text)

def get_projected_scoreboard(league):
    #Gets current week's scoreboard projections
    box_scores = league.box_scores(CURRENT_WEEK)
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, get_projected_total(i.home_lineup),
                                    get_projected_total(i.away_lineup), i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Projected Scores'] + score
    return '\n'.join(text)

def get_projected_total(lineup):
    total_projected = 0
    for i in lineup:
        if i.slot_position != 'BE':
            if i.points != 0:
                total_projected += i.points
            else:
                total_projected += i.projected_points
    return total_projected

def get_matchups(league):
    #Gets current week's Matchups
    matchups = league.scoreboard()

    score = ['%s(%s-%s) vs %s(%s-%s)' % (i.home_team.team_name, i.home_team.wins, i.home_team.losses,
             i.away_team.team_name, i.away_team.wins, i.away_team.losses) for i in matchups
             if i.away_team]
    text = ['This Week\'s Matchups'] + score + random_phrase()
    return '\n'.join(text)

def get_close_scores(league):
    #Gets current closest scores (15.999 points or closer)
    matchups = league.scoreboard()
    score = []

    for i in matchups:
        if i.away_team:
            diffScore = i.away_score - i.home_score
            if -16 < diffScore < 16:
                score += ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
                        i.away_score, i.away_team.team_abbrev)]
    if not score:
        score = ['None']
    text = ['Close Scores'] + score
    return '\n'.join(text)

def get_power_rankings(league):
    #Gets current week's power rankings
    #Using 2 step dominance, as well as a combination of points scored and margin of victory.
    #It's weighted 80/15/5 respectively
    power_rankings = league.power_rankings(week=CURRENT_WEEK)

    score = ['%s - %s' % (i[0], i[1].team_name) for i in power_rankings
             if i]
    text = ['This Week\'s Power Rankings'] + score
    return '\n'.join(text)

def get_trophies(league):
    #Gets trophies for highest score, lowest score, closest score, and biggest win
    matchups = league.scoreboard(week=CURRENT_WEEK)
    low_score = 9999
    low_team_name = ''
    high_score = -1
    high_team_name = ''
    closest_score = 9999
    close_winner = ''
    close_loser = ''
    biggest_blowout = -1
    blown_out_team_name = ''
    ownerer_team_name = ''

    for i in matchups:
        if i.home_score > high_score:
            high_score = i.home_score
            high_team_name = i.home_team.team_name
        if i.home_score < low_score:
            low_score = i.home_score
            low_team_name = i.home_team.team_name
        if i.away_score > high_score:
            high_score = i.away_score
            high_team_name = i.away_team.team_name
        if i.away_score < low_score:
            low_score = i.away_score
            low_team_name = i.away_team.team_name
        if abs(i.away_score - i.home_score) < closest_score:
            closest_score = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                close_winner = i.home_team.team_name
                close_loser = i.away_team.team_name
            else:
                close_winner = i.away_team.team_name
                close_loser = i.home_team.team_name
        if abs(i.away_score - i.home_score) > biggest_blowout:
            biggest_blowout = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                ownerer_team_name = i.home_team.team_name
                blown_out_team_name = i.away_team.team_name
            else:
                ownerer_team_name = i.away_team.team_name
                blown_out_team_name = i.home_team.team_name

    low_score_str = ['Low score: %s with %.2f points' % (low_team_name, low_score)]
    high_score_str = ['High score: %s with %.2f points' % (high_team_name, high_score)]
    close_score_str = ['%s barely beat %s by a margin of %.2f' % (close_winner, close_loser, closest_score)]
    blowout_str = ['%s blown out by %s by a margin of %.2f' % (blown_out_team_name, ownerer_team_name, biggest_blowout)]

    text = ['Trophies of the week:'] + low_score_str + high_score_str + close_score_str + blowout_str
    return '\n'.join(text)

def bot_main(function):
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

    bot = GroupMeBot(bot_id)
    slack_bot = SlackBot(slack_webhook_url)
    discord_bot = DiscordBot(discord_webhook_url)
    if swid == '{1}' and espn_s2 == '1':
        league = League(league_id, year)
    else:
        league = League(league_id, year, espn_s2, swid)

    test = False
    if test:
        print(get_matchups(league))
        print(get_scoreboard_short(league))
        print(get_projected_scoreboard(league))
        print(get_close_scores(league))
        print(get_power_rankings(league))
        print(get_trophies(league))
        function="get_final"
        bot.send_message("Testing")
        slack_bot.send_message("Testing")
        discord_bot.send_message("Testing")

    text = ''
    if function=="get_matchups":
        text = get_matchups(league)
        text = text + "\n" + get_projected_scoreboard(league)
    elif function=="get_scoreboard_short":
        text = get_scoreboard_short(league)
        text = text + "\n" + get_projected_scoreboard(league)
    elif function=="get_projected_scoreboard":
        text = get_projected_scoreboard(league)
    elif function=="get_close_scores":
        text = get_close_scores(league)
    elif function=="get_power_rankings":
        text = get_power_rankings(league)
    elif function=="get_trophies":
        text = get_trophies(league)
    elif function=="get_final":
        text = "Final " + get_scoreboard_short(league)
        text = text + "\n\n" + get_trophies(league)
    elif function=="init":
        try:
            text = os.environ["INIT_MSG"]
        except KeyError:
            #do nothing here, empty init message
            pass
    else:
        text = "Something happened. HALP"

    if text != '' and not test:
        bot.send_message(text)
        slack_bot.send_message(text)
        discord_bot.send_message(text)


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

    game_timezone='America/New_York'
    bot_main("init")
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15*60})

    #power rankings:                     tuesday evening at 6:30pm local time.
    #matchups:                           thursday evening at 7:30pm east coast time.
    #close scores (within 15.99 points): monday evening at 6:30pm east coast time.
    #trophies:                           tuesday morning at 7:30am local time.
    #score update:                       friday, monday, and tuesday morning at 7:30am local time.
    #score update:                       sunday at 4pm, 8pm east coast time.

    sched.add_job(bot_main, 'cron', ['get_power_rankings'], id='power_rankings',
        day_of_week='tue', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=my_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_matchups'], id='matchups',
        day_of_week='thu', hour=19, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=game_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_close_scores'], id='close_scores',
        day_of_week='mon', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=game_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_final'], id='final',
        day_of_week='tue', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=my_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard1',
        day_of_week='fri,mon', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=my_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard2',
        day_of_week='sun', hour='16,20', start_date=ff_start_date, end_date=ff_end_date,
        timezone=game_timezone, replace_existing=True)

    print("Ready!")
    sched.start()
