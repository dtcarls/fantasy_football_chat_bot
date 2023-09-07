from datetime import datetime
import os
from urllib.parse import urlparse


def str_to_bool(check: str) -> bool:
    """
    Converts a string to a boolean value.

    Parameters
    ----------
    check : str
        The string to be converted to a boolean value.

    Returns
    -------
    bool
        The boolean value of the string.
    """
    return check.lower() in ("yes", "true", "t", "1")


def str_limit_check(text: str, limit: int):
    """
    Splits a string into parts of a maximum length.

    Parameters
    ----------
    text : str
        The text to be split.
    limit : int
        The maximum length of each split string part.

    Returns
    -------
    split_str : List[str]
        A list of strings split by the maximum length.
    """

    split_str = []

    if len(text) > limit:
        part_one = text[:limit].split('\n')
        part_one.pop()
        part_one = '\n'.join(part_one)

        part_two = text[len(part_one) + 1:]

        split_str.append(part_one)
        split_str.append(part_two)
    else:
        split_str.append(text)

    return split_str


def str_to_datetime(date_str: str) -> datetime:
    """
    Converts a string in the format of 'YYYY-MM-DD' to a datetime object.

    Parameters
    ----------
    date_str : str
        The string to be converted to a datetime object.

    Returns
    -------
    datetime
        The datetime object created from the input string.
    """

    date_format = "%Y-%m-%d"
    return datetime.strptime(date_str, date_format)


def currently_in_season(season_start_date=None, season_end_date=None, current_date=datetime.now()):
    """
    Check if the current date is during the football season

    Parameters
    ----------
    season_start_date : str, optional
        The start date of the season in the format "YYYY-MM-DD", by default None
    season_end_date : str, optional
        The end date of the season in the format "YYYY-MM-DD", by default None
    current_date : datetime, optional
        The current date to compare against the season range, by default datetime.now()

    Returns
    -------
    bool
        True if the current date is within the range of dates for football season, False otherwise.

    Raises
    ------
    ValueError
        If the season start or end date is not in the correct format "YYYY-MM-DD"
    """

    try:
        season_start_date = str(os.environ["START_DATE"])
    except KeyError:
        pass

    try:
        season_end_date = str(os.environ["END_DATE"])
    except KeyError:
        pass
    return current_date >= str_to_datetime(season_start_date) and current_date <= str_to_datetime(season_end_date)


def get_league_id(league_url: str) -> str:
    """
    Retrieves the league ID from a given league URL.

    Parameters
    ----------
    league_url : str
        The URL of the league.

    Returns
    -------
    league_id : str
        The league ID extracted from the URL.
    """

    return urlparse.parse_qs(urlparse.urlparse(league_url).query)['leagueId'][0]
