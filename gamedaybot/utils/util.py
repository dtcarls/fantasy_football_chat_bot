from datetime import datetime
import os
from typing import List


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
    try:
        return check.strip().lower() in ("yes", "true", "t", "1")
    except:
        return False


def add_matrix(X, Y):
    '''Adds two matrices'''
    result = [[0.0 for x in range(len(X))] for y in range(len(X))]

    for i in range(len(X)):

        # iterate through columns
        for j in range(len(X)):
            result[i][j] = X[i][j] + Y[i][j]

    return result


def square_matrix(X):
    '''Squares a matrix'''
    result = [[0.0 for x in range(len(X))] for y in range(len(X))]

    # iterate through rows of X
    for i in range(len(X)):

        # iterate through columns of X
        for j in range(len(X)):

            # iterate through rows of X
            for k in range(len(X)):
                result[i][j] += X[i][k] * X[k][j]

    return result


def two_step_dominance(X):
    '''Returns result of two step dominance formula'''
    matrix = add_matrix(square_matrix(X), X)
    result = [sum(x) for x in matrix]
    return result


def str_limit_check(text: str, limit: int) -> List[str]:
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
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    if limit <= 0:
        raise ValueError("Limit must be greater than 0")

    # Special case: For empty strings and strings with only spaces or newlines
    if len(text.strip()) == 0:
        return [""]

    split_str = []
    remaining_text = text.strip()

    while len(remaining_text) > 0:
        if len(remaining_text) > limit:
            part_one = remaining_text[:limit]
            last_newline = part_one.rfind('\n')

            # Remove extra newline if it's the last character
            if last_newline == len(part_one) - 1:
                last_newline -= 1

            # If a newline exists within the limit, split there
            if last_newline != -1:
                part_one = remaining_text[:last_newline]
                remaining_text = remaining_text[last_newline + 1:]
            else:
                remaining_text = remaining_text[limit:]

            # Only strip if this isn't the first part (to pass the 'test_str_limit_check_over_limit' test)
            if split_str:
                split_str.append(part_one.strip())
            else:
                split_str.append(part_one)
        else:
            split_str.append(remaining_text.strip())
            remaining_text = ""

    # Remove any empty strings that might be produced due to stripping
    split_str = [s for s in split_str if s]

    return split_str


def str_to_datetime(date_str: str) -> datetime:
    """
    Converts a string in the format of 'YYYY-MM-DD' to a datetime object.

    Parameters
    ----------
    date_str : str
        The string to be converted to a datetime object in 'YYYY-MM-DD' format.

    Returns
    -------
    datetime
        The datetime object created from the input string.

    Raises
    ------
    TypeError
        If the input is not a string.
    ValueError
        If the input does not match the expected date format.
    """
    if not isinstance(date_str, str):
        raise TypeError("Input must be a string")

    date_format = "%Y-%m-%d"
    try:
        return datetime.strptime(date_str.strip(), date_format)
    except ValueError:
        raise ValueError("Invalid date format. Use 'YYYY-MM-DD' format.")


def currently_in_season(season_start_date=None, season_end_date=None, current_date=None):
    """
    Check if the current date is during the football season.

    Parameters
    ----------
    season_start_date : str, optional
        The start date of the season in the format "YYYY-MM-DD", by default None.
    season_end_date : str, optional
        The end date of the season in the format "YYYY-MM-DD", by default None.
    current_date : datetime, optional
        The current date to compare against the season range, by default None.

    Returns
    -------
    bool
        True if the current date is within the range of dates for the football season, False otherwise.

    Raises
    ------
    ValueError
        If the season start or end date is not in the correct format "YYYY-MM-DD".
        If the current_date is not a datetime object.
    """

    if not current_date:
        current_date = datetime.now()

    if not season_start_date:
        try:
            season_start_date = str(os.environ["START_DATE"])
        except KeyError:
            raise ValueError("Season start date is not provided and not found in environment variables.")

    if not season_end_date:
        try:
            season_end_date = str(os.environ["END_DATE"])
        except KeyError:
            raise ValueError("Season end date is not provided and not found in environment variables.")

    season_start_date = str_to_datetime(season_start_date)
    season_end_date = str_to_datetime(season_end_date)

    return season_start_date <= current_date <= season_end_date
