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


def get_scoreboard(league_id, year):
    '''Gets current week's scoreboard'''
    league = League(league_id, year)
    matchups = league.scoreboard()
    score = ['%s(%s) %s - %s %s(%s)' % (i.home_team, i.home_team.team_abbrev, i.home_score,
             i.away_score, i.away_team, i.away_team.team_abbrev) for i in matchups
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)


def main():
    bot_id = os.environ["BOT_ID"]
    league_id = os.environ["LEAGUE_ID"]
    year = os.environ["LEAGUE_YEAR"]
    bot = GroupMeBot(bot_id)
    text = get_scoreboard(league_id, year)
    bot.send_message(text)


if __name__ == '__main__':
    main()
