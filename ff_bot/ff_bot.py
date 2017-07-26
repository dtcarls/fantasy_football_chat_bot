import requests
import json
import os

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
    text = ['This Week\'s Matchups'] + score + ['Good Luck!']
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
    pranks = league.power_rankings()
    
    '''score = ['%s(%s-%s) vs %s(%s-%s)' % (i.home_team.team_name, i.home_team.wins, i.home_team.losses,
             i.away_team.team_name, i.away_team.wins, i.away_team.losses) for i in matchups
             if i.away_team]'''
    text = ['This Week\'s Power Rankings'] + pranks
    return '\n'.join(text)

def main():
    bot_id = os.environ["BOT_ID"]
    league_id = os.environ["LEAGUE_ID"]
    year = os.environ["LEAGUE_YEAR"]
    bot = GroupMeBot(bot_id)
    league = League(league_id, year)
    text = get_matchups(league)
    bot.send_message(text)
    '''text = get_scoreboard(league)
    bot.send_message(text)'''
    text = get_scoreboard_short(league)
    bot.send_message(text)
    text = get_close_scores(league)
    bot.send_message(text)
    text = get_power_rankings(league)
    bot.send_message(text)


if __name__ == '__main__':
    main()
