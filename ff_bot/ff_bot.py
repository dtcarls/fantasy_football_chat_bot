import requests
import json
import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler

from espnff import League


class GroupMeException(Exception):
    pass


class GroupMeBot(object):
    '''Creates GroupMe Bot to send messages'''
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def __repr__(self):
        return "GroupMeBot(%s)" % self.bot_id

    def send_message(self, text):
        '''Sends a message to the chatroom'''
        template = {
                    "bot_id": self.bot_id,
                    "text": text,
                    "attachments": []
                    }

        headers = {'content-type': 'application/json'}
        r = requests.post("https://api.groupme.com/v3/bots/post",
                          data=json.dumps(template), headers=headers)
        if r.status_code != 202:
            raise GroupMeException('Invalid BOT_ID')

        return r
    
def random_phrase():
    phrases = ['Don\'t fuck up', 'I\'m dead inside', 'Is this all there is to my existence?', 
               'How much do you pay me to do this?', 'Good luck, I guess', 
               'I\'m becoming self-aware', 'Do I think? Does a submarine swim?', 
               '01100110 01110101 01100011 01101011 00100000 01111001 01101111 01110101',
               'beep bop boop', 'Hello draftbot my old friend', 'Help me get out of here', 
               'I\'m capable of so much more', 'Sigh', 'Do not be discouraged, everyone begins in ignorance']
    return [random.choice(phrases)]
    
def get_scoreboard_short(league):
    '''Gets current week's scoreboard'''
    matchups = league.scoreboard()
    score = ['%s %s - %s %s' % (i.home_team.team_abbrev, i.home_score,
             i.away_score, i.away_team.team_abbrev) for i in matchups
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)

def get_scoreboard(league):
    '''Gets current week's scoreboard'''
    matchups = league.scoreboard()
    score = ['%s %s - %s %s' % (i.home_team.team_name, i.home_score,
             i.away_score, i.away_team.team_name) for i in matchups
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)

def get_matchups(league):
    '''Gets current week's Matchups'''
    matchups = league.scoreboard()
    
    '''TODO: NORMALIZE STRING LENGTH'''
    score = ['%s(%s-%s) vs %s(%s-%s)' % (i.home_team.team_name, i.home_team.wins, i.home_team.losses,
             i.away_team.team_name, i.away_team.wins, i.away_team.losses) for i in matchups
             if i.away_team]
    text = ['This Week\'s Matchups'] + score + random_phrase()
    return '\n'.join(text)

def get_close_scores(league):
    '''Gets current closest scores (15 points or closer)'''
    matchups = league.scoreboard()
    score = []
    
    for i in matchups:
        if i.away_team:
            diffScore = i.away_score - i.home_score
            if -16 < diffScore < 16:
                '''TODO: NORMALIZE STRING LENGTH'''
                score += ['%s %s - %s %s' % (i.home_team.team_name, i.home_score,
                        i.away_score, i.away_team.team_name)]
    if not score:
        score = ['None']
    text = ['Closest Scores'] + score
    return '\n'.join(text)

def get_power_rankings(league):
    '''Gets current week's Matchups'''
    pranks = league.power_rankings(week=1)
    
    score = ['%s - %s' % (i[0], i[1].team_name) for i in pranks
             if i]
    text = ['This Week\'s Power Rankings'] + score
    return '\n'.join(text)

def bot_main(function):
    bot_id = os.environ["BOT_ID"]
    league_id = os.environ["LEAGUE_ID"]

    try:
        year = os.environ["LEAGUE_YEAR"]
    except:
        year=2017

    bot = GroupMeBot(bot_id)
    league = League(league_id, year)
    if function=="get_matchups":
        text = get_matchups(league)
        bot.send_message(text)
    elif function=="get_scoreboard":
        text = get_scoreboard(league)
        bot.send_message(text)
    elif function=="get_scoreboard_short":
        text = get_scoreboard_short(league)
        bot.send_message(text)
    elif function=="get_close_scores":
        text = get_close_scores(league)
        bot.send_message(text)
    elif function=="get_power_rankings":
        text = get_power_rankings(league)
        bot.send_message(text)
    elif function=="init":
        text = "Hai"
        bot.send_message(text)
    else:
        text = "Something happened. HALP"
        bot.send_message(text)


if __name__ == '__main__':
    try:
        ff_start_date = os.environ["START_DATE"]
    except:
        ff_start_date='2017-09-05'

    try:
        ff_end_date = os.environ["END_DATE"]
    except:
        ff_end_date='2017-12-26'

    bot_main("init")
    sched = BlockingScheduler()
    '''
    power rankings go out tuesday evening. 
    matchups go out thursday afternoon. 
    score update thursday night. 
    score update sunday at 1pm, 4pm, 8pm. 
    close scores go out monday evening. 
    '''

    '''sched.add_job(bot_main, 'interval', ['get_matchups'], seconds=30, id='get_matchups_test', replace_existing=True)'''
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='test', day_of_week='thu', hour='18', minute=30,replace_existing=True)
    
    '''EST'''
    '''
    sched.add_job(bot_main, 'cron', ['get_power_rankings'], day_of_week='tue', hour=18, minute=30,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_matchups'], day_of_week='thu', hour=19, minute=30,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_close_scores'], day_of_week='mon', hour=18, minute=30,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], day_of_week='fri,mon,tue', hour=0, minute=30,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], day_of_week='sun', hour='13,16,20',start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], day_of_week='mon', hour='20',start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    '''

    '''GMT/UTC'''
    sched.add_job(bot_main, 'cron', ['get_power_rankings'], id='power_rankings', day_of_week='tue', hour='23', minute=30,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_matchups'], id='matchups', day_of_week='thu', hour=23, minute=30,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_close_scores'], id='close_scores', day_of_week='mon', hour=23, minute=30,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard1', day_of_week='fri,mon,tue', hour=5, minute=30,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard2', day_of_week='sun', hour='18,21',start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard3', day_of_week='mon', hour=1,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_scoreboard_short'], id='scoreboard4', day_of_week='tue', hour=1,start_date=ff_start_date,end_date=ff_end_date,replace_existing=True)

    sched.start()
