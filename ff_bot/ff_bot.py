import requests
import json
import os
import random
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler
from espn_api.football import League


class GroupMeException(Exception):
    pass


class SlackException(Exception):
    pass


class DiscordException(Exception):
    pass


class GroupMeBot(object):
    # Creates GroupMe Bot to send messages
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def __repr__(self):
        return "GroupMeBot(%s)" % self.bot_id

    def send_message(self, text):
        # Sends a message to the chatroom
        template = {
            "bot_id": self.bot_id,
            "text": text, #limit 1000 chars
            "attachments": []
        }

        headers = {'content-type': 'application/json'}

        if self.bot_id not in (1, "1", ''):
            r = requests.post("https://api.groupme.com/v3/bots/post",
                              data=json.dumps(template), headers=headers)
            if r.status_code != 202:
                raise GroupMeException(r.content)

            return r


class SlackBot(object):
    # Creates GroupMe Bot to send messages
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def __repr__(self):
        return "Slack Webhook Url(%s)" % self.webhook_url

    def send_message(self, text):
        # Sends a message to the chatroom
        message = "```{0}```".format(text)
        template = {
            "text": message #limit 40000
        }

        headers = {'content-type': 'application/json'}

        if self.webhook_url not in (1, "1", ''):
            r = requests.post(self.webhook_url,
                              data=json.dumps(template), headers=headers)

            if r.status_code != 200:
                raise SlackException(r.content)

            return r


class DiscordBot(object):
    # Creates Discord Bot to send messages
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def __repr__(self):
        return "Discord Webhook Url(%s)" % self.webhook_url

    def send_message(self, text):
        # Sends a message to the chatroom
        message = "```{0}```".format(text)
        template = {
            "content": message #limit 3000 chars
        }

        headers = {'content-type': 'application/json'}

        if self.webhook_url not in (1, "1", ''):
            r = requests.post(self.webhook_url,
                              data=json.dumps(template), headers=headers)

            if r.status_code != 204:
                print(r.content)
                raise DiscordException(r.content)

            return r


def get_random_phrase():
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


def get_scoreboard_short(league, week=None):
    # Gets current week's scoreboard
    box_scores = league.box_scores(week=week)
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
                                    i.away_score, i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)


def get_projected_scoreboard(league, week=None):
    # Gets current week's scoreboard projections
    box_scores = league.box_scores(week=week)
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, get_projected_total(i.home_lineup),
                                    get_projected_total(i.away_lineup), i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Approximate Projected Scores'] + score
    return '\n'.join(text)


def get_standings(league, top_half_scoring, week=None):
    standings_txt = ''
    teams = league.teams
    standings = []
    if not top_half_scoring:
        standings = league.standings()
        standings_txt = [f"{pos + 1}: {team.team_name} ({team.wins}-{team.losses})" for
                         pos, team in enumerate(standings)]
    else:
        top_half_totals = {t.team_name: 0 for t in teams}
        if not week:
            week = league.current_week
        for w in range(1, week):
            top_half_totals = top_half_wins(league, top_half_totals, w)

        for t in teams:
            wins = top_half_totals[t.team_name] + t.wins
            standings.append((wins, t.losses, t.team_name))

        standings = sorted(standings, key=lambda tup: tup[0], reverse=True)
        standings_txt = [f"{pos + 1}: {team_name} ({wins}-{losses}) (+{top_half_totals[team_name]})" for
                         pos, (wins, losses, team_name) in enumerate(standings)]
    text = ["Current Standings:"] + standings_txt

    return "\n".join(text)


def top_half_wins(league, top_half_totals, week):
    box_scores = league.box_scores(week=week)

    scores = [(i.home_score, i.home_team.team_name) for i in box_scores] + \
        [(i.away_score, i.away_team.team_name) for i in box_scores if i.away_team]

    scores = sorted(scores, key=lambda tup: tup[0], reverse=True)

    for i in range(0, len(scores)//2):
        points, team_name = scores[i]
        top_half_totals[team_name] += 1

    return top_half_totals


def get_projected_total(lineup):
    total_projected = 0
    for i in lineup:
        if i.slot_position != 'BE' and i.slot_position != 'IR':
            if i.points != 0 or i.game_played > 0:
                total_projected += i.points
            else:
                total_projected += i.projected_points
    return total_projected


def all_played(lineup):
    for i in lineup:
        if i.slot_position != 'BE' and i.slot_position != 'IR' and i.game_played < 100:
            return False
    return True


def get_monitor(league):
    box_scores = league.box_scores()
    monitor = []
    text = ''
    for i in box_scores:
        monitor += scan_roster(i.home_lineup, i.home_team)
        monitor += scan_roster(i.away_lineup, i.away_team)

    if monitor:
        text = ['Starting Players to Monitor: '] + monitor
    else:
        text = ['No Players to Monitor this week. Good Luck!']
    return '\n'.join(text)


def scan_roster(lineup, team):
    count = 0
    players = []
    for i in lineup:
        if i.slot_position != 'BE' and i.slot_position != 'IR' and \
            i.injuryStatus != 'ACTIVE' and i.injuryStatus != 'NORMAL' \
                and i.game_played == 0:

            count += 1
            player = i.position + ' ' + i.name + ' - ' + i.injuryStatus.title().replace('_', ' ')
            players += [player]

    list = ""
    report = ""

    for p in players:
        list += p + "\n"

    if count > 0:
        s = '%s: \n%s \n' % (team.team_name, list[:-1])
        report = [s.lstrip()]

    return report


def scan_inactives(lineup, team):
    count = 0
    players = []
    for i in lineup:
        if (i.slot_position != 'BE' and i.slot_position != 'IR') \
            and (i.injuryStatus == 'OUT' or i.injuryStatus == 'DOUBTFUL' or i.projected_points <= 0) \
                and i.game_played == 0:
                    count += 1
                    players += ['%s %s - %s, %d pts' %
                                (i.position, i.name, i.injuryStatus.title().replace('_', ' '), i.projected_points)]

    inactive_list = ""
    inactives = ""
    for p in players:
        inactive_list += p + "\n"
    if count > 0:
        s = '%s likely inactive starting player(s): \n%s \n' % (team.team_name, inactive_list[:-1])
        inactives = [s.lstrip()]

    return inactives


def get_matchups(league, random_phrase, week=None):
    # Gets current week's Matchups
    matchups = league.box_scores(week=week)

    score = ['%s(%s-%s) vs %s(%s-%s)' % (i.home_team.team_name, i.home_team.wins, i.home_team.losses,
                                         i.away_team.team_name, i.away_team.wins, i.away_team.losses) for i in matchups
             if i.away_team]

    text = ['Matchups'] + score
    if random_phrase:
        text = text + get_random_phrase()
    return '\n'.join(text)


def get_close_scores(league, week=None):
    # Gets current closest scores (15.999 points or closer)
    matchups = league.box_scores(week=week)
    score = []

    for i in matchups:
        if i.away_team:
            diffScore = i.away_score - i.home_score
            if (-16 < diffScore <= 0 and not all_played(i.away_lineup)) or (0 <= diffScore < 16 and not all_played(i.home_lineup)):
                score += ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
                                                 i.away_score, i.away_team.team_abbrev)]
    if not score:
        return('')
    text = ['Close Scores'] + score
    return '\n'.join(text)


def get_waiver_report(league, faab):
    activities = league.recent_activity(50)
    report = []
    today = date.today().strftime('%Y-%m-%d')
    text = ''

    for activity in activities:
        actions = activity.actions
        d2 = date.fromtimestamp(activity.date/1000).strftime('%Y-%m-%d')
        if d2 == today:  # only get waiver activites from today
            if len(actions) == 1 and actions[0][1] == 'WAIVER ADDED':  # player added, but not dropped
                if faab:
                    s = '%s \nADDED %s %s ($%s)\n' % (actions[0][0].team_name,
                                                      actions[0][2].position, actions[0][2].name, actions[0][3])
                else:
                    s = '%s \nADDED %s %s\n' % (actions[0][0].team_name, actions[0][2].position, actions[0][2].name)
                report += [s.lstrip()]
            elif len(actions) > 1:
                if actions[0][1] == 'WAIVER ADDED' or actions[1][1] == 'WAIVER ADDED':
                    if actions[0][1] == 'WAIVER ADDED':
                        if faab:
                            s = '%s \nADDED %s %s ($%s)\nDROPPED %s %s\n' % (
                                actions[0][0].team_name, actions[0][2].position, actions[0][2].name, actions[0][3], actions[1][2].position, actions[1][2].name)
                        else:
                            s = '%s \nADDED %s %s\nDROPPED %s %s\n' % (
                                actions[0][0].team_name, actions[0][2].position, actions[0][2].name, actions[1][2].position, actions[1][2].name)
                    else:
                        if faab:
                            s = '%s \nADDED %s %s ($%s)\nDROPPED %s %s\n' % (
                                actions[0][0].team_name, actions[1][2].position, actions[1][2].name, actions[1][3], actions[0][2].position, actions[0][2].name)
                        else:
                            s = '%s \nADDED %s %s\nDROPPED %s %s\n' % (
                                actions[0][0].team_name, actions[1][2].position, actions[1][2].name, actions[0][2].position, actions[0][2].name)
                    report += [s.lstrip()]

    report.reverse()

    if not report:
        report += ['No waiver transactions']
    else:
        text = ['Waiver Report %s: ' % today] + report

    return '\n'.join(text)


def get_power_rankings(league, week=None):
    # power rankings requires an integer value, so this grabs the current week for that
    if not week:
        week = league.current_week
    # Gets current week's power rankings
    # Using 2 step dominance, as well as a combination of points scored and margin of victory.
    # It's weighted 80/15/5 respectively
    power_rankings = league.power_rankings(week=week)

    score = ['%s (%.1f) - %s' % (i[0], i[1].playoff_pct, i[1].team_name) for i in power_rankings
            if i]
    text = ['Power Rankings (Playoff %)'] + score
    return '\n'.join(text)

def get_luckys(league, week=None):
    box_scores = league.box_scores()
    weekly_scores = {}
    for i in box_scores:
        if i.home_score > i.away_score:
            weekly_scores[i.home_team] = [i.home_score,'W']
            weekly_scores[i.away_team] = [i.away_score,'L']
        else:
            weekly_scores[i.home_team] = [i.home_score,'L']
            weekly_scores[i.away_team] = [i.away_score,'W']
    weekly_scores = dict(sorted(weekly_scores.items(), key=lambda item: item[1], reverse=True))

    # losses = 0
    # for t in weekly_scores:
    #     print(t.team_name + ': (' + str(len(weekly_scores)-1-losses) + '-' + str(losses) +')')
    #     losses+=1

    losses = 0
    unlucky_team_name = ''
    unlucky_record = ''
    lucky_team_name = ''
    lucky_record = ''
    num_teams = len(weekly_scores)-1

    for t in weekly_scores:
        if weekly_scores[t][1] == 'L':
            unlucky_team_name = t.team_name
            unlucky_record = str(num_teams-losses) + '-' + str(losses)
            break
        losses += 1

    wins = 0
    weekly_scores = dict(sorted(weekly_scores.items(), key=lambda item: item[1]))
    for t in weekly_scores:
        if weekly_scores[t][1] == 'W':
            lucky_team_name = t.team_name
            lucky_record = str(wins) + '-' + str(num_teams - wins)
            break
        wins += 1

    lucky_str = ['🍀 Lucky 🍀']+['%s was %s against the league, but still got the win' % (lucky_team_name, lucky_record)]
    unlucky_str = ['😡 Unlucky 😡']+['%s was %s against the league, but still took an L' % (unlucky_team_name, unlucky_record)]
    return(lucky_str + unlucky_str)

def get_trophies(league, week=None):
    # Gets trophies for highest score, lowest score, closest score, and biggest win
    matchups = league.box_scores(week=week)
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
        if i.away_score - i.home_score != 0 and \
                abs(i.away_score - i.home_score) < closest_score:
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

    high_score_str = ['👑 High score 👑']+['%s with %.2f points' % (high_team_name, high_score)]
    low_score_str = ['💩 Low score 💩']+['%s with %.2f points' % (low_team_name, low_score)]
    close_score_str = ['😅 Close win 😅']+['%s barely beat %s by %.2f points' % (close_winner, close_loser, closest_score)]
    blowout_str = ['😱 Blow out 😱']+['%s blew out %s by %.2f points' % (ownerer_team_name, blown_out_team_name, biggest_blowout)]

    text = ['Trophies of the week:'] + high_score_str + low_score_str + blowout_str + close_score_str + get_luckys(league)
    return '\n'.join(text)


def str_to_bool(check):
    return check.lower() in ("yes", "true", "t", "1")

def str_limit_check(text,limit):
    split_str=[]

    if len(text)>limit:
        part_one=text[:limit].split('\n')
        part_one.pop()
        part_one='\n'.join(part_one)

        part_two=text[len(part_one)+1:]

        split_str.append(part_one)
        split_str.append(part_two)
    else:
        split_str.append(text)

    return split_str

def bot_main(function):
    str_limit = 40000 #slack char limit

    try:
        bot_id = os.environ["BOT_ID"]
        str_limit = 1000
    except KeyError:
        bot_id = 1

    try:
        slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    except KeyError:
        slack_webhook_url = 1

    try:
        discord_webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
        str_limit = 3000
    except KeyError:
        discord_webhook_url = 1

    if (len(str(bot_id)) <= 1 and
        len(str(slack_webhook_url)) <= 1 and
            len(str(discord_webhook_url)) <= 1):
        # Ensure that there's info for at least one messaging platform,
        # use length of str in case of blank but non null env variable
        raise Exception("No messaging platform info provided. Be sure one of BOT_ID,\
                        SLACK_WEBHOOK_URL, or DISCORD_WEBHOOK_URL env variables are set")

    league_id = os.environ["LEAGUE_ID"]

    try:
        year = int(os.environ["LEAGUE_YEAR"])
    except KeyError:
        year = 2022

    try:
        swid = os.environ["SWID"]
    except KeyError:
        swid = '{1}'

    if swid.find("{", 0) == -1:
        swid = "{" + swid
    if swid.find("}", -1) == -1:
        swid = swid + "}"

    try:
        espn_s2 = os.environ["ESPN_S2"]
    except KeyError:
        espn_s2 = '1'

    try:
        test = str_to_bool(os.environ["TEST"])
    except KeyError:
        test = False

    try:
        top_half_scoring = str_to_bool(os.environ["TOP_HALF_SCORING"])
    except KeyError:
        top_half_scoring = False

    try:
        random_phrase = str_to_bool(os.environ["RANDOM_PHRASE"])
    except KeyError:
        random_phrase = False

    try:
        waiver_report = str_to_bool(os.environ["WAIVER_REPORT"])
    except KeyError:
        waiver_report = False

    bot = GroupMeBot(bot_id)
    slack_bot = SlackBot(slack_webhook_url)
    discord_bot = DiscordBot(discord_webhook_url)

    if swid == '{1}' or espn_s2 == '1':
        league = League(league_id=league_id, year=year)
    else:
        league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

    faab = league.settings.faab

    if test:
        print(get_matchups(league, random_phrase))
        print(get_scoreboard_short(league))
        print(get_projected_scoreboard(league))
        print(get_close_scores(league))
        print(get_power_rankings(league))
        print(get_scoreboard_short(league))
        print(get_standings(league, top_half_scoring))
        print(get_power_rankings(league))
        print(get_monitor(league))
        if waiver_report and swid != '{1}' and espn_s2 != '1':
            print(get_waiver_report(league, faab))
        function = "get_final"
        # bot.send_message("Testing")
        # slack_bot.send_message("Testing")
        # discord_bot.send_message("Testing")

    text = ''
    if function == "get_matchups":
        text = get_matchups(league, random_phrase)
        text = text + "\n\n" + get_projected_scoreboard(league)
    elif function == "get_monitor":
        text = get_monitor(league)
    elif function == "get_scoreboard_short":
        text = get_scoreboard_short(league)
        text = text + "\n\n" + get_projected_scoreboard(league)
    elif function == "get_projected_scoreboard":
        text = get_projected_scoreboard(league)
    elif function == "get_close_scores":
        text = get_close_scores(league)
    elif function == "get_power_rankings":
        text = get_power_rankings(league)
    # elif function=="get_waiver_report":
    #     text = get_waiver_report(league)
    elif function == "get_trophies":
        text = get_trophies(league)
    elif function == "get_standings":
        text = get_standings(league, top_half_scoring)
        if waiver_report and swid != '{1}' and espn_s2 != '1':
            text += '\n\n' + get_waiver_report(league, faab)
    elif function == "get_final":
        # on Tuesday we need to get the scores of last week
        week = league.current_week - 1
        text = "Final " + get_scoreboard_short(league, week=week)
        text = text + "\n\n" + get_trophies(league, week=week)
    elif function == "get_waiver_report" and swid != '{1}' and espn_s2 != '1':
        text = get_waiver_report(league, faab)
    elif function == "init":
        try:
            text = os.environ["INIT_MSG"]
        except KeyError:
            # do nothing here, empty init message
            pass
    else:
        text = "Something happened. HALP"

    if text != '' and not test:
        messages=str_limit_check(text, str_limit)
        for message in messages:
            bot.send_message(message)
            slack_bot.send_message(message)
            discord_bot.send_message(message)

    if test:
        # print "get_final" function
        print(text)


if __name__ == '__main__':
    try:
        ff_start_date = os.environ["START_DATE"]
    except KeyError:
        ff_start_date = '2022-09-08'

    try:
        ff_end_date = os.environ["END_DATE"]
    except KeyError:
        ff_end_date = '2023-01-04'

    try:
        my_timezone = os.environ["TIMEZONE"]
    except KeyError:
        my_timezone = 'America/New_York'

    try:
        daily_waiver = str_to_bool(os.environ["DAILY_WAIVER"])
    except KeyError:
        daily_waiver = False

    try:
        monitor_report = str_to_bool(os.environ["MONITOR_REPORT"])
    except KeyError:
        monitor_report = True

    game_timezone = 'America/New_York'
    bot_main("init")
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15*60})

    # close scores (within 15.99 points): monday evening at 6:30pm east coast time.
    # power rankings:                     tuesday evening at 6:30pm local time.
    # trophies:                           tuesday morning at 7:30am local time.
    # standings:                          wednesday morning at 7:30am local time.
    # waiver report:                      wednesday morning at 7:30am local time. (optional)
    # matchups:                           thursday evening at 7:30pm east coast time.
    # score update:                       friday, monday, and tuesday morning at 7:30am local time.
    # player monitor report:              sunday morning at 7:30am local time.
    # score update:                       sunday at 4pm, 8pm east coast time.

    sched.add_job(bot_main, 'cron', ['get_close_scores'], id='close_scores',
                  day_of_week='mon', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_power_rankings'], id='power_rankings',
                  day_of_week='tue', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_final'], id='final',
                  day_of_week='tue', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_standings'], id='standings',
                    day_of_week='wed', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                    timezone=my_timezone, replace_existing=True)
    if daily_waiver:
        sched.add_job(bot_main, 'cron', ['get_waiver_report'], id='waiver_report',
                      day_of_week='mon, tue, thu, fri, sat, sun', hour=7, minute=31, start_date=ff_start_date, end_date=ff_end_date,
                      timezone=my_timezone, replace_existing=True)

    sched.add_job(bot_main, 'cron', ['get_matchups'], id='matchups',
                  day_of_week='thu', hour=19, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard1',
                  day_of_week='fri,mon', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)

    if monitor_report:
        sched.add_job(bot_main, 'cron', ['get_monitor'], id='monitor',
                    day_of_week='sun', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                    timezone=my_timezone, replace_existing=True)

    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard2',
                  day_of_week='sun', hour='16,20', start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)

    print("Ready!")
    sched.start()
