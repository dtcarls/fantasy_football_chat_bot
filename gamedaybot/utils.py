import random
import datetime
import os
import urllib.parse as urlparse

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

def str_to_datetime(date_str):
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    # logger.info("Currently converting date_str=" + date_str + " using date_format=" + date_format)
    return datetime.strptime(date_str, date_format)

def currently_in_season():
    current_date = datetime.now()
    season_start_date = None
    try:
        season_start_date = str(os.environ["START_DATE"])
    except KeyError:
        pass
    season_end_date = None
    try:
        season_end_date = str(os.environ["END_DATE"])
    except KeyError:
        pass
    return current_date >= str_to_datetime(season_start_date) and current_date <= str_to_datetime(season_end_date)

def get_league_id(league_url):
    """
    Extract the league ID from the league URL
    :param league_url: The league URL.
    :return: ESPN League ID.
    """
    return urlparse.parse_qs(urlparse.urlparse(league_url).query)['leagueId'][0]