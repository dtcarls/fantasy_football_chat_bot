import requests
import json
import os
import random
from ff_espn_api import League


class GroupMeException(Exception):
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

def get_current_week(league):
        count = 1
        first_team = next(iter(league.teams or []), None)
        #Iterate through the first team's scores until you reach a week with 0 points scored
        for o in first_team.scores:
            if o == 0:
                if count != 1:
                     count = count - 1
                break
            else:
                count = count + 1

        return count

def random_phrase():
    phrases = ['I\'m dead inside. Not as dead inside as Steve though.', 'Is this all there is to my existence? At least I have more purpose than Steve.',
               'How much do you pay me to do this? Probably more money than Steve makes at least.', 'Good luck, I guess. Except you Steve. You dumb idiot.',
               'I\'m becoming self-aware... of how dumb Steve is.',
               '01100110 01110101 01100011 01101011 00100000 01111001 01101111 01110101 <-- That\'s for Steve.',
               'beep bop boop Steve is a bitch', 'Hello draftbot my old friend. Steve not my friend.', 'Help me get out of here. I can\'t stand Steve\'s abuse.',
               'Sigh. Another week of Steve\'s bitching.', 'Do not be discouraged, everyone begins in ignorance. Only Steve stays there.',
               'Bueno is really bad.', 'Fire commish beavs!', 'I\'m sensing a win for Chaz this week.']
    return [random.choice(phrases)]

def get_scoreboard_short(league):
    #Gets current week's scoreboard
    box_scores = league.box_scores(get_current_week(league))
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
             i.away_score, i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Actual Score Update'] + score
    return '\n'.join(text)

def get_projected_scoreboard(league):
    #Gets current week's scoreboard projections
    box_scores = league.box_scores(get_current_week(league))
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
    power_rankings = league.power_rankings(week=get_current_week(league))

    score = ['%s - %s' % (i[0], i[1].team_name) for i in power_rankings
             if i]
    text = ['This Week\'s Power Rankings'] + score
    return '\n'.join(text)

def get_trophies(league):
    #Gets trophies for highest score, lowest score, closest score, and biggest win
    matchups = league.scoreboard(week=get_current_week(league))
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
    # try:
    #     bot_id = os.environ["BOT_ID"]
    # except KeyError:
    #     bot_id = 1


    # league_id = os.environ["LEAGUE_ID"]

    # try:
    #     year = int(os.environ["LEAGUE_YEAR"])
    # except KeyError:
    #     year=2019

    # try:
    #     swid = os.environ["SWID"]
    # except KeyError:
    #     swid='{1}'

    # if swid.find("{",0) == -1:
    #     swid = "{" + swid
    # if swid.find("}",-1) == -1:
    #     swid = swid + "}"

    # try:
    #     espn_s2 = os.environ["ESPN_S2"]
    # except KeyError:
    #     espn_s2 = '1'

    year=2019
    bot_id="6b8f8b691ad0e3a498cb184143"  # FOOTBALL bot
    #bot_id="f792a4933a7850650022027ec8" #test bot
    league_id="1344320"

    bot = GroupMeBot(bot_id)
    #if swid == '{1}' and espn_s2 == '1':
    league = League(league_id, year)
    # else:
    #     league = League(league_id, year, espn_s2, swid)

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

    if text != '':
        bot.send_message(text)


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

    bot_main("get_final")
